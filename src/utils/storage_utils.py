import os
from pathlib import Path

from datatable import Frame, fread

from src.utils.logger import get_logger
from src.utils.constants import DEFAULT_DATA_LOCATION


logger = get_logger(__name__)


def _setup_local_storage():
    BASE_LOCATION = os.environ.get('TRADESMARTDATA', DEFAULT_DATA_LOCATION)
    base_path = Path(BASE_LOCATION).expanduser().resolve()
    if not base_path.is_dir():
        base_path.mkdir(parents=True, exist_ok=True)
        logger.info("Base Directory Created! First Run?")
    return base_path


def save(data: Frame, file: str, folder: str, storage: str = 'local') -> None:
    if storage == 'local':
        store_path = Path(str(_setup_local_storage() /
                          folder / file) + '.jay').resolve()
        store_path.parent.mkdir(parents=True, exist_ok=True)
        data.to_jay(str(store_path.resolve()))
        logger.info(f"{folder}/{file} write completed")
    else:
        logger.error("Non Local Storage Not Implemented")
        raise NotImplementedError("Only Local Storage Implemented")
    # S3 Storage Not Set Up for now


def append(data: Frame, file: str, folder: str, storage: str = 'local') -> None:
    if storage == 'local':
        store_path = Path(str(_setup_local_storage() /
                          folder / file) + '.jay').resolve()
        store_path.parent.mkdir(parents=True, exist_ok=True)
        if store_path.is_file():
            original_data = load(file, folder)
            original_data.rbind(data)
            data = original_data
        data.to_jay(str(store_path.resolve()))
        logger.info(f"{folder}/{file} append completed")
    else:
        logger.error("Non Local Storage Not Implemented")
        raise NotImplementedError("Only Local Storage Implemented")
    # S3 Storage Not Set Up for now


def load(file: str, folder: str, storage: str = 'local') -> Frame:
    if storage == 'local':
        read_path = Path(str(_setup_local_storage() /
                         folder / file) + '.jay').resolve()
        if read_path.is_file():
            return fread(str(read_path.resolve()))
        else:
            logger.info(f"{folder}/{file} does not exist")
            raise FileNotFoundError("Data Missing")
    else:
        logger.error("Non Local Storage Not Implemented")
        raise NotImplementedError("Only Local Storage Implemented")
    # S3 Loading Not Set Up for now
