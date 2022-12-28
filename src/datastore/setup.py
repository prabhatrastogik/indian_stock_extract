from src.datastore.instruments import NSEEquityInstruments, NSEFuturesInstruments, NSEOptionsInstruments
from src.datastore.dailydata import NSEEquity, NSEFuturesMonthly, NSEOptionsMonthly, NSEOptionsWeekly
from src.utils.resources import db
from src.utils.logger import get_logger


logger = get_logger('peewee', 'database.log')


def set_database(set_type='all'):
    instrument_tables = [NSEEquityInstruments,
                         NSEFuturesInstruments, NSEOptionsInstruments]
    dailydata_tables = [NSEEquity, NSEFuturesMonthly,
                        NSEOptionsMonthly, NSEOptionsWeekly]

    if set_type == 'all':
        tables = instrument_tables + dailydata_tables
    elif set_type == 'dailydata':
        tables = dailydata_tables
    elif set_type == 'instruments':
        tables = instrument_tables
    else:
        tables = []

    with db:
        try:
            db.drop_tables(tables)
        except Exception as e:
            logger.error(f"Dropping tables failed - {e}")
    with db:
        db.create_tables(tables, safe=False)
