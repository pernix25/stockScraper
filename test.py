import robin_stocks.robinhood as rh
import pyotp
 
# read file with robinhood login info and create variables
with open('sensitive_information.txt', 'r') as login_file:
    file_lines = login_file.readlines()

    RH_USER = file_lines[0].strip()
    RH_PASS = file_lines[1].strip()
    RH_CODE = file_lines[2].strip()

# login into robinhood
code = pyotp.TOTP(RH_CODE).now()
rh.login(RH_USER, RH_PASS, mfa_code=code)

ticker = 'TSLA'

opts = rh.options
all_options = opts.get_chains(ticker)

def get_exp_dates(ticker: str) -> list: 
    """gets the exipration dates for a tradable options stock"""
    return rh.options.get_chains(ticker)['expiration_dates']

test_option = get_exp_dates(ticker)[2]

#data = opts.find_options_by_expiration(ticker, test_option, info='strike_price') # 'mark_price', 'open_interest', 'volume', 'symbol', 'implied_volatility', 'delta', 'gamma', 'rho', 'theta', 'vega'])
#data = opts.find_options_by_expiration_and_strike(ticker, test_option, 310)
#print(data)


def get_options_strike_prices(ticker: str, expiration_date, step_size=2.5) -> list:
    """returns a list of option strike prices based on the ticker and option type (parameters)
    :param ticker: The ticker of a single stock
    :param opt_call: A boolean value based on if you want strike prices based on calls or puts
    :param step_size: The step size between option contracts
    """
    def round_2_point_5(num: float) -> float:
        return round(num / 2.5) * 2.5
    
    option_data = [None]

    stock_price = float(rh.stocks.get_latest_price(ticker)[0])
    stock_price = round_2_point_5(stock_price)

    curr_price_data = rh.options.find_options_by_expiration_and_strike(ticker, expiration_date, stock_price)
    if curr_price_data:
        for data in curr_price_data:
            option_data.append(data)
    else:
        while not curr_price_data:
            stock_price += step_size
            curr_price_data = rh.options.find_options_by_expiration_and_strike(ticker, expiration_date, stock_price)
        for data in curr_price_data:
            option_data.append(data)

    for i in range(1, 21):
        pos_temp_stock_price = stock_price + (step_size * i)
        neg_temp_stock_price = stock_price - (step_size * i)

        pos_prices = rh.options.find_options_by_expiration_and_strike(ticker, expiration_date, pos_temp_stock_price)
        neg_prices = rh.options.find_options_by_expiration_and_strike(ticker, expiration_date, neg_temp_stock_price)

        if not pos_prices and not neg_prices:
            while not pos_prices:
                pos_temp_stock_price += step_size
        elif not pos_prices:
            pass
        elif not neg_prices:
            pass
        else:
            pass

    return option_data

#x = get_options_strike_prices(ticker)
x = rh.options.find_options_by_expiration_and_strike(ticker, test_option, 300.75)
print(x)