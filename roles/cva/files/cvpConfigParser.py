# Copyright (c) 2015 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import yaml
import re
from os import chmod, chown

YAML_VER_CURRENT = 2
CVP_UID = 10010
CVP_GID = 10010

class CvpConfigParser( object ):
   def __init__( self, fname, ignoreErrors=False ):
      self.attribute = None
      self.fname = fname
      self.config = None

      try:
         self.config = yaml.safe_load( open( fname ) )
      except IOError:
         if ignoreErrors:
            pass
         else:
            raise

      if not self.config:
         self.config = {}

   # TODO: not convinced on this one
   def sanityCheck( self ):
      ''' simple check to verify that this yaml looks OK '''
      if len( self.config.keys() ) < 2:
         return False
      if 'version' not in self.config.keys():
         return False
      return True

   def save( self ):
      with open( self.fname, 'w' ) as yamlFile:
         yamlFile.write( yaml.safe_dump( self.config, default_flow_style=False ) )
         chmod( self.fname, 0660 )
         # ensure that cvp-config.yaml is owned by cvp-user
         chown( self.fname, CVP_UID, CVP_GID )

   def _deriveConfig( self ):
      if self.mode( ) == 'multinode':
         self.config[ 'common' ][ 'primary_hostname' ] = self.hostname( 1 )
         self.config[ 'common' ][ 'primary_host_ip' ] = self.ip_address( 1 )
         self.config[ 'common' ][ 'secondary_hostname' ] = self.hostname( 2 )
         self.config[ 'common' ][ 'secondary_host_ip' ] = self.ip_address( 2 )
         self.config[ 'common' ][ 'tertiary_hostname' ] = self.hostname( 3 )
         self.config[ 'common' ][ 'tertiary_host_ip' ] = self.ip_address( 3 )

   def hostNames( self ):
      if self.mode() == "singlenode":
         return [ self.hostname( 1 ) ]
      else:
         return [ self.hostname( 1 ), self.hostname( 2 ), self.hostname( 3 ) ]

   def mode( self ):
      count = self.nodeCnt( )
      assert count == 1 or count == 3 and 'Must define one or three nodes'
      self.config[ 'common' ][ 'mode' ] = 'singlenode' if count == 1 else 'multinode'
      return self.config[ 'common' ][ 'mode' ]

   def nodeCnt( self ):
      return sum( [ 'node' in n for n in self.config.keys() ] )

   def version( self ):
      return self.config.get( 'version', None )

   def _yaml( self, sections ):
      self._deriveConfig()
      dd = { k:v for k, v in self.config.items() if k in sections }
      return yaml.safe_dump( dd, default_flow_style=False )

   def yamlForNode( self, node ):
      ''' return a string containing the yaml for a given node '''
      sections = ( 'version', 'common', 'node%d' % node )
      return self._yaml( sections )

   def yamlForSystem( self ):
      ''' return a string containing the yaml for a given node '''
      sections = ( 'version', 'common', 'node1', 'node2', 'node3' )
      return self._yaml( sections )

   def __getattr__( self, attribute ):
      ''' This method handles most attribute lookups from the yaml. The idea is
      that the user will make calls like: config.ip_address( node ) Here we'll
      get the attribute name, stash that as the attribute we're looking for and
      then return _getVal() back to the caller. The caller will then pass in
      the node parameter to _getVal() '''
      self.attribute = attribute
      return self._getVal

   def _getVal( self, node=1 ):
      ''' First look under the node, then in the common config '''
      nodeName = 'node%d' % node

      def fltr( val ):
         ''' filter out default looking settings, eg: '<dns1 ip>' '''
         if isinstance( val, list ):
            val = [ v for v in val if not re.match( '<.*>', v ) ]
         elif isinstance( val, str ):
            val = None if re.match( '<.*>', val ) else val
         return val

      try:
         val = self.config[ nodeName ][ self.attribute ]
      except KeyError:
         val = self.config[ 'common' ][ self.attribute ]

      return fltr( val )

   def getIntfIp( self, intfType, defaultIntf, nodeNum ):
      assert intfType in ( 'cluster_interface', 'device_interface' )
      intf = self.get( intfType, defaultIntf, nodeNum )
      ip = self.get( 'interfaces/%s/ip_address' % intf,
                       '', nodeNum )
      netmask = self.get( 'interfaces/%s/netmask' % intf,
                            '', nodeNum )
      return ( ip, netmask )

   def get( self, attribute, defVal=None, node=1 ):
      ''' Like __getattr__(), but return defVal instead of raising a KeyError.
      'attribute' can be in the form of a/b/c where b is a key of 'a' and c is a
      key of 'b'. '''

      nodeName = 'node%d' % node
      val = None
      for nn in ( nodeName, 'common' ):
         try:
            for attr in attribute.split( '/' ):
               if isinstance( val, list ):
                  attr = int( attr ) - 1
               if val is None:
                  val = self.config[ nn ][ attr ]
               else:
                  val = val[ attr ]
         except KeyError:
            val = None
            continue
         else:
            return val
      return defVal

   def set( self, section, key, value=None ):
      if section not in self.config:
         self.config[ section ] = {}

      if section == 'version':
         self.config[ section ] = key
         return

      self.config[ section ][ key ] = value

   def fetchRole( self, ipAddress ):
      for nodeNum in range( 1, 4 ):
         if ipAddress == self.mgmtIp( nodeNum ):
            return { 1: 'primary', 2: 'secondary', 3: 'tertiary' }[ nodeNum ]
      raise RuntimeError( 'IP address %s not in the configuration' % ipAddress )

   def getNodeNum( self, ipAddress ):
      for nodeNum in range( 1, 4 ):
         if ipAddress == self.mgmtIp( nodeNum ):
            return nodeNum
      raise RuntimeError( 'IP address %s not in the configuration' % ipAddress )

   def defaultRoute( self, ipAddress ):
      return self.get( 'default_route', '', node=self.getNodeNum( ipAddress ) )

   def fetchIpAddresses( self ):
      ips = {}
      for nodeNum in range( 1, 4 ):
         role = { 1: 'primary', 2: 'secondary', 3: 'tertiary' }[ nodeNum ]
         ips[ role ] = self.mgmtIp( nodeNum )
      return ips

   def mgmtIp( self, nodeNum ):
      '''Get the "magament" IP address of a node. This is the IP of
      cluster_interface if defined, or eth0.'''
      version = self.version()
      assert version <= YAML_VER_CURRENT, \
            'Error: Unsupported version %s, expected version is %s.' % ( version,
                  YAML_VER_CURRENT )
      cluster_intf = self.get( 'cluster_interface', 'eth0', nodeNum )
      if version == 1:
         cluster_ip = self.get( 'ip_address', '', nodeNum )
      else:
         cluster_ip = self.get( 'interfaces/%s/ip_address' % cluster_intf,
                                '', nodeNum )
      return cluster_ip

   def deviceIp( self, nodeNum ):
      '''Get the "device" IP address of a node. This is the IP of
      device_interface if defined, or eth0.'''
      version = self.version()
      assert version <= YAML_VER_CURRENT,\
            'Error: Unsupported version %s, expected version is %s.' % ( version,
                  YAML_VER_CURRENT )
      device_intf = self.get( 'device_interface', 'eth0', nodeNum )
      if version == 1:
         device_ip = self.get( 'ip_address', '', nodeNum )
      else:
         device_ip = self.get( 'interfaces/%s/ip_address' % device_intf,
                               '', nodeNum )
      return device_ip

   def __str__( self ):
      return yaml.dump( self.config, default_flow_style=False )

   def scrubSrConfig( self, node ):
      '''Post-process to fix necessary keys in static route config.'''

      # Convert the keys static_routes/<rtNum>/{ip_address, netmask} into nested keys
      numSr = self.config[ node ].get( 'num_static_route' )
      if numSr is None or numSr == '':
         self.config[ node ].pop( 'static_routes', None )
         return
      routeConf = []
      srAttr = [ 'route', 'netmask', 'interface' ]
      for srIdx in range( 1, int( numSr )+1 ):
         sr = {}
         for attr in srAttr:
            key = 'static_routes/%s/%s' % ( str( srIdx ), attr )
            route = self.config[ node ].get( key )
            if route is not None:
               sr[ attr ] = route
               del self.config[ node ][ key ]

         routeConf.append( sr )
      self.config[ node ][ 'static_routes' ] = routeConf

   def scrubIntfConfig( self, node, intfs ):
      '''Post-process to fix necessary keys in intfConfig'''

      # Convert the keys <intf>_{ip_address, netmask} into nested keys
      self.config[ node ][ 'interfaces' ] = {}
      for intf in intfs:
         self.config[ node ][ 'interfaces' ][ intf ] = {}
         intfVal = self.config[ node ][ 'interfaces' ][ intf ]
         if 'interfaces/%s/ip_address' % intf in self.config[ node ]:
            intfVal[ 'ip_address' ] = self.config[ node ][
                                     'interfaces/%s/ip_address' % intf ]
            del self.config[ node ][ 'interfaces/%s/ip_address' % intf ]
         if 'interfaces/%s/netmask' % intf in self.config[ node ]:
            intfVal[ 'netmask' ] = self.config[ node ][
                                     'interfaces/%s/netmask' % intf ]
            del self.config[ node ][ 'interfaces/%s/netmask' % intf ]
         if self.config[ node ][ 'interfaces' ][ intf ] == {}:
            del self.config[ node ][ 'interfaces' ][ intf ]

   def scrubTacacsConfig( self, node ):
      ''' Post-process to fix necessary keys in tacacs config'''

      # Convert the keys <tacacs>_{ ip_address, key, port } into nested keys
      if self.config[ 'common' ][ 'tacacs/ip_address' ]:
         section = 'common'
         # clear tacacs config in node section
         try:
            del self.config[ node ][ 'tacacs' ]
         except KeyError:
            pass
      else:
         section = node
         # clear tacacs config in common section
         try:
            del self.config[ 'common' ][ 'tacacs' ]
         except KeyError:
            pass
      self.config[ section ][ 'tacacs' ] = {}
      tacVal = self.config[ section ][ 'tacacs' ]
      if 'tacacs/ip_address' in self.config[ section ]:
         if self.config[ section ][ 'tacacs/ip_address' ]:
            tacVal[ 'ip_address' ] = self.config[ section  ][ 'tacacs/ip_address' ]
         del self.config[ section ][ 'tacacs/ip_address' ]
      if 'tacacs/key' in self.config[ section  ]:
         if self.config[ section ][ 'tacacs/key' ]:
            tacVal[ 'key' ] = self.config[ section ][ 'tacacs/key' ]
         del self.config[ section ][ 'tacacs/key' ]
      if 'tacacs/port' in self.config[ section ]:
         if self.config[ section ][ 'tacacs/port' ]:
            tacVal[ 'port' ] = self.config[ section ][ 'tacacs/port' ]
         del self.config[ section ][ 'tacacs/port' ]

   def removeEmptyKeys( self ):
      ''' Post-process to remove empty items.'''
      for section in self.config.keys():
         if section  == 'version':
            continue
         for key in self.config[ section ].keys():
            if len( self.config[ section ][ key ] ) == 0:
               del self.config[ section ][ key ]
         # we keep both node and common secion since cvpConfigVerifier.verifyConfig()
         # looks for common and node configuration
