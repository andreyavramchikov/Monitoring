# -*- coding: utf-8 -*-

import json
import logging
import os
import requests
import threading

from requests.exceptions import ConnectionError

CONFIGURATION_FILE_NAME = "pages.json"
LOGFILE_NAME = "monitoring.log"
logging.basicConfig(format='%(asctime)s | %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    filemode='a',
                    level="INFO",
                    filename=LOGFILE_NAME)

STATUSES = {'200_VERIFIED': 'Working and content verified',
            '200_NOT_VERIFIED': 'Working but content not verified',
            '3xx': 'Redirection',
            '4xx': 'Bad Request',
            '5xx': 'Internal Server Error'}


class Monitoring(object):

    def __init__(self):
        self.data = None
        self.url = None
        self.requirements = None
        self.period = None

    def run(self):
        self.get_data_from_file(CONFIGURATION_FILE_NAME)
        self.check_pages()

    def get_data_from_file(self, filename):
        file_type = os.path.splitext(filename)[1]
        if file_type == '.json':
            with open(filename) as f:
                self.data = json.load(f)
        # If we will going to use other file types such as excel, xml and etc
        #   we would implement appropriate methods for reading info
        elif file_type == 'other':
            pass

        self.period = self.data['period']

    @staticmethod
    def verify_content(content, requirements):
        """Additional rules for verification of content should be placed in this method"""
        return True if requirements in unicode(content, 'utf-8') else False

    def check_page(self):
        try:
            response = requests.get(self.url)
        except ConnectionError as e:
            logging.error(e)
            return
        total_time = response.elapsed.total_seconds()
        status_code = str(response.status_code)
        status = None
        if status_code.startswith('2'):
            status = STATUSES['200_VERIFIED'] if self.verify_content(response.content, self.requirements) \
                else STATUSES['200_NOT_VERIFIED']
        elif status_code.startswith('3'):
            status = STATUSES['3xx']
        elif status_code.startswith('4'):
            status = STATUSES['4xx']
        elif status_code.startswith('5'):
            status = STATUSES['5xx']

        logging.info('{}; Status - {}; Response time -  {}s'.format(self.url, status, total_time))

    def check_pages(self):
        for page in self.data['pages']:
            self.url = page.keys()[0]
            self.requirements = page.values()[0]
            self.check_page()

        threading.Timer(self.period, self.check_pages).start()


if __name__ == "__main__":
    Monitoring().run()



