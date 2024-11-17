import yfinance as yf
import mysql.connector
from datetime import date, timedelta, datetime

def is_weekday(day: object) -> bool:
    """
    param: date object
    functionality: True for weekdays : False for weekend days
    returns: Boolean
    """

    if (isinstance(day, date)):
        if day.weekday() in [5,6]:
            return False
        else:
            return True
    else:
        raise TypeError
    
def option_upload(option_dict: dict) -> None:
    """
    param: list of dictionarys
    functionality: uploads the dictionary data to all the tables in stockScraper database 
    returns: None
    """

    connection = mysql.connector.connect(
        host='localhost',
        user='mainScript',
        password='1234',
        database='stockScraper'
    )
    cursor = connection.cursor()

    # check if the stock already exists in the stocks table
    check_stock_id = 'SELECT stock_id FROM stocks WHERE ticker = %s'
    cursor.execute(check_stock_id, (option_dict['ticker'],))
    result = cursor.fetchone()

    # if the stock already has an id in the database get it or insert the new data 
    if (result):
        stock_id = result[0]
    else:
        # insert into the database new stock data
        query_insert_stocks = 'INSERT INTO stocks (ticker, company_name, sector) VALUES (%s,%s,%s)'
        temp_data = (option_dict['ticker'], option_dict['company name'], option_dict['sector'])
        cursor.execute(query_insert_stocks, temp_data)

        # get new stock_id
        cursor.execute(check_stock_id, (option_dict['ticker'],))
        stock_id = cursor.fetchone()[0]

    # insert data into options contract table
    query_insert_option_contracts = 'INSERT INTO option_contracts (stock_id, expiration_date, strike_price, option_type, contract_symbol) VALUES (%s, %s, %s, %s, %s)'
    stocks_data = (stock_id, option_dict['expiration date'], option_dict['strike price'], option_dict['option type'], option_dict['contract symbol'])
    cursor.execute(query_insert_option_contracts, stocks_data)

    # get option_id from options contract table
    query_select_option_id = 'SELECT option_id FROM option_contracts WHERE contract_symbol = %s'
    options_data = (option_dict['contract symbol'],)
    cursor.execute(query_select_option_id, options_data)
    option_id = cursor.fetchone()[0]

    # insert data into market data table
    query_insert_market_data = 'INSERT INTO market_data (option_id, time_stamp, last_price, bid, ask, volume, open_interest) VALUES (%s, %s, %s, %s, %s, %s, %s)'
    market_data = (option_id, option_dict['time stamp'], option_dict['last price'], option_dict['bid'], option_dict['ask'], option_dict['volume'], option_dict['open interest'])
    cursor.execute(query_insert_market_data, market_data)

    # commit and close connection
    connection.commit()
    cursor.close()
    connection.close()

def get_exp_date(option_dates: tuple[str]) -> str:
    """
    param: tuple of strings
    funcitonality: gets the date that is larger and closest to a week from today
    return: string
    """
    today = date.today()
    week_from_today = str(today + timedelta(weeks=1))

    for opt_date in option_dates:
        if opt_date >= week_from_today:
            return opt_date

def scrape_stock_info(ticker: str) -> list[dict]:
    """
    param: string representing a stock ticker
    funcitonality: scrapes the stock info from yahoo finance
    return: list of dictionarys
    """

    # gets stock info based on a ticker
    stock = yf.Ticker(ticker)
    stock_info = stock.info
    sector = stock_info.get('sector', 'Sector data not available')
    company_name = stock_info.get('longName', 'Company name not available')

    # get the option date >= to todays date
    exp_dates = stock.options
    opt_date = get_exp_date(exp_dates)

    # get the data for the options based on date, seperate into call/put panda dataframes
    option_chain = stock.option_chain(opt_date)
    calls = option_chain[0]
    puts = option_chain[1]

    # sort dataframes by volume, descending
    calls.sort_values(by='volume', ascending=False, inplace=True)
    puts.sort_values(by='volume', ascending=False, inplace=True)

    # get the top 5 of calls/puts
    top_5_calls = calls.head(n=5)
    top_5_puts = puts.head(n=5)

# form important option information in a dictionary and store them in a list 
    options_list = []
    for _, row in top_5_calls.iterrows():
        options_list.append({'ticker': ticker,
                            'company name': company_name,
                            'sector': sector,
                            'expiration date': opt_date,
                            'strike price': row.iloc[2],
                            'option type': 'c',
                            'contract symbol': row.iloc[0],
                            'time stamp': str(row.iloc[1]),
                            'last price': row.iloc[3],
                            'bid': row.iloc[4],
                            'ask': row.iloc[5],
                            'volume': row.iloc[8],
                            'open interest': row.iloc[9]})

    for _, row in top_5_puts.iterrows():
        options_list.append({'ticker': ticker,
                            'company name': company_name,
                            'sector': sector,
                            'expiration date': opt_date,
                            'strike price': row.iloc[2],
                            'option type': 'p',
                            'contract symbol': row.iloc[0],
                            'time stamp': str(row.iloc[1]),
                            'last price': row.iloc[3],
                            'bid': row.iloc[4],
                            'ask': row.iloc[5],
                            'volume': row.iloc[8],
                            'open interest': row.iloc[9]})
    
    return options_list



def main():
    # reads the tickers.txt file and creates a list of tickers
    tickers = None
    with open('tickers.txt', 'r') as fyle:
        tickers = [line.strip() for line in fyle]

    for ticker in tickers:
        # scrape option info
        option_info = scrape_stock_info(ticker)
        
        # upload the info to database 
        for option_dict in option_info:
            option_upload(option_dict)

if __name__ == "__main__":
    main()
