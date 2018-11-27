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
import pprint

import click
import yaml

from spyglass.parser.generate_intermediary import ProcessDataSource
from spyglass.site_processors.site_processor import SiteProcessor

LOG = logging.getLogger('spyglass')


def generate_manifest_files(intermediary, manifest_dir=None):
    """ Generate manifests """
    if intermediary:
        processor_engine = SiteProcessor(intermediary, manifest_dir)
        processor_engine.render_template()
    else:
        LOG.error('Intermediary not found')


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
    '--intermediary',
    '-i',
    type=click.Path(exists=True),
    help=
    'Intermediary file path  generate manifests, use -m also with this option')
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
    '--intermediary_dir',
    '-idir',
    type=click.Path(exists=True),
    help='The path where intermediary file needs to be generated')
@click.option(
    '--edit_intermediary/--no_edit_intermediary',
    '-e/-nedit',
    default=False,
    help='Flag to let user edit intermediary')
@click.option(
    '--generate_manifests',
    '-m',
    is_flag=True,
    help='Generate manifests from the generated intermediary file')
@click.option(
    '--manifest_dir',
    '-mdir',
    type=click.Path(exists=True),
    help='The path where manifest files needs to be generated')
@click.option(
    '--excel',
    '-x',
    multiple=True,
    type=click.Path(exists=True),
    help=
    'Path to engineering excel file, to be passed with generate_intermediary')
@click.option(
    '--excel_spec',
    '-e',
    type=click.Path(exists=True),
    help='Path to excel spec, to be passed with generate_intermediary')
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
    intermediary_dir = kwargs['intermediary_dir']
    edit_intermediary = kwargs['edit_intermediary']
    generate_manifests = kwargs['generate_manifests']
    manifest_dir = kwargs['manifest_dir']
    intermediary = kwargs['intermediary']
    site = kwargs['site']
    loglevel = kwargs['loglevel']
    # Set default log level to INFO
    LOG.setLevel(loglevel)
    # set console logging. Change to file by changing to FileHandler
    stream_handle = logging.StreamHandler()
    # Set logging format
    formatter = logging.Formatter(
        '(%(name)s): %(asctime)s %(levelname)s %(message)s')
    stream_handle.setFormatter(formatter)
    LOG.addHandler(stream_handle)
    LOG.info("Spyglass start")
    LOG.info("CLI Parameters passed:\n{}".format(kwargs))

    # When intermediary file is specified, Spyglass will generate the
    # manifest without extracting any data from plugin data source
    if (intermediary is None) and (generate_intermediary
                                   or generate_manifests):
        plugin_type = kwargs['type']
        plugin_class = None
        # Get the additional site config data supplied by CLI
        additional_config = kwargs['additional_config']
        for entry_point in pkg_resources.iter_entry_points(
                'data_extractor_plugins'):
            if entry_point.name == plugin_type:
                plugin_class = entry_point.load()
        if plugin_class is None:
            LOG.error(
                "Unsupported Plugin type. Plugin type:{}".format(plugin_type))
            exit()

        data_extractor = plugin_class(site)
        plugin_conf = data_extractor.get_plugin_conf(kwargs)

        if additional_config is not None:
            with open(additional_config, 'r') as config:
                raw_data = config.read()
                additional_config_data = yaml.safe_load(raw_data)

        LOG.debug("Additional site config data passed:\n{}".format(
            pprint.pformat(additional_config_data)))
        data_extractor.set_config_opts(plugin_conf)
        data_extractor.extract_data()
        LOG.info(
            "Apply additional configuration from:{}".format(additional_config))
        data_extractor.apply_additional_data(additional_config_data)
        """
        Initialize ProcessDataSource object to process received data
        """
        process_input_ob = ProcessDataSource(site)
        # Parses the raw input received from data source
        process_input_ob.load_extracted_data_from_data_source(
            data_extractor.site_data)
        intermediary_yaml = {}
        LOG.info("Generating intermediary")
        intermediary_yaml = process_input_ob.generate_intermediary_yaml()
        if edit_intermediary:
            process_input_ob.edit_intermediary_yaml()
        if generate_intermediary:
            process_input_ob.dump_intermediary_file(intermediary_dir)
        if generate_manifests:
            LOG.info("Generating site Manifests")
            generate_manifest_files(intermediary_yaml, manifest_dir)

    elif generate_manifests and intermediary:
        """
        Generating manifest with the supplied intermediary. In this case
        extraction of plugin data source is not required
        """
        LOG.info("Loading intermediary")
        with open(intermediary, 'r') as intermediary_file:
            raw_data = intermediary_file.read()
            yaml_data = yaml.safe_load(raw_data)
            intermediary_yaml = yaml_data
        LOG.info("Generatng Manifests")
        generate_manifest_files(intermediary_yaml, manifest_dir)
    else:
        LOG.error("Invalid CLI parameters passed!! Spyglass exited")
        LOG.info("CLI Parameters:\n{}".format(kwargs))
        exit()

    LOG.info("Spyglass Execution Completed")


if __name__ == '__main__':
    main()
