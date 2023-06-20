from django.shortcuts import render
import requests
import json
from django.http import HttpResponse

api_key = '0ab945f6-154d-41e2-9786-202cf947d47c'
perm = {
    'type': 'settlement',
    'title': 'Пермь',
    'code': 'c50',
    'lat': 58.010259,
    'lng': 56.234195,
}


def index(request):
    lat = perm['lat']
    lng = perm['lng']
    url = f'https://api.rasp.yandex.net/v3.0/nearest_stations/?apikey={api_key}&station_types=bus_stop&format=json&lat={lat}&lng={lng}&distance=50&lang=ru_RU&limit=1000'
    response = requests.get(url)
    data = response.json()

    with open('last_request.json', 'w') as f:
        f.write(json.dumps(data, indent=5, ensure_ascii=False))

    station_names = []
    number_of_stations = data['pagination']['total']
    for i in range(number_of_stations):
        station_names.append(data['stations'][i]['title'])
    json.dumps(data, indent=5, ensure_ascii=False)
    title = ""
    first = ""
    second = ""
    codefirst = ""
    codesecond = ""
    arrival = ""
    departure = ""
    submit = 0
    interval = "—"
    if 'submit' in request.POST:
        first = request.POST.get('from', False)
        second = request.POST.get('to', False)
        submit = 1

        for i in range(number_of_stations):
            if data['stations'][i]['title'] == first:
                codefirst = data['stations'][i]['code']
            if data['stations'][i]['title'] == second:
                codesecond = data['stations'][i]['code']
        if codefirst == "" or codesecond == "":
            title = "Ничего не найдено"
            interval = ""
        else:
            url = f'https://api.rasp.yandex.net/v3.0/search/?apikey={api_key}&format=json&from={codefirst}&to={codesecond}&lang=ru_RU&page=1'
            response1 = requests.get(url)
            stop1 = response1.json()
            with open('segments.json', 'w') as f:
                f.write(json.dumps(stop1, indent=5, ensure_ascii=False))
            if stop1['segments']:
                arrival = stop1['segments'][0]['arrival'][:5]
                departure = stop1['segments'][0]['departure'][:5]
                title = stop1['segments'][0]['thread']['title']
            else:
                title = "Ничего не найдено"
                interval = ""
    print(f'{arrival}  -  {departure}')
    context = {
        'interval': interval,
        'arrival': arrival,
        'departure': departure,
        'title': title,
        'submit': submit,
        'station_names': station_names,
    }

    return render(request, "index.html", context)
