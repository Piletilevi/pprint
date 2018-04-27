import time
current_milli_time = lambda: int(round(time.time() * 1000))

class profiler(object):

    def __init__(self, topic):
        if isinstance(topic, str):
            self.topic = topic
        else:
            raise ValueError('Profiler decorator requires a topic.')

        self.decoration_time = current_milli_time()
        print('PR:inside __init__ of', __name__, self.decoration_time)


    def __call__(self, f):
        """
        If there are decorator arguments, __call__() is only called
        once, as part of the decoration process! You can only give
        it a single argument, which is the function object.
        """
        self.f = f
        print('PR:inside __call__ of', __name__, current_milli_time() - self.decoration_time)
        def wrapped_f(*args):
            start_ms = current_milli_time()
            print('PR:inside wrapped_f() of', __name__)
            print('Begin', self.topic, current_milli_time() - self.decoration_time, 'ms after decoration')
            try:
                self.f(*args)
            except Exception as e:
                print('Failed', self.topic, (current_milli_time() - start_ms) / 1e3, 'sec after begin')
                raise
            print('Finish', self.topic, (current_milli_time() - start_ms) / 1e3, 'sec after begin')
            # print('After f(*args)', current_milli_time() - start_ms, 'ms')
        return wrapped_f


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
