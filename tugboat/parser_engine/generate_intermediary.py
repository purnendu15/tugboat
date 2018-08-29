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
        self.OOB_IPS_TO_LEAVE = settings.OOB_IPS_TO_LEAVE
        parsed_data = self.get_parsed_data(file_name, excel_specs)
        self.ipmi_data = parsed_data['ipmi_data'][0]
        self.hostnames = parsed_data['ipmi_data'][1]
        self.private_network_data = self.get_private_network_data(
            parsed_data['network_data'])
        self.public_network_data = self.get_public_network_data(
            parsed_data['network_data'])
        self.dns_ntp_ldap_data = self.get_dns_ntp_ldap_data(
            parsed_data['network_data'])
        self.location_data = self.get_location_data(
            parsed_data['location_data'])
        self.host_type = {}
        self.data = {
            'network': {},
            'baremetal': {},
            'profiles': {},
            'region_name': '',
            'conf': {},
            'ceph': {},
            'location': {},
        }
        self.service_ip = ''
        self.region_name = ''
        self.dhcp_relay = ''
        self.genesis_rack = ''
        self.network_data = {
            'assigned_subnets': {},
        }
        self.racks = {}

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

    def get_dns_ntp_ldap_data(self, raw_data):
        network_data = raw_data['dns_ntp_ldap']
        return network_data

    def get_location_data(self, raw_data):
        corridor_pattern = '\d+'
        corridor_number = re.findall(corridor_pattern, raw_data['corridor'])[0]
        name = raw_data['name']
        state = settings.STATE_CODES[raw_data['state']]
        country = raw_data['country']
        physical_location_id = raw_data['physical_location_id']
        return {
            'corridor': 'c{}'.format(corridor_number),
            'name': name,
            'state': state,
            'country': country,
            'physical_location_id': physical_location_id,
        }

    def assign_location_data(self):
        self.data['location'] = self.location_data

    def format_network_data(self):
        vlan_pattern = '\d+'
        public_vlan = self.public_network_data['oam']['vlan']
        value = re.findall(vlan_pattern, public_vlan)
        self.public_network_data['oam']['vlan'] = value[0]
        for net_type in self.private_network_data:
            value = ''
            for key in self.private_network_data[net_type]:
                if 'vlan' in key.lower():
                    tmp_value = re.findall(
                        vlan_pattern, self.private_network_data[net_type][key])
                    value = tmp_value[0]
                    self.private_network_data[net_type][key] = value
        for type_ in self.dns_ntp_ldap_data:
            if type_ != 'ldap':
                raw_list = self.dns_ntp_ldap_data[type_].split()
                data_list = []
                for data in raw_list:
                    if '(' not in data:
                        data_list.append(data)
                data_string = ','.join(data_list)
                self.dns_ntp_ldap_data[type_] = data_string
            else:
                url = self.dns_ntp_ldap_data[type_]['url']
                base_url = url.split('//')[1]
                url = '{}://{}'.format(settings.LDAP_PROTOCOL, base_url)
                self.dns_ntp_ldap_data[type_]['base_url'] = base_url
                self.dns_ntp_ldap_data[type_]['url'] = url

    def get_rack(self, host):
        rack_pattern = '\w.*(r\d+)\w.*'
        rack = re.findall(rack_pattern, host)[0]
        if not self.region_name:
            self.region_name = host.split(rack)[0]
        return rack

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
        racks = [self.racks[rack] for rack in self.racks]
        sorted_racks = sorted(racks)
        for rack in sorted_racks:
            rackwise_subnets[rack] = {}
        self.format_network_data()
        rackwise_subnets['common'] = {}
        for net_type in self.private_network_data:
            if not self.private_network_data[net_type]['is_common']:
                i = 0
                subnets = self.private_network_data[net_type]['subnet']
                for subnet in subnets:
                    subnet = netaddr.IPNetwork(subnet)
                    if net_type not in rackwise_subnets[sorted_racks[i]]:
                        rackwise_subnets[sorted_racks[i]][net_type] = ''
                    rackwise_subnets[sorted_racks[i]][net_type] = subnet
                    i += 1
                    if i >= len(sorted_racks):
                        break
            else:
                rackwise_subnets['common'][
                    net_type] = netaddr.IPNetwork(
                        self.private_network_data[net_type]['subnet'][0])
        return rackwise_subnets

    def get_rackwise_hosts(self):
        rackwise_hosts = {}
        for rack in self.racks:
            if rack not in rackwise_hosts:
                rackwise_hosts[self.racks[rack]] = []
            for host in self.hostnames:
                if rack in host:
                    rackwise_hosts[self.racks[rack]].append(host)
        return rackwise_hosts

    def assign_private_ip_to_hosts(self):
        rackwise_hosts = self.get_rackwise_hosts()
        rackwise_subnets = self.get_rackwise_subnet()
        sorted_racks = sorted(self.racks)
        j = 0
        for rack in sorted_racks:
            rack = self.racks[rack]
            self.network_data[rack] = {}
            for net_type in self.private_network_data:
                if not self.private_network_data[net_type]['is_common']:
                    subnet = rackwise_subnets[rack][net_type]
                    ips = list(subnet)
                    for i in range(len(rackwise_hosts[rack])):
                        self.ipmi_data[rackwise_hosts[rack][i]][
                            net_type] = str(ips[i + self.IPS_TO_LEAVE + 1])
                    mid = len(ips) // 2
                    if net_type not in self.network_data['assigned_subnets']:
                        self.network_data['assigned_subnets'][net_type] = []
                    self.network_data['assigned_subnets'][net_type].append(
                        str(subnet)
                    )
                else:
                    subnet = rackwise_subnets['common'][net_type]
                    ips = list(subnet)
                    for i in range(len(rackwise_hosts[rack])):
                        self.ipmi_data[rackwise_hosts[rack][i]][
                            net_type] = str(ips[i + self.IPS_TO_LEAVE + 1 + j])
                    mid = len(ips) // 2
                static_start = str(ips[self.IPS_TO_LEAVE + 1])
                reserved_start = str(ips[1])
                reserved_end = str(ips[self.IPS_TO_LEAVE])
                static_end = str(ips[-2])
                self.network_data[rack][net_type] = {}
                if net_type == 'pxe':
                    static_end = str(ips[mid - 1])
                    dhcp_start = str(ips[mid])
                    dhcp_end = str(ips[-2])
                    self.network_data[rack][
                        net_type]['dhcp_start'] = dhcp_start
                    self.network_data[rack][
                        net_type]['dhcp_end'] = dhcp_end
                self.network_data[rack][
                    net_type]['static_start'] = static_start
                self.network_data[rack][
                    net_type]['static_end'] = static_end
                self.network_data[rack][
                    net_type]['reserved_start'] = reserved_start
                self.network_data[rack][
                    net_type]['reserved_end'] = reserved_end
            j += i + 1

    def assign_public_ip_to_host(self):
        rackwise_hosts = self.get_rackwise_hosts()
        subnet = netaddr.IPNetwork(self.public_network_data['oam']['ip'])
        ips = list(subnet)
        j = 0
        for rack in sorted(self.racks.keys()):
            rack = self.racks[rack]
            for i in range(len(rackwise_hosts[rack])):
                self.ipmi_data[rackwise_hosts[rack][i]]['oam'] = str(
                    ips[j + self.IPS_TO_LEAVE + 1])
                j += 1

    def get_rack_data(self):
        for host in self.hostnames:
            rack = self.get_rack(host)
            self.racks[rack] = rack.replace('r', 'rack')

    def assign_ip(self):
        self.categorize_hosts()
        rackwise_hosts = self.get_rackwise_hosts()
        tmp_data = {}
        for rack in sorted(self.racks.keys()):
            rack = self.racks[rack]
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

    def assign_region_name(self):
        self.data['region_name'] = self.region_name

    def get_oam_network_data(self):
        nw = self.public_network_data['oam']['ip']
        vlan = self.public_network_data['oam']['vlan']
        subnet = netaddr.IPNetwork(nw)
        ips = list(subnet)
        gw = str(ips[settings.GATEWAY_OFFSET])
        static_start = str(ips[self.IPS_TO_LEAVE + 1])
        static_end = str(ips[-1])
        reserved_start = str(ips[1])
        reserved_end = str(ips[self.IPS_TO_LEAVE])
        return {
            'nw': nw,
            'gw': gw,
            'vlan': vlan,
            'routes': ['0.0.0.0/0'],
            'static_start': static_start,
            'static_end': static_end,
            'reserved_start': reserved_start,
            'reserved_end': reserved_end,
        }

    def get_rackwise_oob_data(self):
        oob_data = self.public_network_data['oob']
        oob_network_data = {}
        oob_all_subnets = [
            netaddr.IPNetwork(subnet) for subnet in oob_data['subnets']
        ]
        assigned_subnets = []
        rackwise_hosts = self.get_rackwise_hosts()
        rackwise_oob_subnets = {}
        for rack in rackwise_hosts:
            host = rackwise_hosts[rack][0]
            host_oob_ip = self.ipmi_data[host]['ipmi_address']
            for subnet in oob_all_subnets:
                if host_oob_ip in subnet:
                    rackwise_oob_subnets[rack] = subnet
                    assigned_subnets.append(subnet)
                    break
        for rack in rackwise_oob_subnets:
            nw = rackwise_oob_subnets[rack]
            ips = list(nw)
            gw = str(ips[settings.GATEWAY_OFFSET])
            routes = [
                str(subnet) for subnet in assigned_subnets if subnet != nw
            ]
            static_start = str(ips[self.OOB_IPS_TO_LEAVE])
            static_end = str(ips[-1])
            reserved_start = str(ips[1])
            reserved_end = str(ips[self.OOB_IPS_TO_LEAVE - 1])
            oob_network_data[rack] = {
                'nw': str(nw),
                'gw': gw,
                'routes': routes,
                'static_start': static_start,
                'static_end': static_end,
                'reserved_start': reserved_start,
                'reserved_end': reserved_end,
            }
        return oob_network_data

    def assign_network_data(self):
        rack_data = {}
        rackwise_subnets = self.get_rackwise_subnet()
        common_subnets = {}
        rackwise_oob_data = self.get_rackwise_oob_data()
        for rack in rackwise_subnets:
            for net_type in rackwise_subnets[rack]:
                if not self.private_network_data[net_type]['is_common']:
                    ips = list(rackwise_subnets[rack][net_type])
                    nw = str(rackwise_subnets[rack][net_type])
                    gw = str(ips[settings.GATEWAY_OFFSET])
                    routes = [
                        subnet for subnet in self.network_data[
                            'assigned_subnets'][net_type] if subnet != nw
                    ]
                    rackwise_subnets[rack][net_type] = {
                        'nw': nw,
                        'gw': gw,
                        'vlan': self.private_network_data[net_type]['vlan'],
                        'routes': routes,
                        'static_start': self.network_data[rack][net_type][
                            'static_start'],
                        'static_end': self.network_data[rack][net_type][
                            'static_end'],
                        'reserved_start': self.network_data[rack][net_type][
                            'reserved_start'],
                        'reserved_end': self.network_data[rack][net_type][
                            'reserved_end'],
                    }
                else:
                    ips = list(rackwise_subnets['common'][net_type])
                    nw = str(rackwise_subnets['common'][net_type])
                    gw = str(ips[settings.GATEWAY_OFFSET])
                    racks = sorted(self.racks.keys())
                    rack = self.racks[racks[0]]
                    common_subnets[net_type] = {
                        'nw': nw,
                        'gw': gw,
                        'vlan': self.private_network_data[net_type]['vlan'],
                        'static_start': self.network_data[rack][net_type][
                            'static_start'],
                        'static_end': self.network_data[rack][net_type][
                            'static_end'],
                        'reserved_start': self.network_data[rack][net_type][
                            'reserved_start'],
                        'reserved_end': self.network_data[rack][net_type][
                            'reserved_end'],
                    }
                if net_type == 'pxe':
                    rackwise_subnets[rack][net_type][
                        'dhcp_start'] = self.network_data[rack][net_type][
                            'dhcp_start']
                    rackwise_subnets[rack][net_type][
                        'dhcp_end'] = self.network_data[rack][net_type][
                            'dhcp_end']
        rackwise_subnets.pop('common')
        for rack in rackwise_subnets:
            rackwise_subnets[rack]['oob'] = rackwise_oob_data[rack]
            common_subnets['oam'] = self.get_oam_network_data()
            if rack == self.genesis_rack:
                rackwise_subnets[rack]['is_genesis'] = True
            else:
                rackwise_subnets[rack]['is_genesis'] = False
        rack_data['rack'] = rackwise_subnets
        rack_data['common'] = common_subnets
        self.data['network'] = rack_data
        self.data['network']['ingress'] = self.public_network_data['ingress']
        self.data['network']['proxy'] = settings.PROXY
        self.data['network']['proxy']['no_proxy'] = settings.NO_PROXY
        self.data['network']['ntp'] = {
            'servers': self.dns_ntp_ldap_data['ntp'],
        }
        self.data['network']['dns'] = {
            'domain': self.dns_ntp_ldap_data['domain'],
            'servers': self.dns_ntp_ldap_data['dns'],
            'dhcp_relay': self.dhcp_relay,
        }
        self.data['network']['ldap'] = self.dns_ntp_ldap_data['ldap']
        self.data['network']['bgp'] = settings.BGP

    def get_deployment_configuration(self):
        self.data['deployment_manifest'] = settings.DEPLOYMENT_MANIFEST

    def get_host_profile_wise_racks(self):
        host_profile_wise_racks = {}
        rackwise_host_data = self.data['baremetal']
        for rack in rackwise_host_data:
            for host in rackwise_host_data[rack]:
                host_data = rackwise_host_data[rack][host]
                host_profile = host_data['host_profile']
                if host_profile not in host_profile_wise_racks:
                    host_profile_wise_racks[host_profile] = {
                        'racks': set(),
                    }
                host_profile_wise_racks[host_profile]['racks'].add(rack)
                host_profile_wise_racks[host_profile][
                    'type'] = rackwise_host_data[rack][host]['type']
        return host_profile_wise_racks

    def assign_racks_to_host_profile(self):
        host_profile_wise_racks = self.get_host_profile_wise_racks()
        for host_profile in host_profile_wise_racks:
            rack_list = list(host_profile_wise_racks[host_profile]['racks'])
            host_profile_wise_racks[host_profile]['racks'] = rack_list
            for key in settings.HOSTPROFILE_INTERFACES[host_profile]:
                host_profile_wise_racks[host_profile][
                    key] = settings.HOSTPROFILE_INTERFACES[host_profile][key]
        self.data['profiles'] = host_profile_wise_racks

    def assign_ceph_data(self):
        self.data['ceph'] = settings.CEPH

    def assign_conf_data(self):
        self.data['conf'] = settings.CONF
        ingress_subnet = netaddr.IPNetwork(self.data['network']['ingress'])
        ips = list(ingress_subnet)
        self.data['conf']['ingress'] = '{}/32'.format(str(ips[1]))

    def generate_intermediary_yaml(self):
        self.get_rack_data()
        self.get_rackwise_subnet()
        self.assign_private_ip_to_hosts()
        self.assign_public_ip_to_host()
        self.assign_ip()
        self.assign_network_data()
        self.get_deployment_configuration()
        self.assign_racks_to_host_profile()
        self.assign_region_name()
        self.assign_ceph_data()
        self.assign_conf_data()
        self.assign_location_data()

    def generate_yaml(self):
        self.generate_intermediary_yaml()
        yaml_data = yaml.dump(self.data, default_flow_style=False)
        intermediary_file = "{}_intermediary.yaml".format(self.region_name)
        with open(intermediary_file, 'w') as f:
            f.write(yaml_data)
        return intermediary_file
