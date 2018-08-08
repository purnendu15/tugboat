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
import re

import netaddr
from .base import ParserEngine
from .utils.excel_parser import ExcelParser
import tugboat.config.settings as settings


class GenerateYamlFromExcel(ParserEngine):
    def __init__(self, file_name, excel_specs):
        self.HOST_TYPES = settings.HOST_TYPES
        self.PRIVATE_NETWORK_TYPES = settings.PRIVATE_NETWORK_TYPES
        self.IPS_TO_LEAVE = settings.IPS_TO_LEAVE
        parsed_data = self.get_parsed_data(file_name, excel_specs)
        self.ipmi_data = parsed_data['ipmi_data'][0]
        self.hostnames = parsed_data['ipmi_data'][1]
        self.private_network_data = self.get_private_network_data(
            parsed_data['network_data'])
        self.public_network_data = self.get_public_network_data(
            parsed_data['network_data'])
        self.dns_ntp_data = self.get_dns_ntp_data(
            parsed_data['network_data']
        )
        self.host_type = {}
        self.data = {
            'network': {},
            'baremetal': {},
        }
        self.no_proxy = []
        self.dhcp_relay = ''
        self.genesis_rack = ''
        self.network_data = {
            'assigned_subnets': {},
        }
        self.racks = set()

    def get_parsed_data(self, file_name, excel_specs):
        parser = ExcelParser(file_name, excel_specs)
        return parser.get_data()

    def get_private_network_data(self, raw_data):
        network_data = {}
        for net_type in self.PRIVATE_NETWORK_TYPES:
            for key in raw_data['private']:
                if net_type.lower() in key.lower():
                    network_data[self.PRIVATE_NETWORK_TYPES[
                        net_type]] = raw_data['private'][key]
        return network_data

    def get_public_network_data(self, raw_data):
        network_data = raw_data['public']
        return network_data

    def get_dns_ntp_data(self, raw_data):
        network_data = raw_data['dns_ntp']
        return network_data

    def format_network_data(self):
        vlan_pattern = '\d+'
        public_vlan = self.public_network_data['oam']['vlan']
        value = re.findall(vlan_pattern, public_vlan)
        self.public_network_data['oam']['vlan'] = value[0]
        for net_type in self.private_network_data:
            value = ''
            for key in self.private_network_data[net_type]:
                if key == 'subnet_range':
                    value = self.private_network_data[net_type][key].split(
                        '-')[0].replace(' ', '')
                elif 'vlan' in key.lower():
                    tmp_value = re.findall(
                        vlan_pattern,
                        self.private_network_data[net_type][key])
                    if not tmp_value:
                        continue
                    else:
                        value = tmp_value[0]
                else:
                    cidr_pattern = '/\d\d'
                    value = re.findall(
                        cidr_pattern,
                        self.private_network_data[net_type][key])[0]
                self.private_network_data[net_type][key] = value
        for type_ in self.dns_ntp_data:
            raw_list = self.dns_ntp_data[type_].split()
            data_list = []
            for data in raw_list:
                if '(' not in data:
                    data_list.append(data)
            data_string = ' '.join(data_list)
            self.dns_ntp_data[type_] = data_string

    def get_rack(self, host):
        rack_pattern = '\w.*(r\d+)\w.*'
        return re.findall(rack_pattern, host)[0]

    def categorize_hosts(self):
        is_genesis = False
        controller_pattern = '\w.*r\d+o\d+'
        for host in self.hostnames:
            if re.search(controller_pattern, host):
                if not is_genesis:
                    self.host_type[host] = 'genesis'
                    is_genesis = True
                else:
                    self.host_type[host] = 'controller'
            else:
                self.host_type[host] = 'compute'

    def get_rackwise_subnet(self):
        rackwise_subnets = {}
        sorted_racks = sorted(self.racks)
        for rack in sorted_racks:
            rackwise_subnets[rack] = {}
        self.format_network_data()
        for net_type in self.private_network_data:
            assigned_subnets = []
            network_range = netaddr.IPNetwork(
                self.private_network_data[net_type]['subnet_range'])
            cidr_per_rack = self.private_network_data[net_type][
                'cidr_per_rack']
            cidr = int(cidr_per_rack.split('/')[1])
            total_racks = len(self.racks)
            subnets = network_range.subnet(cidr, count=total_racks)
            i = 0
            for subnet in subnets:
                if net_type not in rackwise_subnets[sorted_racks[i]]:
                    rackwise_subnets[sorted_racks[i]][net_type] = ''
                rackwise_subnets[sorted_racks[i]][net_type] = subnet
                i += 1
                assigned_subnets.append(str(subnet))
            self.network_data['assigned_subnets'][net_type] = assigned_subnets
        return rackwise_subnets

    def get_rackwise_hosts(self):
        rackwise_hosts = {}
        for rack in self.racks:
            if rack not in rackwise_hosts:
                rackwise_hosts[rack] = []
            for host in self.hostnames:
                if rack in host:
                    rackwise_hosts[rack].append(host)
        return rackwise_hosts

    def assign_private_ip_to_hosts(self):
        rackwise_hosts = self.get_rackwise_hosts()
        rackwise_subnets = self.get_rackwise_subnet()
        for rack in self.racks:
            self.network_data[rack] = {}
            for net_type in self.private_network_data:
                subnet = rackwise_subnets[rack][net_type]
                ips = list(subnet)
                mid = len(ips) // 2
                static_start = str(ips[self.IPS_TO_LEAVE + 1])
                static_end = str(ips[mid - 1])
                self.network_data[rack][net_type] = {
                    'static_start': static_start,
                    'static_end': static_end
                }
                if net_type == 'pxe':
                    dhcp_start = str(ips[mid])
                    dhcp_end = str(ips[-2])
                    self.network_data[rack][net_type][
                        'dhcp_start'] = dhcp_start
                    self.network_data[rack][net_type][
                        'dhcp_end'] = dhcp_end
                for i in range(len(rackwise_hosts[rack])):
                    self.ipmi_data[rackwise_hosts[rack][i]][net_type] = str(
                        ips[i + self.IPS_TO_LEAVE + 1])

    def assign_public_ip_to_host(self):
        rackwise_hosts = self.get_rackwise_hosts()
        for rack in self.racks:
            subnet = netaddr.IPNetwork(self.public_network_data['oam']['ip'])
            ips = list(subnet)
            for i in range(len(rackwise_hosts[rack])):
                self.no_proxy.append(str(ips[i + self.IPS_TO_LEAVE + 1]))
                self.ipmi_data[rackwise_hosts[rack][i]]['oam'] = str(
                    ips[i + self.IPS_TO_LEAVE + 1])

    def get_rack_data(self):
        for host in self.hostnames:
            rack = self.get_rack(host)
            self.racks.add(rack)

    def assign_ip(self):
        self.categorize_hosts()
        rackwise_hosts = self.get_rackwise_hosts()
        tmp_data = {}
        for rack in self.racks:
            tmp_data[rack] = {}
            for host in rackwise_hosts[rack]:
                ip_ = {}
                tmp_data[rack][host] = {}
                ip_['oob'] = self.ipmi_data[host]['ipmi_address']
                ip_['oam'] = self.ipmi_data[host]['oam']
                for net_type in self.private_network_data:
                    ip_[net_type] = self.ipmi_data[host][net_type]
                tmp_data[rack][host]['ip'] = ip_
                tmp_data[rack][host]['type'] = self.host_type[host]
                if self.host_type[host] == 'genesis':
                    self.dhcp_relay = tmp_data[rack][host]['ip']['pxe']
                    self.genesis_rack = rack
                tmp_data[rack][host]['host_profile'] = self.ipmi_data[host][
                    'host_profile']
                tmp_data[rack][host]['rack'] = rack
        self.data['baremetal'] = tmp_data

    def assign_network_data(self):
        rackwise_subnets = self.get_rackwise_subnet()
        for rack in rackwise_subnets:
            for net_type in rackwise_subnets[rack]:
                ips = list(rackwise_subnets[rack][net_type])
                nw = str(rackwise_subnets[rack][net_type])
                gw = str(ips[settings.GATEWAY_OFFSET])
                routes = [
                    subnet for subnet in self.network_data['assigned_subnets'][
                        net_type] if subnet != nw
                ]
                rackwise_subnets[rack][net_type] = {
                    'nw': nw,
                    'gw': gw,
                    'routes': routes,
                    'static_start': self.network_data[rack][net_type][
                        'static_start'],
                    'static_end': self.network_data[rack][net_type][
                        'static_end'],
                }
                if net_type == 'pxe':
                    rackwise_subnets[rack][net_type][
                        'dhcp_start'] = self.network_data[rack][net_type][
                            'dhcp_start']
                    rackwise_subnets[rack][net_type][
                        'dhcp_end'] = self.network_data[rack][net_type][
                            'dhcp_end']
                if 'vlan' in self.private_network_data[net_type]:
                    rackwise_subnets[rack][net_type][
                        'vlan'] = self.private_network_data[net_type]['vlan']
            if rack == self.genesis_rack:
                rackwise_subnets[rack]['is_genesis'] = True
        self.data['network'] = rackwise_subnets
        for net_type in self.public_network_data:
            self.data['network'][net_type] = self.public_network_data[net_type]
        self.data['network']['proxy'] = settings.PROXY
        self.data['network']['proxy']['no_proxy'] = ' '.join(self.no_proxy)
        self.data['network']['ntp'] = {
            'servers': self.dns_ntp_data['ntp'],
        }
        self.data['network']['dns'] = {
            'domain': self.dns_ntp_data['domain'],
            'servers': self.dns_ntp_data['dns'],
            'dhcp_relay': self.dhcp_relay,
        }

    def generate_intermediary_yaml(self):
        self.get_rack_data()
        self.get_rackwise_subnet()
        self.assign_private_ip_to_hosts()
        self.assign_public_ip_to_host()
        self.assign_ip()
        self.assign_network_data()

    def generate_yaml(self):
        self.generate_intermediary_yaml()
        yaml_data = yaml.dump(self.data, default_flow_style=False)
        with open('intermediary.yaml', 'w') as f:
            f.write(yaml_data)
