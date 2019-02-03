# This Python file uses the following encoding: utf-8

import decorators


def print2postscript(ticket, job_no):
    bmp_fns, printOrientation = print2bitmap(ticket, job_no)
    from _ticket._postscript import PSPrint
    ticket['printerData']['printOrientation'] = printOrientation
    ps = PSPrint(ticket['printerData'])
    for bmp_fn in bmp_fns:
        ps.printTicket(bmp_fn)


def print2pdf(ticket, job_no):
    raise Exception('print2pdf')
    return None


def print2bitmap(ticket, job_no):
    from _ticket._bitmap import BMPPrint
    bmp = BMPPrint(ticket)
    bmp.printTicket(job_no)
    print('Printed', bmp.out_fn)
    return (bmp.out_fn, bmp.page_settings['printOrientation'])


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
    if 'layout' in plp_json_data['ticketData']:
        g_layout = plp_json_data['ticketData']['layout']

    job_no = 0
    for ticket in plp_json_data['ticketData']['tickets']:
        job_no += 1
        printerData = dict()
        printerData.update(g_printerdata)
        if 'printerData' in ticket:
            printerData.update(ticket['printerData'])
        ticket['printerData'] = printerData
        ticket['transactionData'] = plp_json_data['transactionData']
        ticket.setdefault('layout', {'name': g_layout})

        method = printerData['type']
        print('printing method:', method)
        if method in switcher:
            func = switcher.get(method)
            func(ticket, job_no)
        else:
            cantPrint(method)
