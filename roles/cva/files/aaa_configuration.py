# Copyright (c) 2018 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,  this list of conditions and the following disclaimer in the documentation 
#   and/or other materials provided with the distribution.
# * Neither the name of the Arista nor the names of its contributors may be used to endorse or promote products derived from this software without 
#   specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.

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


# Needed for the API request 
auth_data = json.dumps({'userId':CVP_USER,'password':CVP_PW})
auth_url = "https://%s/cvpservice/login/authenticate.do" % CVP_HOST
auth_response = requests.post(auth_url, data=auth_data, verify=False)
assert auth_response.ok
cookies = auth_response.cookies

client = CvpClient()
client.connect([CVP_HOST], CVP_USER, CVP_PW, protocol='https')


# Add the AAA Servers defined in the YAML

def configure_aaa_servers(aaa_config):   
 aaa_servers = aaa_config["servers"]
 for aaa_server in aaa_servers:
   try:
    print "Try adding AAA server " + aaa_server["ip"]
 
    # Check if AAA Server already exists
    exists = False
    key = ""
    try:
     note_url = "https://%s/cvpservice/aaa/getServers.do?serverType=%s&startIndex=0&endIndex=255" % (CVP_HOST, aaa_config["aaa_type"])
     note_response = requests.get(note_url, cookies=cookies, verify=False)
     json_resp = json.loads(note_response.text)
     if json_resp["total"] > 0:
      for server in json_resp["aaaServers"]:
       if server["ipAddress"] == aaa_server["ip"]:
        exists = True
        key = server["key"]
    except Exception as e:
     print e 

    if not exists:
     print " AAA server does not exist, creating it."
     note_data = json.dumps({"ipAddress":aaa_server["ip"],"serverType":aaa_config["aaa_type"],"secret":aaa_server["secret"],"createdDateInLongFormat":0,"authMode":aaa_server["authMode"],"accountPort":aaa_server["accPort"],"port":aaa_server["authPort"],"status":aaa_server["status"]})    
     note_url = "https://%s/cvpservice/aaa/createServer.do" % CVP_HOST
     note_response = requests.post(note_url, cookies=cookies, data=note_data, verify=False)

     if json.loads(note_response.text)["data"] == "success":
      print " AAA server created successfully."
      # Save new AAA config
      saveAAAChanges(aaa_config["aaa_type"])
       
     else:
      print " Could not create AAA server"
      

    else:
     print " AAA server exists already, udating it."
     note_data = json.dumps({"ipAddress":aaa_server["ip"],"key":key,"serverType":aaa_config["aaa_type"],"secret":aaa_server["secret"],"createdDateInLongFormat":0,"authMode":aaa_server["authMode"],"accountPort":aaa_server["accPort"],"port":aaa_server["authPort"],"status":aaa_server["status"]})    
     note_url = "https://%s/cvpservice/aaa/editServer.do" % CVP_HOST
     note_response = requests.post(note_url, cookies=cookies, data=note_data, verify=False)
   
     if json.loads(note_response.text)["data"] == "success":
      print " AAA server updated successfully."
      # Save new AAA config
      saveAAAChanges(aaa_config["aaa_type"])
      
     else:
      print " Could not update AAA server"

   except Exception as e:
    print " Could not create AAA server."
    print e


def saveAAAChanges(aaa_type):
 # Save new AAA config
 note_data = json.dumps({"authenticationServerType":aaa_config["aaa_type"],"authorizationServerType":aaa_config["aaa_type"]})    
 note_url = "https://%s/cvpservice/aaa/saveAAADetails.do" % CVP_HOST
 note_response = requests.post(note_url, cookies=cookies, data=note_data, verify=False)
 
 if json.loads(note_response.text)["data"] == "success":
  print " AAA config saved."
 else:
  print " Could not save AAA config."

 
json_acceptable_string = param1.replace("u'", "'").replace("'", "\"")
aaa_config = json.loads(json_acceptable_string)



configure_aaa_servers(aaa_config)

