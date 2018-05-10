# This Python file uses the following encoding: utf-8


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
    return r


# SetTime
def setTime():
    ISOdatetime = datetime.datetime.fromtimestamp(1463288494).isoformat()
    url = 'http://169.254.186.173/cgi/proc/setclock?{datetime}' \
        .format(datetime=ISOdatetime)
    talk(url)


# Beep
def beep(ms=300, f=660):
    url = 'http://169.254.186.173/cgi/proc/sound?{ms}&{f}'.format(ms=ms, f=f)
    talk(url)


# State
def getFiskalMode():
    url = 'http://169.254.186.173/cgi/state'
    r = talk(url)
    return json.loads(r.text, 'cp1251')['FskMode']


# whiteIP
def whiteIP():
    url = 'http://169.254.186.173/cgi/proc/register?clear'
    talk(url)
    # print(json.dumps(readTable('whiteIP'), indent=4))
    url = 'http://169.254.186.173/cgi/proc/register'
    talk(url)
    # print(json.dumps(readTable('whiteIP'), indent=4))


# Tables
def tables():
    url = 'http://169.254.186.173/cgi/tbl'
    r = talk(url)

    jbody = json.loads(r.text[3:])
    return jbody


# read table
def readTable(name):
    url = 'http://169.254.186.173/cgi/tbl/{name}'.format(name=name)
    r = talk(url)
    jbody = json.loads(r.text)
    return jbody


# read table
def writeTable(name, data):
    url = 'http://169.254.186.173/cgi/tbl/{name}'.format(name=name)
    r = talk(url, 'PATCH', data)
    jbody = json.loads(r.text)
    return jbody


# cgi/chk
def printBill(data):
    url = 'http://169.254.186.173/cgi/chk'
    r = talk(url, 'POST', data)
    return r


# Set feed
def setFeed(lines):
    print(json.dumps(readTable('Flg'), indent=4))

    data = []
    data.append({'Feed': lines})
    print(json.dumps(writeTable('Flg', 'data'), indent=2))

    print(json.dumps(readTable('Flg'), indent=4))


#
# main
#
whiteIP()
print('Fiscal mode: {}'.format(getFiskalMode()))
# print(json.dumps(readTable('PLU'), indent=4))

# setFeed(4)
url = 'http://169.254.186.173/cgi/tbl/Flg'
data = {'Feed': 2}
r = talk(url, 'PATCH', data)
print(json.dumps(readTable('Flg'), indent=4))

jbill = json.loads('''{"F":[
    {"C":{"cm":"Кассир: Светлана"}},
    {"S":{"code":"1","price":"5","name":"Конфета"}},
    {"S":{"code":"2","price":"15","name":"Печенье", "qty":"0.5"}},
    {"D":{ "prc":"5", "all":"1"}},
    {"P":{}}
    ]}''')

# r = printBill(jbill)
# print(r.text)


# print(json.dumps(tables(), indent=4))
# print(json.dumps(readTable('whiteIP'), indent=4))
# print(json.dumps(readTable('TCP'), indent=4))
# print(json.dumps(readTable('Host'), indent=4))
# print(json.dumps(readTable('Dir'), indent=4))
# # # print(json.dumps(readTable('SysLog'), indent=4))


# Oper
def setOperator(name, pswd):
    url = 'http://169.254.186.173/cgi/tbl/Oper'
    talk(url)
    data = []
    data.append({'id': 1, 'Name': name, 'Pswd': pswd})
    talk(url, 'PATCH', data)
    talk(url)


sys.exit(0)


#
# url = 'http://169.254.186.173/cgi/proc/fiscalization'
# talk(url)

# Do not play this sequence too often
beep(80,  262)  # C4
beep(80,  330)  # E4
beep(80,  392)  # G4
beep(160, 523)  # C5
beep(80,  392)  # G4
beep(480, 523)  # C5
