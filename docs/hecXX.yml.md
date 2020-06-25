# Required input in a per-location yaml file (a.k.a the "group_vars"-file)

There are various information that needs to be adjusted to reflect CVP, CVA and devices like Borderleafs, Storageleafs, NGDR and so on. The most detailled information for those devices is under the respective dictionary below *hec.TYPE* Follow the table for the minimum of data to put into the variables.
Most of the data is taken as the strings or integer _as is_ so they may simply be taken to render the device config.

Variable name in the dictionary tree | Valid data
------------------------------------ | ----------
hec.fabric.interlink_mtu | MTU size for MLAG- and Spine-Uplinks
hec.fabric.interlink_speed | speed setting for MLAG- and Spine-Uplinks
hec.TYPE | required, lists all non-compute leafs (brdr/str/shs)
hec.TYPE.number |  must be two-characters: [1] the number of the leaf pair, [2] a or b for the member of the pair
hec.TYPE.snmp.location | SNMP location string
hec.TYPE.snmp.contact | SNMP contact string
hec.TYPE.oob_ip | IPv4 address of device's OOB interface (no subnet mask)
hec.TYPE.nwmgmt_ip | IPv4 address of device's inband management interface (no subnet mask)
hec.TYPE.uplinks | simple list with all spine uplinks (no interface name, only ID)
hec.TYPE.spine_port_towards_leaf | name the port that is used on spine-XX to connect to the leaf switch. (it needs to start with _Et_)
