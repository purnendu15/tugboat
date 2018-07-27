import re
import yaml
from openpyxl import load_workbook

from check_exceptions import (
    NoSpecMatched,
)


class ExcelParser():

    def __init__(self, file_name, excel_specs):
        self.file_name = file_name
        with open(excel_specs, 'r') as f:
            spec_raw_data = f.read()
        self.excel_specs = yaml.safe_load(spec_raw_data)
        self.wb = load_workbook(file_name)
        self.ipmi_data = {}
        self.hosts = []
        self.spec = None
        self.network_data = {}

    @staticmethod
    def sanitize(string):
        return string.replace(' ', '').lower()

    def compare(self, string1, string2):
        return bool(
            re.search(
                self.sanitize(string1),
                self.sanitize(string2)
            ))

    def validate_sheet(self, spec, sheet):
        ws = self.wb[sheet]
        header_row = self.excel_specs['specs'][spec]['header_row']
        ipmi_header = self.excel_specs['specs'][spec]['ipmi_address_header']
        ipmi_column = self.excel_specs['specs'][spec]['ipmi_address_col']
        header_value = ws.cell(row=header_row, column=ipmi_column).value
        return bool(
            self.compare(ipmi_header,
                         header_value)
            )

    def find_correct_spec(self):
        for spec in self.excel_specs['specs']:
            sheet_name = self.excel_specs['specs'][spec]['ipmi_sheet_name']
            for sheet in self.wb.sheetnames:
                if self.compare(sheet_name, sheet):
                    self.excel_specs['specs'][spec]['ipmi_sheet_name'] = sheet
                    if self.validate_sheet(spec, sheet):
                        return spec
        raise NoSpecMatched(self.excel_specs)

    def get_ipmi_data(self):
        self.spec = self.find_correct_spec()
        sheet_name = self.excel_specs['specs'][self.spec]['ipmi_sheet_name']
        ws = self.wb[sheet_name]
        row = self.excel_specs['specs'][self.spec]['start_row']
        end_row = self.excel_specs['specs'][self.spec]['end_row']
        hostname_col = self.excel_specs['specs'][self.spec]['hostname_col']
        ipmi_address_col = self.excel_specs['specs'][self.spec][
            'ipmi_address_col']
        host_profile_col = self.excel_specs['specs'][self.spec][
            'host_profile_col']
        ipmi_gateway_col = self.excel_specs['specs'][self.spec][
            'ipmi_gateway_col']
        while row <= end_row:
            hostname = self.sanitize(
                ws.cell(row=row, column=hostname_col).value)
            self.hosts.append(hostname)
            ipmi_address = ws.cell(row=row, column=ipmi_address_col).value
            if '/' in ipmi_address:
                ipmi_address = ipmi_address.split('/')[0]
            ipmi_gateway = ws.cell(row=row, column=ipmi_gateway_col).value
            tmp_host_profile = ws.cell(row=row, column=host_profile_col).value
            host_profile = tmp_host_profile.split('-')[1]
            self.ipmi_data[hostname] = {
                'ipmi_address': ipmi_address,
                'ipmi_gateway': ipmi_gateway,
                'host_profile': host_profile,
            }
            row += 1
        return [self.ipmi_data, self.hosts]

    def get_network_data(self):
        import pdb;pdb.set_trace()
        sheet_name = self.excel_specs['specs'][self.spec]['private_ip_sheet']
        ws = self.wb[sheet_name]
        row = self.excel_specs['specs'][self.spec]['net_start_row']
        end_row = self.excel_specs['specs'][self.spec]['net_end_row']
        type_col = self.excel_specs['specs'][self.spec]['net_type_col']
        subnet_col = self.excel_specs['specs'][self.spec]['subnet_col']
        cidr_per_rack_col = self.excel_specs['specs'][self.spec][
            'cidr_per_rack_col']
        while row <= end_row:
            cell_value = ws.cell(row=row, column=type_col).value
            if cell_value:
                subnet_range = ws.cell(row=row, column=subnet_col).value
                cidr_per_rack = ws.cell(row=row,
                                        column=cidr_per_rack_col).value
                self.network_data[cell_value] = {
                    'subnet_range': subnet_range,
                    'cidr_per_rack': cidr_per_rack,
                }
            row += 1
        return self.network_data

    def get_data(self):
        ipmi_data = self.get_ipmi_data()
        network_data = self.get_network_data()
        return {
            'ipmi_data': ipmi_data,
            'network_data': network_data,
            }
