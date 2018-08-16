import json
import argparse
from helper import fatal_error, log_info
from downloader import download_timetable
import shelve
from busyness_info_builder import build_auditoriums_busyness
from importlib import import_module


DEFAULT_ACTION_NAME = 'represent'


def execute_action(busyness, action_name):
    action_module = import_module(action_name)
    action_func = getattr(action_module, 'action')
    result = action_func(busyness)
    return result


def write_result(obj, result_file):
    try:
        f = open(result_file, 'w', encoding='utf-8')
        f.write(json.dumps(obj, ensure_ascii=False, indent=4))
    except OSError as e:
        fatal_error("Can not write results: {}".format(e.strerror))


def main(args):
    if not args.skip_check:
        log_info('Loading timetable')
        download_timetable(args.cache_path)
    timetable_db = shelve.open(args.cache_path, writeback=True)
    result = build_auditoriums_busyness(timetable_db)
    action_name = args.action if args.action else DEFAULT_ACTION_NAME
    output_path = args.output if args.output else f'{action_name}.json'
    log_info('Executing action')
    result = execute_action(result, action_name)
    log_info('Writing results')
    write_result(result, output_path)


if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser(description="BSUIR timetable analysis util")
    argument_parser.add_argument('cache_path', metavar='cache-path', type=str, help='path to the cache of a timetable')
    argument_parser.add_argument('--output', type=str, help='path to the output file, default is <action>.json')
    argument_parser.add_argument('--skip-check', action='store_true', help='skip loading a timetable, use cache')
    argument_parser.add_argument('--action', type=str, help='script to run against built info, default is "represent"')

    args = argument_parser.parse_args()
    main(args)