from _version import __version__
import sys

if sys.argv[-1] == '--after-update':
    print('Just updated to', __version__)
else:
    print('pprint version', __version__)

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
requiredDriverVersion = PLP_JSON_DATA.get('printingDriverVersion')
if requiredDriverVersion and requiredDriverVersion != __version__:
    requiredDriverVersionUrl = PLP_JSON_DATA.get('printingDriverVersionUrl')
    if sys.argv[-1] == '--after-update':
        raise ValueError('Required version "{rel_v}" doesnot match version "{req_v}" in "{rel_url}".'
            .format(rel_v = requiredDriverVersion, req_v = __version__, rel_url = requiredDriverVersionUrl))

    if requiredDriverVersionUrl:
        from _update import update
        print('Need to update from ' + __version__ + ' to ' + requiredDriverVersion)
        update(requiredDriverVersionUrl, requiredDriverVersion)
        python = sys.executable
        sys.argv.append('--after-update')
        os.execl(python, python, * sys.argv)

# print('Initialized', __version__)


# 2
# Tickets
#
if PLP_JSON_DATA.get('ticketData'):
    from _ticket import ticket
    ticket(PLP_JSON_DATA.get('ticketData'))
