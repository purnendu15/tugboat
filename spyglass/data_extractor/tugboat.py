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
# TODO(pg710r): The below lines will be uncommented when tugboat plugib
# code is added
"""
import pprint
import re
import requests
import swagger_client
import urllib3


from spyglass.data_extractor.custom_exceptions import (
    ApiClientError, ConnectionError, MissingAttributeError,
    TokenGenerationError)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
"""
from spyglass.data_extractor.base import BaseDataSourcePlugin
LOG = logging.getLogger(__name__)


class TugboatPlugin(BaseDataSourcePlugin):
    def __init__(self, region):
        LOG.error(" Tugboat currently not supported. Exiting!!")
        exit()

    def set_config_opts(self, conf):
        # TODO(pg710r): Code will be added later
        pass

    def get_plugin_conf(self, kwargs):
        # TODO(pg710r): Code will be added later
        pass

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
        # TODO(pg710r): Code will be added later
        pass

    def get_networks(self, region):
        # TODO(pg710r): Code will be added later
        pass

    def get_ips(self, region, host=None):
        # TODO(pg710r): Code will be added later
        pass

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
