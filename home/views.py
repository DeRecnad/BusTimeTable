from django.shortcuts import render
import requests
import json

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
    url = f'https://api.rasp.yandex.net/v3.0/nearest_stations/?apikey={api_key}&format=json&lat={lat}&lng={lng}&distance=30&lang=ru_RU&limit=1000'
    response = requests.get(url)
    data = response.json()

    with open('last_request.json', 'w') as f:
        f.write(json.dumps(data, indent=5, ensure_ascii=False))

    station_names = []
    number_of_stations = data['pagination']['total']
    for i in range(number_of_stations):
        if data['stations'][i]['station_type'] == 'bus_stop':
            station_names.append(data['stations'][i]['title'])
    json.dumps(data, indent=5, ensure_ascii=False)
    return render(request, "index.html", {'station_names': station_names})
