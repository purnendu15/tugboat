import yaml
import re

import netaddr
from base import ParserEngine
from utils.excel_parser import ExcelParser
import utils.settings as settings


class GenerateYamlFromExcel(ParserEngine):
    def __init__(self, file_name, excel_specs):
        self.HOST_TYPES = settings.HOST_TYPES
        self.PRIVATE_NETWORK_TYPES = settings.PRIVATE_NETWORK_TYPES
        self.IPS_TO_LEAVE = settings.IPS_TO_LEAVE
        parsed_data = self.get_parsed_data(file_name, excel_specs)
        self.ipmi_data = parsed_data['ipmi_data'][0]
        self.hostnames = parsed_data['ipmi_data'][1]
        self.network_data = self.get_network_data(parsed_data['network_data'])
        self.host_type = {}
        self.data = {
            'network': {},
            'baremetal': {},
        }
        self.racks = set()

    def get_parsed_data(self, file_name, excel_specs):
        parser = ExcelParser(file_name, excel_specs)
        return parser.get_data()

    def get_network_data(self, raw_data):
        network_data = {}
        for net_type in self.PRIVATE_NETWORK_TYPES:
            for key in raw_data:
                if net_type.lower() in key.lower():
                    network_data[net_type] = raw_data[key]
        return network_data

    def format_network_data(self):
        for net_type in self.network_data:
            for key in self.network_data[net_type]:
                if key == 'subnet_range':
                    value = self.network_data[net_type][
                        key].split('-')[0].replace(' ', '')
                    self.network_data[net_type][key] = value
                else:
                    cidr_pattern = '/\d\d'
                    value = re.findall(cidr_pattern,
                                       self.network_data[net_type][
                                           key])[0]
                    self.network_data[net_type][key] = value

    def get_rack(self, host):
        rack_pattern = '\w.*(r\d+)\w.*'
        return re.findall(rack_pattern, host)[0]

    def categorize_hosts(self):
        self.host_type[self.hostnames[0]] = 'genesis'
        controller_pattern = '\w.*r\d+o\d+'
        for host in self.hostnames[1:]:
            if re.search(controller_pattern, host):
                self.host_type[host] = 'controller'
            else:
                self.host_type[host] = 'compute'

    def get_rackwise_subnet(self):
        rackwise_subnets = {}
        sorted_racks = sorted(self.racks)
        for rack in sorted_racks:
            rackwise_subnets[rack] = {}
        self.format_network_data()
        for net_type in self.network_data:
            network_range = netaddr.IPNetwork(
                self.network_data[net_type]['subnet_range'])
            cidr_per_rack = self.network_data[net_type]['cidr_per_rack']
            cidr = int(cidr_per_rack.split('/')[1])
            total_racks = len(self.racks)
            subnets = network_range.subnet(cidr, count=total_racks)
            i = 0
            for subnet in subnets:
                if net_type not in rackwise_subnets[sorted_racks[i]]:
                    rackwise_subnets[sorted_racks[i]][net_type] = ''
                rackwise_subnets[sorted_racks[i]][net_type] = subnet
                i += 1
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
            for net_type in self.network_data:
                subnet = rackwise_subnets[rack][net_type]
                ips = list(subnet)
                for i in range(len(rackwise_hosts[rack])):
                    self.ipmi_data[rackwise_hosts[rack][i]][net_type] = str(
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
                for net_type in self.network_data:
                    ip_[net_type] = self.ipmi_data[host][net_type]
                tmp_data[rack][host]['ip'] = ip_
                tmp_data[rack][host]['type'] = self.host_type[host]
                tmp_data[rack][host]['host_profile'] = self.ipmi_data[host][
                    'host_profile']
                tmp_data[rack][host]['rack'] = rack
        self.data['baremetal'] = tmp_data

    def assign_network_data(self):
        rackwise_subnets = self.get_rackwise_subnet()
        for rack in rackwise_subnets:
            for net_type in rackwise_subnets[rack]:
                rackwise_subnets[rack][net_type] = str(
                    rackwise_subnets[rack][net_type])
        self.data['network'] = rackwise_subnets

    def generate_intermediary_yaml(self):
        self.get_rack_data()
        self.get_rackwise_subnet()
        self.assign_private_ip_to_hosts()
        self.assign_ip()
        self.assign_network_data()

    def generate_yaml(self):
        self.generate_intermediary_yaml()
        yaml_data = yaml.dump(self.data, default_flow_style=False)
        with open('intermediary.yaml', 'w') as f:
            f.write(yaml_data)
