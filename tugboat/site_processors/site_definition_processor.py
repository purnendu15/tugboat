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
import logging
import pprint


from jinja2 import Environment
from jinja2 import FileSystemLoader

from tugboat.config import settings


class SiteDeifinitionProcessor:
    def __init__(self, file_name):
        self.logger = logging.getLogger(__name__)
        raw_data = self.read_file(file_name)
        yaml_data = self.get_yaml_data(raw_data)
        self.region_name = yaml_data['region_name']
        self.baremetal_data = yaml_data['baremetal']
        self.ingress = yaml_data['network']['ingress']

    @staticmethod
    def read_file(file_name):
        with open(file_name, 'r') as f:
            raw_data = f.read()
        return raw_data

    @staticmethod
    def get_yaml_data(data):
        yaml_data = yaml.safe_load(data)
        return yaml_data

    def render_template(self):
        """ Renders site config yaml describing site type and information"""
        for template in settings.SITE_DEFINITION_TEMPLATES:
            template_file = pkg_resources.resource_filename(
                'tugboat', 'templates/site_definition/site_definition.yaml.j2')
            template_dir = os.path.dirname(template_file)
            self.logger.info("template :{}.yaml.j2".format(template))
            j2_env = Environment(
                autoescape=False,
                loader=FileSystemLoader(template_dir),
                trim_blocks=True)
            file_path = 'pegleg_manifests/site/{}/'.format(self.region_name)
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)
            template_name = j2_env.get_template('{}.yaml.j2'.format(template))
            outfile = '{}{}.yaml'.format(file_path, "site-definition")
            self.logger.debug(
                "Dict dump to %s:\n%s",
                template, pprint.pformat(self.region_name))
            try:
                out = open(outfile, "w")
                # pylint: disable=maybe-no-member
                template_name.stream(region_name=self.region_name).dump(out)
                self.logger.info('Rendered {}'.format(outfile))
                out.close()
            except IOError as ioe:
                raise SystemExit("Error when generating {:s}:\n{:s}".format(
                    outfile, ioe.strerror))
