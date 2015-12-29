import shelve
from collections import defaultdict
from functools import cmp_to_key

DAYS_LIST = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
TIMETABLE_CACHE_PATH = 'timetable'


def auditoriums_comparator(a, b):
    if a[1] > b[1]:
        return 1
    elif a[1] < b[1]:
        return -1
    elif a[0] > b[0]:
        return 1
    else:
        return -1


def build_auditoriums_busyness(timetable_db_path):
    timetable_db = shelve.open(timetable_db_path)

    result = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))

    for group_name in timetable_db:
        for day_timetable in timetable_db[group_name]:
            for lesson in day_timetable['lessons']:
                for week_number in lesson['week_numbers']:
                    result[lesson['auditory']][day_timetable['week_day']][week_number][
                        lesson['lesson_time']].append(group_name)

    return result


def repr_lesson_time(lesson_time):
    lesson_time = str(lesson_time)
    if len(lesson_time) == 3:
        return '0' + lesson_time[0] + ':' + lesson_time[1:]
    else:
        return lesson_time[0:2] + ':' + lesson_time[2:]


def write_result(busyness_dict, result_file):
    with open(result_file, 'w', encoding='utf-8') as f:
        for auditorium in sorted(busyness_dict.keys(), key=cmp_to_key(auditoriums_comparator)):
            f.write("{}-{}:\n".format(auditorium[0], auditorium[1]))
            for week_day in sorted(busyness_dict[auditorium], key=lambda x: DAYS_LIST.index(x)):
                f.write("\t{}:\n".format(week_day))
                for week_number in busyness_dict[auditorium][week_day]:
                    f.write("\t\tнеделя {}\n".format(week_number))
                    for lesson_time in sorted(busyness_dict[auditorium][week_day][week_number], key=lambda x: x[1]):
                        f.write("\t\t\t{} - {}\n".format(repr_lesson_time(lesson_time[0]), repr_lesson_time(lesson_time[1])))
                        for group in sorted(busyness_dict[auditorium][week_day][week_number][lesson_time]):
                            f.write("\t\t\t\tгруппа {}\n".format(group))


if __name__ == "__main__":
    write_result(build_auditoriums_busyness(TIMETABLE_CACHE_PATH), 'result.txt')
