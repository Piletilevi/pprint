# This Python file uses the following encoding: utf-8

from _version import __version__
import sys
import os
import yaml
import json
# import shutil
# import inspect


if sys.argv[-1] == '--after-update':
    print('Just updated to', __version__)
else:
    print('pprint version', __version__)

if hasattr(sys, "frozen"):
    pass
else:
    import win_unicode_console
    win_unicode_console.enable()

BASEDIR = os.path.dirname(sys.executable) if hasattr(sys, "frozen")\
    else os.path.dirname(__file__)

MAPPINGS_FILENAME = os.path.join(BASEDIR, 'config', 'plp_txt2json.yaml')

if not len(sys.argv) > 1:
    raise ValueError('Missin\' plp file name.')


def nested_set(dic, keys, value):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value


with open(MAPPINGS_FILENAME, 'r', encoding='utf-8') as mappings_file:
    m = yaml.load(mappings_file)
    MAPPINGS = m.setdefault('mappings', {})
    PLP_DATA = m.setdefault('defaults', {})
    PREFIXES = m.setdefault('prefixes', {})
    PLPTXT_FILENAME = sys.argv[1]
    PLPJSON_FILENAME = PLPTXT_FILENAME[:-4] + '.json' + PLPTXT_FILENAME[-4:]
    print('converting', PLPTXT_FILENAME, 'to', PLPJSON_FILENAME)
    with open(PLPTXT_FILENAME, 'r', encoding='utf-8') as plptxt_file:
        plptxt = [line.rstrip('\n \t') for line in plptxt_file]

    print('plptxt', plptxt)
    print('\n --- \n')
    # print('MAPPINGS', MAPPINGS)

    parse_header = True
    for line in plptxt:
        if parse_header:
            # Parse header
            if line == 'BEGIN 1':
                parse_header = False
                print('\n --- \n')
                print('PLP_DATA1', PLP_DATA)
                ticket_no = 0
                PLP_DATA['ticketData'].setdefault('tickets', [{}])
                print('\n --- \n')
                continue
            (k, v) = line.split('=')
            print(k, v)
            if MAPPINGS[k] == 'deprecated':
                PLP_DATA.setdefault('deprecated', []).append(k)
            else:
                v = PREFIXES.setdefault(k, '') + v
                nested_set(PLP_DATA, MAPPINGS[k].split('.'), v)
        else:
            # Parse tickets
            print(line)
            print({'ticket_no': ticket_no, 'line': line})
            if line[:3] == 'END':
                continue
            if line[:5] == 'BEGIN':
                ticket_no = int(line[6:]) - 1
                PLP_DATA['ticketData']['tickets'].append({})
                print('PLP_DATA:', PLP_DATA)
                continue
            (k, v) = line.split('=')
            print('k:', k)
            print({'MAPPINGS_k': MAPPINGS[k]})
            print('v:', v)
            if MAPPINGS[k] == 'deprecated':
                PLP_DATA.setdefault('deprecated', []).append(k)
            else:
                v = PREFIXES.setdefault(k, '') + v
                nested_set(PLP_DATA['ticketData']['tickets'][ticket_no],
                           MAPPINGS[k].split('.'),
                           v)

    with open(PLPJSON_FILENAME, 'w', encoding='utf-8') as plpjson_file:
        plpjson_file.write(json.dumps(PLP_DATA, indent=4, sort_keys=True))
