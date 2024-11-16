import yfinance as yf
import mysql.connector
from datetime import date, timedelta, datetime
import requests
from bs4 import BeautifulSoup as bs

def is_weekday(day):
    """take a date object and returns true for weekdays : false for weekend days"""
    if (isinstance(day, date)):
        if day.weekday() in [5,6]:
            return False
        else:
            return True
    else:
        raise TypeError
    
def option_upload():
    connection = mysql.connector.connect(
        host='localhost',
        user='mainScript',
        password='1234',
        database='stockScraper'
    )



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
exp_dates = stock.options
opt_date = exp_dates[0]

option_chain = stock.option_chain(opt_date)
calls = option_chain[0]
puts = option_chain[1]

column_names = calls.columns

calls.sort_values(by='volume', ascending=False, inplace=True)
puts.sort_values(by='volume', ascending=False, inplace=True)


top_5_calls = calls.head(n=5)
top_5_puts = puts.head(n=5)

option_upload()
print('success')