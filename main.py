
import requests
from bs4 import BeautifulSoup as bs

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'}

stock_price_url = 'https://finance.yahoo.com/quote/TSLA/'
stock_options_url = 'https://finance.yahoo.com/quote/TSLA/options/'

r = requests.get(stock_price_url)
soup = bs(r.text, 'html.parser')

price = soup.find('fin-streamer', {'class': 'livePrice yf-1tejb6'}).text
change = soup.find('fin-streamer', {'class': 'priceChange yf-1tejb6'}).text
change_percent = soup.find('fin-streamer', {'class': 'priceChange yf-1tejb6', 'data-field': 'regularMarketChangePercent'}).text

print(price, change)