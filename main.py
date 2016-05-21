import sys
from helper import fatal_error, press_enter
from downloader import download_timetable
from busyness_info_builder import build_auditoriums_busyness, write_result

if __name__ == '__main__':
    if len(sys.argv) != 3:
        fatal_error("Недостаточно параметров!")

    timetable_cache_path = sys.argv[1]
    result_file_path = sys.argv[2]

    download_timetable(timetable_cache_path)
    write_result(build_auditoriums_busyness(timetable_cache_path), result_file_path)

    press_enter()
