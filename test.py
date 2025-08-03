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


def get_options_strike_prices(ticker: str, expiration_date, step_size=2.5) -> list[dict]:
    """returns a list of option strike prices based on the ticker and option type (parameters)
    :param ticker: The ticker of a single stock
    :param opt_call: A boolean value based on if you want strike prices based on calls or puts
    :param step_size: The step size between option contracts
    """
    def contract_round(num: float, rounding_number) -> float:
        return round(num / rounding_number) * rounding_number
    
    option_data = [None]

    # gets the closest option contract price based on the current prices on contract step size parameter
    stock_price = float(rh.stocks.get_latest_price(ticker)[0])
    contract_price = contract_round(stock_price, step_size)

    # loop that increments contract price by step size unitl contract data is obtained
    contract_data = rh.options.find_options_by_expiration_and_strike(ticker, expiration_date, contract_price)
    while not contract_data:
        contract_price += step_size
        contract_data = rh.options.find_options_by_expiration_and_strike(ticker, expiration_date, contract_price)

    # loop that increments prices by step size to retrieve contract data for 20 contracts centered around original contract price
    high_contract_price = contract_price
    low_contract_price = contract_price
    contract_count = 0
    while (contract_count < 20):
        high_contract_data = rh.options.find_options_by_expiration_and_strike(ticker, expiration_date, high_contract_price)
        low_contract_data = rh.options.find_options_by_expiration_and_strike(ticker, expiration_date, low_contract_price)
        if high_contract_data and low_contract_data:
            for contract in high_contract_data:
                option_data.append(contract)
            for contract in low_contract_data:
                option_data.append(contract)
            contract_count += 1
        else:
            high_contract_price += step_size
            low_contract_price -= step_size

    # increment the prices by step size before entering loops
    high_contract_price += step_size
    low_contract_price -= step_size

    # loop that increments the high price and get data on 30 mroe call contracts
    contract_count = 0
    while (contract_count < 30):
        high_contract_data = rh.options.find_options_by_expiration_and_strike(ticker, expiration_date, high_contract_price, 'call')
        if high_contract_data:
            for contract in high_contract_data:
                option_data.append(contract)
            contract_count += 1
        else:
            high_contract_price += step_size

    # loop that increments the low price to get data on 30 more put contracts
    contract_count = 0
    while (contract_count < 30):
        low_contract_data = rh.options.find_options_by_expiration_and_strike(ticker, expiration_date, low_contract_price, 'put')
        if low_contract_data:
            for contract in low_contract_data:
                option_data.append(contract)
        else:
            low_contract_data -= step_size
    
    return option_data

#x = get_options_strike_prices(ticker)
x = rh.options.find_options_by_expiration_and_strike(ticker, test_option, 300.75)
print(x)