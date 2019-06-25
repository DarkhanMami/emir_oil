from main import models
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from django.http import HttpResponse
from django.db.models import Q
from main.serializers import NewsKZJsonSerializer


@login_required(login_url='/admin/')
def index(request):
    with open('json_data/main.json') as json_file:
        params = json.load(json_file)

    return render(request, "report.html", params)


@login_required(login_url='/admin/')
def feedback(request):
    # with open('json_data/feedback.json') as json_file:
    #     params = json.load(json_file)
    #
    # return render(request, "report.html", params)
    items = models.Feedback.objects.all().values()
    types = ['Автор', 'Контакты', 'Место жительства', 'Вид деятельности', 'Тип', 'Текст']
    params = dict()
    result = []
    for item in items:
        temp = [item['author'], item['contact'], item['location'], item['career'], item['wish_type'], item['body']]
        result.append(temp)
    params['data'] = result
    params['types'] = types
    return render(request, "feedback.html", {'params' : params})


@login_required(login_url='/admin/')
def generate_main_json(request):
    items = models.Feedback.objects.all().values()
    params = dict()
    result = dict()

    params['data'] = []
    params['types'] = []
    types = []

    locs = ['г. Нур-Султан', 'г. Алматы', 'г. Шымкент', 'Акмолинская', 'Актюбинская', 'Алматинская', 'Атырауская',
            'Восточно-Казахстанская', 'Жамбылская', 'Западно-Казахстанская', 'Карагандинская', 'Костанайская',
            'Кызылординская', 'Мангистауская', 'Павлодарская', 'Северо-Казахстанская', 'Туркестанская', 'Другое']

    its = models.Feedback.objects.order_by().values('wish_type').distinct()
    for item in its:
        if item['wish_type'] not in types:
            types.append(item['wish_type'])

    types.append('Всего')
    result['Всего'] = [0 for i in range(len(types))]

    for item in items:
        location = item['location'].split('/')[0].replace(" ", "")
        location = location.split(',')[0].replace(" ", "")
        if "Нур-Султан" in location or "Нұр-Сұлтан" in location or "Нур-Слтан" in location or "Нур-Сулан" in location \
                or "НУР-СУЛТАН" in location or "нур-Султан" in location or "Нур-СУлтан" in location:
            location = "г. Нур-Султан"
        elif "Атырау" in location:
            location = "Атырауская"
        elif "Мангистау" in location or "мангистау" in location or "Магистау" in location or "Манғыстау" in location \
                or "Маңғыстау" in location:
            location = "Мангистауская"

        elif "Павлодар" in location:
            location = "Павлодарская"
        elif "Северо-Казахстанская" in location:
            location = "Северо-Казахстанская"
        elif "Жамбыл" in location:
            location = "Жамбылская"
        elif "Батыс" in location:
            location = "Западно-Казахстанская"
        elif "Алматық." in location or "г.Алматы" in location:
            location = "г. Алматы"
        elif "Алматыоблысы" in location:
            location = "Алматинская"
        elif "Актобе" in location or "Ақтөбе" in location:
            location = "Актюбинская"
        elif "Ақмолаоблысы" in location:
            location = "Акмолинская"
        elif "СолтүстікҚазақстаноблысы" in location:
            location = "Северо-Казахстанская"
        elif "Түркістаноблысы" in location:
            location = "Туркестанская"
        elif "Шымкентқ." in location or "г.Шымкент" in location:
            location = "г. Шымкент"
        elif "Шығыс" in location:
            location = "Восточно-Казахстанская"
        elif "Қарағанды" in location:
            location = "Карагандинская"
        elif "Қостанай" in location:
            location = "Костанайская"
        elif "Қызылорда" in location:
            location = "Кызылординская"
        else:
            location = 'Другое'

        if location in locs:
            if location not in result:
                result[location] = [0 for i in range(len(types))]

            ind = types.index(item['wish_type'])
            result[location][ind] += 1
            result[location][-1] += 1
            result['Всего'][ind] += 1
            result['Всего'][-1] += 1

    for loc in result:
        params['data'].append([loc] + result[loc])

    params['types'] = types

    with open('json_data/main.json', 'w') as f:
        f.write(json.dumps({'params' : params}))

    return HttpResponse("OK")


