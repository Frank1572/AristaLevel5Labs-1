# HEC_Bringup_Automation

This ansible playbook is used to configure the cloud vision appliance (CVA), iDRAC of the appliance and cloud vision portal (CVP).

The following describes how to use the ansible playbook in a greenfield envrionment (currently configlets are designed for EVPN):

- Create OOB01 a/b configuration with the ansible scripts
 		ansible-playbook master.yml -i production/production.yml --tags "oob01"

 - Copy the generated configs onto the OOB01 a/b switches. File location is from main ansible folder in "roles/oob01/files/configs/"
 
 - Install DHCP server and config on the OOB01 a/b. Use the files "dhcp-4.2.5-15.fc18.i686.rpm" (*can be different depending on the EOS version*) and the generated "dhcpd.conf" in the folder "roles/oob01/files/"
 
		1) Copy the DHCP RPM and the dhcpd.conf to the switch in the /mnt/flash/ directory, by issuing the following command
		Example for Windows using pscp:
		pscp.exe -scp roles\oob01\files\dhcp-4.2.5-15.fc18.i686.rpm <user>@<sw-hecXX-OOB01a/b-IP>:/mnt/flash/
		pscp.exe -scp roles\oob01\files\dhcpd.conf <user>@<sw-hecXX-OOB01a/b-IP>:/mnt/flash/


		2) On the OOB switch: Install the DHCP rpm into the extendsions folder
		copy flash:dhcp-4.2.5-15.fc18.i686.rpm extension:


		3) On the OOB switch: Install the DHCP RPM
		extension dhcp-4.2.5-15.fc18.i686.rpm force


		4) On the OOB switch: Make the extension persist over reboots
		copy installed-extensions boot-extensions
 
 
 - Enable DHCP server on OOB01 a/b
		dhcp-on
		dhcp-status 
 
 - Power on the Cloud Vision Appliance (CVA)
 
 - On the bash of the OOB01 a/b verify that the CVA requested an IP address via DHCP 
 		bash
		sudo cat /var/lib/dhcpd/dhcpd.leases

 - Set the IP assigned to the CVA in the file <ansible-home>/production/production.yml
  
 - Run the ansible playbooks to setup the environment
 
      ansible-playbook master.yml -i production/production.yml --tags "idrac" --timeout 60

      ansible-playbook master.yml -i production/production.yml --tags "cva" --timeout 60

      ansible-playbook master.yml -i production/production.yml --tags "cvp_init" --timeout 60

      ansible-playbook master.yml -i production/production.yml --tags "configlets, upload_configlets, create_containers" --timeout 60


 - Software Images need to be assigned manually to the containers (will be automated in future)
 
 - RADIUS configuration needs to be done manually on CVP (will be automated in future)


After all of these setps were successful you can start with ZTP and moving the devices into the containers they belong to. 
