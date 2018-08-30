# Copyright 2018 The Openstack-Helm Authors.
# Copyright (c) 2018 AT&T Intellectual Property. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

HOST_TYPES = [
    'genesis',
    'controllers',
    'computes',
]
TEMPLATES_DIR = 'templates/'
PROCESSORS_DIR = ['baremetal']
PRIVATE_NETWORK_TYPES = {
    'pxe': 'pxe',
    'storage': 'storage',
    'calico': 'ksn',
    'overlay': 'overlay',
}
STATE_CODES = {
    'New Jersey': 'NJ',
    'Texas': 'TX',
}
IPS_TO_LEAVE = 12
OOB_IPS_TO_LEAVE = 10
BAREMETAL_TEMPLATES = ['rack', 'calico-ip-rules',
                       'promjoin', 'sriov-blacklist']
PKI_TEMPLATES = ['pki-catalogue']
SITE_DEFINITION_TEMPLATES = ['site_definition']
HOSTPROFILE_TEMPLATES = ['profile']
NETWORK_TEMPLATES = ['common_addresses, physical/rack']
PROXY = {
    'http': 'http://one.proxy.att.com:8080',
    'https': 'http://one.proxy.att.com:8080',
}

NO_PROXY = '10.96.0.2,10.96.232.136,artifacts-nc.mtn29.cci.att.com,' \
    'docker-nc.mtn29.cci.att.com,docker-open-nc.mtn29.cci.att.com,' \
    '10.96.0.1,cluster.local,svc.cluster.local,,localhost,127.0.0.1,10.0.0.0/8'


GATEWAY_OFFSET = 1
DEPLOYMENT_MANIFEST = 'full-site'

BGP = {
    'peers': ['172.29.0.2', '172.29.0.3'],
    'asnumber': 64671,
    'peer_asnumber': 64688,
}

HOSTPROFILE_INTERFACES = {
    'cp': {
        'networks': {
            'bond1': [
                'gp_nic01',
                'gp_nic02',
            ],
            'p1p1': ['sriov_nic01'],
            'p3p2': ['sriov_nic02'],
        },
    },
    'gv': {
        'networks': {
            'bond1': [
                'gp_nic01',
                'gp_nic02',
            ],
            'p1p1': ['sriov_nic01'],
            'p3p2': ['sriov_nic02'],
        },
    },
    'nsb': {
        'networks': {
            'pxe': ['eno4'],
            'bond1': [
                'gp_nic01',
                'gp_nic02',
            ],
            'p1p1': ['sriov_nic01'],
            'p3p2': ['sriov_nic02'],
        },
    },
    'ns': {
        'networks': {
            'pxe': ['eno4'],
            'bond1': [
                'gp_nic01',
                'gp_nic02',
            ],
            'p1p1': ['sriov_nic01'],
            'p3p2': ['sriov_nic02'],
        },
    }
}
LDAP_PROTOCOL = 'ldap'

CEPH = {
    'osd_count': 6,
    'osd_count_fullsite': 24,
    'osd': ['sdc', 'sdd', 'sde', 'sdf', 'sdg', 'sdh']
}

"""
Assuming that there is a unique hw profile for
controller and compute nodes. This settings shall
be overidden when there are multiple compute/controller
nodes with varying HW types
"""

HARDWARE_PROFILE = {
    'host_type': {
        'ctrl': 'nc-cp',
        'compute': 'nc-ns-r740'
    },
    'hw_type': {
        'ctrl': 'dell_r740_purley_nc',
        'compute': 'dell_r740_purley_nc'
    },
    'profile_name': {
        'ctrl': 'cp',
        'compute': 'nsb'
    },

}


