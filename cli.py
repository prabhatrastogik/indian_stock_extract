from argparse import ArgumentParser
from src.datastore.setup import set_database
from src.extract.instruments import save_nse_instruments
from src.extract.dailydata import save_dailydata


def reset_dailydata(clean_instruments=False):
    set_type = 'all' if clean_instruments else 'dailydata'
    set_database(set_type)
    save_nse_instruments()
    save_dailydata()


def create_parser():
    parser = ArgumentParser(
        description="Extract historical data and store in database")
    parser.add_argument('-a', '--all', action='store_true',
                        help='reset all existing tables; (default: does not reset instruments tables)')
    return parser


if __name__ == '__main__':
    args = create_parser().parse_args()
    reset_dailydata(args.all)
