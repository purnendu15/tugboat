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
}
IPS_TO_LEAVE = 12
OOB_IPS_TO_LEAVE = 10
BAREMETAL_TEMPLATES = ['rack', 'bootaction']
PKI_TEMPLATES = ['pki-catalogue']
SITE_DEFINITION_TEMPLATES = ['site_definition']
HOSTPROFILE_TEMPLATES = ['profile']
NETWORK_TEMPLATES = ['common_addresses, physical/rack']
PROXY = {
    'http': 'http://one.proxy.att.com:8080',
    'https': 'http://one.proxy.att.com:8080',
}
NO_PROXY = 'artifacts-nc.mtn29.cci.att.com,docker-nc.mtn29.cci.att.com,' \
    'docker-open-nc.mtn29.cci.att.com,10.96.0.1,cluster.local,' \
    'svc.cluster.local'
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
            'pxe': ['eno3'],
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
LDAP_PROTOCOL = 'ldap'

CEPH = {
    'osd_count': 6,
    'osd_count_fullsite': 24,
    'osd': ['sdc', 'sdd', 'sde', 'sdf', 'sdg', 'sdh']
}

CONF = {
    'nova': {
        'vcpu_pin_set':
        '4-10',
        'passthrough_whitelist':
        '[{"address": "0000:d8:0a.0", '
        '"physical_network": "sriovnet1", "trusted": "true"}]',
    },
    'neutron': {
        'network_vlan_ranges':
        'oam:100:4000,sriovnet1:100:4000,sriovnet2:100:4000'
    },
}
