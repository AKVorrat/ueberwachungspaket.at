import json
import unicodecsv as csv


## see: https://stackoverflow.com/a/28246154
def flatten_json(b, delim):
    val = {}
    for i in b.keys():
        if isinstance(b[i], dict):
            get = flatten_json(b[i], delim)
            for j in get.keys():
                val[i + delim + j] = get[j]
        else:
            val[i] = b[i]
    return val


def json_file_to_csv_file(in_path, out_path):
    f = open(in_path)
    data = json.load(f)

    f = csv.writer(open(out_path, "wb+"))
    first_line = flatten_json(data[0], '.')
    f.writerow(first_line.keys())

    for line in data:
        line = flatten_json(line, '.')
        f.writerow(line.values())

# paths without extension
paths = {'ueberwachungspaket/data/government.json': 'ueberwachungspaket/static/data/government.csv',
         'ueberwachungspaket/data/representatives.json': 'ueberwachungspaket/static/data/representatives.csv'}
for in_path, out_path in paths.iteritems():
    json_file_to_csv_file(in_path, out_path)
