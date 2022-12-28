from peewee import Model, CharField, FloatField, BigIntegerField, DateField, SmallIntegerField, Check
from src.utils.resources import db


class DailyData(Model):
    class Meta:
        database = db
        legacy_table_names = False
        schema = 'dailydata'


class NSEEquity(DailyData):
    exchange = CharField()
    tradingsymbol = CharField()
    date = DateField()
    open = FloatField()
    high = FloatField()
    low = FloatField()
    close = FloatField()
    volume = BigIntegerField()

    class Meta:
        indexes = (
            (('date', 'tradingsymbol', 'exchange'), True),
            (('tradingsymbol', 'exchange'), False),
        )


class NSEFuturesMonthly(DailyData):
    exchange = CharField()
    tradingsymbol = CharField()
    underlying_tradingsymbol = CharField()
    expiry_month_type = CharField(constraints=[Check(
        "expiry_month_type in ('near-month', 'far-month', 'next-month')")])
    expiry_date = DateField()
    date = DateField()
    open = FloatField()
    high = FloatField()
    low = FloatField()
    close = FloatField()
    volume = BigIntegerField()
    oi = BigIntegerField()

    class Meta:
        indexes = (
            (('date', 'tradingsymbol', 'exchange'), True),
            (('tradingsymbol', 'exchange'), False),
        )


class NSEOptionsMonthly(DailyData):
    exchange = CharField()
    tradingsymbol = CharField()
    underlying_tradingsymbol = CharField()
    strike = FloatField()
    expiry_month_type = CharField(constraints=[Check(
        "expiry_month_type in ('near-month', 'far-month', 'next-month')")])
    expiry_date = DateField()
    date = DateField()
    open = FloatField()
    high = FloatField()
    low = FloatField()
    close = FloatField()
    volume = BigIntegerField()
    oi = BigIntegerField()

    class Meta:
        indexes = (
            (('date', 'tradingsymbol', 'exchange'), True),
            (('tradingsymbol', 'exchange'), False),
        )


class NSEOptionsWeekly(DailyData):
    exchange = CharField()
    tradingsymbol = CharField()
    underlying_tradingsymbol = CharField()
    strike = FloatField()
    expiry_week = SmallIntegerField(constraints=[Check(
        "expiry_week <= 7")])
    expiry_date = DateField()
    date = DateField()
    open = FloatField()
    high = FloatField()
    low = FloatField()
    close = FloatField()
    volume = BigIntegerField()
    oi = BigIntegerField()

    class Meta:
        indexes = (
            (('date', 'tradingsymbol', 'exchange'), True),
            (('tradingsymbol', 'exchange'), False),
        )
