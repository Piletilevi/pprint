# This Python file uses the following encoding: utf-8

import decorators


@decorators.profiler('_fiscal')
def fiscal(fiscalData):
    if fiscalData['printerData']['printerName'] == 'ШТРИХ-ФР-К (B.2)':
        from shtrihm import ShtrihM as cMachine
    else:
        from shtrihm import ShtrihM as cMachine

    _amount = 0
    with cMachine(PLP_JSON_DATA) as cm:
        operations_a = {
        'cut':          {'operation': cm.cut,              },
        'endshift':     {'operation': cm.closeShift,       },
        'feed':         {'operation': cm.feed,             },
        'insertcash':   {'operation': cm.insertCash,       'reverse': cm.withdrawCash},
        'opencashreg':  {'operation': cm.openCashRegister, },
        'refund':       {'operation': cm.cmsale,           'reverse': cm.reverseSale},
        'sale':         {'operation': cm.cmsale,           'reverse': cm.reverseSale},
        'startshift':   {'operation': noop                 },
        'withdrawcash': {'operation': cm.withdrawCash,     'reverse': cm.insertCash},
        'xreport':      {'operation': cm.xReport,          },
        }
        VALID_OPERATIONS = operations_a.keys()
        operation = PLP_JSON_DATA['fiscalData']['operation']
        if operation not in VALID_OPERATIONS:
            raise ValueError('"operation" must be one of {0} in plp file. Got {1} instead.'.format(VALID_OPERATIONS, operation))

        _amount = operations_a[operation]['operation']() or 0

    fiscal_reply_fn = path.join(BASEDIR, 'config', 'fiscal_reply.yaml')
    # fiscal_reply_ofn = path.join(BASEDIR, 'tmp.txt')
    with open(fiscal_reply_fn, 'r', encoding='utf-8') as fiscal_reply_file:
        FISCAL_REPLY = loadYAML(fiscal_reply_file)

    if _amount == 0:
        reply_message = FISCAL_REPLY[operation]['reply']
    else:
        reply_message = FISCAL_REPLY[operation]['exactReply'].format(_amount)

    # print('reply_message: {0}'.format(reply_message))
    feedback({'code': '0', 'message': reply_message}, success=True, reverse=operations_a[operation].get('reverse', None))
    # print('reply_message: {0}'.format(reply_message))


if ( 'fiscalData' in PLP_JSON_DATA
    and 'printerData' in PLP_JSON_DATA['fiscalData']
    and 'type' in PLP_JSON_DATA['fiscalData']['printerData']
    and PLP_JSON_DATA['fiscalData']['printerData']['type'] != '' ):
        try:
            doFiscal()
        except Exception as e:
            # print("Unexpected fiscal error: {0}".format(e), sys.exc_info())
            bye("Unexpected fiscal error: {0}".format(e))



bye()
