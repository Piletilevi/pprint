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


import requests

username = 'service'
password = '751426'


# Beep
url = 'http://169.254.186.173/cgi/proc/sound?300&660'
r = requests.get(url, auth=requests.auth.HTTPDigestAuth(username, password))


# State
url = 'http://169.254.186.173/cgi/state'
r = requests.get(url, auth=requests.auth.HTTPDigestAuth(username, password))
print(r.status_code, r.reason)
print(r.text.encode("utf-8"))


# SetTime
from datetime import datetime
print(datetime.fromtimestamp(1463288494).isoformat())

url = 'http://169.254.186.173/cgi/proc/setclock?2018-04-28T22:06:00'
r = requests.get(url, auth=requests.auth.HTTPDigestAuth(username, password))
print(r.status_code, r.reason)
print(r.text.encode("utf-8"))

url = 'http://169.254.186.173/cgi/tbl/Oper'
r = requests.post(url, auth=requests.auth.HTTPDigestAuth(username, password),
                  data={'id': 2, 'Name': 'OP2', 'Pswd': '123'})


curl --header "Content-Type: application/json" --digest --user service:751426 ^
     --request POST "http://169.254.186.173/cgi/tbl/Oper" ^
     --data "{[ \"id\": \"2\", \"Name\": \"test2\", \"Pswd\": \"123\" ]}"

curl --digest --user service:751426 ^
     --request POST "http://169.254.186.173/cgi/tbl/Oper" ^
     --data '{[ "id": 2, "Name": "test2", "Pswd": "123" ]}'

curl --digest --user service:751426 ^
     --request POST "http://169.254.186.173/cgi/tbl/Flg" ^
     --data '{"Feed": 2, "Name": "test2", "Pswd": "123" ]}'


/cgi/tbl/Flg
