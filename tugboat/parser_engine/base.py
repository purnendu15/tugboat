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


class ParserEngine:
    def __init__(self, file_name, specs):
        self.file_name = file_name
        with open(specs, 'r') as f:
            spec_raw_data = f.read()
        self.specs = yaml.safe_load(spec_raw_data)

    def get_parsed_data(self, file_name, excel_specs):
        pass

    def get_network_data(self, raw_data):
        pass

    def get_rack(self, host):
        pass
