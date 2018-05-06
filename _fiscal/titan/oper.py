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

    body = r.text.encode('utf-8')

    # ro = json.loads(r.text, 'cp1251')
    print('S:"{}"; R:"{}"; B:"{}"'.format(r.status_code, r.reason, body))
    return body


# Beep
url = 'http://169.254.186.173/cgi/proc/sound?300&660'
talk(url)

# State
url = 'http://169.254.186.173/cgi/state'
body = talk(url)
# print('Fiskal mode: ', body['FskMode'])

# SetTime
ISOdatetime = datetime.datetime.fromtimestamp(1463288494).isoformat()
url = 'http://169.254.186.173/cgi/proc/setclock?{datetime}'.format(datetime=ISOdatetime)
talk(url)

# # whiteIP
url = 'http://169.254.186.173/cgi/proc/register?clear'
talk(url)
url = 'http://169.254.186.173/cgi/proc/register'
talk(url)
# talk(url)
url = 'http://169.254.186.173/cgi/tbl/whiteIP'
talk(url)
#
#
# url = 'http://169.254.186.173/cgi/proc/fiscalization'
# talk(url)


# Flg feed 1
# url = 'http://169.254.186.173/cgi/tbl/Flg'
# talk(url)
# data = {'Feed': 1}
# talk(url, 'PATCH', data)
# talk(url)


# Oper
url = 'http://169.254.186.173/cgi/tbl/Oper'
talk(url)
data = []
data.append({'id': 1, 'Name': 'Jaanike', 'Pswd': 123})
talk(url, 'PATCH', data)
talk(url)
