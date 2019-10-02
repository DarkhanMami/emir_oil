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
from datetime import datetime, date, timedelta
import xlrd
from main.models import *


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
    # DIR = "/Users/darik/linux/EmirOil/"
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

        # if email_subject == 'PULSE':
        emails = [email.message_from_string(msg_content)]
        for mail in emails:
            for part in mail.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue

                fp = open(os.path.join('report.xlsx'), 'wb')
                fp.write(part.get_payload(decode=1))
                fp.close()
        break

    server.quit()
    wb = xlrd.open_workbook('report.xlsx')
    sh = wb.sheet_by_index(1)
    row_values = sh.row_values(1)
    timestamp = None
    try:
        a1_tuple = xlrd.xldate_as_tuple(row_values[2], wb.datemode)
        timestamp = datetime(*a1_tuple)
    except:
        timestamp = datetime.strptime(str(row_values[2]).replace('Date: ', ''), "%d.%m.%Y")

    for rownum in range(9, sh.nrows):
        row_values = sh.row_values(rownum)
        try:
            well = Well.objects.get(name=row_values[1].replace(" ", ""))
            try:
                a1_tuple = xlrd.xldate_as_tuple(row_values[8], wb.datemode)
                replacement = datetime(*a1_tuple)
            except:
                replacement = datetime.strptime(str(row_values[8]), "%d/%m/%Y")
            try:
                a1_tuple = xlrd.xldate_as_tuple(row_values[11], wb.datemode)
                otbivka = datetime(*a1_tuple)
            except:
                otbivka = datetime.strptime(str(row_values[11]), "%d/%m/%Y")
            try:
                a1_tuple = xlrd.xldate_as_tuple(row_values[19], wb.datemode)
                measurement = datetime(*a1_tuple)
            except:
                measurement = datetime.strptime(str(row_values[19]), "%d/%m/%Y")
            try:
                a1_tuple = xlrd.xldate_as_tuple(row_values[22], wb.datemode)
                stop_date = datetime(*a1_tuple)
            except:
                stop_date = datetime.strptime(str(row_values[22]), "%d/%m/%Y")
            try:
                a1_tuple = xlrd.xldate_as_tuple(row_values[26], wb.datemode)
                spusk = datetime(*a1_tuple)
            except:
                spusk = datetime.strptime(str(row_values[26]), "%d/%m/%Y")

            ReportExcel.objects.create(
                well=well,
                operating_type=row_values[2],
                thp=row_values[3],
                annulus=row_values[4],
                flow_line=row_values[5],
                tyct=row_values[6],
                choke_size=row_values[7],
                replacement=replacement,
                operated_time=row_values[9],
                emir_oil=row_values[10],
                otbivka=otbivka,
                fluid=row_values[12],
                fluid_tonn=row_values[13],
                teh_rej_water=row_values[14],
                oil=row_values[15],
                oil_tonn=row_values[16],
                daily_prod=row_values[17],
                gor=row_values[18],
                measurement=measurement,
                water_drainage=row_values[20],
                stop_time=row_values[21],
                stop_date=stop_date,
                stop_reason=row_values[23],
                research=row_values[24],
                result=row_values[25],
                spusk=spusk,
                tool_depth=row_values[27],
                comments=row_values[28],
                timestamp=timestamp
            )
        except:
            pass

    return HttpResponse("OK")
