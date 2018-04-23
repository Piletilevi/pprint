from _version import __version__
print(__version__)

import sys
import os

if hasattr(sys, "frozen"):
    pass
else:
    import win_unicode_console
    win_unicode_console.enable()

global BASEDIR

BASEDIR = os.path.dirname(sys.executable) if hasattr(sys, "frozen")\
    else os.path.dirname(__file__)


import json
global PLP_JSON_DATA

PLP_FILENAME = sys.argv[1]
with open(PLP_FILENAME, 'r', encoding='utf-8') as plp_data_file:
    PLP_JSON_DATA = json.load(plp_data_file)
if PLP_JSON_DATA.get('plpVersion') != __version__:
    from _update import update
    print('updating from ' + __version__ + ' to ' + PLP_JSON_DATA.get('plpVersion'))
    update('https://github.com/Piletilevi/printsrv3/raw/8a19e3531a91d77dfa14f51425e6b9ed3bc98df5/plevi.zip')


global FEEDBACK_TEMPLATE
# with open(os.path.join(BASEDIR, 'package.json'), 'r') as package_json_file:
#     global PACKAGE_JSON_DATA
#     PACKAGE_JSON_DATA = json.load(package_json_file)

fbtmpl_fn = os.path.join(BASEDIR, 'config', 'feedbackTemplate.json')
with open(fbtmpl_fn, 'r', encoding='utf-8') as feedback_template_file:
    FEEDBACK_TEMPLATE = json.load(feedback_template_file)
    FEEDBACK_TEMPLATE['feedbackToken'] = PLP_JSON_DATA.get('feedbackToken')
    FEEDBACK_TEMPLATE['operationToken'] = PLP_JSON_DATA\
        .get('operationToken')
    FEEDBACK_TEMPLATE['businessTransactionId'] = PLP_JSON_DATA\
        .get('fiscalData', {'businessTransactionId': ''})\
        .get('businessTransactionId', '')
    FEEDBACK_TEMPLATE['operation'] = PLP_JSON_DATA\
        .get('fiscalData').get('operation')

print('Initialized', __version__)
