class BaseError(Exception):
    pass


class NotEnoughIp(BaseError):
    def __init__(self, cidr, total_nodes):
        self.cidr = cidr
        self.total_nodes = total_nodes

    def display_error(self):
        print(
            '{} can not handle {} nodes'.format(self.cidr, self.total_nodes)
        )


class NoSpecMatched(BaseError):
    def __init__(self, excel_specs):
        self.specs = excel_specs

    def display_error(self):
        print(
            'No spec matched. Following are the available specs:\n'.format(
                self.specs
            )
        )
