"""jc - JSON CLI output utility `zipinfo` command output parser

Options supported:
- none

Note: The default listing format.

Usage (cli):

    $ zipinfo <archive> | jc --zipinfo

    or

    $ jc zipinfo

Usage (module):

    import jc.parsers.zipinfo
    result = jc.parsers.zipinfo.parse(zipinfo_command_output)

Schema:

    {
      "archive":              string,
      "size":                 integer,
      "size_unit":            string,
      "number_entries":       integer,
      "number_files":         integer,
      "bytes_uncompressed":   integer,
      "bytes_compressed":     integer,
      "percent_compressed":   float,
      "files": [
        {
          "flags":            string,
          "zipversion":       string,
          "zipunder":         string
          "filesize":         integer,
          "type":             string,
          "method":           string,
          "date":             string,
          "time":             string,
          "filename":         string
        }
      ]
    }

Examples:

    $ zipinfo log4j-core-2.16.0.jar | jc --zipinfo -p

    [
      {
        "archive": "log4j-core-2.16.0.jar",
        "size": 1789565,
        "size_unit": "bytes",
        "number_entries": 1218,
        "number_files": 1218,
        "bytes_uncompressed": 3974141,
        "bytes_compressed": 1515455,
        "percent_compressed": 61.9,
        "files": [
          {
            "flags": "-rw-r--r--",
            "zipversion": "2.0",
            "zipunder": "unx",
            "filesize": 19810,
            "type": "bl",
            "method": "defN",
            "date": "21-Dec-12",
            "time": "23:35",
            "filename": "META-INF/MANIFEST.MF"
          },
    ...
"""
import jc.utils
import jc.parsers.universal


class info():
    """Provides parser metadata (version, author, etc.)"""
    version = '0.01'
    description = '`zipinfo` command parser'
    author = 'Matt J'
    author_email = 'https://github.com/listuser'
    compatible = ['linux', 'darwin']
    magic_commands = ['zipinfo']


__version__ = info.version


def _process(proc_data):
    """
    Final processing to conform to the schema.

    Parameters:

        proc_data:   (List of Dictionaries) raw structured data to process

    Returns:

        List of Dictionaries. Structured data to conform to the schema.
    """

    for entry in proc_data:
        int_list = ['bytes_compressed', 'bytes_uncompressed', 'number_entries', 'number_files', 'size']
        for key in entry:
            if key in int_list:
                entry[key] = jc.utils.convert_to_int(entry[key])

            if key in "files":
                for d in entry[key]:
                    for key in d:
                        if key in "filesize":
                            d[key] = jc.utils.convert_to_int(d[key])

    return proc_data


def parse(data, raw=False, quiet=False):
    """
    Main text parsing function

    Parameters:

        data:        (string)  text data to parse
        raw:         (boolean) output preprocessed JSON if True
        quiet:       (boolean) suppress warning messages if True

    Returns:

        List of Dictionaries. Raw or processed structured data.
    """
    jc.utils.compatibility(__name__, info.compatible, quiet)
    jc.utils.input_type_check(data)

    raw_output = {}

    datalines = data.splitlines()
    datalist = list(filter(None, datalines))

    if jc.utils.has_data(data):

        archive_info = []

        # 1st line
        # Archive:  log4j-core-2.16.0.jar
        line = datalist.pop(0)
        _, archive = line.split()

        # 2nd line
        # Zip file size: 1789565 bytes, number of entries: 1218
        line = datalist.pop(0)
        _, _, _, size, size_unit, _, _, _, number_entries = line.split()
        size_unit = size_unit.rstrip(',')

        # last line
        # 1218 files, 3974141 bytes uncompressed, 1515455 bytes compressed:  61.9%
        line = datalist.pop(-1)
        number_files, _, bytes_uncompressed, _, _, bytes_compressed, _, _, percent_compressed = line.split()
        percent_compressed = float(percent_compressed.rstrip("%"))

        # Add header row for parsing
        datalist[:0] = ['flags zipversion zipunder filesize type method date time filename']

        file_list = jc.parsers.universal.simple_table_parse(datalist)

        archive_info.append({'archive': archive,
                             'size': size,
                             'size_unit': size_unit,
                             'number_entries': number_entries,
                             'number_files': number_files,
                             'bytes_uncompressed': bytes_uncompressed,
                             'bytes_compressed': bytes_compressed,
                             'percent_compressed': percent_compressed,
                             'files': file_list})

        raw_output = archive_info

    return raw_output if raw else _process(raw_output)
