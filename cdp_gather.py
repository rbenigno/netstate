#!/usr/bin/env python

import argparse
from common import *

# Define and parse command line arguements
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="Device Host/IP")
    parser.add_argument("user", help="User ID")
    parser.add_argument("--passvar", help="Environmental variable with PW.  Otherwise, prompt.")
    return parser.parse_args()


def parse_cdp_neighbors(output):
    """
    Parses the output of IOS "get cdp neighbors" command.

    Based on Napalm get_lldp_neighbors function
    """
    import re

    cdp = {}
    # command = 'show cdp neighbors'

    # Check if router supports the command
    if '% Invalid input' in output:
        return {}

    # Process the output to obtain just the CDP entries
    try:
        split_output = re.split(r'^Device[ |-]ID.*$', output, flags=re.M)[1]
        split_output = re.split(r'^Total cdp entries displayed.*$', split_output, flags=re.M)[0]
    except IndexError:
        return {}

    split_output = split_output.strip()

    # Work through the CDP lines, treating lines starting with whitespace
    # as a continution of the previous line (long device ID)
    for cdp_entry in re.split("\n(?!\s+)", split_output):
        device_id = cdp_entry.split()[0]
        if len(cdp_entry.split('\n')) == 2:
            # Long named entry - device_id is first line
            tmp_field = cdp_entry.split('\n')[1].strip()
        else:
            # Single line entry - spilt at device_id
            tmp_field = cdp_entry.split(None,1)[1].strip()

        # First column is the local port
        local_port = tmp_field[:18].strip()
        # Move to hold time
        tmp_field = re.split(r'\d{1,3}', tmp_field[18:], maxsplit=1)[1]
        # Last column is remote port (not 100% reliable - CAT4507, for example)
        remote_port = tmp_field[30:].strip()

        entry = {'port': remote_port, 'hostname': device_id}
        cdp.setdefault(local_port, [])
        cdp[local_port].append(entry)

    return cdp


def print_cdp_csv(cdp_data, local_device=''):
    """Print out a CDP table in CSV format"""

    print '"Local_Device","Local_Intrfce","Remote_Device","Remote_Port"'
    for local_int in cdp_data:
        for entry in cdp_data[local_int]:
            print '"{}","{}","{}","{}"'.format(local_device, local_int, entry['hostname'], entry['port'])

### ---------------------------------------------------------------------------
### MAIN
### ---------------------------------------------------------------------------

# Main function (when running as an executable)
if __name__ == '__main__':

    # Retrive the command line arguments
    args = parse_args()

    # Establish device connection info
    host = args.host
    username = args.user
    password = get_password(args.passvar)
    if not password:
        print "No password"
        exit()

    # Connect to the device using NAPALM
    from napalm import get_network_driver
    driver = get_network_driver('ios_rtb')
    device = driver(host, username, password)
    device.open()
 
    device_facts = device.get_facts()
    
    # Obtain CDP data using CLI command
    # cli_resp = device.cli(['show cdp neighbors'])
    # cdp_neigh_text = cli_resp['show cdp neighbors']
    # cdp_data = parse_cdp_neighbors(cdp_neigh_text)

    # Get CDP data from NAPALM
    cdp_data = device.get_cdp_neighbors()
    print_cdp_csv(cdp_data, device_facts['hostname'])
