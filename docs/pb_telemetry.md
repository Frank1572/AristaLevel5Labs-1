# Configure and Install/ Upgrade TerminAttr daemon

This playbook helps to ensure correctly configured telemetry data streaming daemon to CVP. It can also be used to install a specific daemon version to switches.

Based on the values that are set in "inv_daemonTerminAttr" file, the configuration is checked and corrected if needed.
Values in "inv_daemonTerminAttr" are:

  teleipv4
  televrf
  teledaemonbinary
  teledaemonversion

Values set under all:vars do match to all groups. Values set under hecXX:vars are more specific to the selected group or the group that a device belongs to.

# Run the playbook

To maintain the daemon configuration on a device, just run

  ansible-playbook -i inv_daemonTerminAttr pb_telemetry.yml --limit hecXX

This will configure the daemon with the values corresponding to "inv_daemonTerminAttr" settings.

To restart or stop, run

  ansible-playbook -i inv_daemonTerminAttr pb_telemetry.yml --limit hecXX --limit daemon_restart
  ansible-playbook -i inv_daemonTerminAttr pb_telemetry.yml --limit hecXX --limit daemon_stop

To remove the daemon configuration, run

  ansible-playbook -i inv_daemonTerminAttr pb_telemetry.yml --limit hecXX --limit daemon_remove

To install the damon in the version given in both values in "inv_daemonTerminAttr", ensure the swix-binary is existent in ./roles/cvp/files/ and then run

  ansible-playbook -i inv_daemonTerminAttr pb_telemetry.yml --limit hecXX --limit daemon_install

If a device has already the target version, nothing is being done. The playbook does not differentiate between higher or lower version number compared to the installed version. This enables you to also downgrade the agent.
