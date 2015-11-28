import xml.etree.ElementTree as ET
from urllib import request
import re
from os import path
import pickle
from functools import cmp_to_key
from datetime import datetime

GROUPS_LIST_URL = r'http://www.bsuir.by/schedule/rest/studentGroup'
GROUP_TIMETABLE_URL = r'http://www.bsuir.by/schedule/rest/schedule'
BSUIR_MAIN_PAGE = r'http://www.bsuir.by/'
DAYS_LIST = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
TIMETABLE_CACHE_PATH = 'timetable.dat'
LESSONS_TIME = {
    1: {'start_time': 800, 'end_time': 935},
    2: {'start_time': 945, 'end_time': 1120},
    3: {'start_time': 1140, 'end_time': 1315},
    4: {'start_time': 1325, 'end_time': 1500},
    5: {'start_time': 1520, 'end_time': 1655},
    6: {'start_time': 1705, 'end_time': 1840}
}


def get_page(url):
    print('Загрузка ' + url + '...')
    return request.urlopen(url).read().decode('1251')


def get_group_timetable(group_id):
    return get_page(GROUP_TIMETABLE_URL + "/" + str(group_id))


def parse_auditorium(lesson_xml):
    auditorium_xml = lesson_xml.find('auditory')
    if auditorium_xml is not None:
        auditorium_info = auditorium_xml.text
    else:
        return None

    auditorium_info = re.sub(r'\D', ' ', auditorium_info).split()

    if len(auditorium_info) != 2:
        return None

    return int(auditorium_info[0]), int(auditorium_info[1])


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
            lesson = {'week_numbers': parse_lesson_week_number(current_lesson_xml),
                      'lesson_time': parse_lesson_time(current_lesson_xml),
                      'auditorium': auditorium}
            result['lessons'].append(lesson)

    return result


def get_all_auditoriums(full_timetable):
    result = set()
    for group_timetable in full_timetable:
        for day in group_timetable['timetable'].values():
            for lesson in day:
                result.add(lesson['auditorium'])

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


def get_empty_auditorium(lesson_number, week_number, day, building_numbers, full_auditoriums, full_timetable):
    if building_numbers[0] != 0:
        empty_auditoriums = set(filter(lambda x: x[1] in building_numbers, full_auditoriums))
    else:
        empty_auditoriums = full_auditoriums

    for group_timetable in full_timetable:
        for current_day_name in group_timetable['timetable']:
            if day.lower() == current_day_name.lower():
                current_day = group_timetable['timetable'][current_day_name]
                for lesson in current_day:
                    if week_number in lesson['week_numbers'] and \
                            lesson['lesson_time']['start_time'] <= LESSONS_TIME[lesson_number]['start_time'] and \
                            lesson['lesson_time']['end_time'] >= LESSONS_TIME[lesson_number]['end_time']:
                        empty_auditoriums.discard(lesson['auditorium'])
    return empty_auditoriums


def auditoriums_comparator(a, b):
    if a[1] > b[1]:
        return 1
    elif a[1] < b[1]:
        return -1
    elif a[0] > b[0]:
        return 1
    else:
        return -1


def get_current_week_number():
    return int(re.search(r'(\d)\s+учебная неделя', get_page(BSUIR_MAIN_PAGE)).group(1))


def get_current_week_day():
    return DAYS_LIST[datetime.now().weekday()]


def print_result(auditoriums_list):
    for auditorium in auditoriums_list:
        print('{auditorium[0]}-{auditorium[1]}'.format(auditorium=auditorium))


if __name__ == '__main__':
    isToday = input(r'Сегодня? (yes/no): ') == 'yes'

    lesson_number = int(input('Введите номер пары: '))
    building_numbers = [int(x) for x in input('Введите номер(а) корпусов (0 - все корпуса): ').split()]

    if isToday:
        week_number = get_current_week_number()
        day = get_current_week_day()
        print('{} учебная неделя, {}'.format(week_number, day))
    else:
        week_number = int(input('Введите номер недели: '))
        day = input('Введите день недели: ')

    full_timetable = get_full_timetable()
    auditoriums_list = get_all_auditoriums(full_timetable)
    empty_auditoriums = get_empty_auditorium(lesson_number, week_number, day, building_numbers, auditoriums_list,
                                             full_timetable)
    empty_auditoriums_list = sorted(empty_auditoriums, key=cmp_to_key(auditoriums_comparator))
    print_result(empty_auditoriums_list)
