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

import logging
import pkg_resources
import click
import yaml

from spyglass.parser.generate_intermediary import ProcessDataSource
from spyglass.site_processors.site_processor import SiteProcessor


def generate_manifest_files(intermediary):
    """ Generate manifests """
    if intermediary:
        processor_engine = SiteProcessor(intermediary)
        # logger.info('Generating manifest files')
        processor_engine.render_template()
    else:
        logging.error('Intermediary not found')


@click.command()
@click.option(
    '--site',
    '-s',
    help='Specify the site for which manifests to be generated')
@click.option(
    '--type', '-t', help='Specify the plugin type formation or tugboat')
@click.option('--formation_url', '-f', help='Specify the formation url')
@click.option('--formation_user', '-u', help='Specify the formation user id')
@click.option(
    '--formation_password', '-p', help='Specify the formation user password')
@click.option(
    '--additional_config',
    '-d',
    type=click.Path(exists=True),
    help='Site specific configuraton details')
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
    '--loglevel',
    '-l',
    default=20,
    multiple=False,
    show_default=True,
    help='Loglevel NOTSET:0 ,DEBUG:10, \
    INFO:20, WARNING:30, ERROR:40, CRITICAL:50')
def main(*args, **kwargs):
    generate_intermediary = kwargs['generate_intermediary']
    generate_manifests = kwargs['generate_manifests']
    site = kwargs['site']
    loglevel = kwargs['loglevel']
    logger = logging.getLogger('spyglass')
    # Set default log level to INFO
    logger.setLevel(loglevel)
    # set console logging. Change to file by changing to FileHandler
    stream_handle = logging.StreamHandler()
    # Set logging format
    formatter = logging.Formatter('(%(name)s)[%(levelname)s]'
                                  '%(filename)s [%(lineno)d]:'
                                  '(%(funcName)s)\n:%(message)s')
    stream_handle.setFormatter(formatter)
    logger.addHandler(stream_handle)
    logger.info("Spyglass start")

    plugin_type = kwargs['type']
    plugin_class = None
    for entry_point in pkg_resources.iter_entry_points(
            'data_extractor_plugins'):
        if entry_point.name == plugin_type:
            plugin_class = entry_point.load()

    if plugin_class is None:
        logger.error("Plugin class not loaded")
        exit()

    plugin_conf = {}
    additional_config_data = {}
    if plugin_type == 'formation':
        url = kwargs['formation_url']
        user = kwargs['formation_user']
        password = kwargs['formation_password']
        additional_config = kwargs['additional_config']

        # TODO(nh863p): Do we need to check if the arguments are null
        # or is it handled in click
        plugin_conf = {'url': url, 'user': user, 'password': password}
        plugin_conf['token'] = 'faketoken'

        if additional_config is not None:
            with open(additional_config, 'r') as config:
                raw_data = config.read()
                additional_config_data = yaml.safe_load(raw_data)

    data_extractor = plugin_class(site)
    data_extractor.set_config_opts(plugin_conf)
    data_extractor.extract_data()
    data_extractor.apply_additional_data(additional_config_data)
    logger.info(data_extractor.site_data)
    """
    Initialize ProcessDataSource object to process received data
    """
    process_input_ob = ProcessDataSource(site)
    # Parses the raw input received from data source
    process_input_ob.load_extracted_data_from_data_source(
        data_extractor.site_data)
    intermediary_yaml = {}
    intermediary_yaml = process_input_ob.generate_intermediary_yaml()
    if generate_intermediary:
        logger.info("Generating Intermediary File")
        process_input_ob.dump_intermediary_file()
    if generate_manifests:
        logger.info("Generatng Manifests")
        generate_manifest_files(intermediary_yaml)
    else:
        logger.info('No suitable options passed')
        logger.info("Usage Instructions:")
        logger.info(
            "Generate Intermediary:\ntugboat -g -d <additional_config>")
        logger.info(
            "Generate Manifest & Intermediary :\ntugboat -mg -d <site config>")

    logger.info("Spyglass Execution Completed")


if __name__ == '__main__':
    main()
