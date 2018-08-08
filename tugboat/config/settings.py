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
PROXY = {
    'http': 'http://one.proxy.att.com:8080',
    'https': 'http://one.proxy.att.com:8080',
}
GATEWAY_OFFSET = 3
