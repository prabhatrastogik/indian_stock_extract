import re
from src.utils.resources import kite
from src.utils.logger import get_logger
from src.datastore.readwrite import write_instrument

logger = get_logger('instruments', 'instruments.log')


def get_nse_instruments():
    all_instruments = kite.instruments()

    nse_equity = [instrument for instrument in all_instruments if instrument['segment'] in (
        'NSE', 'INDICES') and instrument['name'] != '' and instrument['exchange'] == 'NSE']

    nfo_fut_monthly = [instrument for instrument in all_instruments if instrument['segment'] in (
        'NFO-FUT') and instrument['name'] != '' and instrument['exchange'] == 'NFO'
        and re.search(instrument['name'] + r"[0-9]{2}[A-Z]{3}FUT", instrument['tradingsymbol']) != None]

    nfo_opt_monthly = [instrument for instrument in all_instruments if instrument['segment'] in (
        'NFO-OPT') and instrument['name'] != '' and instrument['exchange'] == 'NFO'
        and re.search(instrument['name'] + r"[0-9]{2}[A-Z]{3}\d*(PE|CE)", instrument['tradingsymbol']) != None]

    nfo_opt_weekly = [instrument for instrument in all_instruments if instrument['segment'] in (
        'NFO-OPT') and instrument['name'] != '' and instrument['exchange'] == 'NFO'
        and re.search(instrument['name'] + r"[0-9]{2}\w{1}\d*(PE|CE)", instrument['tradingsymbol']) != None]

    return {
        'equities': nse_equity,
        'futures': nfo_fut_monthly,
        'options': nfo_opt_monthly + nfo_opt_weekly,
    }


def get_underlying(name, equities):
    underlying_index_mapping = {
        'NIFTY': 'NIFTY 50',
        'BANKNIFTY': 'NIFTY BANK',
        'MIDCPNIFTY': 'NIFTY MID SELECT',
        'FINNIFTY': 'NIFTY FIN SERVICE',
    }
    if name in [equity['tradingsymbol'] for equity in equities]:
        return name
    elif name in underlying_index_mapping.keys():
        return underlying_index_mapping[name]
    else:
        logger.warning(
            "A NFO Derivative has no underlying mapped - name = {name}")


def save_nse_instruments():
    instruments = get_nse_instruments()

    equities = []
    for equity in instruments['equities']:
        equities.append({
            'instrument_token': equity['instrument_token'],
            'exchange_token': equity['exchange_token'],
            'tradingsymbol': equity['tradingsymbol'],
            'name': equity['name'],
            'tick_size': equity['tick_size'],
            'instrument_type': equity['instrument_type'],
            'segment': equity['segment'],
            'exchange': equity['exchange'],
        })

    futures = []
    for future in instruments['futures']:
        if underlying := get_underlying(future['name'], equities):
            futures.append({
                'instrument_token': future['instrument_token'],
                'exchange_token': future['exchange_token'],
                'tradingsymbol': future['tradingsymbol'],
                'name': future['name'],
                'underlying_tradingsymbol': underlying,
                'expiry': future['expiry'],
                'lot_size': future['lot_size'],
                'tick_size': future['tick_size'],
                'instrument_type': future['instrument_type'],
                'segment': future['segment'],
                'exchange': future['exchange'],
            })

    options = []
    for option in instruments['options']:
        if underlying := get_underlying(option['name'], equities):
            options.append({
                'instrument_token': option['instrument_token'],
                'exchange_token': option['exchange_token'],
                'tradingsymbol': option['tradingsymbol'],
                'name': option['name'],
                'underlying_tradingsymbol': underlying,
                'expiry': option['expiry'],
                'strike': option['strike'],
                'lot_size': option['lot_size'],
                'tick_size': option['tick_size'],
                'instrument_type': option['instrument_type'],
                'segment': option['segment'],
                'exchange': option['exchange'],
            })

    write_instrument(equities, 'equities')
    logger.info("Equities Instruments Data Write Completed")
    write_instrument(futures, 'futures')
    logger.info("Futures Instruments Data Write Completed")
    write_instrument(options, 'options')
    logger.info("Options Instruments Data Write Completed")
