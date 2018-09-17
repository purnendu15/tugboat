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
import logging

PROCESSORS = [
    BaremetalProcessor, DeploymentProcessor, NetworkProcessor, PkiProcessor,
    ProfileProcessor, SiteDeifinitionProcessor, SoftwareProcessor
]


def generate_intermediary_file(excel, spec, sitetype, all_param=None):
    """ Generate intermediary file """
    if excel and spec and sitetype:
        parser = GenerateYamlFromExcel(excel, spec, sitetype)
        intermediary = parser.generate_yaml()
        print('Generating intermediary file {}'.format(intermediary))
    else:
        print('Please pass engineering excel and spec file')
    if all_param:
        return intermediary


def generate_manifest_files(intermediary):
    """ Generate manifests """
    if intermediary:
        print('Generating manifest files')
        for processor in PROCESSORS:
            processor_engine = processor(intermediary)
            processor_engine.render_template()
    else:
        logging.error('Please pass intermediary file')


@click.command()
@click.option(
    '--generate_intermediary',
    '-g',
    is_flag=True,
    help='Generate intermediary file from passed excel and excel spec')
@click.option(
    '--generate_manifests',
    '-m',
    is_flag=True,
    help='Generate manifests from the generated intermediary file')
@click.option(
    '--excel',
    '-x',
    type=click.Path(exists=True),
    help='Path to engineering excel file, to be passed with '
    'generate_intermediary')
@click.option(
    '--spec',
    '-s',
    type=click.Path(exists=True),
    help='Path to excel spec, to be passed with generate_intermediary')
@click.option(
    '--intermediary',
    '-i',
    type=click.Path(exists=True),
    help='Path to intermediary file, \
    to be passed with generate_manifests')
@click.option(
    '--sitetype',
    '-S',
    default='nc',
    multiple=False,
    show_default=True,
    help='Specify the sitetype \'5ec\' or \'nc\'')
@click.option(
    '--loglevel',
    '-l',
    default=20,
    multiple=False,
    show_default=True,
    help='Loglevel NOTSET:0 ,DEBUG:10,\
    INFO:20, WARNING:30, ERROR:40, CRITICAL:50')

def main(*args, **kwargs):
    generate_intermediary = kwargs['generate_intermediary']
    generate_manifests = kwargs['generate_manifests']
    excel = kwargs['excel']
    spec = kwargs['spec']
    intermediary = kwargs['intermediary']
    sitetype = kwargs['sitetype']
    loglevel = kwargs['loglevel']
    logger = logging.getLogger('tugboat')
    # Set default log level to INFO
    logger.setLevel(loglevel)
    # set console logging. Change to file by changing to FileHandler
    stream_handle = logging.StreamHandler()
    # Set logging format
    formatter = logging.Formatter('(%(name)s)[%(levelname)s]%(filename)s' +
                                  '[%(lineno)d]:(%(funcName)s)\n:%(message)s')
    stream_handle.setFormatter(formatter)
    logger.addHandler(stream_handle)
    logger.info("Tugboat start")
    """
    Generate intermediary and manifests files using the
    engineering package excel and respective excel spec.
    """
    if generate_intermediary and generate_manifests:
        logger.info("Generate Intermediary File")
        intermediary = generate_intermediary_file(
            excel, spec, sitetype, all_param=True)
        logger.info("Generate Manifest File")
        generate_manifest_files(intermediary)

    elif generate_intermediary:
        logger.info("Generate Intermediary File")
        intermediary = generate_intermediary_file(
            excel, spec, sitetype, all_param=True)
        logger.info("Intermediary File Generated: {}".format(intermediary))

    elif generate_manifests:
        logger.info("Generate Manifest File")
        intermediary = generate_intermediary_file(
            excel, spec, sitetype, all_param=True)
        generate_manifest_files(intermediary)

    else:
        print('No options passed')
        print("Usage Instructions:")
        print("Generate Manifests:\ntugboat -m -x <DesignSpec> -s <excel spec>") 
        print("Generate Intermediary:\ntugboat -g -x <DesignSpec> -s <excel spec>") 
        print("Generate Manifest & Intermediary:\ntugboat -mg -x <DesignSpec> -s <excel spec>") 

    logger.info("Tugboat Execution Completed")


if __name__ == '__main__':
    main()
