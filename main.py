import xml.etree.ElementTree as ET
from urllib import request
import re

GROUPS_LIST_URL = "http://www.bsuir.by/schedule/rest/studentGroup"
LECTURERS_LIST_URL = "http://www.bsuir.by/schedule/rest/employee"


def get_page(url):
    print("Загружаю " + url + "...")
    return request.urlopen(url).read().decode("utf-8")


def get_lecturer_timetable(lecturer_id):
    return get_page(LECTURERS_LIST_URL + "/" + str(lecturer_id))


def get_group_timetable(group_id):
    return get_page(GROUPS_LIST_URL + "/" + str(group_id))


def parse_auditory(lesson_xml):
    auditory_xml = lesson_xml.find("auditory")
    if auditory_xml:
        auditory_str = auditory_xml.text
    else:
        return None

    result = {}
    auditory_str = re.sub(r"\D", " ", auditory_str).split()
    result['number'] = int(auditory_str[0])
    result['building'] = int(auditory_str[1])

    return result


def parse_lesson_time(lesson_xml):
    lesson_time_str = lesson_xml.find("lessonTime").text
    lesson_time_values = re.sub(r"\D", " ", lesson_time_str).split()

    return {"start_time": int(''.join(lesson_time_values[:2])), "end_time": int(''.join(lesson_time_values[2:4]))}


def parse_lesson_week_number(lesson_xml):
    result = []
    for week_number in lesson_xml.iter("weekNumber"):
        if int(week_number.text) != 0:
            result.append(int(week_number.text))

    return result

def get_all_auditories(groups_timetables_list):
    result = []
    for group_timetable in groups_timetables_list:
        auditory = group_timetable
        result.append(parse_auditory(group_timetable))


def parse_group_info(group_xml):
    return {'number': group_xml.find("name").text, 'id': int(group_xml.find["id"].text)}




if __name__ == '__main__':
    lesson_number = int(input("Введите номер пары: "))
    for schedule_model in xml.findall("scheduleModel"):
        print(schedule_model.find("weekNumber").text)

