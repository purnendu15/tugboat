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

from tugboat.parser_engine.generate_intermediary import ProcessInputFiles

from tugboat.site_processors.site_processor import SiteProcessor 
import logging


def generate_manifest_files(intermediary):
    """ Generate manifests """
    if intermediary:
        processor_engine = SiteProcessor(intermediary)
        print('Generating manifest files')
        processor_engine.render_template()
    else:
        logging.error('Intermediary not found')


@click.command()
@click.option(
    '--generate_intermediary',
    '-g',
    is_flag=True,
    help='Dump intermediary file from passed excel and excel spec')
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
    '--exel_spec',
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
    '--site_config',
    '-d',
    required=True,
    type=click.Path(exists=True),
    help='Path to the site specific yaml file')
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
    exel_spec = kwargs['exel_spec']
    intermediary = kwargs['intermediary']
    sitetype = kwargs['sitetype']
    site_config = kwargs['site_config']
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
    process_input_ob = ProcessInputFiles(excel,exel_spec,sitetype)

    """ Collects rules.yaml data """
    process_input_ob.apply_design_rules(site_config)
    """ Parses the design spec supplied to raw yaml """
    logger.info("Parsing raw data from design spec")
    process_input_ob.get_parsed_raw_data_from_excel()
    logger.info("Generating Intermediary File")
    intermediary_yaml = {}

    """ Check if mandatory params exists """

    if generate_intermediary and generate_manifests:
        logger.info("Generating Intermediary File")
        intermediary_yaml = process_input_ob.generate_intermediary_yaml()
        process_input_ob.dump_intermediary_file()
        logger.info("Generatng Manifests")
        generate_manifest_files(intermediary_yaml)

    elif  generate_manifests and intermediary:
        """ 
        Generating manifest with the supplied intermediary
        In this case supplied design spec and excel-spec
        is not required
        """
        logger.info("Loading intermediary")
        with open(intermediary, 'r') as intermediary_file:
            raw_data = intermediary_file.read()
            yaml_data = yaml.safe_load(raw_data)
            intermediary_yaml = raw_data 
        logger.info("Generatng Manifests")
        generate_manifest_files(intermediary_yaml)

    elif generate_intermediary:
        logger.info("Generating Intermediary File")
        intermediary_yaml = process_input_ob.generate_intermediary_file()
        process_input_ob.dump_intermediary_file()
        
    else:
        print('No suitable options passed')
        print("Usage Instructions:")
        print("Generate Intermediary:\ntugboat -g -x <DesignSpec> -s <excel spec>") 
        print("Generate Manifest & Intermediary:\ntugboat -mg -x <DesignSpec> -s <excel spec>") 
        print("Generate Manifest with supplied Intermediary" +
              ":\ntugboat -m -i  <intemediary_file>") 

    logger.info("Tugboat Execution Completed")


if __name__ == '__main__':
    main()
