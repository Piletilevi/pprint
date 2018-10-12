# This Python file uses the following encoding: utf-8

import decorators


def print2postscript(ticket):
    bmp_fn = print2bitmap(ticket)
    from _ticket._postscript import PSPrint
    ps = PSPrint(ticket['printerData'])
    ps.printTicket(bmp_fn)


def print2pdf(ticket):
    raise Exception('print2pdf')
    return None


def print2bitmap(ticket):
    from _ticket._bitmap import BMPPrint
    bmp = BMPPrint(ticket)
    bmp.printTicket()
    print('Printed', bmp.out_fn)
    return bmp.out_fn


def cantPrint(method):
    raise Exception('Method "{0}" not supported'.format(method))
    return None


@decorators.profiler('_ticket')
def ticket(plp_json_data):

    switcher = {
        'tickets': print2postscript,
        'tickets_postscript': print2postscript,
        'tickets_pdf': print2pdf,
        'tickets_bitmap': print2bitmap
    }

    g_printerdata = dict()
    if 'printerData' in plp_json_data['ticketData']:
        g_printerdata.update(plp_json_data['ticketData']['printerData'])

    for ticket in plp_json_data['ticketData']['tickets']:
        printerData = dict()
        printerData.update(g_printerdata)
        if 'printerData' in ticket:
            printerData.update(ticket['printerData'])
        ticket['printerData'] = printerData
        ticket['transactionData'] = plp_json_data['transactionData']

        method = printerData['type']
        if method in switcher:
            func = switcher.get(method)
            func(ticket)
        else:
            cantPrint(method)
