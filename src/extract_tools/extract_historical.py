from datetime import date, timedelta
from time import sleep

from datatable import Frame, f, dt

from src.utils.storage_utils import save, load, append
from src.utils.logger import get_logger
from src.extract_tools.extract_instruments import get_nse_equities, get_nse_options_subset, get_nse_futures
from src.utils.constants import kite

logger = get_logger(__name__)
today_str = date.today().strftime("%Y%m%d")

today = date.today()
yesterday = date.today() - timedelta(days=1)


def get_equity_historical():
    eq = get_nse_equities()[:, f['instrument_token',
                                 'tradingsymbol', 'exchange', 'name']]
    eq.key = 'instrument_token'
    interval = 'day'
    for token in eq['instrument_token'].to_list()[0][0:1]:
        chart_data = []
        for year in range(2000, today.year, 5):
            from_date = date(year, 1, 1)
            to_date = min(date(year+4, 12, 31), yesterday)
            sleep(0.5)
            chart_data.extend(kite.historical_data(
                token, from_date, to_date, interval))
        data = Frame(chart_data)
        data['instrument_token'] = token
        save(
            data[:, :, dt.join(eq)],
            eq[f.instrument_token == token, f.tradingsymbol].to_list()[0][0],
            'equities'
        )

def get_quotes(instruments):
    quote_requests = instruments[:, f['instrument_token', 'tradingsymbol', 'exchange', 'name'].extend(
        {'exchange_tradingsymbol': f.exchange+':'+f.tradingsymbol})]
    list_of_inputs = quote_requests['exchange_tradingsymbol'].to_list()[0]
    quotes_data = {}
    for i in range(0, len(list_of_inputs), 400):
        quotes_data.update(kite.quote(*list_of_inputs[i:i+400]))
        sleep(0.5)
    quotes_data
