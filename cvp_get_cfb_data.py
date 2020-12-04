import sys
import json
import requests
from cvprac.cvp_client import CvpClient
from os import walk

param1 = sys.argv[1]
param2 = sys.argv[2]
param3 = sys.argv[3]

CVP_HOST = param2
CVP_USER = "cvpadmin"
CVP_PW = param3


# Needed for the API request to map configlets to containers
auth_data = json.dumps({'userId':CVP_USER,'password':CVP_PW})
auth_url = "https://%s/cvpservice/login/authenticate.do" % CVP_HOST
auth_response = requests.post(auth_url, data=auth_data, verify=False)
assert auth_response.ok
cookies = auth_response.cookies

client = CvpClient()
client.connect([CVP_HOST], CVP_USER, CVP_PW, protocol='https')

CONFLET_NAME="sw-hec-autoconf-generate-only"
NOTE_URL = "https://%s/cvpservice/configlet/getConfigletByName.do?name=%s" % CVP_HOST, CONFLET_NAME
NOTE_RESPONSE = requests.get(NOTE_URL, cookies=cookies, verify=False)

print json.loads(NOTE_RESPONSE.text)
