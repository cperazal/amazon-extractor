from datetime import datetime
import logging
import os
from pathlib import Path



class LoggingApp():

    def __init__(self):
        self.basedir = os.path.dirname(__file__)
        self.log_name = 'log_' + datetime.today().strftime('%Y%m%d') + '.log'
        Path(os.path.join(self.basedir, '../logs')).mkdir(parents=True, exist_ok=True)

    def reg_log(self, message, level=None):
        logging.basicConfig(filename=os.path.join(self.basedir, f'../logs/{self.log_name}'), level=logging.ERROR,
                            format="%(asctime)s %(message)s")
        if level == "info":
            logging.info(message)
        elif level == "warning":
            logging.warning(message)
        elif level == "error":
            logging.error(message)
        elif level == "critical":
            logging.critical(message)
        else:
            logging.debug(message)