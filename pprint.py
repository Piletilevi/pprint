# This Python file uses the following encoding: utf-8

from _version import __version__
import sys
import os
import json
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

global PLP_JSON_DATA

if not len(sys.argv) > 1:
    raise ValueError('Missin\' plp file name.')

PLP_FILENAME = sys.argv[1]
with open(PLP_FILENAME, 'r', encoding='utf-8') as plp_data_file:
    PLP_JSON_DATA = json.load(plp_data_file)

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
# Tickets
#
if PLP_JSON_DATA.get('ticketData'):
    # from _ticket import PSPrint
    import _ticket
    ps = _ticket.PSPrint(PLP_JSON_DATA)
    ps.printTickets()
    # inspect(pp.printTickets())
    # with PSPrint(PLP_JSON_DATA) as ps:
