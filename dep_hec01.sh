#!/bin/bash
echo "Updating from repo"
git pull
echo "Generating all Configlets and uploading them to HEC01"
ansible-playbook -i cvp cvp.yml -l hec01 --tags "configlets, upload_configlets"
