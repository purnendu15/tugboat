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

import abc
import six


@six.add_metaclass(abc.ABCMeta)
class BaseDataSourcePlugin(object):
    """Provide basic hooks for data source plugins"""

    def __init__(self):
        self.source_type = None
        self.source_name = None
        super().__init__()

    @abc.abstractmethod
    def set_config_opts(self, conf):
        """Placeholder to set confgiuration options
        specific to each plugin.

        :param dict conf: Configuration options as dict

        Example: conf = { 'excel_spec': 'spec1.yaml',
                          'excel_path': 'excel.xls' }

        Each plugin will have their own config opts.
        """
        return

    @abc.abstractmethod
    def get_racks(self, zone):
        """Return list of racks in the zone

        :param string zone: Zone name

        :returns: list of rack names

        :rtype: list

        Example: ['rack01', 'rack02']
        """
        return []

    @abc.abstractmethod
    def get_hosts(self, zone, rack):
        """Return list of hosts in the zone

        :param string zone: Zone name
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
        return []

    @abc.abstractmethod
    def get_networks(self, zone):
        """Return list of networks in the zone

        :param string zone: Zone name

        :returns: list of networks and their vlans

        :rtype: list of dict

        Example: [
                     {
                         'name': 'oob',
                         'vlan': '41',
                         'subnet': '192.168.1.0/24',
                         'gateway': '192.168.1.1'
                     },
                     {
                         'name': 'pxe',
                         'vlan': '42',
                         'subnet': '192.168.2.0/24',
                         'gateway': '192.168.2.1'
                     },
                     {
                         'name': 'oam',
                         'vlan': '43',
                         'subnet': '192.168.3.0/24',
                         'gateway': '192.168.3.1'
                     },
                     {
                         'name': 'ksn',
                         'vlan': '44',
                         'subnet': '192.168.4.0/24',
                         'gateway': '192.168.4.1'
                     },
                     {
                         'name': 'storage',
                         'vlan': '45',
                         'subnet': '192.168.5.0/24',
                         'gateway': '192.168.5.1'
                     },
                     {
                         'name': 'overlay',
                         'vlan': '45',
                         'subnet': '192.168.6.0/24',
                         'gateway': '192.168.6.1'
                     }
                 ]
        """
        # TODO(nh863p): Can we fix the network names here so that plugin
        # will return exactly with same network names?

        # TODO(nh863p): Expand the return type if they are rack level subnets
        # TODO(nh863p): Is ingress information can be provided here?
        return []

    @abc.abstractmethod
    def get_ips(self, zone, host):
        """Return list of IPs on the host

        :param string zone: Zone name
        :param string host: Host name

        :returns: Dict of IPs per network on the host

        :rtype: dict

        Example: {'oob': {'ipv4': '192.168.1.10'},
                  'pxe': {'ipv4': '192.168.2.10'}}

        The network name from get_networks is expected to be the keys of this
        dict. In case some networks are missed, they are expected to be either
        DHCP or internally generated n the next steps by the design rules.
        """
        return {}

    @abc.abstractmethod
    def get_dns_servers(self, zone):
        """Return the DNS servers

        :param string zone: Zone name

        :returns: List of DNS servers to be configured on host

        :rtype: List

        Example: ['8.8.8.8', '8.8.8.4']
        """
        return []

    @abc.abstractmethod
    def get_ntp_servers(self, zone):
        """Return the NTP servers

        :param string zone: Zone name

        :returns: List of NTP servers to be configured on host

        :rtype: List

        Example: ['ntp1.ubuntu1.example', 'ntp2.ubuntu.example']
        """
        return []

    @abc.abstractmethod
    def get_ldap_information(self, zone):
        """Return the LDAP server information

        :param string zone: Zone name

        :returns: LDAP server information

        :rtype: Dict

        Example: {'url': 'ldap.example.com',
                  'common_name': 'ldap-site1',
                  'domain': 'test',
                  'subdomain': 'test_sub1'}
        """
        return {}

    @abc.abstractmethod
    def get_location_information(self, zone):
        """Return location information

        :param string zone: Zone name

        :returns: Dict of location information

        :rtype: dict

        Example: {'name': 'Dallas',
                  'physical_location': 'DAL01',
                  'state': 'Texas',
                  'country': 'US',
                  'corridor': 'CR1'}
        """
        return {}

    @abc.abstractmethod
    def get_domain_name(self, zone):
        """Return the Domain name

        :param string zone: Zone name

        :returns: Domain name

        :rtype: string

        Example: example.com
        """
        return ""

    @abc.abstractmethod
    def get_region_name(self, zone):
        """Return the Region name

        :param string zone: Zone name

        :returns: Region name

        :rtype: string

        Example: "RegionOne"
        """
        return ""
