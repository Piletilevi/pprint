class profiler(object):

    def __init__(self, f):
        self.f = f
        self.__name__ = f.__name__
        def wrapped():
            print('EED:inside profiler.__init__() for', f.__name__)
        return wrapped()

    def __call__(self):
        def wrapped():
            print('EED:entering', self.f.__name__)
            self.f()
            print('EED:exiting', self.f.__name__)
        return wrapped()


class logging(object):
    def __init__(self, f):
        # print(f.__dir__())
        self.logfilename = 'pprint.log'
        self.f = f
        self.__name__ = f.__qualname__
        def wrapped():
            with open(self.logfilename, 'a') as logfile:
                print('LD:inside logging.__init__() for ' + self.__name__ + '\n')
                logfile.write('LD:inside logging.__init__() for ' + self.__name__ + '\n')
        return wrapped()

    def __call__(self):
        def wrapped():
            with open(self.logfilename, 'a') as logfile:
                print('LD:entering ' + self.__name__ + '\n')
                logfile.write('LD:entering ' + self.__name__ + '\n')
            self.f()
            with open(self.logfilename, 'a') as logfile:
                print('LD:exiting ' + self.__name__ + '\n')
                logfile.write('LD:exiting ' + self.__name__ + '\n')
        return wrapped()
