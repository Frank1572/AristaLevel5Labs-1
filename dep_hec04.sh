#!/bin/bash
echo "Updating from repo"
git checkout fabric-onboard && git pull
echo "Generating all Configlets and uploading them to HEC04"
ansible-playbook -i cvp cvp.yml -l hec04 --tags "configlets, upload_configlets"
