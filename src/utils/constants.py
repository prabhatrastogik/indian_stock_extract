from datetime import date
from pathlib import Path

from zlogin import fetch_kiteconnect_instance

kite = fetch_kiteconnect_instance()

DEFAULT_DATA_LOCATION = str(Path.home() / 'Personal' / 'tradesmart' / 'data')

underlying_index_mapping = {
    'NIFTY': 'NIFTY 50',
    'BANKNIFTY': 'NIFTY BANK',
    'MIDCPNIFTY': 'NIFTY MID SELECT',
    'FINNIFTY': 'NIFTY FIN SERVICE',
}

options_include_list = [
    'NIFTY 50',
    'NIFTY BANK',
    'ADANIENT',
    'ADANIPORTS',
    #  'AUROPHARMA',
    #  'AXISBANK',
    #  'BAJAJFINSV',
    #  'BAJFINANCE',
    #  'BHARTIARTL',
    #  'DIVISLAB',
    #  'DLF',
    #  'DRREDDY',
    #  'HDFC',
    #  'HDFCBANK',
    #  'ICICIBANK',
    #  'INFY',
    #  'JINDALSTEL',
    #  'JSWSTEEL',
    #  'JUBLFOOD',
    #  'KOTAKBANK',
    #  'L&TFH',
    #  'LALPATHLAB',
    #  'MARUTI',
    #  'RELIANCE',
    #  'SBIN',
    #  'TCS',
]
