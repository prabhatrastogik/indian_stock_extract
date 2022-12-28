import calendar
import re
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from time import sleep
from peewee import fn
from src.utils.resources import kite, options_monthly_include_list, options_weekly_include_list
from src.utils.logger import get_logger
from src.datastore.instruments import NSEEquityInstruments, NSEFuturesInstruments, NSEOptionsInstruments
from src.datastore.readwrite import write_dailydata, read

logger = get_logger('dailydata', 'dailydata.log')


def get_25_years_data(instrument, type):
    all_ohlc = []
    for steps in range(5):
        today = date.today()
        end_date = today.replace(year=today.year - 5*steps)
        start_date = (today + timedelta(days=1)
                      ).replace(year=today.year - 5*(steps+1))
        # print(start_date, end_date)
        if steps == 3:
            sleep(1)

        if type == 'equities':
            all_ohlc += kite.historical_data(instrument_token=instrument['instrument_token'],
                                             from_date=start_date, to_date=end_date, interval='day')
        else:
            all_ohlc += kite.historical_data(instrument_token=instrument['instrument_token'],
                                             from_date=start_date, to_date=end_date, interval='day', continuous=True, oi=True)

    all_ohlc = sorted(all_ohlc, key=lambda x: x['date'])
    data = []
    for ohlc in all_ohlc:
        row_data = {
            'exchange': instrument['exchange'],
            'tradingsymbol': instrument['tradingsymbol'],
            'date': ohlc['date'],
            'open': ohlc['open'],
            'high': ohlc['high'],
            'low': ohlc['low'],
            'close': ohlc['close'],
            'volume': ohlc['volume'],
        }

        if type != 'equities':
            row_data.update({
                'underlying_tradingsymbol': instrument['underlying_tradingsymbol'],
                'oi': ohlc['oi'],
            })

        if type == 'futures_monthly':
            row_data.update({
                'expiry_month_type': instrument['expiry_month_type'],
                'expiry_date': get_monthly_expiry_date(ohlc['date'], instrument['expiry_month_type'], instrument['expiry_weekday']),
            })

        if type == 'options_monthly':
            row_data.update({
                'expiry_month_type': instrument['expiry_month_type'],
                'strike': instrument['strike'],
                'expiry_date':  get_monthly_expiry_date(ohlc['date'], instrument['expiry_month_type'], instrument['expiry_weekday']),
            })

        if type == 'options_weekly':
            row_data.update({
                'expiry_week': instrument['expiry_week_int'],
                'strike': instrument['strike'],
                'expiry_date': get_weekly_expiry_date(ohlc['date'], instrument['expiry_week_int'], instrument['expiry_weekday']),
            })

        data.append(row_data)
    return data


def is_expiry_data_correct(futures_name):
    expiries = sorted(map(lambda x: x['expiry'], futures_name))
    last_expiry = date.today()
    for expiry in expiries:
        if expiry - last_expiry > timedelta(days=40):
            return False
        last_expiry = expiry
    return True


def get_month_type(expiry_date, first_date):
    if expiry_date == first_date:
        return 'near-month'
    elif expiry_date - first_date <= timedelta(days=40):
        return 'next-month'
    else:
        return 'far-month'


def get_expiry_week(expiry_date):
    return (expiry_date - date.today()).days // 7 + 1


def get_monthly_expiry_date(
        ohlc_date, expiry_month_type, expiry_weekday):
    months = [
        calendar.monthcalendar(
            (ohlc_date + relativedelta(months=month)).year, (ohlc_date + relativedelta(months=month)).month) for month in range(4)
    ]
    month_year = [
        ohlc_date.replace(day=1) + relativedelta(months=month) for month in range(4)
    ]
    expiry_dates = list(map(lambda x: max(
        x[-1][expiry_weekday], x[-2][expiry_weekday]), months))

    if ohlc_date.day <= expiry_dates[0]:
        offset = 0
    else:
        offset = 1
    month_dict = {
        'near-month': 0,
        'next-month': 1,
        'far-month': 2,
    }

    return date(
        month_year[month_dict[expiry_month_type] + offset].year, month_year[month_dict[expiry_month_type] +
                                                                            offset].month, expiry_dates[month_dict[expiry_month_type] + offset]
    )


def get_weekly_expiry_date(
        ohlc_date, expiry_week_int, expiry_weekday):
    diff_days = ohlc_date.weekday() - expiry_weekday + 7 if ohlc_date.weekday() - \
        expiry_weekday <= 0 else ohlc_date.weekday() - expiry_weekday
    return ohlc_date + relativedelta(days=7*expiry_week_int) - relativedelta(days=diff_days)


def get_equities_subset(options_traded: bool):
    with read() as db:
        futures_last_date = NSEFuturesInstruments.select(
            fn.MAX(NSEFuturesInstruments.date)).scalar()
        equities_last_date = NSEEquityInstruments.select(
            fn.MAX(NSEEquityInstruments.date)).scalar()
        futures_instruments = NSEFuturesInstruments.select(
            NSEFuturesInstruments.underlying_tradingsymbol).where(NSEFuturesInstruments.date == futures_last_date).distinct()
        equity_options_traded = NSEEquityInstruments.select().where(NSEEquityInstruments.date == equities_last_date).join(futures_instruments, on=(
            futures_instruments.c.underlying_tradingsymbol == NSEEquityInstruments.tradingsymbol))
        equity_options_not_traded = NSEEquityInstruments.select().where(
            NSEEquityInstruments.date == equities_last_date) - equity_options_traded
        requested_equities = equity_options_traded if options_traded else equity_options_not_traded
        equities = [ins for ins in requested_equities.dicts()]
    return equities


