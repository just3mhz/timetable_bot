import csv
import xlrd

from utils import float_to_time


def get_loader(ext: str):
    return {
        '.csv': CsvTimetableLoader,
        '.xlsx': ExcelTimetableLoader
    }.get(ext, default=None)


class BaseTimetableLoader:
    def __init__(self, path_to_file, group_id):
        self.path_to_file = path_to_file
        self.group_id = group_id

    def __iter__(self):
        pass


class CsvTimetableLoader(BaseTimetableLoader):
    def __init__(self, path_to_file, group_id):
        super(CsvTimetableLoader, self).__init__(path_to_file, group_id)

    def __iter__(self):
        with open(self.path_to_file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            # TODO: Header validation
            header = next(reader)
            for row in reader:
                yield [self.group_id] + row


class ExcelTimetableLoader(BaseTimetableLoader):
    def __init__(self, path_to_file: str, group_id: int):
        super(ExcelTimetableLoader, self).__init__(path_to_file, group_id)

    def __iter__(self):
        rb = xlrd.open_workbook(self.path_to_file)
        sheet = rb.sheet_by_index(0)
        # TODO: Header validation
        header = sheet.row_values(0)
        for row_number in range(1, sheet.nrows):
            row = sheet.row_values(row_number)
            row[-1] = float_to_time(row[-1])
            yield [self.group_id] + row

