from main import models
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from django.http import HttpResponse
from django.db.models import Q
from main.serializers import ProductionSerializer, ParkProductionSerializer
import poplib
import email
from email.parser import Parser
import os


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


@login_required(login_url='/admin/')
def get_mail_report(request):
    DIR = "/Users/darik/linux/EmirOil/"
    subject = 'Emir, welcome to your new Google Account'
    SERVER = 'pop.gmail.com'
    USER = 'emir.report@gmail.com'
    PASSWORD = 'Qw0zxc13TteD'
    server = poplib.POP3_SSL(SERVER)
    server.user(USER)
    server.pass_(PASSWORD)
    resp, items, octets = server.list()

    for i in range(len(items) - 1, 0, -1):
        id, size = items[i].decode('utf-8').split()
        resp, text, octets = server.retr(id)
        msg_content = b'\r\n'.join(text).decode('utf-8')
        msg = Parser().parsestr(msg_content)
        email_subject = msg.get('Subject')

        if email_subject == 'PULSE':
            emails = [email.message_from_string(msg_content)]
            for mail in emails:
                for part in mail.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                    filename = part.get_filename()
                    if not filename:
                        filename = "Pulse.xlsx"

                    fp = open(os.path.join(DIR, filename), 'wb')
                    fp.write(part.get_payload(decode=1))
                    fp.close()
            break

    server.quit()
    return HttpResponse("OK")