def get_futures_subset():
    with read():
        futures_last_date = NSEFuturesInstruments.select(
            fn.MAX(NSEFuturesInstruments.date)).scalar()
        futures_instruments = NSEFuturesInstruments.select().where(
            NSEFuturesInstruments.date == futures_last_date)
        futures = [future for future in futures_instruments.dicts()]
    futures_monthly = []
    for name in set(map(lambda x: x['name'], futures)):
        futures_name = sorted(
            filter(lambda x: x['name'] == name, futures), key=lambda x: x['expiry'])[0:3]
        weekday = max(map(lambda x: x['expiry'].weekday(), futures_name))
        first_expiry = min(map(lambda x: x['expiry'], futures_name))
        if is_expiry_data_correct(futures_name):
            for row in futures_name:
                extra = {
                    'expiry_weekday': weekday,
                    'expiry_month_type': get_month_type(row['expiry'], first_expiry),
                }
                updated_row = {
                    **row,
                    **extra,
                }
                futures_monthly.append(updated_row)
    return futures_monthly


def get_options_monthly_subset():
    with read():
        options_last_date = NSEOptionsInstruments.select(
            fn.MAX(NSEOptionsInstruments.date)).scalar()
        options_instruments = NSEOptionsInstruments.select().where(
            NSEOptionsInstruments.date == options_last_date)
        options = [option for option in options_instruments.dicts() if re.search(
            option['name'] + r"[0-9]{2}[A-Z]{3}\d*(PE|CE)", option['tradingsymbol']) != None and option['underlying_tradingsymbol'] in options_monthly_include_list]
    options_monthly = []
    for name in set(map(lambda x: x['name'], options)):
        for instrument_type in set(map(lambda x: x['instrument_type'], options)):
            options_name = sorted(
                filter(lambda x: x['name'] == name and x['instrument_type'] == instrument_type, options), key=lambda x: x['expiry'])  # [0:3]
            weekday = max(map(lambda x: x['expiry'].weekday(), options_name))
            first_expiry = min(map(lambda x: x['expiry'], options_name))
            for strike in set(map(lambda x: x['strike'], options_name)):
                options_strike = sorted(
                    filter(lambda x: x['strike'] == strike and x['expiry'] <= (first_expiry + relativedelta(months=3)).replace(day=1), options_name), key=lambda x: x['expiry'])
                for row in options_strike:
                    extra = {
                        'expiry_weekday': weekday,
                        'expiry_month_type': get_month_type(row['expiry'], first_expiry),
                    }
                    updated_row = {
                        **row,
                        **extra,
                    }
                    options_monthly.append(updated_row)
    return options_monthly


def get_options_weekly_subset():
    with read():
        options_last_date = NSEOptionsInstruments.select(
            fn.MAX(NSEOptionsInstruments.date)).scalar()
        options_instruments = NSEOptionsInstruments.select().where(
            NSEOptionsInstruments.date == options_last_date)
        options = [option for option in options_instruments.dicts() if re.search(
            option['name'] + r"[0-9]{2}\w{1}\d*(PE|CE)", option['tradingsymbol']) != None and option['underlying_tradingsymbol'] in options_weekly_include_list]
    # return options
    options_weekly = []
    for name in set(map(lambda x: x['name'], options)):
        for instrument_type in set(map(lambda x: x['instrument_type'], options)):
            options_name = sorted(
                filter(lambda x: x['name'] == name and x['instrument_type'] == instrument_type, options), key=lambda x: x['expiry'])  # [0:3]
            weekday = max(map(lambda x: x['expiry'].weekday(), options_name))
            first_expiry = min(map(lambda x: x['expiry'], options_name))
            for strike in set(map(lambda x: x['strike'], options_name)):
                options_strike = sorted(
                    filter(lambda x: x['strike'] == strike and x['expiry'] <= (first_expiry + relativedelta(months=3)).replace(day=1), options_name), key=lambda x: x['expiry'])
                for row in options_strike:
                    extra = {
                        'expiry_weekday': weekday,
                        'expiry_week': get_expiry_week(row['expiry']),
                    }
                    updated_row = {
                        **row,
                        **extra,
                    }
                    options_weekly.append(updated_row)
    return options_weekly


def save_equities_dailydata():
    equity_instruments = get_equities_subset(options_traded=True)
    for instrument in equity_instruments:
        equities = get_25_years_data(instrument, type='equities')
        write_dailydata(equities, 'equities')


def save_futures_monthly_dailydata():
    futures_instruments = get_futures_subset()
    for instrument in futures_instruments:
        futures_monthly = get_25_years_data(instrument, type='futures_monthly')
        write_dailydata(futures_monthly, 'futures_monthly')


def save_options_monthly_dailydata():
    options_instruments = get_options_monthly_subset()
    for instrument in options_instruments:
        options_monthly = get_25_years_data(instrument, type='options_monthly')
        write_dailydata(options_monthly, 'options_monthly')


def save_options_weekly_dailydata():
    options_instruments = get_options_weekly_subset()
    for instrument in options_instruments:
        options_weekly = get_25_years_data(instrument, type='options_weekly')
        write_dailydata(options_weekly, 'options_weekly')


def save_dailydata():
    save_equities_dailydata()
    logger.info("Equities Data Write Completed")
    save_futures_monthly_dailydata()
    logger.info("Futures Data Write Completed")
    save_options_monthly_dailydata()
    logger.info("Options Monthly Data Write Completed")
    save_options_weekly_dailydata()
    logger.info("Options Weekly Data Write Completed")
