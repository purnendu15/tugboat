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
import logging
import pprint
import pkg_resources
import netaddr
from .base import ParserEngine
from .utils.excel_parser import ExcelParser
from collections import OrderedDict


class ProcessInputFiles(ParserEngine):
    def __init__(self, file_name, excel_specs):
        """ Save file_name and exel_spec """
        self.logger = logging.getLogger(__name__)
        self.file_name = file_name
        self.excel_specs = excel_specs
        self.prepare_data_structure_for_intermediary_yaml()

    @staticmethod
    def read_file(file_name):
        with open(file_name, 'r') as f:
            raw_data = f.read()
        return raw_data

    def prepare_data_structure_for_intermediary_yaml(self):
        self.host_type = {}
        self.data = {
            'network': {},
            'baremetal': {},
            'profiles': {},
            'region_name': '',
            'conf': {},
            'ceph': {},
            'location': {},
            'sitetype': '',
            'hw_profile': {},
        }
        self.service_ip = ''
        self.region_name = ''
        self.dhcp_relay = ''
        self.genesis_rack = ''
        self.network_data = {
            'assigned_subnets': {},
        }
        self.racks = OrderedDict()
        self.parsed_xl_data = {}

    def apply_design_rules(self, site_config):
        """ The function applies global and site specific design rules to
        a common design rule
        """
        """ Load and save global tugboat design rules.yaml """
        global_config_dir = pkg_resources.resource_filename(
            'tugboat', 'config/')
        global_config_file = global_config_dir + 'global_config.yaml'
        global_config_data = self.read_file(global_config_file)
        global_config_yaml = yaml.safe_load(global_config_data)
        """ Load site specific design rules """
        site_config_data = self.read_file(site_config)
        site_config_yaml = yaml.safe_load(site_config_data)
        """ combine global and site design rules """
        rules_data = {}
        rules_data.update(global_config_yaml)
        rules_data.update(site_config_yaml)

        self.rules_data = rules_data

        self.HOST_TYPES = self.rules_data['host_types']
        self.PRIVATE_NETWORK_TYPES = self.rules_data['private_network_types']
        self.IPS_TO_LEAVE = self.rules_data['ips_to_leave']
        self.OOB_IPS_TO_LEAVE = self.rules_data['oob_ips_to_leave']
        self.sitetype = self.rules_data['sitetype']

    def get_parsed_raw_data_from_excel(self):
        """
        Get a data dictionary by reading the input excel files
        and excel specs. The excel specs contains metadata for reading
        the excel information
        """
        parser = ExcelParser(self.file_name, self.excel_specs)
        self.parsed_xl_data = parser.get_data()

    def get_private_network_data(self, raw_data):
        """
        Get private network data from information extracted
        by ExcelParser(i.e raw data)
        """
        network_data = {}
        for net_type in self.PRIVATE_NETWORK_TYPES:
            for key in raw_data['private']:
                if net_type.lower() in key.lower():
                    network_data[self.PRIVATE_NETWORK_TYPES[
                        net_type]] = raw_data['private'][key]
        self.logger.debug("Private Network Data:\n%s",
                          pprint.pformat(network_data))
        return network_data

    def get_public_network_data(self, raw_data):
        """
        Get public network data from information extracted
        by ExcelParser(i.e raw data)
        """
        network_data = raw_data['public']
        self.logger.debug("Public Network Data:\n%s",
                          pprint.pformat(network_data))
        return network_data

    def get_dns_ntp_ldap_data(self, raw_data):
        """
        Get dns, ntp and ldap data from  information extracted
        by ExcelParser(i.e raw data)
        """
        network_data = raw_data['dns_ntp_ldap']
        network_data['dns'] = " ".join(network_data['dns'])
        network_data['ntp'] = " ".join(network_data['ntp'])
        self.logger.debug("DNS, NTP, LDAP data:\n%s",
                          pprint.pformat(network_data))
        return network_data

    def get_location_data(self, raw_data):
        """
        Prepare location data from information extracted
        by ExcelParser(i.e raw data)
        """
        corridor_pattern = '\d+'
        corridor_number = re.findall(corridor_pattern, raw_data['corridor'])[0]
        name = raw_data['name']
        state = self.rules_data['state_codes'][raw_data['state']]
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
        """ Assign the prepared location data """
        self.data['location'] = self.location_data

    def format_network_data(self):
        """
        Network data extracted from xl is formatted
        to have a predictable data type. For e.g VlAN 45
        extracted from xl is formatted as 45
        """
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
                url = '{}://{}'.format(self.rules_data['ldap_protocol'],
                                       base_url)
                self.dns_ntp_ldap_data[type_]['base_url'] = base_url
                self.dns_ntp_ldap_data[type_]['url'] = url

    def get_rack(self, host):
        """
        Get rack id  from the rack string extracted
        from xl
        """
        rack_pattern = '\w.*(r\d+)\w.*'
        rack = re.findall(rack_pattern, host)[0]
        if not self.region_name:
            self.region_name = host.split(rack)[0]
        return rack

    def categorize_hosts(self):
        """
        Categorize host as genesis, controller and compute based on
        the hostname string extracted from xl
        """
        """ loop through IPMI data and determine hosttype """
        is_genesis = False
        sitetype = self.sitetype
        ctrl_profile_type = \
        self.rules_data['hardware_profile'][sitetype]['profile_name']['ctrl']
        for host in sorted(self.ipmi_data.keys()):
            if (self.ipmi_data[host]['host_profile'] == ctrl_profile_type):
                if not is_genesis:
                    self.host_type[host] = 'genesis'
                    is_genesis = True
                else:
                    self.host_type[host] = 'controller'
            else:
                self.host_type[host] = 'compute'

    def get_rackwise_subnet(self):
        """
        Extract subnet information for private and public networks
        for each rack
        """
        self.logger.info("Getting rackwise subnet")
        rackwise_subnets = {}
        rackwise_subnets['common'] = {}
        self.format_network_data()
        racks = [self.racks[rack] for rack in self.racks]
        sorted_racks = sorted(racks)
        for rack in sorted_racks:
            rackwise_subnets[rack] = {}
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
                rackwise_subnets['common'][net_type] = netaddr.IPNetwork(
                    self.private_network_data[net_type]['subnet'][0])
        self.logger.debug("rackwise subnets:\n%s",
                          pprint.pformat(rackwise_subnets))
        return rackwise_subnets

    def get_rackwise_hosts(self):
        """ Mapping hosts with rack ids """
        rackwise_hosts = {}
        for rack in self.racks:
            if rack not in rackwise_hosts:
                rackwise_hosts[self.racks[rack]] = []
            for host in self.hostnames:
                if rack in host:
                    rackwise_hosts[self.racks[rack]].append(host)
        self.logger.debug("rackwise hosts:\n%s",
                          pprint.pformat(rackwise_hosts))
        return rackwise_hosts

    def assign_private_ip_to_hosts(self):
        """ Assigning private IP to Hosts """
        self.logger.info("Assigning private IP to Hosts")
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
                        self.ipmi_data[rackwise_hosts[rack]
                                       [i]][net_type] = str(
                                           ips[i + self.IPS_TO_LEAVE + 1])
                    mid = len(ips) // 2
                    if net_type not in self.network_data['assigned_subnets']:
                        self.network_data['assigned_subnets'][net_type] = []
                    self.network_data['assigned_subnets'][net_type].append(
                        str(subnet))
                else:
                    subnet = rackwise_subnets['common'][net_type]
                    ips = list(subnet)
                    for i in range(len(rackwise_hosts[rack])):
                        self.ipmi_data[rackwise_hosts[rack]
                                       [i]][net_type] = str(
                                           ips[i + self.IPS_TO_LEAVE + 1 + j])
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
                    self.network_data[rack][net_type][
                        'dhcp_start'] = dhcp_start
                    self.network_data[rack][net_type]['dhcp_end'] = dhcp_end
                self.network_data[rack][net_type][
                    'static_start'] = static_start
                self.network_data[rack][net_type]['static_end'] = static_end
                self.network_data[rack][net_type][
                    'reserved_start'] = reserved_start
                self.network_data[rack][net_type][
                    'reserved_end'] = reserved_end
            j += i + 1

    def assign_public_ip_to_host(self):
        """ Assigning public IP to Hosts """
        self.logger.info("Assigning public IP to Hosts")
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
        """ Format rack name """
        self.logger.info("Getting rack data")
        for host in self.hostnames:
            rack = self.get_rack(host)
            self.racks[rack] = rack.replace('r', 'rack')

    def assign_ip(self):
        self.logger.info("Assign IP")
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
        """ Assign region name """
        self.logger.info("Assigning region name")
        self.data['region_name'] = self.region_name

    def assign_sitetype(self):
        """ Assign profile name """
        self.logger.info("Assigning sitetype  name")
        self.data['sitetype'] = self.sitetype

    def get_oam_network_data(self):
        """ Extracting OAM network info"""
        self.logger.info("Extracting oam network data")
        self.data['region_name'] = self.region_name
        nw = self.public_network_data['oam']['ip']
        vlan = self.public_network_data['oam']['vlan']
        subnet = netaddr.IPNetwork(nw)
        ips = list(subnet)
        gw = str(ips[self.rules_data['gateway_offset']])
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
        """
        Extracting oob data per rack and prepare derived data.
        for e.g gateway, ip address ranges etc
        """
        self.logger.info("Extracting oob data per rack")
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
            gw = str(ips[self.rules_data['gateway_offset']])
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

    def assign_design_spec_data(self):
        """ Assign Design Spec data to internal datastructures """
        self.logger.info("Assigning network data")
        self.ipmi_data = self.parsed_xl_data['ipmi_data'][0]
        self.hostnames = self.parsed_xl_data['ipmi_data'][1]
        self.private_network_data = self.get_private_network_data(
            self.parsed_xl_data['network_data'])
        self.public_network_data = self.get_public_network_data(
            self.parsed_xl_data['network_data'])
        self.dns_ntp_ldap_data = self.get_dns_ntp_ldap_data(
            self.parsed_xl_data['network_data'])
        self.location_data = self.get_location_data(
            self.parsed_xl_data['location_data'])

    def assign_network_data(self):
        """
        Create derived network data with information from xl and static
        configuration and then store them into the dictionary
        """
        self.logger.info("Assigning network data")
        rack_data = {}
        rackwise_subnets = self.get_rackwise_subnet()
        common_subnets = {}
        rackwise_oob_data = self.get_rackwise_oob_data()
        for rack in rackwise_subnets:
            for net_type in rackwise_subnets[rack]:
                if not self.private_network_data[net_type]['is_common']:
                    ips = list(rackwise_subnets[rack][net_type])
                    nw = str(rackwise_subnets[rack][net_type])
                    gw = str(ips[self.rules_data['gateway_offset']])
                    routes = [
                        subnet for subnet in self.
                        network_data['assigned_subnets'][net_type]
                        if subnet != nw
                    ]
                    rackwise_subnets[rack][net_type] = {
                        'nw':
                        nw,
                        'gw':
                        gw,
                        'vlan':
                        self.private_network_data[net_type]['vlan'],
                        'routes':
                        routes,
                        'static_start':
                        self.network_data[rack][net_type]['static_start'],
                        'static_end':
                        self.network_data[rack][net_type]['static_end'],
                        'reserved_start':
                        self.network_data[rack][net_type]['reserved_start'],
                        'reserved_end':
                        self.network_data[rack][net_type]['reserved_end'],
                    }
                else:
                    ips = list(rackwise_subnets['common'][net_type])
                    nw = str(rackwise_subnets['common'][net_type])
                    gw = str(ips[self.rules_data['gateway_offset']])
                    routes = [
                        subnet for subnet in self.
                        private_network_data[net_type]['subnet']
                        if subnet != nw
                    ]
                    racks = sorted(self.racks.keys())
                    rack = self.racks[racks[0]]
                    common_subnets[net_type] = {
                        'nw':
                        nw,
                        'gw':
                        gw,
                        'routes':
                        routes,
                        'vlan':
                        self.private_network_data[net_type]['vlan'],
                        'static_start':
                        self.network_data[rack][net_type]['static_start'],
                        'static_end':
                        self.network_data[rack][net_type]['static_end'],
                        'reserved_start':
                        self.network_data[rack][net_type]['reserved_start'],
                        'reserved_end':
                        self.network_data[rack][net_type]['reserved_end'],
                    }
                    if net_type == 'pxe':
                        common_subnets[net_type]['dhcp_start'] =\
                                self.network_data[rack][net_type]['dhcp_start']
                        common_subnets[net_type]['dhcp_end'] =\
                                self.network_data[rack][net_type]['dhcp_end']

        rackwise_subnets.pop('common')
        common_subnets['oob'] = rackwise_oob_data[rack]
        common_subnets['oam'] = self.get_oam_network_data()
        for rack in rackwise_subnets:
            if rack == self.genesis_rack:
                rackwise_subnets[rack]['is_genesis'] = True
            else:
                rackwise_subnets[rack]['is_genesis'] = False
        rack_data['rack'] = rackwise_subnets
        rack_data['common'] = common_subnets
        self.data['network'] = rack_data
        self.data['network']['ingress'] = self.public_network_data['ingress']
        self.data['network']['proxy'] = self.rules_data['proxy']
        self.data['network']['proxy']['no_proxy'] = self.rules_data['no_proxy']
        self.data['network']['ntp'] = {
            'servers': self.dns_ntp_ldap_data['ntp'],
        }
        self.data['network']['dns'] = {
            'domain': self.dns_ntp_ldap_data['domain'],
            'servers': self.dns_ntp_ldap_data['dns'],
            'dhcp_relay': self.dhcp_relay,
        }
        self.data['network']['ldap'] = self.dns_ntp_ldap_data['ldap']
        self.data['network']['ldap']['domain'] = \
                self.data['network']['ldap']['base_url'].split('.')[1]
        self.data['network']['bgp'] = self.rules_data['bgp']
        self.data['network']['bgp']['public_service_cidr'] =\
                self.data['network']['ingress']
        subnet = \
                netaddr.IPNetwork(
                    self.data['network']['bgp']['public_service_cidr'])
        ips = list(subnet)
        self.data['network']['bgp']['ingress_vip'] = str(ips[1])

    def get_deployment_configuration(self):
        """ Get deployment configuration from self.rules_data['py """
        self.logger.info("Getting deployment config")
        self.data['deployment_manifest'] = self.rules_data[
            'deployment_manifest']

    def get_host_profile_wise_racks(self):
        """
        Extracting rack information per host profile and
        associating them with each profile(compute or controller)
        """
        self.logger.info("Extracting rack information per host profile ")
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
        """ Create profile key and assigning host profile data to it """
        self.logger.info("Assigning rack to host profile")
        host_profile_wise_racks = self.get_host_profile_wise_racks()
        for host_profile in host_profile_wise_racks:
            rack_list = list(host_profile_wise_racks[host_profile]['racks'])
            host_profile_wise_racks[host_profile]['racks'] = rack_list
            for key in self.rules_data['hostprofile_interfaces'][host_profile]:
                host_profile_wise_racks[host_profile][key] = self.rules_data[
                    'hostprofile_interfaces'][host_profile][key]
        self.data['profiles'] = host_profile_wise_racks

    def assign_ceph_data(self):
        """ Assigning ceph data from configuration in setttings.py """
        self.logger.info("Assigning ceph data")
        self.data['ceph'] = self.rules_data['ceph']

    def assign_conf_data(self):
        """ Creating a conf key and storing common network config for UCP """
        self.logger.info("Assigning conf data")
        self.data['ceph'] = self.rules_data['ceph']
        self.data['conf'] = self.rules_data['conf']
        ingress_subnet = netaddr.IPNetwork(self.data['network']['ingress'])
        ips = list(ingress_subnet)
        self.data['conf']['ingress'] = '{}/32'.format(str(ips[1]))

    def assign_hardware_profile(self):
        """ Get sitetype and set Hardware profile accordingly """
        hardware_profile = {}
        for key in self.rules_data['hardware_profile']:
            if self.data["sitetype"] == key:
                hardware_profile = self.rules_data['hardware_profile'][key]
        self.data['hw_profile'] = hardware_profile

    def generate_intermediary_yaml(self):
        """ Generating intermediary yaml """
        self.logger.info("Generating intermediary yaml")
        self.assign_design_spec_data()
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
        self.assign_sitetype()
        self.assign_hardware_profile()
        self.intermediary_yaml = self.data
        return self.intermediary_yaml

    def dump_intermediary_file(self):
        """ Dumping intermediary yaml """
        self.logger.info("Dumping intermediary yaml")
        intermediary_file = "{}_intermediary.yaml".format(self.region_name)
        yaml_file = yaml.dump(self.data, default_flow_style=False)
        with open(intermediary_file, 'w') as f:
            f.write(yaml_file)
        f.close()
