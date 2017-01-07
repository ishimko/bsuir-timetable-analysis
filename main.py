import argparse
from helper import press_enter
from downloader import download_timetable
from busyness_info_builder import build_auditoriums_busyness, write_result

if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser(description="Building BSUIR auditoriums' busyness info")
    argument_parser.add_argument('cache_path', type=str, help='path to the cache for the loading timetable')
    argument_parser.add_argument('output_path', type=str, help='path to the output file')
    args = argument_parser.parse_args()

    download_timetable(args.cache_path)
    write_result(build_auditoriums_busyness(args.cache_path), args.output_path)

    press_enter()
