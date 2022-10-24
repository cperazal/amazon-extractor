from datetime import datetime
import logging
import os
from pathlib import Path




class LoggingApp():

    def __init__(self):
        self.basedir = os.path.dirname(__file__)
        self.log_name = 'log_app.text' #'log_' + datetime.today().strftime('%Y%m%d') + '.text'
        Path(os.path.join(self.basedir, '../logs')).mkdir(parents=True, exist_ok=True)
        logging.basicConfig(filename=os.path.join(self.basedir, f'../logs/{self.log_name}'), level=logging.DEBUG,
                            format="%(asctime)s %(message)s", filemode="w")