import shelve
from collections import defaultdict, OrderedDict
from helper import fatal_error, log_info
import json


def build_auditoriums_busyness(timetable_db):
    result = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))))

    for group_name in timetable_db:
        for day_timetable in timetable_db[group_name]:
            for lesson in day_timetable['lessons']:
                if 'auditory' not in lesson:
                    continue
                for week_number in lesson['week_numbers']:
                    lesson_info = result[lesson["auditory"]] \
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


def repr_employee(employee):
    if not employee:
        return 'no info'
    else:
        return '{employee[last_name]} {employee[first_name]} {employee[middle_name]}'.format(employee=employee)
