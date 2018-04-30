import time
import sys
current_milli_time = lambda: int(round(time.time() * 1000))

class profiler(object):

    def __init__(self, topic):
        if isinstance(topic, str):
            self.topic = topic
        else:
            raise ValueError('Profiler decorator requires a topic.')

        self.decoration_time = current_milli_time()
        # print('PR:inside __init__ of', __name__, self.decoration_time)


    def __call__(self, f):
        """
        If there are decorator arguments, __call__() is only called
        once, as part of the decoration process! You can only give
        it a single argument, which is the function object.
        """
        self.f = f
        # print('PR:inside __call__ of', __name__, current_milli_time() - self.decoration_time)
        def wrapped_f(*args):
            start_ms = current_milli_time()
            # print('PR:inside wrapped_f() of', __name__)
            print('Begin', self.topic, current_milli_time() - self.decoration_time, 'ms after decoration')
            try:
                self.f(*args)
            except Exception as e:
                print(e)
                print('Failed', self.topic, (current_milli_time() - start_ms) / 1e3, 'sec after begin')
                sys.exit(1)
            print('Finish', self.topic, (current_milli_time() - start_ms) / 1e3, 'sec after begin')
            # print('After f(*args)', current_milli_time() - start_ms, 'ms')
        return wrapped_f


class feedback():

    def __init__(self, f):
        # print(f.__dir__())
        f.bye = bye
        f.feedback = feedback

    def bye(title = ''):
        # input("Press Enter to continue...")
        if title:
            import ctypes
            (a,b,c) = sys.exc_info()
            if b:
                ctypes.windll.user32.MessageBoxW(0, "{0}\n-----\n{1}".format(title,b), title, 0)
                # ctypes.windll.user32.MessageBoxW(0, "{0}\n{1}\n{2}".format(a,b,c), title, 0)
            else:
                ctypes.windll.user32.MessageBoxW(0, "{0}\n-----\nExiting".format(title), title, 0)
        kill(getpid(), signal.SIGTERM)

    fbtmpl_fn = path.join(BASEDIR, 'config', 'feedbackTemplate.json')
    with open(fbtmpl_fn, 'r', encoding='utf-8') as feedback_template_file:
        FEEDBACK_TEMPLATE = loadJSON(feedback_template_file)
        FEEDBACK_TEMPLATE['feedbackToken'] = PLP_JSON_DATA.get('feedbackToken')
        FEEDBACK_TEMPLATE['operationToken'] = PLP_JSON_DATA.get('operationToken')
        FEEDBACK_TEMPLATE['businessTransactionId'] = PLP_JSON_DATA.get('fiscalData', {'businessTransactionId':''}).get('businessTransactionId', '')
        FEEDBACK_TEMPLATE['operation'] = PLP_JSON_DATA.get('fiscalData').get('operation')


    fblog_fn = path.join(BASEDIR, 'feedback.log')
    def fb2log(line):
        with open(fblog_fn, 'a', encoding='utf-8') as feedback_log_file:
            feedback_log_file.write(datetime.now().isoformat() + ' ' + str(line) + '\n')


    def feedback(feedback, success=True, reverse=None):
        FEEDBACK_TEMPLATE['status'] = success
        FEEDBACK_TEMPLATE['feedBackMessage'] = feedback.get('message')

        _fburl = PLP_JSON_DATA.get('feedbackUrl', PLP_JSON_DATA.get('feedBackurl'))
        # print('Sending "{0}" to "{1}"'.format(dumpsJSON(FEEDBACK_TEMPLATE, indent=4), _fburl))
        fb2log('Sending ' + feedback.get('message'))
        headers = {'Content-type': 'application/json'}
        r = requests.post(_fburl, allow_redirects=True, timeout=30, json=FEEDBACK_TEMPLATE, verify=False)
        fb2log('\\_ sent ok.')

        if r.status_code != requests.codes.ok:
            fb2log('Not Ok - (' + r.status_code + ')')
            if reverse:
                reverse()
            bye('{0}; status_code={1}'.format(r.headers['content-type'], r.status_code))

        try:
            response_json = r.json()
            # print('BO response: {0}'.format(dumpsJSON(response_json, indent=4)))
        except Exception as e:
            fb2log('Not Ok - Feedback failed, reversing operation')
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, "Feedback failed", "Reversing operation", 0)
            # print(e)
            # print('BO response: {0}'.format(r.text))
            if reverse:
                reverse()
            bye()

        fb2log('Ok')



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
