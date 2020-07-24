#!/bin/bash
echo "Updating from repo"
git checkout fabric-onboard && git pull
echo "Generating all Configlets and uploading them to HEC14"
ansible-playbook -i cvp cvp.yml -l hec14 --tags "configlets, upload_configlets"
