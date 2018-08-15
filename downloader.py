import re
import shelve
import urllib
import json
from urllib import request, error

from helper import fatal_error, log_info

GROUPS_LIST_URL = r'https://students.bsuir.by/api/v1/groups'
GROUP_TIMETABLE_URL = r'https://students.bsuir.by/api/v1/studentGroup/schedule?id={}'

TOTAL_DECS = 'Total'
LOADED_DECS = 'Loaded'


def parse_auditory(lesson):
    auditory = lesson['auditory']
    if auditory:
        auditory_str = auditory[0]
    else:
        return None

    auditory_str = re.sub(r'\D', ' ', auditory_str).split()

    if len(auditory_str) != 2:
        return None

    return int(auditory_str[0]), int(auditory_str[1])


def parse_lesson_time(lesson):
    return lesson['startLessonTime'], lesson['endLessonTime']


def parse_lesson_week_number(lesson):
    result = []
    for week_number in lesson['weekNumber']:
        if int(week_number) != 0:
            result.append(int(week_number))

    return result


def parse_group_timetable(group_timetable):
    result = []
    for current_day in group_timetable['schedules']:
        day_timetable = parse_day_timetable(current_day)
        result.append(day_timetable)

    return result


def parse_employee(lesson):
    employee = lesson['employee']
    if employee:
        employee = employee[0]
        return {
            'first_name': employee['firstName'],
            'middle_name': employee['middleName'],
            'last_name': employee['lastName']
        }
    else:
        return {}


def parse_day_timetable(day_timetable):
    result = {'week_day': day_timetable['weekDay'], 'lessons': []}

    for current_lesson in day_timetable['schedule']:
        lesson = {'week_numbers': parse_lesson_week_number(current_lesson),
                  'lesson_time': parse_lesson_time(current_lesson),
                  'employee': parse_employee(current_lesson),
                  'subject': current_lesson['subject']}
        auditory = parse_auditory(current_lesson)
        if auditory:
            lesson['auditory'] = auditory

        result['lessons'].append(lesson)

    return result


def load_group_timetable(group_id):
    try:
        return get_page(GROUP_TIMETABLE_URL.format(group_id))
    except urllib.error.HTTPError:
        return None


def get_page(url):
    log_info('Loading ' + url)
    return request.urlopen(url).read()


def get_all_groups():
    log_info("Loading groups list")

    result = []
    response_string = get_page(GROUPS_LIST_URL)
    groups = json.loads(response_string)
    for current_group in groups:
        result.append((current_group['id'], current_group['name']))

    return result


def download_timetable(cache_path):
    try:
        timetable_db = shelve.open(cache_path, writeback=True)
    except OSError as e:
        fatal_error("Can not open local db: {}".format(e.strerror))
        return

    try:
        groups = sorted(get_all_groups(), key=lambda x: x[1])
        total_number = len(groups)
        log_info('{} - {}'.format(TOTAL_DECS, total_number))

        loaded_number = [x[1] for x in groups].index(max(timetable_db.keys())) + 1 if len(timetable_db) else 0
        log_info('{} - {}'.format(LOADED_DECS.rjust(len(TOTAL_DECS)), str(loaded_number).rjust(len(str(total_number)))))

        groups = groups[loaded_number:]

        for group_id, group_name in groups:
            log_info(r'{}/{}'.format(str(loaded_number + 1).rjust(len(str(total_number))), total_number))
            response_string = load_group_timetable(group_id)
            if response_string:
                timetable_json = json.loads(response_string)
                timetable_db[group_name] = parse_group_timetable(timetable_json)
            else:
                log_info(f'Unable to load a timetable for the group {group_name}, skipping')
            loaded_number += 1
    except (ConnectionError, TimeoutError, urllib.error.URLError):
        fatal_error('Connection error')
    finally:
        timetable_db.close()
