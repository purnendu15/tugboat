class BaseProcessor:

    def __init__(self, file_name):
        raw_data = self.read_file(file_name)
        yaml_data = self.get_yaml_data(raw_data)

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
      pass

