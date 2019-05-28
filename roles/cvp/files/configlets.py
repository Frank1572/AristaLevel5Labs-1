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
from cvprac.cvp_client import CvpClient
from os import walk

param1 = sys.argv[1]
param2 = sys.argv[2]
param3 = sys.argv[3]

CVP_HOST = param2
CVP_USER = "cvpadmin"
CVP_PW = param3


configlet_path = param1

configlet_list = []
for (dirpath, dirnames, filenames) in walk(configlet_path):
 configlet_list.extend(filenames)
 break


client = CvpClient()
client.connect([CVP_HOST], CVP_USER, CVP_PW, protocol='https')

# Add the configlets found in the configlet path to CVP
for configlet in configlet_list:
 try:
  file = open(configlet_path+configlet, "r")
  config_string = file.read()
  
  print "Try adding a configlet " + configlet
 
  # Check if configlet already exists
  exists = True
  try:
    result = client.api.get_configlet_by_name(configlet)
  except Exception as e:
   if "does not exist" in str(e):
    exists = False
    pass
   else:
    print e 

  if not exists:
   result = client.api.add_configlet(configlet, config_string)
   if "configlet" in result:
    print " Configlet was created: "+configlet
   else:
    print " Configlet could not be created: "+configlet
  else:
   print " Configlet exists already, udating it: "+configlet
   result = client.api.update_configlet(config_string, result["key"], configlet)
   print " "+result["data"]

 except Exception as e:
  print e



