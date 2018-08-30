# Copyright 2018 AT&T Intellectual Property.  All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import yaml
import pkg_resources
import os
import netaddr

from jinja2 import Environment
from jinja2 import FileSystemLoader
from tugboat.site_processors.base import BaseProcessor


class NetworkProcessor(BaseProcessor):
    def __init__(self, file_name):
        raw_data = self.read_file(file_name)
        self.yaml_data = self.get_yaml_data(raw_data)
        self.network_data = self.yaml_data['network']
        self.dir_name = self.yaml_data['region_name']

    @staticmethod
    def read_file(file_name):
        with open(file_name, 'r') as f:
            raw_data = f.read()
        return raw_data

    @staticmethod
    def get_yaml_data(data):
        yaml_data = yaml.safe_load(data)
        return yaml_data

    """ To get genesis ip we take the ksn ip of the genesis node"""
    def get_genesis_ip(self):
        genesis_ip = '0.0.0.0'
        for rack in self.yaml_data['baremetal']:
            for host in self.yaml_data['baremetal'][rack]:
                if self.yaml_data['baremetal'][rack][host][
                        'type'] == 'genesis':
                    genesis_ip = self.yaml_data['baremetal'][rack][
                        host]['ip']['ksn']
        return genesis_ip

    def get_network_data(self):
        network_data = self.yaml_data['network']
        dns_servers = network_data['dns']['servers'].split(',')
        ntp_servers = network_data['ntp']['servers'].split(',')
        proxy = network_data['proxy']
        ceph_cidr = []
        """
        for rack in network_data['rack']:
            ceph_cidr.append(network_data['rack'][rack]['storage']['nw'])
        """
        ceph_cidr.append(network_data['common']['storage']['nw'])
        ksn_vlan_info = network_data['common']['ksn']['vlan']
        overlay_vlan_info = network_data['common']['overlay']['vlan']
        ldap_data = network_data['ldap']
        ldap_data['domain'] = ldap_data['base_url'].split('.')[1]
        bgp_data = network_data['bgp']
        bgp_data['public_service_cidr'] = network_data['ingress']
        subnet = netaddr.IPNetwork(bgp_data['public_service_cidr'])
        ips = list(subnet)
        bgp_data['ingress_vip'] = str(ips[1])

        return {
            'dns_servers': dns_servers,
            'ntp_servers': ntp_servers,
            'proxy': proxy,
            'ceph_cidr': ' '.join(ceph_cidr),
            'ksn_gw': network_data['common']['ksn']['gw'],
            'ksn_vlan': ksn_vlan_info,
            'bgp': bgp_data,
            'dns': network_data['dns'],
            'genesis_ip': self.get_genesis_ip(),
            'ldap': ldap_data,
            'overlay_vlan': overlay_vlan_info
        }

    def get_conf_data(self):
        conf_data = self.yaml_data['conf']
        return {'conf': conf_data}

    def render_template(self):
        template_software_dir = pkg_resources.resource_filename(
            'tugboat', 'templates/networks')
        template_dir_abspath = os.path.dirname(template_software_dir)
        outfile_path = 'pegleg_manifests/site/{}/networks/'.format(
            self.dir_name)
        outfile_dir = os.path.dirname(outfile_path)
        if not os.path.exists(outfile_dir):
            os.makedirs(outfile_dir)
        outfile_j2 = ''
        template = 'common_addresses'
        j2_env = Environment(
            autoescape=False,
            loader=FileSystemLoader(template_software_dir),
            trim_blocks=True)
        data = {
            'hosts': self.get_role_wise_nodes(self.yaml_data),
            'network': self.get_network_data(),
            'conf': self.get_conf_data()
        }
        template_name = j2_env.get_template('{}.yaml.j2'.format(template))
        outfile = '{}{}.yaml'.format(outfile_path, template.replace('_', '-'))
        try:
            print('Rendering data for {}'.format(outfile))
            out = open(outfile, "w")
            # pylint: disable=maybe-no-member
            template_name.stream(data=data).dump(out)
            out.close()
        except IOError as ioe:
            raise SystemExit("Error when generating {:s}:\n{:s}".format(
                outfile, ioe.strerror))

        for dirpath, dirs, files in os.walk(template_dir_abspath):
            for filename in files:
                j2_env = Environment(
                    autoescape=False,
                    loader=FileSystemLoader(dirpath),
                    trim_blocks=True)
                templatefile = os.path.join(dirpath, filename)
                outfile_j2 = ''
                if not outfile_j2 and 'networks/physical' in templatefile:
                    outfile_j2 = outfile_path + templatefile.split(
                        'templates/networks/physical', 1)[1]
                else:
                    continue
                outfile = outfile_j2.split('.j2')[0]
                outfile_dir = os.path.dirname(outfile) + '/physical/'
                if not os.path.exists(outfile_dir):
                    os.makedirs(outfile_dir)
                template_j2 = j2_env.get_template(filename)
                rack_list_data = []
                for racks in self.network_data['rack'].keys():
                    rack_list_data.append(racks)

                self.network_data['rack_list'] = rack_list_data
                self.network_data['region_name'] = self.yaml_data[
                    'region_name']
                yaml_filename = filename.split('.j2')[0]
                try:
                    outfile = '{}{}'.format(outfile_dir, yaml_filename)

                    print('Rendering data for {}'.format(outfile))
                    out = open(outfile, "w")
                    template_j2.stream(
                        data=self.yaml_data['network']).dump(out)
                    out.close()
                except IOError as ioe:
                    raise SystemExit("Error when generating {:s}:\n{:s}"
                                     .format(outfile, ioe.strerror))
