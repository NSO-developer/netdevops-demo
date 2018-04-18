# nso-netdevops-demo

# Introduction

This is a slightly different take on the wonderful [nso-ansible-demo](https://github.com/NSO-developer/nso-ansible-demo)
demo.  

## Demo video

You can see a sample of the demo workflow [here](https://asciinema.org/a/lYRbSZOTKQif2jycTwhygreD1?speed=2)

## NetDevOps
NetDevOps and Infrastructure as Code continue to be hot topics in the networking industry, and the goal
of this demo is to demonstrate how the power of Cisco Network Services Orchestrator and Ansible
can be combined to quickly generate device configurations as code which could be checked into
version control and integrated into a CI/CD pipeline.

## TL;DR

You should be able to quickly run this demo using the following commands

Run the demo
```
make demo
```

Restart/Cleanup the demo
```
make clean
```

Check out the [Makefile](./Makefile) for some other handy shortcuts.

## Detailed Instructions

There are a few dependencies for running this demo which can be installed by

```
pip install -r requirements.txt
```

Use the ncs-netsim tool to prepare to simulate a network consisting of three instances of simulated cisco IOS-XE devices

```
ncs-netsim create-network cisco-ios 3 router
ncs-netsim start
```

This creates all the required files for starting the simulated instances and starts the devices.

The next step is to set up the local NSO runtime environment and start it. The `ncs-setup` command will pick up on the fact that it is being executed
in an environment with netsim set up.  It will provide initial configuration in NSO to communicate with them.

```
ncs-setup --dest .
ncs -v --foreground
```

**Note**  

The steps above can also be done using the `setup` target in the local `Makefile`:

```
make setup
```

### Setup Verification

To verify that the process went correctly, you can login to NSO and verify the
netsim devices were added correctly

Launch NSO CLI by using :

```
ncs_cli -u admin -C
```

Verify the devices are present using `show devices list`
```
admin@ncs# show devices list
NAME     ADDRESS    DESCRIPTION  NED ID     ADMIN STATE  
-------------------------------------------------------
router0  127.0.0.1  -            cisco-ios  unlocked     
router1  127.0.0.1  -            cisco-ios  unlocked     
router2  127.0.0.1  -            cisco-ios  unlocked    
```



## Generate the ansible vars

As NSO provides a northbound API which can represent the YANG data in JSON, we can
easily convert the JSON into YAML which is suitable for usage as host_vars files in Ansible.

A simple python script [generate_ansible.py](./generate_ansible.py) is provided
which will dynamically generate an ansible inventory file, as well as individual host_vars files for each of the devices. This is output in the following files.

```
├── inventory.yaml
├── host_vars
    ├── router0.yaml
    ├── router1.yaml
    └── router2.yaml

```


## Test the generated variables

The data generated in the previous step can be used with a simple playbook which is provided [site.yaml](./site.yaml).  As this configuration originated directly
from the devices themselves, we should be able to run the playbook as many times
as we want, and only making changes if something has drifted.

Execute the playbook
```
ansible-playbook -i inventory.yaml site.yaml
```


Sample output
```
PLAY [Check Synchronization of Devices] *********************************************************************

TASK [check-sync] *******************************************************************************************
changed: [localhost]

PLAY [Verify device configuration] **************************************************************************

TASK [Device configuration] *********************************************************************************
ok: [router0]
ok: [router2]
ok: [router1]

PLAY [Push Desired Configuration to Devices] ****************************************************************

TASK [NSO sync-to action] ***********************************************************************************
changed: [localhost]

PLAY RECAP **************************************************************************************************
localhost                  : ok=2    changed=2    unreachable=0    failed=0   
router0                    : ok=1    changed=0    unreachable=0    failed=0   
router1                    : ok=1    changed=0    unreachable=0    failed=0   
router2                    : ok=1    changed=0    unreachable=0    failed=0   

```

## Infrastructure as Code

What we've really accomplished here is to create a simple YAML representation of
the devices configuration and wrapped them in simple playbook which can be version
controlled and put into a CI/CD pipeline.  

Let's go what step further, and actually make a change to the configuration using
the newly created tool chain.

open up host_vars/router0.yaml in your favorite text editor and look for the following
section

```
tailf-ned-cisco-ios:interface:
  FastEthernet:
  - name: 1/0
  Loopback:
  - name: '0'
```

We want to modify this by adding some additional configuration, like such

```
tailf-ned-cisco-ios:interface:
  FastEthernet:
  - description: this used to just be code
    ip:
      address:
        primary:
          address: 10.10.10.1
          mask: 255.255.255.0
    name: 1/0
  Loopback:
  - description: now its config
    name: '0'
```

Simply rerunning the playbook now will push this change to the devices.


Execute the playbook again, and notice the difference.
```
ansible-playbook -i inventory.yaml site.yaml
```

Sample output
```

PLAY [Check Synchronization of Devices] *********************************************************************

TASK [check-sync] *******************************************************************************************
changed: [localhost]

PLAY [Verify device configuration] **************************************************************************

TASK [Device configuration] *********************************************************************************
ok: [router1]
ok: [router2]
changed: [router0]

PLAY [Push Desired Configuration to Devices] ****************************************************************

TASK [NSO sync-to action] ***********************************************************************************
changed: [localhost]

PLAY RECAP **************************************************************************************************
localhost                  : ok=2    changed=2    unreachable=0    failed=0   
router0                    : ok=1    changed=1    unreachable=0    failed=0   
router1                    : ok=1    changed=0    unreachable=0    failed=0   
router2                    : ok=1    changed=0    unreachable=0    failed=0   

```


You can verify the changes by logging into the netsim device

Launch netsim CLI

```
ncs-netsim cli-c router0
```

```
router0# show running-config interface              
interface FastEthernet1/0
 description this used to just be code
 ip address 10.10.10.1 255.255.255.0
exit
interface Loopback0
 description now its config
exit
```
