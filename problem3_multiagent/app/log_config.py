import logging
from pathlib import Path
from typing import Union

BASE_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "multiagent.log"


def configure_global_logger(log_file: Union[str, Path] = None) -> None:
    """Configure shared logging for all modules."""
    if log_file is None:
        log_file = LOG_FILE
    else:
        log_file = Path(log_file)

    if not log_file.is_absolute():
        log_file = BASE_DIR / log_file

    log_file.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )
