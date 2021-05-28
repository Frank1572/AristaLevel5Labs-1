# Required input in a per-location yaml file (a.k.a the "group_vars"-file)

There are various information that needs to be adjusted to reflect CVP, CVA and devices like Borderleafs, Storageleafs, NGDR and so on. The most detailled information for those devices is under the respective dictionary below *hec.TYPE* Follow the table for the minimum of data to put into the variables.
Most of the data is taken as the strings or integer _as is_ so they may simply be taken to render the device config.

Variable name in the dictionary tree | Description
------------------------------------ | -----------
hec.fabric.interlink_mtu | MTU size for MLAG- and Spine-Uplinks
hec.fabric.interlink_speed | speed setting for MLAG- and Spine-Uplinks
hec.fabric.vtep_distribution_mode | set this to either use 'manual', 'cvx', 'migrate' or 'evpn'
hec.core_vlans | if routing between core routers and WAN/VPN routers is with static routed subinterfaces, the 3000-3499 vlans will be created and 'vni-mapped'
hec.routes.static.TYPE | per device pairs, define a list of key-values that describe routes that are to be generated. See next options.
hec.routes.static.TYPE.destination | network/host to add a route for. CIDR notation. (mandatory)
hec.routes.static.TYPE.nexthop | the route's nexthop router (optional)
hec.routes.static.TYPE.interface | source interface to use (optional)
hec.routes.static.TYPE.metric | the route's metric (optional)
hec.routes.static.TYPE.vrf | install route in specific vrf (optional)
hec.routes.static.TYPE.redist_bgp | set to 'true' or 'false' if required to redistribute that route into BGP (optional)
hec.spine.fortygig | list interfaces that have 40G, all others will have value of 'hec.fabric.interlink_speed'
hec.spine.underlay_bfd | enable or disable Bfd for underlay
hec.spine.pod.number | A list of dictionaries, at least pod 1 must be present.
hec.spine.pod.number.id | integer number (1-6) as identifier for Fabric POD
hec.spine.pod.number.model | spine device model.
hec.spine.pod.number.linecards | number of active linecards for spines in this POD.
hec.spine.number.spine_port_towards_superspine | List of 4 uplink ports to superspines.
hec.superspine.model | superspine device model
hec.superspine.linecards | number of active linecards for superspines
hec.superspine.number | list of dictionaries with superspines 1-4
hec.superspine.number.id | superspine id (1-4)
hec.superspine.number.snmp | see spine snmp data Notation
hec.superspine.number.oob_ip | see spine oob ip notation
hec.superspine.number.nwmgmt_ip | see spine nwmgmt ip notation
hec.TYPE | required, lists all non-compute leafs (brdr/str/shs)
hec.TYPE.number |  must be two-characters: [1] the number of the leaf pair, [2] a or b for the member of the pair
hec.TYPE.snmp.location | SNMP location string
hec.TYPE.snmp.contact | SNMP contact string
hec.TYPE.oob_ip | IPv4 address of device's OOB interface (no subnet mask)
hec.TYPE.nwmgmt_ip | IPv4 address of device's inband management interface (no subnet mask)
hec.TYPE.uplinks | simple list with all spine uplinks (no interface name, only ID)
hec.TYPE.spine_port_towards_leaf | name the port that is used on spine-XX to connect to the leaf switch. (it needs to start with _Et_)
hec.TYPE.ports | list of interface IDs without the interface name but only the ID
hec.TYPE.ports.id | interface ID without the interface name but only the ID
hec.TYPE.ports.description | the interface description
hec.TYPE.ports.type | optional value. Valid options: `vlan`, `spine_link`
hec.TYPE.ports.ip | optional value. IPv4 address in CIDR notation
hec.TYPE.ports.po | optional value. Assign port to given port-channel number. Requires also to define the port-channel.
hec.TYPE.ports.trunk | optional value. If set to _all_ the port will be a vlan trunk port with no limitations. Instead of _all_ list all vlans that should only be allowed on the trunk. Notation is colons-separated list of vlan-ids.
hec.TYPE.ports.speed | optional value.

# How to configure NGDR-underlay direct transit networks on Borderleafs.

## Settings in the locations yml file

Variable name in the dictionary tree | Description
------------------------------------ | -----------
hec.ngdr_underlay.edge_as | This is the ASN to be used in EVPN peering.
hec.TYPE.ports.ngdr_underlay | set to `true` to indicate that BGP will use this interface for setting up BGP peering
hec.TYPE.ports.ngdr_underlay_neighbor | IPv4 address of the BGP neighbor for this transit network (do not provide CIDR subnet mask)

## Example content in yml file

The interface must be an SVI (port of `type: vlan`) and it must have an IPv4 address (`ip: XX`)
````
    ngdr_underlay:
      edge_as: 65195
    brdr:
      - number: 1a
        ports:
          - id: 965
            type: vlan
            description: Transfer to rt-hec13-vpn-01a
            mtu: 9100
            ip: 10.254.253.9/31
            ngdr_underlay: true
            ngdr_underlay_neighbor: 10.254.253.8
````
