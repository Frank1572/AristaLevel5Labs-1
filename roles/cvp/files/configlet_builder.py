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


# Read from configletBuilter path all filenames
configletBuilder_list = []
for (dirpath, dirnames, filenames) in walk(param1):
 configletBuilder_list.extend(filenames)
 break


# Needed for the API request to map configlets to containers
auth_data = json.dumps({'userId':CVP_USER,'password':CVP_PW})
auth_url = "https://%s/cvpservice/login/authenticate.do" % CVP_HOST
auth_response = requests.post(auth_url, data=auth_data, verify=False)
assert auth_response.ok
cookies = auth_response.cookies

client = CvpClient()
client.connect([CVP_HOST], CVP_USER, CVP_PW, protocol='https')


# Add the configlet builders found in the configlet builder path to CVP
for configletBuilder in configletBuilder_list:
 try:
  file = open(param1+configletBuilder, "r")
  config_string = file.read()

  print "Try adding a configlet builder " + configletBuilder

  # Check if configlet builder already exists
  exists = True
  try:
    result = client.api.get_configlet_by_name(configletBuilder)
  except Exception as e:
   if "does not exist" in str(e):
    exists = False
    pass
   else:
    print e

  if not exists:
   note_url = "https://%s/cvpservice/configlet/addConfigletBuilder.do?isDraft=false" % CVP_HOST
   note_response = requests.post(note_url, cookies=cookies, data=config_string, verify=False)

   if json.loads(note_response.text)["data"] == configletBuilder:
    print " Configlet builder created successfully."
   else:
    print "Could not create configlet builder"

  else:
   print " Configlet builder exists already, updating it."
   note_url = "https://%s/cvpservice/configlet/updateConfigletBuilder.do?isDraft=false&id=%s&action=save" % (CVP_HOST, result["key"])
   note_response = requests.post(note_url, cookies=cookies, data=config_string, verify=False)

   if json.loads(note_response.text)["data"] == "success":
    print " Configlet builder updated successfully."
   else:
    print "Could not update configlet builder"

 except Exception as e:
  print " Could not create/update configlet builder."
  print e
