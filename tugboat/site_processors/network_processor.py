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
from tugboat.site_processors.base import BaseProcessor


class NetworkProcessor(BaseProcessor):
    def __init__(self, file_name):
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
            'tugboat', 'templates/networks')
        template_dir_abspath = os.path.dirname(template_software_dir)
        self.logger.debug("Template dif abspath:%s", template_dir_abspath)
        outfile_path = 'pegleg_manifests/site/{}/networks/'.format(
            self.yaml_data['region_name'])
        outfile_dir = os.path.dirname(outfile_path)
        if not os.path.exists(outfile_dir):
            os.makedirs(outfile_dir)
        outfile_j2 = ''
        template = 'common_addresses'
        self.logger.info("template :{}.yaml.j2".format(template))
        j2_env = Environment(
            autoescape=False,
            loader=FileSystemLoader(template_software_dir),
            trim_blocks=True)
        j2_env.filters['get_role_wise_nodes'] = self.get_role_wise_nodes
        template_name = j2_env.get_template('{}.yaml.j2'.format(template))
        outfile = '{}{}.yaml'.format(outfile_path, template.replace('_', '-'))
        self.logger.debug("Dict dump to %s:\n%s", template,
                          pprint.pformat(self.yaml_data['network']))
        """ Generating common config """
        try:
            out = open(outfile, "w")
            # pylint: disable=maybe-no-member
            template_name.stream(data=self.yaml_data).dump(out)
            self.logger.info('Rendered {}'.format(outfile))
            out.close()
        except IOError as ioe:
            raise SystemExit("Error when generating {:s}:\n{:s}".format(
                outfile, ioe.strerror))
        """ Generating rack specific configs """
        for dirpath, dirs, files in os.walk(template_dir_abspath):
            for filename in files:
                j2_env = Environment(
                    autoescape=False,
                    loader=FileSystemLoader(dirpath),
                    trim_blocks=True)
                templatefile = os.path.join(dirpath, filename)
                outfile_j2 = ''
                if not outfile_j2 and 'networks/physical' in templatefile:
                    outfile_j2 = outfile_path + templatefile.split(
                        'templates/networks/physical', 1)[1]
                    self.logger.info("template :{}".format(filename))
                else:
                    continue
                outfile = outfile_j2.split('.j2')[0]
                outfile_dir = os.path.dirname(outfile) + '/physical/'
                if not os.path.exists(outfile_dir):
                    os.makedirs(outfile_dir)
                template_j2 = j2_env.get_template(filename)
                yaml_filename = filename.split('.j2')[0]
                self.logger.debug("Dict dump to %s:\n%s", filename,
                                  pprint.pformat(self.yaml_data['network']))
                """ Generating rack specific configs """
                try:
                    outfile = '{}{}'.format(outfile_dir, yaml_filename)
                    out = open(outfile, "w")
                    template_j2.stream(
                        data=self.yaml_data).dump(out)
                        #data=self.yaml_data['network']).dump(out)
                    self.logger.info('Rendered {}'.format(outfile))
                    out.close()
                except IOError as ioe:
                    raise SystemExit("Error when generating {:s}:\n{:s}"
                                     .format(outfile, ioe.strerror))

