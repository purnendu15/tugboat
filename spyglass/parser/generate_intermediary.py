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
import pkg_resources
import netaddr
from .base import Parser
from collections import OrderedDict
from spyglass.data_extractor.formation import FormationPlugin

import pprint
import pdb


class ProcessInput():
    def __init__(self):
        """ Save file_name and exel_spec """
        self.logger = logging.getLogger(__name__)
        self.prepare_data_structure_for_intermediary_yaml()
        self.formation = FormationPlugin()

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
            'region_name': '',
            'storage': {},
            'site_info': {},
        }
        self.genesis_node = ''
        self.generic_data_object = {}

    def save_design_rules(self, site_config):
        #The function saves global design rules
        self.logger.info("Apply Design Rules")
        global_config_dir = pkg_resources.resource_filename(
            'tugboat', 'config/')
        global_config_file = global_config_dir + 'global_config.yaml'
        global_config_data = self.read_file(global_config_file)
        global_config_yaml = yaml.safe_load(global_config_data)
        """ combine global and site design rules """
        rules_data = {}
        rules_data.update(global_config_yaml)
        self.rules_data = rules_data
        self.IPS_TO_LEAVE = self.rules_data['ips_to_leave']
        self.OOB_IPS_TO_LEAVE = self.rules_data['oob_ips_to_leave']
        """ Set deployment configuration from self.rules_data """
        self.data['deployment_manifest'] = self.rules_data[
            'deployment_manifest']
        self.logger.debug("Extracted Rules:{}".format(
            pprint.pformat(self.rules_data)))

    def get_network_subnets(self):
        """
        Extract subnet information for private and public networks
        """
        self.logger.info("Getting rackwise subnet")
        network_subnets = {}
        #self.format_network_data()
        for net_type in self.data['network']['vlan_network_data']:
            # One of the type is ingress and we don't want that here
            if (net_type != 'ingress'):
                self.logger.info("Network" + "Info:net_type {}: {}".format(
                    net_type, self.data['network']['vlan_network_data']
                    [net_type]))
                network_subnets[net_type] = netaddr.IPNetwork(
                    self.data['network']['vlan_network_data'][net_type]
                    ['subnet'][0])

        self.logger.debug("rackwise subnets:\n%s",
                          pprint.pformat(network_subnets))
        return network_subnets

    def set_genesis_node_details(self):
        #Returns the genesis node details
        self.logger.info("Getting Genesis Node Details")
        for racks in self.data['baremetal'].keys():
            rack_hosts = self.data['baremetal'][racks]
            for host in rack_hosts:
                if rack_hosts[host]['type'] == 'genesis':
                    self.genesis_node = rack_hosts[host]
                    self.genesis_node['name'] = host
        self.logger.debug("Genesis Node Details:{}".format(
            pprint.pformat(self.genesis_node)))

    def save_generic_data_object(self):
        """ Assign Design Spec data to internal data structures """
        self.logger.info("Saving incoming data to local data structures")
        self.logger.info("Assigning baremetal data")
        # Baremetal data is used as is from plugin
        self.data['baremetal'] = self.generic_data_object['baremetal']
        self.logger.debug("Assigned baremetal data{}".format(
            pprint.pformat(self.data['baremetal'])))

        # Set network data
        self.logger.info("Assigning network data")
        self.data['network'] = self.generic_data_object['network_data']
        self.logger.debug("Assigned network data{}".format(
            pprint.pformat(self.data['network'])))

        self.logger.info("Assigning site info data")
        self.data['site_info'] = self.generic_data_object['site_info']
        self.logger.debug("Assigned site_info data:{}".format(
            pprint.pformat(self.data['site_info'])))

        self.logger.info("Assigning storage data")
        self.data['storage'] = self.generic_data_object['storage']
        self.logger.debug("Assigned storage data:{}".format(
            pprint.pformat(self.data['storage'])))

        self.logger.info("Assigning Region Name")
        self.data['region_name'] = self.generic_data_object['site_info'][
            'region_name']
        self.logger.debug("Assigned region name:{}".format(
            pprint.pformat(self.data['region_name'])))

    def create_derived_network_data(self):
        """
        Create derived network data with information from xl and static
        configuration and then store them into the dictionary
        """
        self.logger.info("Assigning network data")
        self.data['network'][
            'vlan_network_data'] = self.apply_network_design_rules()

        # dhcp relay is set as pxe ip of the genesis node
        self.data['site_info']['dns']['dhcp_relay'] = {}
        self.data['site_info']['dns']['dhcp_relay'] = self.genesis_node['ip'][
            'pxe']

        # The incoming URL is in the form 'incoming_url':
        # 'url:ldap://its-ad-ldap.atttest.com'
        self.data['site_info']['ldap'] = self.generic_data_object['site_info'][
            'ldap']
        incoming_url = self.data['site_info']['ldap']['incoming_url']
        self.data['site_info']['ldap']['url'] = incoming_url.split('url:')[1]
        self.data['site_info']['ldap']['domain'] = incoming_url.split('.')[1]
        self.data['site_info']['ldap']['base_url'] = incoming_url.split(
            '//')[1]

        self.data['network']['bgp'] = self.generic_data_object['network_data'][
            'bgp']
        subnet = \
                netaddr.IPNetwork(
                    self.data['network']['vlan_network_data']['ingress'])
        ips = list(subnet)
        self.data['network']['bgp']['ingress_vip'] = str(ips[1])
        self.data['network']['bgp']['public_service_cidr'] = self.data[
            'network']['vlan_network_data']['ingress']
        self.logger.debug("Updated network data:\n{}".format(
            pprint.pformat(self.data['network'])))

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
        self.logger.debug(
            "Host profile wise racks:{}".format(host_profile_wise_racks))
        return host_profile_wise_racks

    def apply_network_design_rules(self):
        self.logger.info("Apply network design rules")
        # Assign common network profile for each network type
        vlan_network_data = {}
        # Assign the ingress subnet as it will get overwritten
        vlan_network_data['ingress'] = self.data['network'][
            'vlan_network_data']['ingress']
        # Assign private  network profile
        network_subnets = self.get_network_subnets()
        for net_type in network_subnets:
            self.logger.info("net_types:{}".format(net_type))
            vlan_network_data[net_type] = {}
            subnet = network_subnets[net_type]
            ips = list(subnet)
            self.logger.info("net_type:{} subnet:{}".format(net_type, subnet))
            vlan_network_data[net_type]['nw'] = str(network_subnets[net_type])
            vlan_network_data[net_type]['gw'] = str(
                ips[self.rules_data['gateway_offset']])
            vlan_network_data[net_type]['reserved_start'] = str(ips[1])
            vlan_network_data[net_type]['reserved_end'] = str(
                ips[self.IPS_TO_LEAVE])
            static_start = str(ips[self.IPS_TO_LEAVE + 1])
            static_end = str(ips[-2])

            if net_type == 'pxe':
                mid = len(ips) // 2
                static_end = str(ips[mid - 1])
                dhcp_start = str(ips[mid])
                dhcp_end = str(ips[-2])
                vlan_network_data[net_type]['dhcp_start'] = dhcp_start
                vlan_network_data[net_type]['dhcp_end'] = dhcp_end
            # Review this logic TBD
            vlan_network_data[net_type]['static_start'] = static_start
            vlan_network_data[net_type]['static_end'] = static_end
            # There is no vlan for oob network
            if (net_type != 'oob'):
                vlan_network_data[net_type]['vlan'] = self.data['network'][
                    'vlan_network_data'][net_type]['vlan']
            # OAM have default routes. Only for cruiser. TBD
            if (net_type == 'oam'):
                routes = ["0.0.0.0/0"]
            else:
                routes = []
            vlan_network_data[net_type]['routes'] = routes

        self.logger.debug("vlan network data:%s\n",
                          pprint.pformat(vlan_network_data))
        return vlan_network_data

    def load_extracted_data_from_formation(extracted_data):
        self.logger.info("Load extracted data from formation")
        self.generic_data_object = extracted_data
        self.logger.debug("Dump extracted data from formation:\n%s",
                          pprint.pformat(extracted_data))

    def dump_intermediary_file(self):
        """ Dumping intermediary yaml """
        self.logger.info("Dumping intermediary yaml")
        intermediary_file = \
        "{}_intermediary.yaml".format(self.data['region_name'])
        yaml_file = yaml.dump(self.data, default_flow_style=False)
        with open(intermediary_file, 'w') as f:
            f.write(yaml_file)
        f.close()

    def generate_intermediary_yaml(self):
        """ Generating intermediary yaml """
        self.logger.info("Generating intermediary yaml")
        self.save_generic_data_object()
        self.set_genesis_node_details()
        self.create_derived_network_data()
        self.intermediary_yaml = self.data
        return self.intermediary_yaml
