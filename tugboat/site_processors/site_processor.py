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
import pkg_resources
import os
import netaddr
import logging
import pprint

from jinja2 import Environment
from jinja2 import FileSystemLoader
from .base import BaseProcessor



class SiteProcessor(BaseProcessor):
    def __init__(self, file_name):
        BaseProcessor.__init__(self, file_name)
        self.logger = logging.getLogger(__name__)
        raw_data = self.read_file(file_name)
        self.yaml_data = self.get_yaml_data(raw_data)

    @staticmethod
    def read_file(file_name):
        with open(file_name, 'r') as f:
            raw_data = f.read()
        return raw_data

    @staticmethod
    def get_yaml_data(data):
        """ load yaml data """
        yaml_data = yaml.safe_load(data)
        return yaml_data

    def render_template(self):
        """
        The function renders network config yaml from j2 templates.
        Network configs common to all racks (i.e oam, overlay, storage,
        ksn) are generated in a single file. Rack specific
        configs( pxe and oob) are generated per rack.
        """
        template_software_dir = pkg_resources.resource_filename(
            'tugboat', 'templates/')
        template_dir_abspath = os.path.dirname(template_software_dir)
        self.logger.debug("Template dif abspath:%s", template_dir_abspath)

        """ Get sitetype and set Hardware profile accordingly """
        hardware_profile = {}
        for key in self.rules_data['hardware_profile']:
            if self.yaml_data["sitetype"] == key:
                hardware_profile = self.rules_data['hardware_profile'][key]
        self.yaml_data['hw_profile'] = hardware_profile

        for dirpath, dirs, files in os.walk(template_dir_abspath):
            for filename in files:
                j2_env = Environment(
                    autoescape=False,
                    loader=FileSystemLoader(dirpath),
                    trim_blocks=True)
                j2_env.filters['get_role_wise_nodes'] = self.get_role_wise_nodes
                templatefile = os.path.join(dirpath, filename)
                outdirs = dirpath.split('templates')[1]
                outfile_path = 'pegleg_manifests/site/{}{}'.format(
                    self.yaml_data['region_name'], outdirs )
                outfile_yaml = templatefile.split('.j2')[0].split('/')[-1]
                outfile = outfile_path +'/'+ outfile_yaml
                outfile_dir = os.path.dirname(outfile) 
                if not os.path.exists(outfile_dir):
                    os.makedirs(outfile_dir)
                template_j2 = j2_env.get_template(filename)
                self.logger.info("Rendering {}".format(template_j2))
                try:
                    out = open(outfile, "w")
                    template_j2.stream(
                        data=self.yaml_data).dump(out)
                    self.logger.info('Rendered {}'.format(outfile))
                    out.close()
                except IOError as ioe:
                    raise SystemExit("Error when generating {:s}:\n{:s}"
                                     .format(outfile, ioe.strerror))

