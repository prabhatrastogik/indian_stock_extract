import os
from playhouse.db_url import connect

from zlogin import fetch_kiteconnect_instance


def _get_database():
    if dburl := os.environ.get('DBURL'):
        conn_type = 'postgresext:' if 'postgres' in dburl.split(
            ':', 1)[0] else dburl.split(':', 1)[0]
        return connect(conn_type + dburl.split(':', 1)[1])
    else:
        raise OSError('DBURL not set in environment')


db = _get_database()

kite = fetch_kiteconnect_instance()


options_monthly_include_list = [
    'NIFTY 50',
    'NIFTY BANK',
    'ADANIENT',
    # 'DIVISLAB',
    'ADANIPORTS',
    # 'RELIANCE',
    # 'SBIN',
    # 'AUROPHARMA',
    # 'AXISBANK',
    # 'BAJAJFINSV',
    # 'BAJFINANCE',
    # 'BHARTIARTL',
    # 'DLF',
    # 'DRREDDY',
    # 'HDFCBANK',
    # 'ICICIBANK',
    # 'INFY',
    # 'JINDALSTEL',
    # 'JSWSTEEL',
    # 'JUBLFOOD',
    # 'KOTAKBANK',
    # 'L&TFH',
    # 'LALPATHLAB',
    # 'MARUTI',
    # 'TCS',
]

options_weekly_include_list = [
    'NIFTY 50',
    'NIFTY BANK',
]
