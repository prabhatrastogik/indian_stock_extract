from peewee import Model, CharField, FloatField, BigIntegerField, DateField, SQL, IntegerField
from src.utils.resources import db


class Instrument(Model):
    class Meta:
        database = db
        legacy_table_names = False
        schema = 'instruments'


class NSEEquityInstruments(Instrument):
    instrument_token = BigIntegerField()
    exchange_token = CharField()
    tradingsymbol = CharField()
    name = CharField()
    tick_size = FloatField()
    instrument_type = CharField()
    segment = CharField()
    exchange = CharField()
    date = DateField(constraints=[SQL('DEFAULT CURRENT_DATE')])

    class Meta:
        indexes = (
            (('date', 'tradingsymbol', 'exchange'), True),
            (('tradingsymbol', 'exchange'), False),
        )


class NSEFuturesInstruments(Instrument):
    instrument_token = BigIntegerField()
    exchange_token = CharField()
    tradingsymbol = CharField()
    name = CharField()
    underlying_tradingsymbol = CharField()
    expiry = DateField()
    lot_size = IntegerField()
    tick_size = FloatField()
    instrument_type = CharField()
    segment = CharField()
    exchange = CharField()
    date = DateField(constraints=[SQL('DEFAULT CURRENT_DATE')])

    class Meta:
        indexes = (
            (('date', 'tradingsymbol', 'exchange'), True),
            (('tradingsymbol', 'exchange'), False),
        )


class NSEOptionsInstruments(Instrument):
    instrument_token = BigIntegerField()
    exchange_token = CharField()
    tradingsymbol = CharField()
    name = CharField()
    underlying_tradingsymbol = CharField()
    expiry = DateField()
    strike = FloatField()
    lot_size = IntegerField()
    tick_size = FloatField()
    instrument_type = CharField()
    segment = CharField()
    exchange = CharField()
    date = DateField(constraints=[SQL('DEFAULT CURRENT_DATE')])

    class Meta:
        indexes = (
            (('date', 'tradingsymbol', 'exchange'), True),
            (('tradingsymbol', 'exchange'), False),
        )
