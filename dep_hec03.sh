#!/bin/bash
echo "Updating from repo"
git checkout fabric-onboard && git pull
echo "Generating all Configlets and uploading them to HEC03"
ansible-playbook -i cvp cvp.yml -l hec03 --tags "configlets, upload_configlets"
