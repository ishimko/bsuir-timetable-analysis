import re
import shelve
import urllib
import xml.etree.ElementTree as ET
from urllib import request, error

from helper import fatal_error, log_info

GROUPS_LIST_URL = r'http://www.bsuir.by/schedule/rest/studentGroup'
GROUP_TIMETABLE_URL = r'http://www.bsuir.by/schedule/rest/schedule'

TOTAL_DECS = 'Всего групп'
LOADED_DECS = 'Загружено'


def parse_auditory(lesson):
    auditory_xml = lesson.find('auditory')
    if auditory_xml is not None:
        auditory_info = auditory_xml.text
    else:
        return None

    auditory_info = re.sub(r'\D', ' ', auditory_info).split()

    if len(auditory_info) != 2:
        return None

    return int(auditory_info[0]), int(auditory_info[1])


def parse_lesson_time(lesson):
    lesson_time_str = lesson.find('lessonTime').text
    lesson_time_values = re.sub(r'\D', ' ', lesson_time_str).split()

    return int(''.join(lesson_time_values[:2])), int(''.join(lesson_time_values[2:4]))


def parse_lesson_week_number(lesson):
    result = []
    for week_number in lesson.iter('weekNumber'):
        if int(week_number.text) != 0:
            result.append(int(week_number.text))

    return result


def parse_group_timetable(group_timetable):
    result = []
    for current_day_xml in group_timetable.iter('scheduleModel'):
        day_timetable = parse_day_timetable(current_day_xml)
        result.append(day_timetable)

    return result


def parse_employee(lesson):
    employee = lesson.find('employee')
    if employee is not None:
        return {'first_name': employee.find('firstName').text,
                'middle_name': employee.find('middleName').text,
                'last_name': employee.find('lastName').text}
    else:
        return {}


def parse_day_timetable(day_timetable_xml):
    result = {'week_day': day_timetable_xml.find('weekDay').text, 'lessons': []}

    for current_lesson_xml in day_timetable_xml.iter('schedule'):
        lesson = {'week_numbers': parse_lesson_week_number(current_lesson_xml),
                  'lesson_time': parse_lesson_time(current_lesson_xml),
                  'employee': parse_employee(current_lesson_xml),
                  'subject': current_lesson_xml.find('subject').text}
        auditory = parse_auditory(current_lesson_xml)
        if auditory:
            lesson['auditory'] = auditory

        result['lessons'].append(lesson)

    return result


def load_group_timetable(group_id):
    return get_page(GROUP_TIMETABLE_URL + '/' + str(group_id))


def get_page(url):
    log_info('Загрузка ' + url + '...')
    return request.urlopen(url).read()


def get_all_groups():
    log_info("Получение списка групп с расписанием...")

    result = []
    groups_xml = ET.fromstring(get_page(GROUPS_LIST_URL))
    for current_group in groups_xml.iter('studentGroup'):
        result.append((current_group.find('id').text, current_group.find('name').text))

    return result


def download_timetable(cache_path):
    try:
        timetable_db = shelve.open(cache_path, writeback=True)
    except OSError as e:
        fatal_error("Не удалось использовать базу: {}".format(e.strerror))
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
            timetable_db[group_name] = parse_group_timetable(ET.fromstring(load_group_timetable(group_id)))
            loaded_number += 1
    except (ConnectionError, TimeoutError, urllib.error.HTTPError, urllib.error.URLError):
        fatal_error('Невозможно загрузить данные. Проверьте соединение с интернетом!')
    finally:
        timetable_db.close()
