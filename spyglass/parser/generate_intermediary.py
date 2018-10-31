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
import logging
import pkg_resources
import netaddr
import pprint


class ProcessDataSource():
    def __init__(self, sitetype):
        """ Save file_name and exel_spec """
        self.logger = logging.getLogger(__name__)
        self.initialize_intermediary_yaml()
        self.region_name = sitetype

    @staticmethod
    def read_file(file_name):
        with open(file_name, 'r') as f:
            raw_data = f.read()
        return raw_data

    def initialize_intermediary_yaml(self):
        self.host_type = {}
        self.data = {
            'network': {},
            'baremetal': {},
            'region_name': '',
            'storage': {},
            'site_info': {},
        }
        self.sitetype = None
        self.genesis_node = None
        self.region_name = None
        self.generic_data_object = {}
        self.vlan_network_data = {}

    def get_network_subnets(self):
        """
        Extract subnet information for private and public networks
        """
        self.logger.info("Getting rackwise subnet")
        network_subnets = {}
        # self.format_network_data()
        for net_type in self.data['network']['vlan_network_data']:
            # One of the type is ingress and we don't want that here
            if (net_type != 'ingress'):
                self.logger.info("Network" + "Info:net_type {}: {}".format(
                    net_type, self.data['network']['vlan_network_data']
                    [net_type]))
                network_subnets[net_type] = netaddr.IPNetwork(
                    self.data['network']['vlan_network_data'][net_type]
                    ['subnet'])

        self.logger.debug("rackwise subnets:\n%s",
                          pprint.pformat(network_subnets))
        return network_subnets

    def set_genesis_node_details(self):
        # Returns the genesis node details
        self.logger.info("Getting Genesis Node Details")
        for racks in self.data['baremetal'].keys():
            rack_hosts = self.data['baremetal'][racks]
            for host in rack_hosts:
                if rack_hosts[host]['type'] == 'genesis':
                    self.genesis_node = rack_hosts[host]
                    self.genesis_node['name'] = host
        self.logger.debug("Genesis Node Details:{}".format(
            pprint.pformat(self.genesis_node)))

    def create_derived_network_data(self):
        """
        Create derived network data with information from xl and static
        configuration and then store them into the dictionary
        """
        self.logger.info("Assigning network data")

        # TODO(pg710r) Enhance to support multiple ingress subnet
        subnet = netaddr.IPNetwork(
            self.data['network']['vlan_network_data']['ingress']['subnet'][0])
        ips = list(subnet)
        # TODO(pg710r) Include code to derive ingress_vip using rules
        self.data['network']['bgp']['ingress_vip'] = str(ips[1])
        self.data['network']['bgp']['public_service_cidr'] = self.data[
            'network']['vlan_network_data']['ingress']['subnet'][0]
        self.logger.debug("Updated network data:\n{}".format(
            pprint.pformat(self.data['network'])))

    def apply_design_rules(self):
        self.logger.info("Apply design rules")
        rules_dir = pkg_resources.resource_filename('spyglass', 'config/')
        rules_file = rules_dir + 'rules.yaml'
        rules_data_raw = self.read_file(rules_file)
        rules_yaml = yaml.safe_load(rules_data_raw)
        rules_data = {}
        rules_data.update(rules_yaml)
        for rule in rules_data.keys():
            rule_name = rules_data[rule]['name']
            function_str = "apply_rule_" + rule_name
            rule_data_name = rules_data[rule][rule_name]
            function = getattr(self, function_str)
            function(rule_data_name)
            self.logger.info("Applying rule:{} by calling:{}".format(
                rule_name, function_str))

    def apply_rule_host_profile_interfaces(self, rule_data):
        # Nothing to do as of now
        pass

    def apply_rule_hardware_profile(self, rule_data):
        # Nothing to do as of now
        pass

    def apply_rule_ip_alloc_offset(self, rule_data):
        """
        This rule is applied to incoming network data from
        source while creating ip ranges for vlan networks
        """
        self.logger.info("Apply network design rules")
        # Assign common network profile for each network type
        vlan_network_data = {}

        # Collect Rules
        default_ip_offset = rule_data['default']
        oob_ip_offset = rule_data['oob']
        gateway_ip_offset = rule_data['gateway']

        # Assign private network profile
        network_subnets = self.get_network_subnets()

        for net_type in network_subnets:
            if net_type == 'oob':
                ip_offset = oob_ip_offset
            else:
                ip_offset = default_ip_offset
            self.logger.info("net_types:{}".format(net_type))
            vlan_network_data[net_type] = {}
            subnet = network_subnets[net_type]
            ips = list(subnet)
            self.logger.info("net_type:{} subnet:{}".format(net_type, subnet))

            vlan_network_data[net_type]['network'] = str(
                network_subnets[net_type])

            vlan_network_data[net_type]['gateway'] = str(
                ips[gateway_ip_offset])

            vlan_network_data[net_type]['reserved_start'] = str(ips[1])
            vlan_network_data[net_type]['reserved_end'] = str(ips[ip_offset])

            static_start = str(ips[ip_offset + 1])
            static_end = str(ips[-2])

            if net_type == 'pxe':
                mid = len(ips) // 2
                static_end = str(ips[mid - 1])
                dhcp_start = str(ips[mid])
                dhcp_end = str(ips[-2])

                vlan_network_data[net_type]['dhcp_start'] = dhcp_start
                vlan_network_data[net_type]['dhcp_end'] = dhcp_end

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

            # Update network data to self.data
            self.data['network']['vlan_network_data'][
                net_type] = vlan_network_data[net_type]

        self.logger.debug("vlan network data:%s\n",
                          pprint.pformat(vlan_network_data))

    def load_extracted_data_from_data_source(self, extracted_data):
        self.logger.info("Load extracted data from data source")
        self.data = extracted_data
        self.logger.debug("Dump extracted data from data source:\n%s",
                          pprint.pformat(extracted_data))
        formation_file = "formation_file.yaml"
        yaml_file = yaml.dump(extracted_data, default_flow_style=False)
        with open(formation_file, 'w') as f:
            f.write(yaml_file)
        f.close()
        # Append region_data supplied from CLI to self.data
        self.data['region_name'] = self.region_name

    def dump_intermediary_file(self):
        """ Dumping intermediary yaml """
        self.logger.info("Dumping intermediary yaml")
        intermediary_file = "{}_intermediary.yaml".format(
            self.data['region_name'])
        yaml_file = yaml.dump(self.data, default_flow_style=False)
        with open(intermediary_file, 'w') as f:
            f.write(yaml_file)
        f.close()

    def generate_intermediary_yaml(self):
        """ Generating intermediary yaml """
        self.logger.info("Generating intermediary yaml")
        self.apply_design_rules()
        self.set_genesis_node_details()
        self.create_derived_network_data()
        self.intermediary_yaml = self.data
        return self.intermediary_yaml
