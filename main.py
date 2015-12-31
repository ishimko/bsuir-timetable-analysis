import shelve
import sys
from collections import defaultdict
from downloader import download_timetable
from helper import log_error, press_enter


def build_auditoriums_busyness(timetable_db_path):
    print('Обработка расписания...')

    timetable_db = shelve.open(timetable_db_path)

    result = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))))

    for group_name in timetable_db:
        for day_timetable in timetable_db[group_name]:
            for lesson in day_timetable['lessons']:
                if 'auditory' not in lesson:
                    continue
                for week_number in lesson['week_numbers']:
                    lesson_info = result[lesson['auditory']] \
                        [day_timetable['week_day']] \
                        [week_number] \
                        [lesson['lesson_time']]

                    lesson_info['groups'].append(group_name)
                    lesson_info['employee'] = lesson['employee']
                    lesson_info['subject'] = lesson['subject']

    return result


def repr_lesson_time(lesson_time):
    time_str_list = []
    for time in lesson_time:
        time_str = str(time)
        if len(time_str) == 3:
            time_str_list.append('0' + time_str[0] + ':' + time_str[1:])
        else:
            time_str_list.append(time_str[0:2] + ':' + time_str[2:])

    return ' - '.join(time_str_list)


def repr_employee(employee_dict):
    if not employee_dict:
        return 'нет информации'
    else:
        return '{employee[last_name]} {employee[first_name]} {employee[middle_name]}'.format(employee=employee_dict)


def write_result(busyness_dict, result_file):
    days_list = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']

    try:
        print('Запись результата...\n')
        f = open(result_file, 'w', encoding='utf-8')

        for auditorium in sorted(busyness_dict.keys(), key=lambda x: (x[1], x[0])):
            f.write('{}-{}:\n'.format(auditorium[0], auditorium[1]))
            for week_day in sorted(busyness_dict[auditorium], key=lambda x: days_list.index(x)):
                f.write('\t{}:\n'.format(week_day))
                for week_number in busyness_dict[auditorium][week_day]:
                    f.write('\t\tнеделя {}\n'.format(week_number))
                    for lesson_time in sorted(busyness_dict[auditorium][week_day][week_number], key=lambda x: x[1]):
                        lesson_info = busyness_dict[auditorium][week_day][week_number][lesson_time]

                        f.write('\t' * 3 + '{}\n'.format(repr_lesson_time(lesson_time)))
                        f.write('\t' * 4 + 'предмет: {}\n'.format(lesson_info['subject']))
                        f.write('\t' * 4 + 'преподаватель: {}\n\n'.format(repr_employee(lesson_info['employee'])))

                        for group in sorted(lesson_info['groups']):
                            f.write('\t' * 4 + 'группа {}\n'.format(group))
    except OSError as e:
        log_error("Невозможно записать результат: {}".format(e.strerror))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        log_error("Недостаточно параметров!")

    timetable_cache_path = sys.argv[1]
    result_file_path = sys.argv[2]

    download_timetable(timetable_cache_path)
    write_result(build_auditoriums_busyness(timetable_cache_path), result_file_path)

    press_enter()
