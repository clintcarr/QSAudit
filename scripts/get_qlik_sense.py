import qrspy
import json
import sys
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--server', help='Qlik Sense Server to connect to.')
parser.add_argument('--certs', help='Path to certificates.')
parser.add_argument('--user', help='Username in format domain\\user')
parser.add_argument('--wmi', help='True/False, set to True to collect WMI information from servers. This switch requires windows authentication (username and password)')
parser.add_argument('--password', help='Password of user.')
args = parser.parse_args()

if args.certs:
    if args.certs[-1] == '/':
        qrs = qrspy.ConnectQlik(server=args.server+':4242', 
                            certificate=(args.certs+'client.pem',
                                            args.certs+'client_key.pem'),
                            root=args.certs+'root.pem')
    else:
        qrs = qrspy.ConnectQlik(server=args.server+':4242', 
                            certificate=(args.certs+'/client.pem',
                                            args.certs+'/client_key.pem'),
                            root=args.certs+'/root.pem')
elif args.user:
    qrs = qrspy.ConnectQlik(server=args.server,
                            credential=args.user,
                            password=args.password)

# qrs = qrspy.ConnectQlik(server='qs2.qliklocal.net:4242', 
#                     certificate=('C:/certs/qs2.qliklocal.net/client.pem',
#                                       'C:/certs/qs2.qliklocal.net/client_key.pem'),
#                     root='C:/certs/qs2.qliklocal.net/root.pem')

def get_about():
    about = qrs.get_about()
    return about

# def get_auditRead():
#     users = qrsntlm.get_user(filterparam='userDirectory eq', filtervalue='qmi-qs-sn')
#     auditUser = []
#     for user in range(len(users)):
#         userId = users[user]['id']
#         userName = users[user]['name']
#         auditDict = {"user": userName}
#         audit = qrsntlm.get_accessibleobjects(userId = userId, action = 2)
#         availApps = []
#         for item in range(len(audit)):
#             availApps.append(audit[item]['name'])
#         auditDict["apps"] = availApps
#         auditUser.append(auditDict)
#     return auditUser

def get_apps():
    x = qrs.get_app(opt='full')
    apps = []
    for item in range(len(x)):
        if x[item]['published'] is False:
            apps.append([x[item]['name'], x[item]['description'],'Not Published', 'Not Published',x[item]['fileSize'], x[item]['owner']['userId'], x[item]['owner']['name']])
        else:
            apps.append([x[item]['name'], x[item]['description'],x[item]['publishTime'],x[item]['stream']['name'], x[item]['fileSize'], x[item]['owner']['userId'], x[item]['owner']['name']])

    return apps

def getAppOwners():
    x = qrs.get_app(opt='Full')
    apps = []
    for item in range(len(x)):
        if x[item]['published'] is False:
            apps.append([x[item]['name'],'Not Published', 'Not Published', x[item]['owner']['userId'], x[item]['owner']['name']])
        else:
            apps.append([x[item]['name'],x[item]['publishTime'],x[item]['stream']['name'], x[item]['owner']['userId'], x[item]['owner']['name']])
    appSummary = []
    return apps

def getAppObjects():
    appObjects = qrs.get_appobject(opt='Full')
    appObj = []
    objects = ['sheet', 'story']
    for obj in objects:
        for object in range(len(appObjects)):
            if appObjects[object]['objectType'] == obj:
                appObj.append([appObjects[object]['app']['name'],appObjects[object]['objectType'], appObjects[object]['name'], appObjects[object]['owner']['userId'], appObjects[object]['owner']['name']])
    return appObj

def totalUsers():
    Owners = qrs.get_app(opt='full')
    uniqueUsers= set()
    for app in range(len(Owners)):
        uniqueUsers.add(Owners[app]['owner']['userId'])
    objectOwners= qrs.get_appobject(opt='full')
    for user in range(len(objectOwners)):
        uniqueUsers.add(objectOwners[user]['owner']['userId'])
    return len(uniqueUsers)



if __name__ == '__main__':
    qrs = qrspy.ConnectQlik(server='qmi-qs-cln', 
                    credential='qmi-qs-cln\\qlik',
                    password='Qlik1234')


