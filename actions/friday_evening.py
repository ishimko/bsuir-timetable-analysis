def action(result):
    filtered_results = { x: {'18:45': [], '20:25': []} for x in (1, 3)}
    for auditorium, timetable in filter(lambda x: x[0][1] in (4, 5) and str(x[0][0])[0] == '2', result.items()):
        for week_number, week_result in filtered_results.items():
            lessons = timetable['Пятница'][week_number].keys()
            for t in week_result.keys():
                if t not in map(lambda x: x[0], lessons):
                    week_result[t].append(f'{auditorium[0]}-{auditorium[1]}')
    return filtered_results
