import csv


def get_loader(ext: str):
    return {
        '.csv': CsvTimetableLoader
    }.get(ext)


class BaseTimetableLoader:
    def __iter__(self):
        pass


class CsvTimetableLoader(BaseTimetableLoader):
    def __init__(self, path_to_file, group_id):
        self.path_to_file = path_to_file
        self.group_id = group_id

    def __iter__(self):
        with open(self.path_to_file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            # TODO: Header validation
            header = next(reader)
            for row in reader:
                yield [self.group_id] + row