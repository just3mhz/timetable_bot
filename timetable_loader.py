import csv
import typing

from utils import float_to_time


def get_loader(ext: str):
    return {
        '.csv': CsvTimetableLoader,
    }.get(ext, None)


class BaseTimetableLoader:
    def __init__(self, path_to_file, scheme):
        self.path_to_file = path_to_file
        self.scheme = scheme

    def __iter__(self):
        pass


class CsvTimetableLoader(BaseTimetableLoader):
    def __init__(self, path_to_file, scheme):
        super(CsvTimetableLoader, self).__init__(path_to_file, scheme)

    def __iter__(self):
        with open(self.path_to_file, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            header = set(reader.fieldnames)
            if header != self.scheme:
                raise RuntimeError(f'Header does not match table scheme: {header} != {self.scheme}')
            for row in reader:
                yield row
