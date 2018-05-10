# This Python file uses the following encoding: utf-8

# // 20180506102118
# // http://169.254.186.173/cgi/tbl/Oper
#
# [
#   { "id": 1, "Name": "OP1", "Pswd": 1 },
#   { "id": 2, "Name": "OP2", "Pswd": 22 },
#   { "id": 3, "Name": "ОПЕРАТОР 3", "Pswd": 3 },
#   { "id": 4, "Name": "ОПЕРАТОР 4", "Pswd": 4 },
#   { "id": 5, "Name": "ОПЕРАТОР 5", "Pswd": 5 },
#   { "id": 6, "Name": "ОПЕРАТОР 6", "Pswd": 6 },
#   { "id": 7, "Name": "ОПЕРАТОР 7", "Pswd": 7 },
#   { "id": 8, "Name": "ОПЕРАТОР 8", "Pswd": 8 },
#   { "id": 9, "Name": "ОПЕРАТОР 9", "Pswd": 9 },
#   { "id": 10, "Name": "ОПЕРАТОР 10", "Pswd": 10 },
#   { "id": 11, "Name": "ОПЕРАТОР 11", "Pswd": 11 },
#   { "id": 12, "Name": "ОПЕРАТОР 12", "Pswd": 12 },
#   { "id": 13, "Name": "ОПЕРАТОР 13", "Pswd": 13 },
#   { "id": 14, "Name": "ОПЕРАТОР 14", "Pswd": 14 },
#   { "id": 15, "Name": "ОПЕРАТОР 15", "Pswd": 15 },
#   { "id": 16, "Name": "mmp", "Pswd": 123 }
# ]


import sys
import requests
import json
import datetime

username = 'service'
password = '751426'

print('\n\n\n')


def talk(url, method='GET', data={}):
    print('\nU:"{}"'.format(url))
    auth = requests.auth.HTTPDigestAuth(username, password)

    if method == 'GET':
        r = requests.get(url, auth=auth)
    elif method == 'POST':
        r = requests.post(url, auth=auth, json=data)
    elif method == 'PATCH':
        headers = {'X-HTTP-Method-Override': 'PATCH'}
        print('D: {}'.format(data))
        r = requests.post(url, auth=auth, json=data, headers=headers)

    print('S:"{}"; R:"{}"'.format(r.status_code, r.reason))
    print(r.text.encode('cp1251'))
    ro = {
        'status_code': r.status_code,
        'reason': r.reason,
        'body': json.loads(r.text, 'cp1251')
    }
    # print('S:"{}"; R:"{}"; B:"{}"'.format(r.status_code, r.reason, body))
    return ro


# Beep
def beep(ms=300, f=660):
    url = 'http://169.254.186.173/cgi/proc/sound?{ms}&{f}'.format(ms=ms, f=f)
    talk(url)


# State
def fiskalMode():
    url = 'http://169.254.186.173/cgi/state'
    r = talk(url)
    return r['body']['FskMode']


# Flg feed 1
def setFeed(lines):
    url = 'http://169.254.186.173/cgi/tbl/Flg'
    talk(url)
    data = {'Feed': lines}
    talk(url, 'PATCH', data)
    talk(url)


# Oper
def setOperator(name, pswd):
    url = 'http://169.254.186.173/cgi/tbl/Oper'
    talk(url)
    data = []
    data.append({'id': 1, 'Name': name, 'Pswd': pswd})
    talk(url, 'PATCH', data)
    talk(url)


# whiteIP
def whiteIP():
    url = 'http://169.254.186.173/cgi/proc/register?clear'
    talk(url)
    url = 'http://169.254.186.173/cgi/proc/register'
    talk(url)
    # talk(url)
    url = 'http://169.254.186.173/cgi/tbl/whiteIP'
    talk(url)


beep(40, 2000)

sys.exit(0)
# SetTime
ISOdatetime = datetime.datetime.fromtimestamp(1463288494).isoformat()
url = 'http://169.254.186.173/cgi/proc/setclock?{datetime}'.format(datetime=ISOdatetime)
talk(url)


#
# url = 'http://169.254.186.173/cgi/proc/fiscalization'
# talk(url)
