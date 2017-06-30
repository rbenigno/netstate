#!/usr/bin/env python

import argparse
import re
from common import *

from inventory_loader import get_ansible_inventory
from inventory_loader import get_inventory_hosts

# Define and parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="Device Host/IP")
    parser.add_argument("--inventory", help="Ansible Inventory file to use (instead of --host)")
    parser.add_argument("--user", help="User ID")
    parser.add_argument("--passvar", help="Environmental variable with PW.  Otherwise, prompt.")
    return parser.parse_args()


def parse_cdp_neighbors(output):
    """
    Parses the output of IOS "get cdp neighbors" command.

    Based on Napalm get_lldp_neighbors function
    """

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


# Connect to a device with NAPALM and run a cli command
def run_napalm_cdp_getter(host, username, password):
    # Connect to the device using NAPALM
    from napalm import get_network_driver
    driver = get_network_driver('ios_rtb')
    device = driver(host, username, password)
    try:
        device.open()
        result = device.get_cdp_neighbors()
        device.close()
        return result
    except Exception as e:
        print 'Error: {}'.format(e)
        return {}


### ---------------------------------------------------------------------------
### MAIN
### ---------------------------------------------------------------------------

# Main function (when running as an executable)
if __name__ == '__main__':

    # Retrive the command line arguments
    args = parse_args()

    # Establish device connection info
    if args.inventory:
        inventory = get_ansible_inventory(args.inventory)
        inventory_hosts = get_inventory_hosts(inventory)
    else:
        host = args.host
    username = args.user
    password = get_password(args.passvar)
    if not password:
        print "No password"
        exit()

    try:
        for host in inventory_hosts:
            print '\n# Running on device {}'.format(host['name'])
            cdp_data = run_napalm_cdp_getter(host['address'], username, password)
            print_cdp_csv(cdp_data, host['name'])
    except:
        cdp_data = run_napalm_cdp_getter(host, username, password)
        print_cdp_csv(cdp_data, host)
