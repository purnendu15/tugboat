# Copyright 2018 AT&T Intellectual Property.  All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import pprint
import re
from spyglass.data_extractor.base import BaseDataSourcePlugin
from spyglass.data_extractor.tugboat.excel_parser import ExcelParser
LOG = logging.getLogger(__name__)


class TugboatPlugin(BaseDataSourcePlugin):
    def __init__(self, region):
        LOG.info("Tugboat Initializing")
        self.source_type = 'excel'
        self.source_name = 'tugboat'

        # Configuration parameters
        self.excel_path = None
        self.excel_spec = None

        # Site related data
        self.region = region
        self.region_zone_map = {}
        self.site_name_id_mapping = {}
        self.zone_name_id_mapping = {}
        self.region_name_id_mapping = {}
        self.rack_name_id_mapping = {}
        self.device_name_id_mapping = {}

        # Raw data from excel
        self.parsed_xl_data = None

        # TODO(pg710r) currently hardcoder. will be removed later
        self.sitetype = '5ec'
        LOG.info("Initiated data extractor plugin:{}".format(self.source_name))

    def set_config_opts(self, conf):
        """
        Placeholder to set confgiuration options
        specific to each plugin.

        :param dict conf: Configuration options as dict

        Example: conf = { 'excel_spec': 'spec1.yaml',
                          'excel_path': 'excel.xls' }

        Each plugin will have their own config opts.
        """
        self.excel_path = conf['excel_path']
        self.excel_spec = conf['excel_spec']

        # Extract raw data from excel sheets
        self._get_excel_obj()
        self._extract_raw_data_from_excel()
        return

    def _get_excel_obj(self):
        """ Creation of an ExcelParser object to store site information.

        The information is obtained based on a excel spec yaml file.
        This spec contains row, column and sheet information of
        the excel file from where site specific data can be extracted.
        """
        self.excel_obj = ExcelParser(self.excel_path, self.excel_spec)

    def _extract_raw_data_from_excel(self):
        """ Extracts raw information from excel file based on excel spec"""
        self.parsed_xl_data = self.excel_obj.get_data()
        self.ipmi_data = self.parsed_xl_data['ipmi_data'][0]
        self.hostnames = self.parsed_xl_data['ipmi_data'][1]
        import pdb
        pdb.set_trace()
        """
        self.private_network_data = self._get_private_network_data(
            self.parsed_xl_data['network_data'])
        self.public_network_data = self._get_public_network_data(
            self.parsed_xl_data['network_data'])
        self.dns_ntp_ldap_data = self._get_dns_ntp_ldap_data(
            self.parsed_xl_data['network_data'])
        self.location_data = self._get_location_data(
            self.parsed_xl_data['location_data'])
        """

    def get_plugin_conf(self, kwargs):
        """ Validates the plugin param from CLI and return if correct


        Ideally the CLICK module shall report an error if excel file
        and excel specs are not specified. The below code has been
        written as an additional safeguard.
        """
        try:
            assert (len(kwargs['excel']) !=
                    0), "Engineering Specification file not specified"
            excel_file_info = kwargs['excel']
            assert (kwargs['excel_spec']
                    ) is not None, "Excel Specification file not specified"
            excel_spec_info = kwargs['excel_spec']
        except AssertionError:
            LOG.error(
                "Insufficient plugin parameter for Tugboat! Spyglass exited!")
            raise
            exit()
        plugin_conf = {
            'excel_path': excel_file_info,
            'excel_spec': excel_spec_info
        }
        return plugin_conf

    def get_zones(self, site=None):
        # TODO(pg710r): Code will be added later
        pass

    def get_regions(self, zone):
        # TODO(pg710r): Code will be added later
        pass

    def get_racks(self, region):
        # TODO(pg710r): Code will be added later
        pass

    def get_hosts(self, region, rack=None):
        """Return list of hosts in the region
        :param string region: Region name
        :param string rack: Rack name
        :returns: list of hosts information
        :rtype: list of dict
        Example: [
                     {
                         'name': 'host01',
                         'type': 'controller',
                         'host_profile': 'hp_01'
                     },
                     {
                         'name': 'host02',
                         'type': 'compute',
                         'host_profile': 'hp_02'}
                 ]
        """
        LOG.info("Get Host Information")
        rackwise_hosts = self._get_rackwise_hosts()
        host_list = []
        for rack in rackwise_hosts.keys():
            for host in rackwise_hosts[rack]:
                host_list.append({
                    'rack_name':
                    rack,
                    'name':
                    host,
                    'host_profile':
                    self.ipmi_data[host]['host_profile']
                    #'type': self.host_type[host]
                })
        return host_list

    def _get_rack_data(self):
        """ Format rack name """
        LOG.info("Getting rack data")
        racks = {}
        for host in self.hostnames:
            rack = self._get_rack(host)
            racks[rack] = rack.replace('r', 'rack')
        return racks

    def _get_rack(self, host):
        """
        Get rack id  from the rack string extracted
        from xl
        """
        rack_pattern = '\w.*(r\d+)\w.*'
        rack = re.findall(rack_pattern, host)[0]
        if not self.region:
            self.region = host.split(rack)[0]
        return rack

    def _get_rackwise_hosts(self):
        """ Mapping hosts with rack ids """
        rackwise_hosts = {}
        racks = self._get_rack_data()
        for rack in racks:
            if rack not in rackwise_hosts:
                rackwise_hosts[racks[rack]] = []
            for host in self.hostnames:
                if rack in host:
                    rackwise_hosts[racks[rack]].append(host)
        LOG.debug("rackwise hosts:\n%s", pprint.pformat(rackwise_hosts))
        return rackwise_hosts

    def _categorize_hosts(self):
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

    def get_networks(self, region):
        # TODO(pg710r): Code will be added later
        pass

    def get_ips(self, region, host=None):
        """Return list of IPs on the host
        :param string region: Region name
        :param string host: Host name
        :returns: Dict of IPs per network on the host
        :rtype: dict
        Example: {'oob': {'ipv4': '192.168.1.10'},
                  'pxe': {'ipv4': '192.168.2.10'}}
        The network name from get_networks is expected to be the keys of this
        dict. In case some networks are missed, they are expected to be either
        DHCP or internally generated n the next steps by the design rules.
        """

        ip_ = {}
        ip_[host] = {
            'oob': self.ipmi_data[host].get('ipmi_address', ''),
            'oam': self.ipmi_data[host].get('oam', ''),
            'calico': self.ipmi_data[host].get('calico', ''),
            'overlay': self.ipmi_data[host].get('overlay', ''),
            'pxe': self.ipmi_data[host].get('pxe', ''),
            'storage': self.ipmi_data[host].get('storage', '')
        }
        return ip_

    def get_dns_servers(self, region):
        # TODO(pg710r): Code will be added later
        pass

    def get_ntp_servers(self, region):
        # TODO(pg710r): Code will be added later
        pass

    def get_ldap_information(self, region):
        # TODO(pg710r): Code will be added later
        pass

    def get_location_information(self, region):
        # TODO(pg710r): Code will be added later
        pass

    def get_domain_name(self, region):
        # TODO(pg710r): Code will be added later
        pass
