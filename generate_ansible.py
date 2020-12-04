"""
generate_ansible.py

This script allows to generate some host variable YAML files
for each device existing in an NSO instance.

These files can later on be modified and the ansible-playbook site.yaml can be run in order to
"""
import os

import yaml

from helpers.nso import NSO


def represent_none(self, _):
    """
    A convenience function to return the null value
    in the YAML file when a value is None in python
    """
    return self.represent_scalar('tag:yaml.org,2002:null', '')


yaml.add_representer(type(None), represent_none)


def main():
    """
    Main function for the script

    It reads the variables to connect to NSO in group_vars/all.yaml
    Then sync_from configuration from the devices.
    It then retrieve the configuration for each via RESTCONF api and save
    each configuration to a yaml file in host_vars/<hostname>.yaml which
    will be used by the ansible-playbook site.yaml.
    """
    with open('group_vars/all.yaml', 'r') as file:
        config = yaml.safe_load(file)

    if not os.path.exists('host_vars'):
        os.makedirs('host_vars')

    nso_ip = config['nso']['ip']
    username = config['nso']['username']
    password = config['nso']['password']
    nso = NSO(nso_ip, username, password)
    #
    print("Syncing Configuration from Devices")
    nso.sync_from()

    devices = nso.get_device_list()

    # track devices to be added to inventory
    inv_devices = list()

    for dev in devices:
        print("Generating host_vars for {}".format(dev))
        config = dict()
        try:
            config['config'] = nso.get_device_config(dev)['tailf-ncs:config']
            with open('host_vars/{}.yaml'.format(dev), 'w') as file:
                yaml.dump(config, file, default_flow_style=False,
                          explicit_start=False)
            inv_devices.append(dev)
        except ValueError:
            print("Failed to parse JSON for {}".format(dev))

    # create inventory yaml
    inv_dict = {"all": {"hosts": {}}}
    inv_dict["all"]["hosts"] = {k: None for k in inv_devices}

    with open('inventory.yaml', 'w') as inv:
        yaml.safe_dump(inv_dict, inv, default_flow_style=False,
                       explicit_start=False,
                       encoding='utf-8')


if __name__ == "__main__":
    main()
