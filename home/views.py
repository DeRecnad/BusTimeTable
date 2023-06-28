from django.shortcuts import render
import requests
import json
import datetime

api_key = '0ab945f6-154d-41e2-9786-202cf947d47c'
perm = {
    'type': 'settlement',
    'title': 'Пермь',
    'code': 'c50',
    'lat': 58.010259,
    'lng': 56.234195,
}


def get_data(url):
    response = requests.get(url)
    data = response.json()
    with open('logs/log1.json', 'w') as f:
        f.write('{' + f'"URL": "{url}",\n"data": ')
        f.write(json.dumps(data, indent=5, ensure_ascii=False))
        f.write('\n}')
    f.close()
    return data


def get_station_names(url):
    data = get_data(url)
    station_names = []
    number_of_stations = data['pagination']['total']
    for i in range(number_of_stations):
        station_names.append(data['stations'][i]['title'] + ', ' + data['stations'][i]['station_type_name'])
    return station_names


def index(request):
    lat = perm['lat']
    lng = perm['lng']
    url = f'https://api.rasp.yandex.net/v3.0/nearest_stations/?apikey={api_key}&transport_types=train,suburban,bus&format=json&lat={lat}&lng={lng}&distance=50&lang=ru_RU&limit=1000'
    station_names = get_station_names(url)
    submit = 0
    print(request.POST)
    codefrom = codeto = From = To = Date = Time = ''
    Sent = []
    if 'submit1' in request.POST:
        submit = 1
        checked = ['', '', '']
        if 'btncheck1' in request.POST:
            checked[0] = 'bus'
        if 'btncheck2' in request.POST:
            checked[1] = 'suburban'
        if 'btncheck3' in request.POST:
            checked[2] = 'train'
        url = f'https://api.rasp.yandex.net/v3.0/nearest_stations/?apikey={api_key}&transport_types={",".join(checked)}&format=json&lat={lat}&lng={lng}&distance=50&lang=ru_RU&limit=1000'
        data = get_data(url)
        with open('logs/log2.json', 'w') as f:
            f.write('{' + f'"URL": "{url}",\n"data": ')
            f.write(json.dumps(data, indent=5, ensure_ascii=False))
            f.write('\n}')
        f.close()
        From = request.POST.get('from', False)
        To = request.POST.get('to', False)
        Date = request.POST.get('date')
        Time = request.POST.get('time')
        if Time == '':
            Time = str(datetime.datetime.now().time())[:5]
        print(From, To, Date, Time)
        for i in range(data['pagination']['total']):
            if (data['stations'][i]['title'] + ', ' + data['stations'][i]['station_type_name']) == From:
                codefrom = data['stations'][i]['code']
            if (data['stations'][i]['title'] + ', ' + data['stations'][i]['station_type_name']) == To:
                codeto = data['stations'][i]['code']
        url = f'https://api.rasp.yandex.net/v3.0/search/?apikey={api_key}&format=json&from={codefrom}&to={codeto}&lang=ru_RU&page=1&transport_types={",".join(checked)}&date={Date}&limit=10000'
        transfers = get_data(url)
        with open('logs/log3.json', 'w') as f:
            f.write('{' + f'"URL": "{url}",\n"data": ')
            f.write(json.dumps(transfers, indent=5, ensure_ascii=False))
            f.write('\n}')
        f.close()
        try:
            total = transfers['pagination']['total']
            if total != 0 and (checked[0] != '' or checked[1] != '' or checked[2] != ''):
                if Date == '':
                    for i in range(total):
                        temp = []
                        if datetime.time(int(transfers['segments'][i]['departure'][0:2]), int(transfers['segments'][i]['departure'][3:5])) > datetime.time(int(Time[0:2]), int(Time[3:5])):
                            temp.append(transfers['segments'][i]['arrival'][0:5])
                            temp.append(transfers['segments'][i]['departure'][0:5])
                            temp.append(transfers['segments'][i]['start_date'])
                            temp.append(transfers['segments'][i]['thread']['title'])
                            temp.append(str(datetime.datetime(1, 1, 1, int(transfers['segments'][i]['arrival'][0:2]), int(transfers['segments'][i]['arrival'][3:5])) - datetime.datetime(1, 1, 1, int(transfers['segments'][i]['departure'][0:2]), int(transfers['segments'][i]['departure'][3:5])))[0:4]+'')
                            temp.append(transfers['segments'][i]['thread']['transport_type'])
                            Sent.append(temp)
                else:
                    for i in range(total):
                        temp = []
                        if datetime.time(int(transfers['segments'][i]['departure'][11:13]), int(transfers['segments'][i]['departure'][14:16])) > datetime.time(int(Time[0:2]), int(Time[3:5])):
                            temp.append(transfers['segments'][i]['arrival'][11:16])
                            temp.append(transfers['segments'][i]['departure'][11:16])
                            temp.append(transfers['segments'][i]['start_date'])
                            temp.append(transfers['segments'][i]['thread']['title'])
                            temp.append(str(datetime.datetime(1, 1, 1, int(transfers['segments'][i]['arrival'][11:13]), int(transfers['segments'][i]['arrival'][14:16])) - datetime.datetime(1, 1, 1, int(transfers['segments'][i]['departure'][11:13]), int(transfers['segments'][i]['departure'][14:16])))[0:4]+'')
                            temp.append(transfers['segments'][i]['thread']['transport_type'])
                            Sent.append(temp)
            else:
                Sent = [['', '', 'Ничего не найдено', '', '', '']]
        except:
            Sent = [['', '', 'Ничего не найдено', '', '', '']]
    context = {
        'sent': Sent,
        'submit': submit,
        'station_names': station_names,
    }
    return render(request, "index.html", context)
