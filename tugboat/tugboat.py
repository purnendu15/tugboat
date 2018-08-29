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

import click

from tugboat.parser_engine.generate_intermediary import GenerateYamlFromExcel

from tugboat.site_processors.baremetal_processor import BaremetalProcessor
from tugboat.site_processors.deployment_processor import DeploymentProcessor
from tugboat.site_processors.network_processor import NetworkProcessor
from tugboat.site_processors.pki_processor import PkiProcessor
from tugboat.site_processors.profile_processor import ProfileProcessor
from tugboat.site_processors.site_definition_processor import (
    SiteDeifinitionProcessor)
from tugboat.site_processors.software_processor import SoftwareProcessor

PROCESSORS = [
    BaremetalProcessor, DeploymentProcessor, NetworkProcessor, PkiProcessor,
    ProfileProcessor, SiteDeifinitionProcessor, SoftwareProcessor
]


def generate_intermediary_file(excel, spec, both=None):
    """ Generate intermediary file """
    if excel and spec:
        parser = GenerateYamlFromExcel(excel, spec)
        intermediary = parser.generate_yaml()
        print('Generating intermediary file {}'.format(intermediary))
    else:
        print('Please pass engineering excel and spec file')
    if both:
        return intermediary


def generate_manifest_files(intermediary):
    """ Generate manifests """
    if intermediary:
        print('Generating manifest files')
        for processor in PROCESSORS:
            processor_engine = processor(intermediary)
            processor_engine.render_template()
    else:
        print('Please pass intermediary file')


@click.command()
@click.option(
    '--generate_intermediary', '-g', is_flag=True,
    help='Generate intermediary file from passed excel and excel spec'
)
@click.option(
    '--generate_manifests', '-m', is_flag=True,
    help='Generate manifests from the generated intermediary file'
)
@click.option(
    '--excel', '-x', type=click.Path(exists=True),
    help='Path to engineering excel file, to be passed with '
    'generate_intermediary'
)
@click.option(
    '--spec', '-s', type=click.Path(exists=True),
    help='Path to excel spec, to be passed with generate_intermediary'
)
@click.option(
    '--intermediary', '-i', type=click.Path(exists=True),
    help='Path to intermediary file, to be passed with generate_manifests'
)
def main(*args, **kwargs):
    """
    Generate intermediary and manifests files using the
    engineering package excel and respective excel spec.
    """
    generate_intermediary = kwargs['generate_intermediary']
    generate_manifests = kwargs['generate_manifests']
    excel = kwargs['excel']
    spec = kwargs['spec']
    intermediary = kwargs['intermediary']
    if generate_intermediary and generate_manifests:
        intermediary = generate_intermediary_file(excel, spec, both=True)
        generate_manifest_files(intermediary)

    elif generate_intermediary:
        generate_intermediary_file(excel, spec)

    elif generate_manifests:
        generate_manifest_files(intermediary)

    else:
        print('No options passed. Please pass either of -g or -m')


if __name__ == '__main__':
    main()
