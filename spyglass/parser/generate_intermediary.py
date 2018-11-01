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

import json
import logging
import pprint
import netaddr
import jsonschema
import pkg_resources
import yaml


class ProcessDataSource():
    def __init__(self, sitetype):
        # Initialize intermediary and save site type
        self.logger = logging.getLogger(__name__)
        self._initialize_intermediary()
        self.region_name = sitetype

    @staticmethod
    def _read_file(file_name):
        with open(file_name, 'r') as f:
            raw_data = f.read()
        return raw_data

    def _initialize_intermediary(self):
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

    def _get_network_subnets(self):
        # Extract subnet information for networks
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

    def _get_genesis_node_details(self):
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

    def _validate_extracted_data(self, data):
        """
        Validates the extracted data from input source. It checks
        wether the data types and data format are as expected. The
        function validates this with regext pattern defined for each
        data type.
        """
        self.logger.info('Validating data read from extracted data')
        schema_dir = pkg_resources.resource_filename('spyglass', 'schemas/')
        schema_file = schema_dir + "data_schema.json"
        json_data = json.loads(json.dumps(data))
        with open(schema_file, 'r') as f:
            json_schema = json.load(f)
        try:
            with open('data2.json', 'w') as outfile:
                json.dump(data, outfile, sort_keys=True, indent=4)
            jsonschema.validate(json_data, json_schema)
        except jsonschema.exceptions.ValidationError as e:
            self.logger.error(
                "Validation Failed with following error:{}".format(e.message))
            exit(1)
        self.logger.info("Data validation Passed!")

    def _apply_design_rules(self):
        """
        Applies design rules from rules.yaml to create a subnet address,
        gateway ip, ranges for dhcp and static ip address
        """
        self.logger.info("Apply design rules")
        rules_dir = pkg_resources.resource_filename('spyglass', 'config/')
        rules_file = rules_dir + 'rules.yaml'
        rules_data_raw = self._read_file(rules_file)
        rules_yaml = yaml.safe_load(rules_data_raw)
        rules_data = {}
        rules_data.update(rules_yaml)
        for rule in rules_data.keys():
            rule_name = rules_data[rule]['name']
            function_str = "_apply_rule_" + rule_name
            rule_data_name = rules_data[rule][rule_name]
            function = getattr(self, function_str)
            function(rule_data_name)
            self.logger.info("Applying rule:{} by calling:{}".format(
                rule_name, function_str))

    def _apply_rule_host_profile_interfaces(self, rule_data):
        # TODO(pg710r)Nothing to do as of now
        pass

    def _apply_rule_hardware_profile(self, rule_data):
        # TODO(pg710r)Nothing to do as of now
        pass

    def _apply_rule_ip_alloc_offset(self, rule_data):
        """
        This rule is applied to incoming network data to determine
        network address, gateway ip and other address ranges
        """
        self.logger.info("Apply network design rules")
        vlan_network_data = {}

        # Collect Rules
        default_ip_offset = rule_data['default']
        oob_ip_offset = rule_data['oob']
        gateway_ip_offset = rule_data['gateway']
        ingress_vip_offset = rule_data['ingress_vip']
        # static_ip_end_offset for non pxe network
        static_ip_end_offset = rule_data['static_ip_end']
        # dhcp_ip_end_offset for pxe network
        dhcp_ip_end_offset = rule_data['dhcp_ip_end']

        # Set ingress vip and CIDR for bgp
        self.logger.info("Applying rules to network bgp data")
        subnet = netaddr.IPNetwork(
            self.data['network']['vlan_network_data']['ingress']['subnet'][0])
        ips = list(subnet)
        self.data['network']['bgp']['ingress_vip'] = str(
            ips[ingress_vip_offset])
        self.data['network']['bgp']['public_service_cidr'] = self.data[
            'network']['vlan_network_data']['ingress']['subnet'][0]
        self.logger.debug("Updated network bgp data:\n{}".format(
            pprint.pformat(self.data['network']['bgp'])))

        self.logger.info("Applying rules to vlan network data")
        # Assign private network profile
        network_subnets = self._get_network_subnets()
        # Apply rules to vlan networks
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
            static_end = str(ips[static_ip_end_offset])

            if net_type == 'pxe':
                mid = len(ips) // 2
                static_end = str(ips[mid - 1])
                dhcp_start = str(ips[mid])
                dhcp_end = str(ips[dhcp_ip_end_offset])

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
        """
        Function called from spyglass.py to pass extracted data
        from input data source
        """
        self.logger.info("Load extracted data from data source")
        self._validate_extracted_data(extracted_data)
        self.data = extracted_data
        self.logger.debug("Dump extracted data from data source:\n%s",
                          pprint.pformat(extracted_data))
        extracted_file = "extracted_file.yaml"
        yaml_file = yaml.dump(extracted_data, default_flow_style=False)
        with open(extracted_file, 'w') as f:
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
        self._apply_design_rules()
        self._get_genesis_node_details()
        self.intermediary_yaml = self.data
        return self.intermediary_yaml