@login_required(login_url='/admin/')
def generate_birge_data2(request):
    params = dict()
    result = dict()
    params['data'] = []

    locs = ['г. Нур-Султан', 'г. Алматы', 'г. Шымкент', 'Акмолинская', 'Актюбинская', 'Алматинская', 'Атырауская',
            'Восточно-Казахстанская', 'Жамбылская', 'Западно-Казахстанская', 'Карагандинская', 'Костанайская',
            'Кызылординская', 'Мангистауская', 'Павлодарская', 'Северо-Казахстанская', 'Туркестанская']

    for loc in locs:
        result[loc] = []
        if loc == 'г. Нур-Султан':
            result[loc].append(models.Feedback.objects.filter(Q(location__contains='Нур-Султан')
                                                              | Q(location__contains='Нұр-Сұлтан')).count())
        elif loc == 'г. Алматы':
            result[loc].append(models.Feedback.objects.filter(Q(location__contains=loc)
                                                              | Q(location__contains='Алматы қ')).count())
        elif loc == 'Павлодарская':
            result[loc].append((models.Feedback.objects.filter(location__contains='Павлодар')).count())
        elif loc == 'Мангистауская':
            result[loc].append(models.Feedback.objects.filter(Q(location__contains='Мангистау')
                                                              | Q(location__contains='Магистау')
                                                              | Q(location__contains='Манғыстау')
                                                              | Q(location__contains='Маңғыстау')).count())
        elif loc == 'Актюбинская':
            result[loc].append(models.Feedback.objects.filter(Q(location__contains=loc)
                                                              | Q(location__contains='Актобе')
                                                              | Q(location__contains='Ақтөбе')).count())
        elif loc == 'Западно-Казахстанская':
            result[loc].append((models.Feedback.objects.filter(location__contains=loc)).count())
            result[loc][0] += (models.Feedback.objects.filter(location__contains='Батыс').count())
        elif loc == 'Северо-Казахстанская':
            result[loc].append((models.Feedback.objects.filter(location__contains=loc)).count())
            result[loc][0] += (models.Feedback.objects.filter(location__contains='Солтүстік Қазақстан облысы').count())
        elif loc == 'Алматинская':
            result[loc].append((models.Feedback.objects.filter(location__contains=loc)).count())
            result[loc][0] += (models.Feedback.objects.filter(location__contains='Алматы облысы').count())
        elif loc == 'Кызылординская':
            result[loc].append((models.Feedback.objects.filter(location__contains=loc)).count())
            result[loc][0] += (models.Feedback.objects.filter(location__contains='Қызылорда').count())
        elif loc == 'Костанайская':
            result[loc].append((models.Feedback.objects.filter(location__contains=loc)).count())
            result[loc][0] += (models.Feedback.objects.filter(location__contains='Қостанай').count())
        elif loc == 'Карагандинская':
            result[loc].append((models.Feedback.objects.filter(location__contains=loc)).count())
            result[loc][0] += (models.Feedback.objects.filter(location__contains='Қарағанды').count())
        elif loc == 'Восточно-Казахстанская':
            result[loc].append((models.Feedback.objects.filter(location__contains=loc)).count())
            result[loc][0] += (models.Feedback.objects.filter(location__contains='Шығыс').count())
        elif loc == 'Туркестанская':
            result[loc].append((models.Feedback.objects.filter(location__contains=loc)).count())
            result[loc][0] += (models.Feedback.objects.filter(location__contains='Түркістан облысы').count())
        elif loc == 'г. Шымкент':
            result[loc].append((models.Feedback.objects.filter(location__contains='Шымкент')).count())
        elif loc == 'Жамбылская':
            result[loc].append((models.Feedback.objects.filter(location__contains='Жамбыл')).count())
        elif loc == 'Павлодарская':
            result[loc].append((models.Feedback.objects.filter(location__contains='Павлодар')).count())
        elif loc == 'Атырауская':
            result[loc].append((models.Feedback.objects.filter(location__contains='Атырау')).count())
        else:
            result[loc].append((models.Feedback.objects.filter(location__contains=loc)).count())
    total = 0
    for loc in result:
        total += result[loc][0]
        params['data'].append([loc] + result[loc])
    params['data'].append(['Всего'] + [total])
    with open('json_data/birge.json', 'w') as f:
        f.write(json.dumps({'params' : params}))

    return HttpResponse("OK")


@login_required(login_url='/admin/')
def generate_birge_data(request):
    params = dict()
    result = dict()
    params['data'] = []

    with open('json_data/main.json') as json_file:
        data = json.load(json_file)

    items = data['params']['data']

    locs = ['г. Нур-Султан', 'г. Алматы', 'г. Шымкент', 'Акмолинская', 'Актюбинская', 'Алматинская', 'Атырауская',
            'Восточно-Казахстанская', 'Жамбылская', 'Западно-Казахстанская', 'Карагандинская', 'Костанайская',
            'Кызылординская', 'Мангистауская', 'Павлодарская', 'Северо-Казахстанская', 'Туркестанская', 'Всего']

    for loc in locs:
        for item in items:
            if item[0] == loc:
                params['data'].append([item[0]] + [item[-1]])

    with open('json_data/birge.json', 'w') as f:
        f.write(json.dumps({'params' : params}))

    return HttpResponse("OK")


@login_required(login_url='/admin/')
def generate_kz_news(request):
    params = NewsKZJsonSerializer(models.NewsKZ.objects.all().order_by('-timestamp'), many=True)
    with open('json_data/kz_news.json', 'w') as f:
        f.write(json.dumps(params.data))

    return HttpResponse("OK")