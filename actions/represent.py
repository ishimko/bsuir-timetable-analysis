def action(result):
    return to_representable(result)


def to_representable(auditoriums_usage):
    result = []
    days_list = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    for auditorium in sorted(auditoriums_usage.keys(), key=lambda x: (x[1], x[0])):
        week_days = []
        result.append({f'{auditorium[0]}-{auditorium[1]}': week_days})
        for week_day in sorted(auditoriums_usage[auditorium], key=lambda x: days_list.index(x)):
            week_numbers = []
            week_days.append({week_day: week_numbers})
            for week_number in auditoriums_usage[auditorium][week_day]:
                lessons = []
                week_numbers.append({week_number: lessons})
                for lesson_time in sorted(auditoriums_usage[auditorium][week_day][week_number], key=lambda x: x[1]):
                    lesson_info = auditoriums_usage[auditorium][week_day][week_number][lesson_time]
                    lesson_info['groups'] = sorted(lesson_info['groups'])
                    lesson_info['employee'] = ' '.join(lesson_info['employee'].values())
                    lessons.append({f'{lesson_time[0]}-{lesson_time[1]}': lesson_info})

    return result