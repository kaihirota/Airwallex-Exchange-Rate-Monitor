import os
from pathlib import Path

from loguru import logger

# configure log output directory
PROJECT_ROOT_DIR = Path(__file__).parent.parent
LOG_DIR = os.path.join(PROJECT_ROOT_DIR, "logs")
logger.add(os.path.join(LOG_DIR, "file_{time}.log"))

# moving average window
MOVING_AVERAGE_WINDOW = 60 * 5

PCT_CHANGE_THRESHOLD = 0.1

OUTPUT_FILE = os.path.join(PROJECT_ROOT_DIR, "output/output.jsonl")

"""
if VERBOSE is set to True, new conversation rate, moving average, and 
percentage change will also be included in the output jsonlines file.
"""
VERBOSE = False
