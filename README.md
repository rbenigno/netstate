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

    usage: cdp_gather.py [-h] [--host HOST] [--inventory INVENTORY] [--user USER]
                         [--passvar PASSVAR]
    
    optional arguments:
      -h, --help              show this help message and exit
      --host HOST             Device Host/IP
      --inventory INVENTORY   Ansible Inventory file to use (instead of --host)
      --user USER             User ID
      --passvar PASSVAR       Environmental variable with PW. Otherwise, prompt.
