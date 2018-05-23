# This Python file uses the following encoding: utf-8

import decorators
import random


@decorators.profiler('_payment')
def payment(PLP_JSON_DATA):
    print("inside", __name__)

    rnd = random.getrandbits(4)  # 0..15
    if rnd > 10:
        raise ValueError('''
            Payment failed. Random number generator returned "{rnd}"
            .'''.format(rnd=rnd))

    if PLP_JSON_DATA.get(
        'fiscalData', {}).get(
            'cardPaymentUnitSettings', {}).get(
                'cardPaymentUnit', False):

        fiscal_data = PLP_JSON_DATA['fiscalData']
        cpu_settings = fiscal_data['cardPaymentUnitSettings']
        cpu_name = cpu_settings['cardPaymentUnit']
        # payments_data = fiscal_data['payments']

        def unit_posxml(fiscal_data):
            cpu_settings = fiscal_data['cardPaymentUnitSettings']
            payments_data = fiscal_data['payments']

            operation = fiscal_data['operation']
            if operation == 'sale':
                _transactionRequest = 'TransactionRequest'
                _transactionId = fiscal_data['businessTransactionId']
            else:
                _transactionRequest = 'ReverseTransactionRequest'
                _transactionId = fiscal_data['saleTransactionId']

            card_payment_amount = 0
            for payment in payments_data:
                if payment['type'] == '4':
                    card_payment_amount += payment['cost']

            posxmlIP = cpu_settings['cardPaymentUnitIp']
            posxmlPort = cpu_settings['cardPaymentUnitPort']
            posxmlURL = 'http://{0}:{1}'.format(posxmlIP, posxmlPort)
            from posxml import PosXML
            with PosXML(posxmlURL) as posxml:
                posxml.post('CancelAllOperationsRequest', '')

                response = posxml.post(
                    _transactionRequest,
                    {
                        'TransactionID': _transactionId,
                        'Amount': int(round(card_payment_amount * 100)),
                        'CurrencyName': 'EUR',
                        'PrintReceipt': 1,
                        'ReturnReceipts': 64,
                        'Timeout': 100,
                    }
                )
                # print('response', response)
                if response['ReturnCode'] != '0':
                    raise ValueError(
                        'Card payment failed: {0}'.format(response['Reason']))

        def unit_default(fiscal_data):
            raise ValueError('Card payment unit not specified')

        switcher = {
            'Ingenico': unit_posxml
        }

        def choose_payment_unit(unit_name):
            func = switcher.get(cpu_name, "unit_default")
            return func

        cpu = choose_payment_unit(cpu_name)
        return cpu(fiscal_data)
