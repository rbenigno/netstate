# Overview

Set of scripts used to gather current state from a network.  This can be
used to take a point-in-time snapshot of a network before and after a change
is made.

Uses the NAPALM Python library as the interface to network devices.

Inventory files use the Ansible inventory format.

# Usage

Currently extending the IOSDriver class from NAPALM with a new `get_cdp_neighbors` function.  Goal is to submit a PR to bring this into NAPALM.

Example:

    # Print the CDP table from a device in a CSV format
    ./cdp_gather.py <host> <username>