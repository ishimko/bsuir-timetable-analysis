import xml.etree.ElementTree as ET
from urllib import request
import re
from os import path
import pickle

GROUPS_LIST_URL = r'http://www.bsuir.by/schedule/rest/studentGroup'
GROUP_TIMETABLE_URL = r'http://www.bsuir.by/schedule/rest/schedule'
DAYS_LIST = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
TIMETABLE_CACHE_PATH = 'timetable.dat'


def get_page(url):
    print('Загрузка ' + url + '...')
    return request.urlopen(url).read().decode("utf-8")


def get_group_timetable(group_id):
    return get_page(GROUP_TIMETABLE_URL + "/" + str(group_id))


def parse_auditorium(lesson_xml):
    auditory_xml = lesson_xml.find('auditory')
    if auditory_xml is not None:
        auditory_info = auditory_xml.text
    else:
        return None

    auditory_info = re.sub(r'\D', ' ', auditory_info).split()

    if len(auditory_info) != 2:
        return None

    return {'number': int(auditory_info[0]), 'building': int(auditory_info[1])}


def parse_lesson_time(lesson_xml):
    lesson_time_str = lesson_xml.find("lessonTime").text
    lesson_time_values = re.sub(r'\D', ' ', lesson_time_str).split()

    return {'start_time': int(''.join(lesson_time_values[:2])), 'end_time': int(''.join(lesson_time_values[2:4]))}


def parse_lesson_week_number(lesson_xml):
    result = []
    for week_number in lesson_xml.iter('weekNumber'):
        if int(week_number.text) != 0:
            result.append(int(week_number.text))

    return result


def parse_day_timetable(day_timetable_xml):
    result = {'week_day': day_timetable_xml.find('weekDay').text, 'lessons': []}

    for current_lesson_xml in day_timetable_xml.iter('schedule'):
        auditorium = parse_auditorium(current_lesson_xml)
        if auditorium:
            lesson = {'week_number': parse_lesson_week_number(current_lesson_xml),
                      'lesson_time': parse_lesson_time(current_lesson_xml),
                      'auditorium': auditorium}
            result['lessons'].append(lesson)

    return result


def get_all_auditoriums(full_timetable):
    result = []
    for group_timetable in full_timetable:
        for day in group_timetable['timetable'].values():
            for lesson in day:
                result.append(lesson['auditorium'])

    return result


def get_all_groups_ids():
    result = []
    groups_xml = ET.fromstring(get_page(GROUPS_LIST_URL))
    for current_group in groups_xml.iter("studentGroup"):
        result.append(current_group.find("id").text)

    return result


def parse_group_timetable(group_timetable_xml):
    result = {day: [] for day in DAYS_LIST}
    for current_day_xml in group_timetable_xml.iter('scheduleModel'):
        day_timetable = parse_day_timetable(current_day_xml)
        result[day_timetable['week_day']].extend(day_timetable['lessons'])

    return result


def load_full_timetable(groups_ids):
    groups_count = len(groups_ids)
    i = 1

    full_timetable = []

    for group_id in groups_ids:
        print(r"{}/{}".format(i, groups_count))
        group_timetable_xml = ET.fromstring(get_group_timetable(group_id))
        group_timetable = {'id': group_id, 'timetable': parse_group_timetable(group_timetable_xml)}
        full_timetable.append(group_timetable)

        i += 1

    return full_timetable


def get_full_timetable():
    if path.isfile(TIMETABLE_CACHE_PATH):
        f = open(TIMETABLE_CACHE_PATH, 'rb')
        timetable = pickle.load(f)
        f.close()
    else:
        groups_ids_list = get_all_groups_ids()
        timetable = load_full_timetable(groups_ids_list)
        f = open(TIMETABLE_CACHE_PATH, 'wb')
        pickle.dump(timetable, f)
        f.close()

    return timetable


# def get_empty_auditorium(lesson_number, week_number, building_number):



if __name__ == '__main__':
    # lesson_number = int(input('Введите номер пары: '))
    # week_number = int(intput('Введите номер недели: '))
    # building_number = int(input('Введите номер корпуса: '))
    full_timetable = get_full_timetable()
    auditoriums_list = get_all_auditoriums(full_timetable)
    for auditorium in auditoriums_list:
        print('{auditorium[number]}-{auditorium[building]}'.format(auditorium=auditorium))
