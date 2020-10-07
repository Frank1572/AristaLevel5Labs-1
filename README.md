# HEC_Bringup_Automation

These ansible playbooks are used to configure the cloud vision appliance (CVA), iDRAC of the appliance and cloud vision portal (CVP).

It is required to install data from repository "repo_hec_globals". Run the following after cloning this repository:

 - ansible-galaxy install -r roles/requirements.yml -c --force

The following describes how to use the ansible playbooks in a greenfield environment (currently configlets are designed for EVPN):

Always consider the use of "--limit hecXX" (with 'XX' being the location number) to ensure you are not running against the wrong/ all CVP installations in HEC. (This is work in process and may change)

# DHCP on OOB01a/b to provide a dynamic IP to CVA and iDRAC for initial setup

- Create OOB01 a/b dhcp configuration with the ansible scripts

		ansible-playbook oob01.yml -i dhcp --tags "oob01_dhcp" --limit hecXX

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

  - Put the following alias configuration snippet on OOB01 a/b to be able to enable and disable the DHCP service
		
		alias dhcp-off
		   10 bash sudo service dhcpd stop
		   20 bash sudo service dhcpd status
		!
		alias dhcp-on
		   10 bash sudo cp /mnt/flash/dhcpd.conf /etc/dhcp/
		   20 bash sudo service dhcpd start
		   30 bash sudo service dhcpd status
		!
		alias dhcp-status
		   10 bash sudo service dhcpd status
		   20 bash sudo cat /var/lib/dhcpd/dhcpd.leases

 - Enable DHCP server on OOB01 a/b
		
		dhcp-on
		dhcp-status

 - Power on the Cloud Vision Appliance (CVA)

 - On the bash of the OOB01 a/b verify that the CVA requested an IP address via DHCP
 		bash
		sudo cat /var/lib/dhcpd/dhcpd.leases

# Initial Setup of the CVA and CVP

 - Prerequisite is that the CVA received an IP address from DHCP on an OOB Switch 

 - Set the dynamic IP assigned to the CVA in the file "\<ansible-home\>/dhcp"
 
 - Run the ansible playbooks to initially setup the CVA and iDRAC

       ansible-playbook cva.yml -i dhcp --tags "idrac" --timeout 240  --limit hecXX

       ansible-playbook cva.yml -i dhcp --tags "cva" --timeout 240  --limit hecXX
       
 Note: last task "restart network service" will fail because IP address change to static IP.

 - Set the static IP assigned to the CVA in the file "\<ansible-home\>/cva" example x.x.x.43

 - Run the ansible playbooks to setup the CVP

       ansible-playbook cva.yml -i cva --tags "cvp_stop" --timeout 240  --limit hecXX
       
       ansible-playbook cva.yml -i cva --tags "cvp_install" --timeout 240  --limit hecXX
       
       ansible-playbook cva.yml -i cva --tags "cvp_init" --timeout 240  --limit hecXX
       
  - Set the static IP assigned to the CVP in the file "\<ansible-home\>/cvp" example x.x.x.253

       ansible-playbook cvp.yml -i cvp --tags "configlets, upload_configlets, create_containers" --timeout 240  --limit hecXX

 - Software Images need to be assigned manually to the containers (will be automated in future)

 - RADIUS configuration needs to be done manually on CVP (will be automated in future)


After all of these steps were successful you can start with ZTP and moving the devices into the containers they belong to.

# Backup and Restore cell switch configlets from CVP

To manage configlets that have been created via the dynamic onfiglet builders on a CVP server itself, it is required to backup them.

 - Setup local directory to store configlets to

       ansible-playbook pb_custom_configlets.yml --tags "env_local_setup"

 - Download cell switch configgurations from CVP

       ansible-playbook pb_custom_configlets.yml --tags "configlets_download_from_cvp" -i static --limit hecXX

 - Upload the stored configlets into remote repository

       ansible-playbook pb_custom_configlets.yml --tags "configlets_upload_to_repo"

 - Clean up local directory

       ansible-playbook pb_custom_configlets.yml --tags "env_local_clean"

# Deploy/ Maintain TerminAttr (telemetry streaming configuration)

To deploy or correct configuration for TerminAttr agent on switches (if considered incorrect), run the following:

       ansible-playbook pb_telemetry.yml -i inv_daemonTerminAttr --limit hecXX

Maintain the correct parameters for the daemon configuration in file inv_daemonTerminAttr.

To stop daemon on device(s):

      ansible-playbook pb_telemetry.yml -i inv_daemonTerminAttr --tags "daemon_stop" --limit hecXX

To restart daemon service on device(s):

      ansible-playbook pb_telemetry.yml -i inv_daemonTerminAttr --tags "daemon_restart" --limit hecXX

To remove daemon configration from device(s):

      ansible-playbook pb_telemetry.yml -i inv_daemonTerminAttr --tags "daemon_remove" --limit hecXX
