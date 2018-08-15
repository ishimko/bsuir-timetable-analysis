import json
import argparse
from helper import fatal_error, log_info
from downloader import download_timetable
import shelve
from busyness_info_builder import build_auditoriums_busyness
from importlib import import_module


def execute_action(busyness, action_name, output_path):
    action_module = import_module(action_name)
    action_func = getattr(action_module, 'action')
    result = action_func(busyness)
    return result


def write_result(obj, result_file):
    try:
        log_info('Writing results\n')
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
    if args.action:
        result = execute_action(result, args.action, args.output_path)
    else:
        result = result
    log_info('Executing action')
    write_result(result, args.output_path)


if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser(description="BSUIR timetable analysis util")
    argument_parser.add_argument('cache_path', metavar='cache-path', type=str, help='path to the cache of a timetable')
    argument_parser.add_argument('output_path', metavar='output_path', type=str, help='path to the output file')
    argument_parser.add_argument('--skip-check', action='store_true', help='skip loading a timetable, use cache')
    argument_parser.add_argument('--action', type=str, help='script to run against built info')

    args = argument_parser.parse_args()
    main(args)