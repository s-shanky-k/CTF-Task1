import requests
from requests.auth import HTTPBasicAuth 
import json

#BASE = "http://127.0.0.1:5000/"
BASE = "https://shanky-ctf-task1-api.herokuapp.com/"


#SignUp
response = requests.post(BASE + "signup", json = ({"username":"user","password":"pwd"}))
print(response.json())
input()


#Login
response = requests.get(BASE + "login",auth = HTTPBasicAuth('user', 'pwd'))
print(response.json())
input()


#Get the token
response_json = json.loads(response.text)
token = response_json['token']


#Initialze the X-API-KEY header with obtained token
header={"x-api-key" : token}


#Adding a record
response = requests.post(BASE + "record", json = ({"name":"boom1"}), headers = header)
print(response.json())
input()


#Adding another record
response = requests.post(BASE + "record",json = {"name":"boom2"},headers = header)
print(response.json())
input()


#Fetch all records
response = requests.get(BASE + "record", headers = header)
print(response.json())
input()


#Easy way to find a record using id (primary key)
response = requests.get(BASE + "record/1",headers = header)
print(response.json())
input()


#Search using record ID
response = requests.get(BASE + "search",{"id":"1"},headers = header)
print(response.json())
input()


#Search using record name
response = requests.get(BASE + "search",{"name":"boom2"},headers = header)
print(response.json())
input()


#Update record
response = requests.patch(BASE + "record/2",json = {"new_name":"newBoom"},headers = header)
print(response.json())
response = requests.get(BASE + "record/2",headers = header)
print(response.json())
input()


#Delete record
response = requests.delete(BASE + "record/1",headers = header)
print(response.json())
response = requests.get(BASE + "record/1",headers = header)
print(response.json())
