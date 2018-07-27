import re

class ParserEngine:

    def __init__(self, file_name, specs):
        self.file_name = file_name
        with open(specs, 'r') as f:
            spec_raw_data = f.read()
        self.specs = yaml.safe_load(spec_raw_data)

    def get_parsed_data(self, file_name, excel_specs):
      pass

    def get_network_data(self, raw_data):
      pass

    def get_rack(self, host):
      pass
