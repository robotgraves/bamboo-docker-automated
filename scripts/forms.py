import requests
from requests import ConnectionError
import json
import time
from HTMLParser import HTMLParser


class MyHTMLParser(HTMLParser):

    """
    Debugging parser, useful for printing out the whole web page as a parsed set of content
    """

    def handle_starttag(self, tag, attrs):
        print "encountered a start tag:", tag
        for attr in attrs:
            print "     attr:", attr

    def handle_endtag(self, tag):
        print "encountered an end tag:", tag

    def handle_data(self, data):
        print "encountered some data", data


class IllegalStateParser(HTMLParser):
    """
    pulls out error codes from data sections
    """
    def __init__(self, data):
        """
        :param data: string 
        """
        HTMLParser.__init__(self)
        self.data = data
        self.results = False

    def handle_data(self, data):
        if self.data in data:
            self.results = True


class LicenseIDParser(HTMLParser):
    """
    Pulls data out of a tag, name, value setup
    """
    def __init__(self, tag, name=None, value=None):
        """
        :param tag: string
        :param name: string
        :param value: string
        """
        HTMLParser.__init__(self)
        self.recording = 0
        self.data = []
        self.tag = tag
        self.name = name
        self.value = value

    def handle_starttag(self, tag, attrs):
        if tag != self.tag:
            return

        if self.recording:
            self.recording += 1
            return

        if self.name:
            for name, value in attrs:
                if name == self.name and value == self.value:
                    break
            else:
                return
            self.recording = 1

        if not self.name:
            # print "getting tag"
            if tag == self.tag:
                # print "tag gotten, adding recording"
                self.recording = 1

    def handle_endtag(self, tag):
        if tag == self.tag and self.recording:
            # print "clearing tag"
            self.recording -= 1

    def handle_data(self, data):
        if self.recording:
            # print "adding DATA!"
            self.data.append(data)


"""
SETTING DATA
"""
z = file('/home/vagrant/PycharmProjects/bamboo/bamboo/bambookey_modified').read()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Host': 'localhost:8085'
}

license_payload = {
    'sid': 'B0BT-25VZ-MRVP-HV41',
    'licenseString': str(z),
    'expressInstall': 'Express+installation',
    'atl_token': ''
}

config_payload = {
    'instanceName': 'Atlassian+Bamboo',
    'baseUrl': 'http://localhost:8085',
    'configDir': '/var/atlassian-home/xml-data/configuration',
    'buildDir': '/var/atlassian-home/xml-data/builds',
    'buildWorkingDir': '/var/atlassian-home/xml-data/build-dir',
    'artifactsDir': '/var/atlassian-home/artifacts',
    'brokerUrl': 'tcp://0.0.0.0:54663?wireFormat.maxInactivityDuration=300000',
    'save': 'Continue',
    'atl_token': ''
}

database_payload = {
    'dbChoice': 'embeddedDb',
    'selectedDatabase': 'postgresql',
    'selectFields': 'selectedDatabase',
    'save': 'Continue',
    'atl_token': ''
}

import_payload = {
    'dataOption': 'clean',
    'importPath': '',
    'save': 'Continue',
    'atl_token': ''
}

admin_payload = {
    'username': 'bamboo',
    'password': 'test',
    'confirmPassword': 'test',
    'fullName': 'test',
    'email': 'test@test.test',
    'save': 'Finish',
    'atl_token': ''
}

r = requests.session()

x = 1
while x != 0:
    try:
        r.get(
            url='http://localhost:8085/',
            headers=headers
        )
        x = 0
    except ConnectionError:
        print "server still building"
        time.sleep(1)
        x += 1
    if x == 30:
        print "server taking too long to start"
        raise Exception

cookies = {
    'bamboo.dash.display.toggles': 'buildQueueActions-actions-queueControl',
    'BAMBOO-BUILD-FILTER': 'LAST_25_BUILDS',
    'JSESSIONID': r.cookies['JSESSIONID'],
    'atl.xsrf.token': r.cookies['atl.xsrf.token']
}

page = r.get(
    url='http://localhost:8085/setup/setupLicense.action',
    headers=headers,
    cookies=cookies
)

