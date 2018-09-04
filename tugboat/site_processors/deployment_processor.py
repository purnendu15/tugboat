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

import pkg_resources
import os
import yaml
import logging
import pprint

from jinja2 import Environment
from jinja2 import FileSystemLoader

from tugboat.config import settings


class DeploymentProcessor:
    def __init__(self, file_name):
        self.logger = logging.getLogger(__name__)
        self.deployment_manifest = settings.DEPLOYMENT_MANIFEST
        raw_data = self.read_file(file_name)
        yaml_data = self.get_yaml_data(raw_data)
        self.dir_name = yaml_data['region_name']

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
        template_file = pkg_resources.resource_filename(
            'tugboat', 'templates/deployment/deployment-configuration.yaml.j2')
        template = 'deployment-configuration'
        template_dir = os.path.dirname(template_file)
        self.logger.info("template :{}.yaml.j2".format(template))
        j2_env = Environment(
            autoescape=False,
            loader=FileSystemLoader(template_dir),
            trim_blocks=True)
        file_path = 'pegleg_manifests/site/{}/deployment/'.format(
            self.dir_name)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        template_name = j2_env.get_template('{}.yaml.j2'.format(template))
        outfile = '{}{}.yaml'.format(file_path, 'deployment-configuration')
        self.logger.debug("Dict dump to %s %s", template,
                          pprint.pformat(self.deployment_manifest))
        try:
            out = open(outfile, "w")
            # pylint: disable=maybe-no-member
            template_name.stream(data=self.deployment_manifest).dump(out)
            self.logger.info('Rendered {}'.format(outfile))
            out.close()
        except IOError as ioe:
            raise SystemExit("Error when generating {:s}:\n{:s}".format(
                outfile, ioe.strerror))
