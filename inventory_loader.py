#!/usr/bin/env python

#import json
#from pprint import pprint

from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory

def get_ansible_inventory(inventory_file):
    #  Ansible: initialize needed objects
    variable_manager = VariableManager()
    loader = DataLoader()

    #  Ansible: Load inventory
    inventory = Inventory(
        loader = loader,
        variable_manager = variable_manager,
        host_list = inventory_file,
    )
    return inventory

def get_inventory_hosts(inventory):
    if not isinstance(inventory, Inventory):
        return dict()

    data = list()
    for group in inventory.get_groups():
        if group != 'all':
            for host in inventory.get_group(group).hosts:
                data.append(host.serialize())

    return data

### ---------------------------------------------------------------------------
### MAIN
### ---------------------------------------------------------------------------

# Main function (when running as an executable)
if __name__ == '__main__':
    import sys
    inventory = get_ansible_inventory(sys.argv[1])
    inventory_hosts = get_inventory_hosts(inventory)

    for host in inventory_hosts:
        print '{}\t{}'.format(host['address'], host['name'])