cookies['JSESSIONID'] = page.cookies['JSESSIONID']

LicenseParsed = LicenseIDParser(tag='span', name='id', value='validateLicense_sid')
LicenseParsed.feed(page.text)
license_payload['sid'] = LicenseParsed.data[0]
license_payload['atl_token'] = cookies['atl.xsrf.token']

r.post(
    url='http://localhost:8085/setup/validateLicense.action',
    headers=headers,
    cookies=cookies,
    data=license_payload
)

config_payload['atl_token'] = license_payload['atl_token']

r.post(
    url='http://localhost:8085/setup/validateGeneralConfiguration.action',
    headers=headers,
    cookies=cookies,
    data=config_payload
)

database_payload['atl_token'] = config_payload['atl_token']

r.post(
    url='http://localhost:8085/setup/chooseDatabaseType.action',
    headers=headers,
    cookies=cookies,
    data=database_payload
)

r.get(
    url='http://localhost:8085/setup/setupEmbeddedDatabase.action',
    headers=headers,
    cookies=cookies
)

headers['X-Atlassian-Token'] = 'no-check'
headers['X-Requested-With'] = 'XMLHttpRequest'

x = 1
while x != 0:
    x += 1
    json_response = r.post(
        url='http://localhost:8085/setup/setupEmbeddedDatabase.action',
        headers=headers,
        cookies=cookies)
    try:
        json_data = json.loads(json_response.text)
        print json_data
        x = 0
    except ValueError:
        if json_response.status_code == 200:
            try:
                data = LicenseIDParser(tag='h2', name="id", value="setupWaitMessage")
                data.feed(json_response.text)
                if "Please wait" in data.data[0]:
                    print 'waiting for response'
                else:
                    print data.data
            except IndexError:
                x = 0
            except Exception as e:
                print e.message
                print e.args

                MyHTMLParser().feed(json_response.text)
                print "not expected error"
                raise Exception
        else:
            print json_response.status_code
            print json_response.text
            print "valueError"
    time.sleep(1)
    if x == 60:
        print "taking too long to set up"
        raise Exception

import_payload['atl_token'] = database_payload['atl_token']

r.post(
    url="http://localhost:8085/setup/performImportData.action",
    headers=headers,
    cookies=cookies,
    data=import_payload
)

r.get(
    url='http://localhost:8085/setup/setupAdminUser.action',
    headers=headers,
    cookies=cookies
)

admin_payload['atl_token'] = import_payload['atl_token']

r.post(
    url='http://localhost:8085/setup/performSetupAdminUser.action',
    headers=headers,
    cookies=cookies,
    data=admin_payload
)

r.get(
    url='http://localhost:8085/setup/finishsetup.action',
    headers=headers,
    cookies=cookies
)


cookies['bamboo.dash.display.toggles'] = 'buildQueueActions-actions-queueControl'

x = 1
while x != 0:
    x += 1
    json_response = r.post(
        url='http://localhost:8085/setup/finishsetup.action',
        headers=headers,
        cookies=cookies)
    try:
        json_data = json.loads(json_response.text)
        print json_data
        x = 0
    except ValueError:
        if json_response.status_code == 200:
            response = LicenseIDParser(tag='title')
            response.feed(json_response.text)
            if 'Please wait' in response.data[0]:
                print "waiting for response"
            else:
                find_illegal = IllegalStateParser(data='IllegalStateException')
                find_illegal.feed(json_response.text)
                find_timeout = IllegalStateParser(data='Timeout exceeded')
                find_timeout.feed(json_response.text)
                find_building = LicenseIDParser(tag='h2', name='class', value='welcome-title')
                find_building.feed(json_response.text)
                if find_illegal.results:
                    print "Illegal Exception while OSGI is down, waiting"
                elif find_timeout.results:
                    print "Timeout waiting for OSGI, waiting"
                elif find_building.data[0]:
                    print "build complete"
                    x = 0
                else:
                    print json_response.text
                    print "unexpected response"
                    print find_building.data
                    raise Exception
        else:
            print json_response.status_code
            print json_response.text
            print "valueError"
    time.sleep(1)
    if x == 220:
        print "taking too long to set up"
        raise Exception
