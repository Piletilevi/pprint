class payment():
    print("inside", __name__)
    import decorators

    def __init__(self):
        print("INSIDE", __name__, ".__init__()")

    @decorators.entry_exit
    @decorators.logging
    def __call__():
        print("inside", __name__, ".__call__()")
