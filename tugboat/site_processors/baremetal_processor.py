#!/usr/bin/python3
import yaml
from jinja2 import Environment
from jinja2 import FileSystemLoader


class BaremetalProcessor():
    def __init__(self, file_name):
        raw_data = self.read_file(file_name)
        yaml_data = self.get_yaml_data(raw_data)
        self.baremetal_data = yaml_data['baremetal']

    def constructor(loader, node):
        return node.value

    @staticmethod
    def read_file(file_name):
        with open(file_name, 'r') as f:
            raw_data = f.read()
        return raw_data

    @staticmethod
    def get_yaml_data(data):
        yaml.SafeLoader.add_constructor("tag:yaml.org,2002:python/unicode", constructor)
        yaml_data = yaml.safe_load(data)
        return yaml_data

    def render_template(self, template):
        j2_env = Environment(
                autoescape=False,
                loader=FileSystemLoader('templates/baremetal'),
                trim_blocks=True)
        template = j2_env.get_template(template)
        for rack in self.baremetal_data:
            data = self.baremetal_data[rack]
            outfile = 'baremetal/{}.yaml'.format(rack)
            try:
                out = open(outfile, "w")
                # pylint: disable=maybe-no-member
                template.stream(data=data).dump(out)
                out.close()
            except IOError as ioe:
                raise SystemExit("Error when generating {:s}:\n{:s}"
                                 .format(outfile, ioe.strerror))
