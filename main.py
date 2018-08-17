import json
import argparse
import shelve
from importlib import import_module
from core.helper import fatal_error, log_info
from core.downloader import download_timetable
from core.usage_info_builder import find_auditoriums_usage


class Defaults:
    DefaultActionName = 'represent'
    DefaultCachePath = 'timetable'


def execute_action(auditoriums_usage, action_name):
    action_module = import_module(f'.{action_name}', 'actions')
    action_func = getattr(action_module, 'action')
    result = action_func(auditoriums_usage)
    return result


def write_result(obj, result_file):
    try:
        f = open(result_file, 'w', encoding='utf-8')
        f.write(json.dumps(obj, ensure_ascii=False, indent=4))
    except OSError as e:
        fatal_error("Can not write results: {}".format(e.strerror))


def main(args):
    cache_path = args.cache_path if args.cache_path else Defaults.DefaultCachePath
    action_name = args.action if args.action else Defaults.DefaultActionName
    output_path = args.output if args.output else f'{action_name}.json'

    if not args.skip_check:
        log_info('Loading timetable')
        download_timetable(cache_path)
    timetable_db = shelve.open(cache_path, writeback=True)
    result = find_auditoriums_usage(timetable_db)
    log_info('Executing action')
    result = execute_action(result, action_name)
    log_info('Writing results')
    write_result(result, output_path)


if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser(description="BSUIR timetable analysis tool")
    argument_parser.add_argument('--cache-path', type=str, help='path to the cache of a timetable, default is "timetable"')
    argument_parser.add_argument('--output', type=str, help='path to the output file, default is <action>.json')
    argument_parser.add_argument('--skip-check', action='store_true', help='skip loading a timetable, use cache')
    argument_parser.add_argument('--action', type=str, help='script to run against built info, default is "represent", '+
        'the file should be placed under "actions" folder and have "action" function defined with one argument '+
        '(built timetable info will be passed as an argument)')

    args = argument_parser.parse_args()
    main(args)