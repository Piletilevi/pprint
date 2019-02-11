# This Python file uses the following encoding: utf-8

# import json
# import os
import sys
import time
import traceback


def current_milli_time():
    return int(round(time.time() * 1000))


init_milli_time = current_milli_time()


class log(object):

    def __init__(self, topic):
        if isinstance(topic, str):
            self.topic = topic
        else:
            raise ValueError('Profiler decorator requires a topic.')

        self.decoration_time = current_milli_time()

    def __call__(self, f):
        self.f = f

        def wrapped_f(*args):
            # print('Args', args)
            print('[{total:4d} {diff:4d} {name}: {message}]'.format(
                total=current_milli_time() - init_milli_time,
                diff=current_milli_time() - self.decoration_time,
                name=self.topic, message=', '.join(args)))
            try:
                self.f(*args)
            except Exception as e:
                traceback.print_exc()
                print('[{total:4d} {diff:4d} Fail:{name}] {e}'.format(
                    total=current_milli_time() - init_milli_time,
                    diff=current_milli_time() - self.decoration_time,
                    name=self.topic,
                    e=e))
                sys.exit(1)
        return wrapped_f


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
            print('[{total:4d} {diff:4d} Begin:{name}]'.format(
                total=current_milli_time() - init_milli_time,
                diff=current_milli_time() - self.decoration_time,
                name=self.topic))
            try:
                self.f(*args)
            except Exception as e:
                traceback.print_exc()
                print('[{total:4d} {diff:4d} Fail:{name}] {e}'.format(
                    total=current_milli_time() - init_milli_time,
                    diff=current_milli_time() - self.decoration_time,
                    name=self.topic,
                    e=e))
                sys.exit(1)
            print('[{total:4d} {diff:4d} Finish:{name}]'.format(
                total=current_milli_time() - init_milli_time,
                diff=current_milli_time() - self.decoration_time,
                name=self.topic))
        return wrapped_f
