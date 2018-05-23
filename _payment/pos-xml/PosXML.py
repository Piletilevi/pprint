# This Python file uses the following encoding: utf-8

# PosXML module
import requests
import xmltodict
import sys
from datetime import datetime
from os import path as path
from json import dumps as dumpsJSON
from yaml import load as loadYAML
from time import sleep
# from sys import stdin
# from yaml import dump as dumpYAML
# from os import chdir


class PosXML:
    def __init__(self, feedback, bye, options):
        self.feedback = feedback
        self.bye = bye
        self.OPTIONS = {'headers': {'content-type': "application/xml"}}
        for key, val in options.items():
            self.OPTIONS[key] = val
        if hasattr(sys, "frozen"):
            self.BASEDIR = path.dirname(sys.executable)
        else:
            self.BASEDIR = path.dirname(__file__)
        # chdir(self.BASEDIR)
        posxml_responses_fn = \
            path.join(self.BASEDIR, 'config', 'posxml_responses.yaml')
        with open(posxml_responses_fn, 'r') as posxml_responses_file:
            self.PXRESPONSES = loadYAML(posxml_responses_file)
        self.log_fn = path.join(self.BASEDIR, 'posxml.log')
        self.receipts_fn = path.join(self.BASEDIR, 'receipts.log')

    def __enter__(self):
        # print('Enter PosXML')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        None
        # print('Exit PosXML')

    def _extractReceipt(self, responseMessage, label):
        if label in responseMessage:
            _value = responseMessage[label]
            # print('extracting', label)
            del responseMessage[label]
            return _value

    def post(self, func, data):
        # print('data', data)
        dict = {'PosXML': {'@version': '7.2.0', }}
        dict['PosXML'][func] = data
        payload_xml = xmltodict.unparse(dict, pretty=True).encode('utf-8')
        # print('payload_xml', payload_xml)

        try:
            http_response = requests.post(
                self.OPTIONS['url'],
                data=payload_xml,
                headers=self.OPTIONS['headers'])
        except requests.exceptions.RequestException as e:
            self.feedback({'code': '', 'message': e.__str__()}, False)
            self.bye()

        response = xmltodict.parse(http_response.content)['PosXML']

        try:
            # find if any key in response matches one of expected response keys
            responseKey = \
                [key for key in self.PXRESPONSES[func] if key in response][0]
        except Exception as e:
            message = 'Expected responses: "{0}" not present in returned ' + \
                'response keys: "{1}".'.format(
                    ';'.join(self.PXRESPONSES[func]),
                    ';'.join(response.keys())
                )
            message = \
                'Expected responses: "{0}" not present '\
                .format(';'.join(self.PXRESPONSES[func])) \
                + 'in returned response keys: "{0}".'\
                .format(';'.join(response.keys()))
            self.feedback({'code': '', 'message': message}, False)
            self.bye()

        with open(self.log_fn, 'a') as f:
            f.write('---- {0}\n'.format(datetime.now().isoformat()))

            _payload_txt = dumpsJSON(xmltodict.parse(payload_xml))
            f.write('Request: \n{0}\n'.format(_payload_txt))

            _MerchReceipt = self._extractReceipt(
                response[responseKey], 'MerchReceipt')
            _CustReceipt = self._extractReceipt(
                response[responseKey], 'CustReceipt')

            _response_txt = dumpsJSON(response)
            f.write('Response: \n{0}\n'.format(_response_txt))

            if _MerchReceipt:
                with open(self.receipts_fn, 'a') as fr:
                    fr.write('MerchReceipt: \n{0}\n\n'.format(_MerchReceipt))
                f.write('MerchReceipt: \n{0}\n'.format(_MerchReceipt))
            if _CustReceipt:
                with open(self.receipts_fn, 'a') as fr:
                    fr.write('CustReceipt: \n{0}\n\n'.format(_CustReceipt))
                f.write('CustReceipt: \n{0}\n'.format(_CustReceipt))
            f.write('\n')

        if response[responseKey]['ReturnCode'] != '0':
            if response[responseKey]['Reason']:
                message = response[responseKey]['Reason']
            else:
                message = response[responseKey]['ReturnCode']
            self.feedback({
                'code': response[responseKey]['ReturnCode'],
                'message': message}, False)
            self.bye()

        return response[responseKey]

    def beep(self):
        self.post('DoBeepRequest', {'Frequency1': 2000, 'Duration1': 40})

    def message(self, destination, message):
        self.post('DisplayMessageRequest', {
            'Action': 1,
            'BackLight': 1,
            'Destination': destination,
            'Line2': message.encode('utf-8')
        })

    def resetMessages(self):
        self.post('DisplayMessageRequest', {
            'Action': 0
        })

    def waitForRemoveCardFromTerminal(self):
        response = self.post('GetTerminalStatusRequest', '')
        CardStts = response['CardStatus']
        # if CardStts != '0':
        #     print('Remove card from terminal')
        #     message(2,'Remove card from terminal')
        while CardStts != '0':
            self.beep()
            sleep(0.3)
            CardStts = self.post('GetTerminalStatusRequest', '')['CardStatus']
        self.resetMessages()
