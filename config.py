import os
from loguru import logger

LOG_DIR = "logs"
logger.add(os.path.join(LOG_DIR, "file_{time}.log"))

# 5 minute moving average
MOVING_AVERAGE_WINDOW = 60 * 5

PCT_CHANGE_THRESHOLD = 0.1

OUTPUT_FILE = "output/output.jsonl"

"""
if VERBOSE is set to True, new conversation rate, moving average, and 
percentage change will also be included in the output jsonlines file.
"""
VERBOSE = False
