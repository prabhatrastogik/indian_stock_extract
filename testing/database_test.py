import os
import pytest
from playhouse.db_url import connect


@pytest.fixture
def postgres(postgresql_db):
    postgresql_db.create_schema('instruments', 'dailydata', exists_ok=True)
    return postgresql_db


def test_equity_storage(postgres, monkeypatch):
    connection = str(postgres.engine.url)
    monkeypatch.setenv('DBURL', connection)
    from src.extract.instruments import save_nse_instruments
    from src.datastore.setup import set_database
    from src.datastore.instruments import NSEEquityInstruments, NSEFuturesInstruments, NSEOptionsInstruments
    set_database(set_type='all')
    save_nse_instruments()
    NSEEquityInstruments.delete().where(
        NSEEquityInstruments.tradingsymbol.not_in(['NIFTY 50', 'ADANIENT'])).execute()
    NSEFuturesInstruments.delete().where(
        NSEFuturesInstruments.underlying_tradingsymbol.not_in(['NIFTY 50'])).execute()
    NSEOptionsInstruments.delete().where(
        NSEOptionsInstruments.underlying_tradingsymbol.not_in(['NIFTY 50'])).execute()
    from src.extract.dailydata import save_dailydata
    from src.datastore.dailydata import NSEEquity, NSEFuturesMonthly, NSEOptionsMonthly, NSEOptionsWeekly
    options_weekly_include_list = options_monthly_include_list = ['NIFTY 50']
    save_dailydata()
    eq = NSEEquity.select()
    futm = NSEFuturesMonthly.select()
    optm = NSEOptionsMonthly.select()
    optw = NSEOptionsWeekly.select()
    assert len(eq) > 0
    assert len(futm) > 0
    assert len(optm) > 0
    assert len(optw) > 0