CONF = {
    'nova': {
        'vcpu_pin_set':
        '4-10',
        'passthrough_whitelist':
        '[{"address": "0000:d8:0a.0", "physical_network": "sriovnet2",'
        '"trusted": "true"},{"address": "0000:d8:0a.1", "physical_network": '
        '"sriovnet2", "trusted": "true"},{"address": "0000:d8:0b.2", '
        '"physical_network": "sriovnet2", "trusted": "true"},{"address": '
        '"0000:d8:0b.3", "physical_network": "sriovnet2", "trusted": "true"},'
        '{"address": "0000:d8:0b.4", "physical_network": "sriovnet2", '
        '"trusted": "true"},{"address": "0000:d8:0b.5", "physical_network": '
        '"sriovnet2", "trusted": "true"},{"address": "0000:d8:0b.6", '
        '"physical_network": "sriovnet2", "trusted": "true"},{"address": '
        '"0000:d8:0b.7", "physical_network": "sriovnet2", "trusted": "true"},'
        '{"address": "0000:d8:0c.0", "physical_network": "sriovnet2", '
        '"trusted": "true"},{"address": "0000:d8:0c.1", "physical_network": '
        '"sriovnet2", "trusted": "true"},{"address": "0000:d8:0c.2", '
        '"physical_network": "sriovnet2", "trusted": "true"},{"address": '
        '"0000:d8:0c.3", "physical_network": "sriovnet2", "trusted": "true"},'
        '{"address": "0000:d8:0a.2", "physical_network": "sriovnet2", '
        '"trusted": "true"},{"address": "0000:d8:0c.4", "physical_network": '
        '"sriovnet2", "trusted": "true"},{"address": "0000:d8:0c.5", '
        '"physical_network": "sriovnet2", "trusted": "true"},{"address": '
        '"0000:d8:0c.6", "physical_network": "sriovnet2", "trusted": "true"},'
        '{"address": "0000:d8:0c.7", "physical_network": "sriovnet2", '
        '"trusted": "true"},{"address": "0000:d8:0d.0", "physical_network": '
        '"sriovnet2", "trusted": "true"},{"address": "0000:d8:0d.1", '
        '"physical_network": "sriovnet2", "trusted": "true"},{"address": '
        '"0000:d8:0d.2", "physical_network": "sriovnet2", "trusted": "true"},'
        '{"address": "0000:d8:0d.3", "physical_network": "sriovnet2", '
        '"trusted": "true"},{"address": "0000:d8:0d.4", "physical_network": '
        '"sriovnet2", "trusted": "true"},{"address": "0000:d8:0d.5", '
        '"physical_network": "sriovnet2", "trusted": "true"},{"address": '
        '"0000:d8:0a.3", "physical_network": "sriovnet2", "trusted": "true"},'
        '{"address": "0000:d8:0d.6", "physical_network": "sriovnet2", '
        '"trusted": "true"},{"address": "0000:d8:0d.7", "physical_network": '
        '"sriovnet2", "trusted": "true"},{"address": "0000:d8:0a.4", '
        '"physical_network": "sriovnet2", "trusted": "true"},{"address": '
        '"0000:d8:0a.5", "physical_network": "sriovnet2", "trusted": "true"},'
        '{"address": "0000:d8:0a.6", "physical_network": "sriovnet2", '
        '"trusted": "true"},{"address": "0000:d8:0a.7", "physical_network": '
        '"sriovnet2", "trusted": "true"},{"address": "0000:d8:0b.0", '
        '"physical_network": "sriovnet2", "trusted": "true"},{"address": '
        '"0000:d8:0b.1", "physical_network": "sriovnet2", "trusted": "true"},'
        '{"address": "0000:3b:02.0", "physical_network": "sriovnet1", '
        '"trusted": "true"},{"address": "0000:3b:02.1", "physical_network": '
        '"sriovnet1", "trusted": "true"},{"address": "0000:3b:03.2", '
        '"physical_network": "sriovnet1", "trusted": "true"},{"address": '
        '"0000:3b:03.3", "physical_network": "sriovnet1", "trusted": "true"},'
        '{"address": "0000:3b:03.4", "physical_network": "sriovnet1", '
        '"trusted": "true"},{"address": "0000:3b:03.5", "physical_network": '
        '"sriovnet1", "trusted": "true"},{"address": "0000:3b:03.6", '
        '"physical_network": "sriovnet1", "trusted": "true"},{"address": '
        '"0000:3b:03.7", "physical_network": "sriovnet1", "trusted": "true"},'
        '{"address": "0000:3b:04.0", "physical_network": "sriovnet1", '
        '"trusted": "true"},{"address": "0000:3b:04.1", "physical_network": '
        '"sriovnet1", "trusted": "true"},{"address": "0000:3b:04.2", '
        '"physical_network": "sriovnet1", "trusted": "true"},{"address": '
        '"0000:3b:04.3", "physical_network": "sriovnet1", "trusted": "true"},'
        '{"address": "0000:3b:02.2", "physical_network": "sriovnet1", '
        '"trusted": "true"},{"address": "0000:3b:04.4", "physical_network": '
        '"sriovnet1", "trusted": "true"},{"address": "0000:3b:04.5", '
        '"physical_network": "sriovnet1", "trusted": "true"},{"address": '
        '"0000:3b:04.6", "physical_network": "sriovnet1", "trusted": "true"},'
        '{"address": "0000:3b:04.7", "physical_network": "sriovnet1", '
        '"trusted": "true"},{"address": "0000:3b:05.0", "physical_network": '
        '"sriovnet1", "trusted": "true"},{"address": "0000:3b:05.1", '
        '"physical_network": "sriovnet1", "trusted": "true"},{"address": '
        '"0000:3b:05.2", "physical_network": "sriovnet1", "trusted": "true"},'
        '{"address": "0000:3b:05.3", "physical_network": "sriovnet1", '
        '"trusted": "true"},{"address": "0000:3b:05.4", "physical_network": '
        '"sriovnet1", "trusted": "true"},{"address": "0000:3b:05.5", '
        '"physical_network": "sriovnet1", '
        '"trusted": "true"},{"address": "0000:3b:02.3", "physical_network": '
        '"sriovnet1", "trusted": "true"},{"address": "0000:3b:05.6", '
        '"physical_network": "sriovnet1", "trusted": "true"},{"address": '
        '"0000:3b:05.7", "physical_network": "sriovnet1", "trusted": "true"},'
        '{"address": "0000:3b:02.4", "physical_network": "sriovnet1", '
        '"trusted": "true"},{"address": "0000:3b:02.5", "physical_network": '
        '"sriovnet1", "trusted": "true"},{"address": "0000:3b:02.6", '
        '"physical_network": "sriovnet1", "trusted": "true"},{"address": '
        '"0000:3b:02.7", "physical_network": "sriovnet1", "trusted": "true"},'
        '{"address": "0000:3b:03.0", "physical_network": "sriovnet1", '
        '"trusted": "true"},{"address": "0000:3b:03.1", "physical_network": '
        '"sriovnet1", "trusted": "true"}]',
    },
    'neutron': {
        'network_vlan_ranges':
        ' oam:100:1000,sriovnet1:105:109,sriovnet2:121:124'
    },
}
