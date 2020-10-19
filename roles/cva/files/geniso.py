#! /usr/bin/env python
#
# Copyright (c) 2015 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import os
import argparse
import tempfile
import shutil
import crypt
import getpass
import datetime
import cvpConfigParser
import random

yamlname = 'cvp-config.yaml'

def genIso( args ):
   config = cvpConfigParser.CvpConfigParser( args.yaml )

   # Parse the yaml file and generate an ISO for each node.
   # Each ISO will be named: node<n>-<vmname>.iso
   # Each ISO will contain:
   # 1. cvp-config.yaml: An exact copy of the YAML file passed in.
   # 2. nodename.txt: Name of the node that the ISO should be loaded on.
   # 3. id_rsa: private key, same content in all ISOs
   # 4. id_rsa.pub: public key, same content in all ISOs
   # 5. password: The hashed password to stuff into /etc/shadow. Note that the
   #              password is the same for all nodes, but the hash is unique for
   #              each node
   id_rsa = tempfile.NamedTemporaryFile()
   id_rsa.close()
   res = os.system( 'ssh-keygen -t rsa -f %s -N "" -q' % id_rsa.name )
   assert res == 0, 'ssh-keygen: %s' % os.strerror( res )

   isoFiles = []
   for n in range( 1, config.nodeCnt() + 1 ):
      tempDir = tempfile.mkdtemp()
      try:
         vmname = config.vmname( n )
      except KeyError:
         hostname = config.hostname( n )
         vmname = hostname.partition( "." )[ 0 ]
      isoname = 'node%d' % n + '-' + vmname + '.iso'
      isopath = '%s/%s' % ( args.outdir, isoname )
      print 'Building ISO for %s %s: %s' % ( 'node%d' % n, vmname, isopath )

      shutil.copyfile( args.yaml, os.path.join( tempDir, yamlname ) )
      with open( os.path.join( tempDir, 'nodename.txt' ), 'w' ) as nodenameFile:
         nodenameFile.write( 'node%d\n' % n )
      shutil.copyfile( id_rsa.name, os.path.join( tempDir, 'id_rsa' ) )
      shutil.copyfile( id_rsa.name + '.pub', os.path.join( tempDir, 'id_rsa.pub' ) )
      os.chmod( os.path.join( tempDir, 'id_rsa' ), 0600 )
      os.chmod( os.path.join( tempDir, 'id_rsa.pub' ), 0600 )

      # If password is empty the user does not want to set a root password
      if args.password:
         with open( os.path.join( tempDir, 'password' ), 'w' ) as passwordFile:
            # This is a floating point number, it still serves our purpose
            salt = str( random.random() )
            passwordFile.write( crypt.crypt( args.password, "$6$%s" % salt ) )

      res = os.system( 'mkisofs -quiet -r -o {} {}'.format( isopath, tempDir ) )
      assert res == 0, 'mkisofs: %s' % os.strerror( res )
      shutil.rmtree( tempDir )
      isoFiles.append( isopath )

   os.unlink( id_rsa.name )
   os.unlink( id_rsa.name + '.pub' )
   return isoFiles

def readPassword():
   print "Please enter a password for root user on cvp"
   while True:
      password = getpass.getpass()
      passRepeat = getpass.getpass( "Please re-enter the password: " )
      if password == passRepeat:
         return password
      print "Passwords don't match, please retry"

def parseArgs():
   parser = argparse.ArgumentParser( description='Generate CVP Tools ISO' )
   parser.add_argument( '-y', '--yaml',
                        help='Config file in YAML', required=True )
   parser.add_argument( '-o', '--outdir',
                        help='Optional directory to place ISO files into' )
   parser.add_argument( '-p', '--password',
                        help="Password for the root user. If no password is "
                             "given then prompt for the password." )

   args = parser.parse_args()
   if not args.outdir:
      outdir = str(datetime.datetime.now()).rpartition( "." )[ 0 ]
      args.outdir = "cvp.iso." + outdir.replace( " ", "_" )

   if not os.path.exists( args.outdir ):
      os.makedirs( args.outdir )

   if not args.password:
      args.password = readPassword()

   return args

def main():
   args = parseArgs()
   genIso( args )

if __name__ == '__main__':
   main()
