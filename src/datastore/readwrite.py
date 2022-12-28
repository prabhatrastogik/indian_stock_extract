from contextlib import contextmanager
from peewee import chunked, IntegrityError
from src.datastore.instruments import NSEEquityInstruments, NSEFuturesInstruments, NSEOptionsInstruments
from src.datastore.dailydata import NSEEquity, NSEFuturesMonthly, NSEOptionsMonthly, NSEOptionsWeekly
from src.utils.resources import db
from src.utils.logger import get_logger

logger = get_logger('peewee', 'database.log')


instrument_mapping = {
    'equities': NSEEquityInstruments,
    'futures': NSEFuturesInstruments,
    'options': NSEOptionsInstruments,
}


dailydata_mapping = {
    'equities': NSEEquity,
    'futures_monthly': NSEFuturesMonthly,
    'options_monthly': NSEOptionsMonthly,
    'options_weekly': NSEOptionsWeekly,
}


@contextmanager
def read():
    try:
        db.connect(reuse_if_open=True)
        yield db
    finally:
        db.close()


def _batch_write(data, table):
    with db.atomic():
        for batch in chunked(data, 1000):
            try:
                table.insert_many(batch).execute()
            except IntegrityError as e:
                logger.error(
                    f"Possibly table constraint on unique keys broken for {table}, with exception {e}"
                )


def write_instrument(data, type):
    _batch_write(data, instrument_mapping[type])


def write_dailydata(data, type):
    _batch_write(data, dailydata_mapping[type])
