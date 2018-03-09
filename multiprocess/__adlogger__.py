import os
import json
import shutil
from datetime import datetime

import logging
import logging.config

def setup_logger():
    if os.path.isfile("logging.json"):
        with open("logging.json", "r", encoding="utf-8") as fd:
            config = json.load(fd)
            logfilename = "log.txt"
            if os.path.isfile(logfilename):
                shutil.move(logfilename, 'log-old.txt')
            config['handlers']['file_handler']['filename'] = logfilename
            config['handlers']['file_handler']['mode'] = 'w'
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(filename="yourlog-basic.txt",
                level=logging.DEBUG,
                format="%(message)s",
                filemode="w")
