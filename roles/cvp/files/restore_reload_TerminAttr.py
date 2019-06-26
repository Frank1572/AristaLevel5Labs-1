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
import paramiko

param1 = sys.argv[1]
param2 = sys.argv[2]

CVP_HOST = param1
CVP_USER = "cvpadmin"
CVP_PW = param2


# Needed for the API request 
auth_data = json.dumps({'userId':CVP_USER,'password':CVP_PW})
auth_url = "https://%s/cvpservice/login/authenticate.do" % CVP_HOST
auth_response = requests.post(auth_url, data=auth_data, verify=False)
assert auth_response.ok
cookies = auth_response.cookies

client = CvpClient()
client.connect([CVP_HOST], CVP_USER, CVP_PW, protocol='https')


# Get a list of provisioned devices IP addresses
def getProvisionedDevices():   
  print "Getting the IP addresses of provisioned devices."
  devicesList = list()
  try:
    note_url = "https://%s/cvpservice/inventory/devices?provisioned=true" % (CVP_HOST)
    note_response = requests.get(note_url, cookies=cookies, verify=False)
    json_resp = json.loads(note_response.text)
    for device in json_resp:
      devicesList.append(device["ipAddress"])
  except Exception as e:
    print e 
  
  return devicesList

# SSH to the device and reload the TerminAttr daemon 
def relaodTerminAttr(ip_address):
  print "Reload TerminAttr on device with Mgmt IP: %s" % ip_address
  try:
    p = paramiko.SSHClient()
    p.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    p.connect(ip_address, port=22, username=CVP_USER, password=CVP_PW)
    stdin, stdout, stderr = p.exec_command("enable  \n bash sudo killall TerminAttr")
    opt = stdout.readlines()
    opt = "".join(opt)
    print(opt)
  except Exception as e:
    print e
    pass
 

ip_list = getProvisionedDevices()

print ip_list

for ip in ip_list:
  relaodTerminAttr(ip)
