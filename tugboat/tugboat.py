#/usr/bin/python
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

from parser_engine.generate_intermediary import GenerateYamlFromExcel
from site_processors.baremetal_processor import BaremetalProcessor


def main():
    file_name = '{}{}'.format('/Users/gurpreets/Documents/clcp/Parser excels',
                              '/MTN_57_AEC_Design_Specs_v_1.1.xlsx')
    excel_specs = 'parser_engine/config/excel_spec.yaml'
    ob = GenerateYamlFromExcel(file_name, excel_specs)
    ob.generate_yaml()
    ob1 = BaremetalProcessor('intermediary.yaml')
    ob1.render_template('rack.yaml.j2')


if __name__ == "__main__":
    main()
