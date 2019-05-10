# This Python file uses the following encoding: utf-8

from _version import __version__
import sys
import os
import json
import shutil

import sentry_sdk

sentry_sdk.init(
    'https://e03ea87113a644bb9ffd2a53318158e5@sentry.io/1456705',
    max_breadcrumbs=50,
    debug=False,
)

# import inspect


if sys.argv[-1] == '--after-update':
    print('Just updated to', __version__)
else:
    print('pprint version', __version__)

if hasattr(sys, "frozen"):
    pass
else:
    import win_unicode_console
    win_unicode_console.enable()

BASEDIR = os.path.dirname(sys.executable) if hasattr(sys, "frozen")\
    else os.path.dirname(__file__)

os.makedirs(os.path.join(BASEDIR, 'img'), exist_ok=True)
os.makedirs(os.path.join(BASEDIR, 'tmp'), exist_ok=True)

global PLP_JSON_DATA

if not len(sys.argv) > 1:
    raise ValueError('Missin\' plp file name.')

PLP_FILENAME = sys.argv[1]
try:
    with open(PLP_FILENAME, 'r', encoding='utf-8') as plp_data_file:
        PLP_JSON_DATA = json.load(plp_data_file)
except Exception as e:
    from plp_txt2json import main as plpT2J
    PLPJSON_FILENAME = PLP_FILENAME[:-4] + '.json' + PLP_FILENAME[-4:]
    PLP_JSON_DATA = plpT2J(PLP_FILENAME, PLPJSON_FILENAME)

transactionData = {
    'salesPointText': PLP_JSON_DATA.setdefault('salesPointText'),
    'salesPointCountry': PLP_JSON_DATA.setdefault('salesPointCountry'),
    'salesPoint': PLP_JSON_DATA.setdefault('salesPoint'),
    'transactionDateTime': PLP_JSON_DATA.setdefault('transactionDateTime')
}
PLP_JSON_DATA['transactionData'] = transactionData
# 0
# Update
# Make sure we are on required version
reqDrvrVer = PLP_JSON_DATA.get('printingDriverVersion')
if reqDrvrVer and reqDrvrVer != __version__:
    reqDrvrVerUrl = PLP_JSON_DATA.get('printingDriverVersionUrl')
    if sys.argv[-1] == '--after-update':
        raise ValueError(
            '''Required version "{rel_v}" doesnot match version
            {req_v}" in "{rel_url}".'''
            .format(rel_v=reqDrvrVer, req_v=__version__,
                    rel_url=reqDrvrVerUrl))

    if reqDrvrVerUrl:
        from _update import update
        print('Need to update from ' + __version__ + ' to ' + reqDrvrVer)
        update(reqDrvrVerUrl, reqDrvrVer)
        python = sys.executable
        sys.argv.append('--after-update')
        os.execl(python, python, * sys.argv)

# print('Initialized', __version__)


# 2
# Payment
#
if PLP_JSON_DATA.get('fiscalData', {}).get('payments', False):
    import _payment
    if _payment.payment(PLP_JSON_DATA):
        print('Payment succeeded')


# 2
# Tickets
#
if PLP_JSON_DATA.get('ticketData'):
    # from _ticket import PSPrint
    import _ticket
    if _ticket.ticket(PLP_JSON_DATA):
        print('Ticket(s) succeeded')
    # ps.printTickets()
    # inspect(pp.printTickets())
    # with PSPrint(PLP_JSON_DATA) as ps:


# 2
# Cards
#
if PLP_JSON_DATA.get('cardData'):
    # from _ticket import PSPrint
    import _card
    if _card.card(PLP_JSON_DATA):
        print('Card print succeeded')

# Cleanup
print('\n\n----\ncleanup')
# os.unlink(PLP_FILENAME)
shutil.rmtree(os.path.join(BASEDIR, 'tmp'))
