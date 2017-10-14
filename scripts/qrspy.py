import requests
from requests_ntlm import HttpNtlmAuth
import json
import csv
import random
import string
import datetime

requests.packages.urllib3.disable_warnings()

def set_xrf():
    characters = string.ascii_letters + string.digits
    return ''.join(random.sample(characters, 16))

xrf = set_xrf()

headers = {"X-Qlik-XrfKey": xrf,
           "Accept": "application/json",
           "X-Qlik-User": "UserDirectory=Internal;UserID=sa_repository",
           "Content-Type": "application/json"}

session = requests.session()

class ConnectQlik:
    """
    Instantiates the Qlik Repository Service Class
    """

    def __init__(self, server, certificate=False, root=False,
                 userdirectory=False, userid=False, credential=False, password=False):
        """
        Establishes connectivity with Qlik Sense Repository Service
        :param server: servername.domain:4242
        :param certificate: path to client.pem and client_key.pem certificates
        :param root: path to root.pem certificate
        :param userdirectory: userdirectory to use for queries
        :param userid: user to use for queries
        :param credential: domain\\username for Windows Authentication
        :param password: password of windows credential
        """
        self.server = server
        self.certificate = certificate
        self.root = root
        if userdirectory is not False:
            headers["X-Qlik-User"] = "UserDirectory={0};UserID={1}".format(userdirectory, userid)
        self.credential = credential
        self.password = password

    @staticmethod
    def current_time():
        year = datetime.date.today().year
        month = datetime.date.today().month
        day = datetime.date.today().day
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute
        seconds = datetime.datetime.now().second
        mseconds = 123
        if month <= 9:
            month = ('0'+str(month))
        else:
            month
        if day <= 9:
            day  = ('0' + str(day))
        else:
            day

        return ('{0}-{1}-{2}T{3}:{4}:{5}.{6}Z'.format(year, month, day,hour,minute,seconds,mseconds))
    
    def get(self, endpoint, filterparam=None, filtervalue=None):
        """
        Function that performs GET method to Qlik Repository Service endpoints
        :param endpoint: API endpoint path
        :param filterparam: Filter for endpoint, use None for no filtering
        :param filtervalue: Value to filter on, use None for no filtering
        """
        if self.credential is not False:
            session.auth = HttpNtlmAuth(self.credential, self.password, session)
            headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
        if filterparam is None:
            if '?' in endpoint:
                response = session.get('https://{0}/{1}&xrfkey={2}'.format (self.server, endpoint, xrf),
                                        headers=headers, verify=self.root, cert=self.certificate)
                return response.content
            else:
                response = session.get('https://{0}/{1}?xrfkey={2}'.format (self.server, endpoint, xrf),
                                        headers=headers, verify=self.root, cert=self.certificate)
                
                return response.content
        else:
            if filtervalue in [True, False]:
                response = session.get("https://{0}/{1}?filter={2} {3}&xrfkey={4}".format 
                                        (self.server, endpoint, filterparam, filtervalue, xrf), 
                                        headers=headers, verify=self.root, cert=self.certificate)
            else:
                response = session.get("https://{0}/{1}?filter={2} '{3}'&xrfkey={4}".format 
                                       (self.server, endpoint, filterparam, filtervalue, xrf),
                                        headers=headers, verify=self.root, cert=self.certificate)
            return response.content

    def post(self, endpoint, data=None):
        """
        Function that performs POST method to Qlik Repository Service endpoints
        :param endpoint: API endpoint path
        :param data: Data that is posted in body of request.
        """
        if '?' in endpoint:
            if data is None:
                response = session.post('https://{0}/{1}&xrfkey={2}'.format (self.server, endpoint, xrf),
                                                headers=headers, 
                                                verify=self.root, cert=self.certificate)
                return response.status_code
            else:
                response = session.post('https://{0}/{1}&xrfkey={2}'.format (self.server, endpoint, xrf),
                                                headers=headers, data=data, 
                                                verify=self.root, cert=self.certificate)
                print (response.url)
                return response.status_code
        else:
            if data is None:
                response = session.post('https://{0}/{1}?xrfkey={2}'.format (self.server, endpoint, xrf),
                                                headers=headers, 
                                                verify=self.root, cert=self.certificate)
                return response.status_code, response.content
            else:
                response = session.post('https://{0}/{1}?xrfkey={2}'.format (self.server, endpoint, xrf),
                                                headers=headers, data=data, 
                                                verify=self.root, cert=self.certificate)
                return response.status_code, response.content

    def get_about(self,opt=None):
        """
        Returns system information
        :returns: JSON
        """
        path = 'qrs/about'
        return json.loads(self.get(path).decode('utf-8'))

    def get_app(self, opt=None,filterparam=None, filtervalue=None):
        """
        Returns the applications
        :param filterparam: Property and operator of the filter
        :param filtervalue: Value of the filter
        :returns: JSON
        """
        path = 'qrs/app'
        if opt:
            path += '/full'
        return json.loads(self.get(path, filterparam, filtervalue).decode('utf-8'))

    def get_user(self, opt=None, filterparam=None, filtervalue=None):
        """
        Returns the users
        :param filterparam: Property and operator of the filter
        :param filtervalue: Value of the filter
        :returns: JSON
        """
        path = 'qrs/user'
        if opt:
            path += '/full'
        return json.loads(self.get(path, filterparam, filtervalue).decode('utf-8'))

    def get_accessibleobjects(self, userId, action):
        path = 'qrs/systemrule/security/audit/accessibleobjects'
        self.get_about()
        data = {"resourceType": "App",
                "Action": action,
                "UserId": userId}
        json_data = json.dumps(data)
       
        status, response = self.post(path, json_data)
        return json.loads(response.decode('utf8'))

    def get_appobject(self, opt=None, filterparam=None, filtervalue=None):
        """
        Returns the application objects
        :param filterparam: Property and operator of the filter
        :param filtervalue: Value of the filter
        :returns: JSON
        """
        path = 'qrs/app/object'
        if opt:
            path += '/full'
        return json.loads(self.get(path, filterparam, filtervalue).decode('utf-8'))

if __name__ == '__main__':
    qrs = ConnectQlik(server='qmi-qs-sn:4242', 
                    certificate=('client.pem',
                                      'client_key.pem'),
                    root='root.pem')

    qrsntlm = ConnectQlik(server='qmi-qs-cln', 
                    credential='qmi-qs-cln\\qlik',
                    password='Qlik1234')

 
    