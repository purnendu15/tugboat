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
from .base import BaseProcessor

class SoftwareProcessor:
    def __init__(self, file_name):
        BaseProcessor.__init__(self, file_name)
        self.logger = logging.getLogger(__name__)
        raw_data = self.read_file(file_name)
        yaml_data = self.get_yaml_data(raw_data)
        self.data = yaml_data
        self.dir_name = yaml_data['region_name']
        self.data['ldap_username'] = self.rules_data['ldap_username']

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
        template_software_dir = pkg_resources.resource_filename(
            'tugboat', 'templates/software/')
        template_dir_abspath = os.path.dirname(template_software_dir)
        outfile_path = 'pegleg_manifests/site/{}/software'.format(
            self.dir_name)

        for dirpath, dirs, files in os.walk(template_dir_abspath):
            for filename in files:
                j2_env = Environment(
                    autoescape=False,
                    loader=FileSystemLoader(dirpath),
                    trim_blocks=True)
                self.logger.info("template :{}".format(filename))
                templatefile = os.path.join(dirpath, filename)
                outfile_j2 = outfile_path + templatefile.split(
                    'templates/software', 1)[1]
                outfile = outfile_j2.split('.j2')[0]
                outfile_dir = os.path.dirname(outfile)
                if not os.path.exists(outfile_dir):
                    os.makedirs(outfile_dir)
                template_j2 = j2_env.get_template(filename)
                self.logger.debug("Dict dump to %s:\n%s", filename,
                                  pprint.pformat(self.data))
                try:
                    out = open(outfile, "w")
                    # pylint: disable=maybe-no-member
                    template_j2.stream(data=self.data).dump(out)
                    self.logger.info('Rendered {}'.format(outfile))
                    out.close()
                except IOError as ioe:
                    raise SystemExit("Error when generating {:s}:\n{:s}"
                                     .format(outfile, ioe.strerror))
