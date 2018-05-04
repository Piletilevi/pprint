# This Python file uses the following encoding: utf-8

import json
import os
import sys
import time


def current_milli_time():
    return int(round(time.time() * 1000))


init_milli_time = current_milli_time()

# current_milli_time = lambda: int(round(time.time() * 1000))


class profiler(object):

    def __init__(self, topic):
        if isinstance(topic, str):
            self.topic = topic
        else:
            raise ValueError('Profiler decorator requires a topic.')

        self.decoration_time = current_milli_time()

        print('[{total:4d} {diff:4d} D:{name}]'.format(
            total=current_milli_time() - init_milli_time,
            diff=current_milli_time() - self.decoration_time,
            name=self.topic))

    def __call__(self, f):
        """
        If there are decorator arguments, __call__() is only called
        once, as part of the decoration process! You can only give
        it a single argument, which is the function object.
        """
        self.f = f

        def wrapped_f(*args):
            start_ms = current_milli_time()
            print('[{total:4d} {diff:4d} Begin:{name}]'.format(
                total=current_milli_time() - init_milli_time,
                diff=current_milli_time() - self.decoration_time,
                name=self.topic))
            try:
                self.f(*args)
            except Exception as e:
                print(e)
                print('[{total:4d} {diff:4d} Fail:{name}]'.format(
                    total=current_milli_time() - init_milli_time,
                    diff=current_milli_time() - self.decoration_time,
                    name=self.topic))
                sys.exit(1)
            print('[{total:4d} {diff:4d} Finish:{name}]'.format(
                total=current_milli_time() - init_milli_time,
                diff=current_milli_time() - self.decoration_time,
                name=self.topic))
        return wrapped_f


class logging(object):
    def __init__(self, f):
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
