import decorators

@decorators.profiler('_ticket')
def ticket(plpdata):
    print("my PLP data", plpdata['printerData'])
