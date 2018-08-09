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

import sys
import getopt

from tugboat.parser_engine.generate_intermediary import GenerateYamlFromExcel

from tugboat.site_processors.baremetal_processor import BaremetalProcessor
from tugboat.site_processors.deployment_processor import DeploymentProcessor
from tugboat.site_processors.network_processor import NetworkProcessor
from tugboat.site_processors.pki_processor import PkiProcessor
from tugboat.site_processors.profile_processor import ProfileProcessor
from tugboat.site_processors.site_definition_processor import (
    SiteDeifinitionProcessor
)
from tugboat.site_processors.software_processor import SoftwareProcessor



def main(argv=None):
    if argv is None:
        argv = sys.argv
    # parse command line options
    filename_path = ''
    excel_spec_path = ''
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h', 'help')
    except getopt.GetoptError as msg:
        print('for help use --help')
    for o, a in opts:
        if o in ('-h', '--help'):
            print('Please provide xls and excelspec files as follows: python '
                  'tugboat.py <spreadsheet> <excelspec>')
            sys.exit(0)
    # for arg in args:
    filename_path = args[0]
    excel_spec_path = args[1]
    # Generate YAML from Excel Workbook engine
    ob = GenerateYamlFromExcel(filename_path, excel_spec_path)
    ob.generate_yaml()
    # Baremetal Processor
    ob1 = BaremetalProcessor('intermediary.yaml')
    ob1.render_template()

    # Deployment Processor
    ob2 = DeploymentProcessor()
    ob2.render_template()

    # Network Processor
    ob3 = NetworkProcessor('intermediary.yaml')
    ob3.render_template()

    # Pki Processor
    ob4 = PkiProcessor('intermediary.yaml')
    ob4.render_template()

    # Profile PROCESSOR
    ob5 = ProfileProcessor('intermediary.yaml')
    ob5.render_template()

    # Site Definition Processor
    ob6 = SiteDeifinitionProcessor('intermediary.yaml')
    ob6.render_template()

    # Software Processor
    ob7 = SoftwareProcessor('intermediary.yaml')
    ob7.render_template()


if __name__ == '__main__':
    main()
