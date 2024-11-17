import yfinance as yf
import mysql.connector
from datetime import date, timedelta, datetime
import requests
from bs4 import BeautifulSoup as bs

def is_weekday(day):
    """
    Input: date object
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
    
def initial_option_upload(lyst):
    """
    Input: list of dictionarys
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

    first_dict = lyst[0]

    # check if the stock already exists in the stocks table
    check_stock_id = 'SELECT stock_id FROM stocks WHERE ticker = %s'
    cursor.execute(check_stock_id, (first_dict['ticker'],))
    result = cursor.fetchone()

    # if the stock already has an id in the database get it or insert the new data 
    if (result):
        stock_id = result[0]
    else:
        # insert into the database new stock data
        query_insert_stocks = 'INSERT INTO stocks (ticker, company_name, sector) VALUES (%s,%s,%s)'
        temp_data = (first_dict['ticker'], first_dict['company name'], first_dict['sector'])
        cursor.execute(query_insert_stocks, temp_data)

        # get new stock_id
        cursor.execute(check_stock_id, (first_dict['ticker'],))
        stock_id = cursor.fetchone()[0]

    # insert data into options contract table
    query_insert_option_contracts = 'INSERT INTO option_contracts (stock_id, expiration_date, strike_price, option_type, contract_symbol) VALUES (%s, %s, %s, %s, %s)'
    stocks_data = (stock_id, first_dict['expiration date'], first_dict['strike price'], first_dict['option type'], first_dict['contract symbol'])
    cursor.execute(query_insert_option_contracts, stocks_data)

    # get option_id from options contract table
    query_select_option_id = 'SELECT option_id FROM option_contracts WHERE contract_symbol = %s'
    options_data = (first_dict['contract symbol'],)
    cursor.execute(query_select_option_id, options_data)
    option_id = cursor.fetchone()[0]

    # insert data into market data table
    query_insert_market_data = 'INSERT INTO market_data (option_id, time_stamp, last_price, bid, ask, volume, open_interest) VALUES (%s, %s, %s, %s, %s, %s, %s)'
    market_data = (option_id, first_dict['time stamp'], first_dict['last price'], first_dict['bid'], first_dict['ask'], first_dict['volume'], first_dict['open interest'])
    cursor.execute(query_insert_market_data, market_data)

    # commit and close connection
    connection.commit()
    cursor.close()
    connection.close()



headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'}

stock_price_url = 'https://finance.yahoo.com/quote/TSLA/'

#r = requests.get(stock_price_url)
#soup = bs(r.text, 'html.parser')

#price = soup.find('fin-streamer', {'class': 'livePrice yf-1tejb6'}).text
#change = soup.find('fin-streamer', {'class': 'priceChange yf-1tejb6'}).text
#change_percent = soup.find('fin-streamer', {'class': 'priceChange yf-1tejb6', 'data-field': 'regularMarketChangePercent'}).text



# options scraping #

today = date.today()
week_from_today = today + timedelta(weeks=1)

# makes week_from_days into a unix tiemstamp for scraping
unix_date = int(datetime.combine(week_from_today, datetime.min.time()).timestamp())

stock_options_url = f'https://finance.yahoo.com/quote/TSLA/options/'

r = requests.get(stock_options_url)
soup = bs(r.text, 'html.parser')

options_table = soup.find('fin-streamer', {'class': 'livePrice yf-1tejb6'})



# yfinance options #
ticker = 'TSLA'

stock = yf.Ticker(ticker)
stock_info = stock.info
exp_dates = stock.options
opt_date = exp_dates[0]

sector = stock_info.get('sector', 'Sector data not available')
company_name = stock_info.get('longName', 'Company name not available')

option_chain = stock.option_chain(opt_date)
calls = option_chain[0]
puts = option_chain[1]

column_names = calls.columns

calls.sort_values(by='volume', ascending=False, inplace=True)
puts.sort_values(by='volume', ascending=False, inplace=True)

top_5_calls = calls.head(n=5)
top_5_puts = puts.head(n=5)

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

initial_option_upload(options_list)
print('success')
