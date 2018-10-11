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

# The InputParser class is the base class for all parser plugins supported
# by Tugboat. Any new Parser plugin shall inherit InputParser and 


import yaml


class InputParser:
    def __init__():
        self.file_name = file_name
        with open(specs, 'r') as f:
            spec_raw_data = f.read()
        self.specs = yaml.safe_load(spec_raw_data)

    def compare(self, string1, string2):
        pass

    @staticmethod
    def sanitize(string):
        """ Remove extra spaces and convert string to lower case """
        return string.replace(' ', '').lower()

    def compare(self, string1, string2):
        pass

    def validate_sheet(self, spec, sheet):
        pass

    def find_correct_spec(self):
        pass

    def get_ipmi_data(self):
        pass

    def get_private_vlan_data(self, ws):
        pass

    def get_private_network_data(self):
        pass

    def get_public_network_data(self):
        pass

    def get_dns_ntp_ldap_data(self):
        pass

    def get_location_data(self):
        pass

    def validate_data(self, data):
        pass

    def validate_sheet_names_with_spec(self):
        pass

    def get_data(self):
        pass

    def combine_excel_design_specs(self, filenames):
        pass

    def get_xl_obj_and_sheetname(self, sheetname):
        pass

    def get_network_data(self, raw_data):
        pass


