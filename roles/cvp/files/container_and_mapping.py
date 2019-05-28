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


param1 = sys.argv[1]
param2 = sys.argv[2]
param3 = sys.argv[3]
param4 = sys.argv[4]

hec_id = param2

CVP_HOST = param3
CVP_USER = "cvpadmin"
CVP_PW = param4

# Needed for the API request to map configlets to containers
auth_data = json.dumps({'userId':CVP_USER,'password':CVP_PW})
auth_url = "https://%s/cvpservice/login/authenticate.do" % CVP_HOST
auth_response = requests.post(auth_url, data=auth_data, verify=False)
assert auth_response.ok
cookies = auth_response.cookies


parent_container = ""

def loop(containers):
 for container in containers:

  if "is_root" in container.keys():
   # Set the name of the root container
   try:
    print "Renaming Root Container"
    root_name = container["name"]
    note_data = json.dumps({"data":[{"info": "","infoPreview": "","action":"update","nodeType":"container","nodeId":"root","toId": "","fromId": "","nodeName":root_name,"toName":"","fromName":"","toIdType":"container","configCompareCount":{}}]})
    note_url = "https://%s/cvpservice/provisioning/addTempAction.do?nodeId=root&format=list" % CVP_HOST
    note_response = requests.post(note_url, cookies=cookies, data=note_data, verify=False)

    if note_response.status_code == 200:
     print " Added temporary change for renaming root container."
    else:
     print " Failed to add temporary change for renaming root container."
 
    note_data = json.dumps([])
    note_url = "https://%s/cvpservice/provisioning/v2/saveTopology.do" % CVP_HOST
    note_response = requests.post(note_url, cookies=cookies, data=note_data, verify=False)
    
    if note_response.status_code == 200:
     print " Successfully renamed root container."
    else:
     print " Failed to rename root container."
  

   except Exception as e:
    print " Failed to rename root container."
    print e  


  elif "below_root" in container.keys():
   # Add the containers below the root container
   try:
    print "Adding container below Root Container"
    # Check if container already exists
    result = getContainerId(container["name"])
    
    if not result:
     result = client.api.add_container(container["name"], "" , "root")
     if result["data"]["status"] == "success":
      print " Container was created: "+container["name"]
      if "configlets" in container.keys():
       mapConfigletToContainer(container["name"], container["configlets"])
     else:
      print " Container could not be created: "+container["name"]
    else:
     print " Container exists already: "+container["name"]
     if "configlets" in container.keys():
      mapConfigletToContainer(container["name"], container["configlets"])

   except Exception as e:
    print " Container could not be created."
    print e
  


  # Loop trough all subcontainers recursivly
  if "subcontainer" in container.keys():
   
   # Before going to the container, create all subcontainers for the current container 
   createSubContainerInCVP(container["name"], container["subcontainer"])
 
   loop(container["subcontainer"])


def createSubContainerInCVP(parent_container, subcontainers ):
 for subcontainer in subcontainers:
  # Add subcontainers under it's parent container
  try:
   print "Adding container below container: "+parent_container

   # Check if container already exists
   result = getContainerId(subcontainer["name"])
   
   if not result:
    result = client.api.add_container(subcontainer["name"], parent_container , getContainerId(parent_container))
    if result["data"]["status"] == "success":
     print " Container was created: "+subcontainer["name"]
     if "configlets" in subcontainer.keys():
      mapConfigletToContainer(subcontainer["name"], subcontainer["configlets"])
    else:
     print " Container could not be created: "+subcontainer["name"]
   else:
    print " Container exists already: "+subcontainer["name"]
    if "configlets" in subcontainer.keys():
      mapConfigletToContainer(subcontainer["name"], subcontainer["configlets"])

  except Exception as e:
   print " Container could not be created."
   print e


def mapConfigletToContainer(container_name, container_configlets):
 try:
  containerID =  getContainerId(container_name)
  if containerID:
 
   for configlet_name in container_configlets:
    configletID =  getConfigletId(configlet_name["name"])
    if configletID:
     # create json data for mapping
     note_data = json.dumps({"data":{"configlets": [],"configletBuilders": [],"configletMappers":[{"key":"","configletId":configletID,"type":"container","objectId":containerID,"containerId":"","appliedBy":"cvpadmin","configletType":"Static","appliedDateInLongFormat":0}]}})
     note_url = "https://%s/cvpservice/configlet/addConfigletsAndAssociatedMappers.do" % CVP_HOST
     note_response = requests.post(note_url, cookies=cookies, data=note_data, verify=False)
    
     if note_response.status_code == 200:
      print (" Configlet %s was assigned to container %s." % (configlet_name["name"], container_name))
    
    else:
     print "Could not read configlet ID for: "+configlet_name["name"]

  else:
   print "Could not read container ID for: "+container_name

 except Exception as e:
   print " Could not map configlet to container."
   print e
 

def getContainerName(id):
 result = client.api.get_container_by_id(id)
 if result:
  return result["name"]
 else:
  return None

def getContainerId(name):
 result = client.api.get_container_by_name(name)
 if result:
  return result["key"]
 else:
  return None

def getConfigletId(name):
 result = client.api.get_configlet_by_name(name)
 if result:
  return result["key"]
 else:
  return None




client = CvpClient()
client.connect([CVP_HOST], CVP_USER, CVP_PW, protocol='https')



json_acceptable_string = param1.replace("u'", "'").replace("'", "\"")
containers = json.loads(json_acceptable_string)


loop(containers)
