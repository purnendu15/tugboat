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
    'calico': 'calico',
    'cni': 'overlay'
}
IPS_TO_LEAVE = 12
BAREMETAL_TEMPLATES = ['rack', 'bootaction']
PKI_TEMPLATES = ['pki-catalogue']
SITE_DEFINITION_TEMPLATES = ['site_definition']
PROXY = {
    'http': 'http://one.proxy.att.com:8080',
    'https': 'http://one.proxy.att.com:8080',
}
GATEWAY_OFFSET = 3
DEPLOYMENT_MANIFEST = 'full-site'

BGP = {
    'peers': [
        '172.29.0.2',
        '172.29.0.3'
    ],
    'asnumber': 64671,
    'peer_asnumber': 64688,
}

HOSTPROFILE_INTERFACES = {
    'cp': {
        'networks': {
            'pxe': [
                'eno3'
            ],
            'bond1': [
                'gp_nic01',
                'gp_nic02',
            ],
            'p1p1': [
                'sriov_nic01'
            ],
            'p3p2': [
                'sriov_nic02'
            ],
        },
    },
    'gv': {
        'networks': {
            'pxe': ['eno3'],
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
    }
}
LDAP = {
    'admin': 'xyz@ldapservices.test.com'
}

CEPH = {
    'osd_count': 6,
    'osd_count_fullsite': 24,
    'osd': ['sdc', 'sdd', 'sde', 'sdf', 'sdg', 'sdh']
}

CONF = {
    'nova': {
        'vcpu_pin_set': '4-10',
        'passthrough_whitelist': '[{"address": "0000:d8:0a.0", '
        '"physical_network": "sriovnet1", "trusted": "true"}]',
    },
    'neutron': {
        'network_vlan_ranges': 'oam:100:1000,sriovnet1:105:109,'
        'sriovnet2:121:124',
    },
}

OAM = {
    'gw': '172.29.0.3',
    'nw': '172.29.0.0/25',
    'routes': ['172.29.0.128/25', '172.29.1.0/25', '172.29.1.128/25'],
    'static_end': '172.29.0.63',
    'static_start': '172.29.0.13',
    'vlan': '41'
}

OOB = {
    'gw': '172.29.0.3',
    'nw': '172.29.0.0/25',
    'static_end': '172.29.0.63',
    'static_start': '172.29.0.13',
}
