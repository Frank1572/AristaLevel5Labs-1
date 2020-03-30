# HEC_Bringup_Automation

These ansible playbooks are used to configure the cloud vision appliance (CVA), iDRAC of the appliance and cloud vision portal (CVP).

It is required to install data from repository "repo_hec_globals". Run the following after cloning this repository:

 - ansible-galaxy install -r roles/requirements.yml

The following describes how to use the ansible playbooks in a greenfield environment (currently configlets are designed for EVPN):

Always consider the use of "--limit hecxx" (with 'xx' being the location number) to ensure you are not running against the wrong/ all CVP installations in HEC. (This is work in process and may change)

- Create OOB01 a/b configuration with the ansible scripts

		ansible-playbook dhcp.yml -i dhcp --tags "oob01" --limit HECxx

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

       ansible-playbook dhcp.yml -i dhcp --tags "idrac" --timeout 60  --limit hecxx

       ansible-playbook dhcp.yml -i dhcp --tags "cva" --timeout 60  --limit hecxx

       ansible-playbook static.yml -i static --tags "cvp_init" --timeout 60  --limit hecxx

       ansible-playbook static.yml -i static --tags "configlets, upload_configlets, create_containers" --timeout 60  --limit hecxx

 - Software Images need to be assigned manually to the containers (will be automated in future)

 - RADIUS configuration needs to be done manually on CVP (will be automated in future)


After all of these steps were successful you can start with ZTP and moving the devices into the containers they belong to.

# Backup and Restore cell switch configlets from CVP

To manage configlets that have been created via the dynamic onfiglet builders on a CVP server itself, it is required to backup them.

 - Setup local directory to store configlets to

       ansible-playbook pb_custom_configlets.yml --tags "env_local_setup"

 - Download cell switch configgurations from CVP


 - Upload the stored configlets into remote repository

       ansible-playbook pb_custom_configlets.yml --tags "configlets_upload_to_repo"

 - Clean up local directory

       ansible-playbook pb_custom_configlets.yml --tags "env_local_clean"
