# Configure and Install/ Upgrade TerminAttr daemon

For information about variables for the agent, please see the README.md in https://github.wdf.sap.corp/thecoolkids/arista_terminattr/blob/master/README.md

# Run the playbook

The following playbook "pb_telemetry.yml" is just a non-existing example. In order to create a playbook and use the role "arista_terminattr", please follow the information mentioned in the above paragraph.

To maintain the daemon configuration on a device, just run

    ansible-playbook -i inv_daemonTerminAttr pb_telemetry.yml --limit hecXX

This will configure the daemon with the values corresponding to "inv_daemonTerminAttr" settings.

To restart or stop, run

    ansible-playbook -i inv_daemonTerminAttr pb_telemetry.yml --limit hecXX --tags daemon_restart
    ansible-playbook -i inv_daemonTerminAttr pb_telemetry.yml --limit hecXX --tags daemon_stop

To remove the daemon configuration, run

    ansible-playbook -i inv_daemonTerminAttr pb_telemetry.yml --limit hecXX --tags daemon_remove

To install the damon in the version given in both values in "inv_daemonTerminAttr", ensure the swix-binary is existent in ./roles/cvp/files/ and then run

    ansible-playbook -i inv_daemonTerminAttr pb_telemetry.yml --limit hecXX --tags daemon_install

If a device has already the target version, nothing is being done. The playbook does not differentiate between higher or lower version number compared to the installed version. This enables you to also downgrade the agent.
