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

# 0
# Update
# Make sure we are on required version
if PLP_JSON_DATA.get('printingDriverVersion') != __version__:
    from _update import update
    print('updating from ' + __version__ + ' to ' + PLP_JSON_DATA.get('printingDriverVersion'))
    update('https://github.com/Piletilevi/printsrv3/raw/8a19e3531a91d77dfa14f51425e6b9ed3bc98df5/plevi.zip')



print('Initialized', __version__)
