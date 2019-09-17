from main import models
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from django.http import HttpResponse
from django.db.models import Q
from main.serializers import ProductionSerializer, ParkProductionSerializer


@login_required(login_url='/admin/')
def index(request):
    with open('json_data/main.json') as json_file:
        params = json.load(json_file)

    return render(request, "report.html", params)


@login_required(login_url='/admin/')
def generate_production(request):
    params = ProductionSerializer(models.Production.objects.all(), many=True)
    with open('json_data/production.json', 'w') as f:
        f.write(json.dumps(params.data))

    return HttpResponse("OK")


@login_required(login_url='/admin/')
def generate_park_production(request):
    params = ParkProductionSerializer(models.ParkProduction.objects.all(), many=True)
    with open('json_data/park_production.json', 'w') as f:
        f.write(json.dumps(params.data))

    return HttpResponse("OK")