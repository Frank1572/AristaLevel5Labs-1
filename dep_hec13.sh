#!/bin/bash
echo "Updating from repo"
git checkout fabric-onboard && git pull
echo "Generating all Configlets and uploading them to HEC13"
ansible-playbook -i cvp cvp.yml -l hec13 --tags "configlets, upload_configlets"
