# from datatable import dt, f
# , fetch_access_token, fetch_kiteticker_instance
from datetime import date

from datatable import Frame, f, dt

from src.utils.storage_utils import save, load
from src.utils.logger import get_logger
from src.utils.constants import underlying_index_mapping, options_include_list, kite

logger = get_logger(__name__)
today_str = date.today().strftime("%Y%m%d")


def get_instruments() -> Frame:
    file = 'instruments' + today_str
    folder = 'instruments'
    try:
        return load(file, folder)
    except FileNotFoundError:
        instruments_dict = kite.instruments()
        instruments = Frame(
            list(
                map(
                    lambda x: {k: v if v !=
                               '' else None for k, v in x.items()},
                    instruments_dict
                )
            )
        )
        save(instruments, file, folder)
        return instruments


def _assign_underlying_tradingsymbol(data: Frame, mapping: dict = underlying_index_mapping) -> Frame:
    data = data[:, f[:].extend({"underlying_tradingsymbol": f.name})]
    data['underlying_tradingsymbol'] = dt.Frame(
        underlying_tradingsymbol=list(map(lambda x: mapping.get(x, x),
                                          data['underlying_tradingsymbol'].to_list()[0])))
    return data


def get_nse_futures() -> Frame:
    """Function returns all futures instruments available in NSE"""
    instruments = get_instruments()
    nfo_fut_instruments = _assign_underlying_tradingsymbol(
        instruments[f.segment == 'NFO-FUT', :])[:, f[:].remove([f.strike, f.last_price, f.name])]

    # Test if futures underlying map to at least one of the equities / indexes in NSE (Log issues)
    all_underlying = set(get_nse_equities()[
                         0, 'tradingsymbol', dt.by('tradingsymbol')].to_list()[0])
    futures_underlying = set(nfo_fut_instruments[0, 'underlying_tradingsymbol', dt.by(
        'underlying_tradingsymbol')].to_list()[0])
    if futures_underlying - all_underlying:
        logger.error(
            f"Futures <> Underlying Mapping missing for {futures_underlying - all_underlying}")

    return nfo_fut_instruments


def get_nse_equities() -> Frame:
    """Function returns all equities / indexes instruments available in NSE"""
    instruments = get_instruments()
    return instruments[((f.segment == 'NSE') | (f.segment == 'INDICES'))
                       & (f.exchange == 'NSE') & (f.name != None),
                       ["instrument_token", "exchange_token", "tradingsymbol", "name", "instrument_type", "segment", "exchange"]]


def get_nse_options_subset() -> Frame:
    """Function returns the tradingsymbols of specific subset of options defined in constants"""
    instruments = get_instruments()
    nfo_opt_instruments = _assign_underlying_tradingsymbol(
        instruments[f.segment == 'NFO-OPT', :])[:, f[:].remove([f.last_price, f.name])]

    options_inclusions = dt.Frame(underlying_tradingsymbol=options_include_list, dummy=[
        1]*len(options_include_list))
    options_inclusions.key = 'underlying_tradingsymbol'
    nfo_opt_instruments = nfo_opt_instruments[:, :, dt.join(
        options_inclusions)][~dt.isna(f.dummy), f[:].remove(f.dummy)]
    return nfo_opt_instruments
