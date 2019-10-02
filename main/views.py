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
            replacement = None
            otbivka = None
            measurement = None
            stop_date = None
            spusk = None
            try:
                a1_tuple = xlrd.xldate_as_tuple(row_values[8], wb.datemode)
                replacement = datetime(*a1_tuple)
            except:
                if len(row_values[8]) > 5:
                    replacement = datetime.strptime(str(row_values[8]), "%m/%d/%Y")
            try:
                a1_tuple = xlrd.xldate_as_tuple(row_values[11], wb.datemode)
                otbivka = datetime(*a1_tuple)
            except:
                if len(row_values[11]) > 5:
                    otbivka = datetime.strptime(str(row_values[11]), "%m/%d/%Y")
            try:
                a1_tuple = xlrd.xldate_as_tuple(row_values[19], wb.datemode)
                measurement = datetime(*a1_tuple)
            except:
                if len(row_values[19]) > 5:
                    measurement = datetime.strptime(str(row_values[19]), "%m/%d/%Y")
            try:
                a1_tuple = xlrd.xldate_as_tuple(row_values[22], wb.datemode)
                stop_date = datetime(*a1_tuple)
            except:
                if len(row_values[22]) > 5:
                    stop_date = datetime.strptime(str(row_values[22]), "%m/%d/%Y")
            try:
                a1_tuple = xlrd.xldate_as_tuple(row_values[26], wb.datemode)
                spusk = datetime(*a1_tuple)
            except:
                if len(row_values[26]) > 5:
                    spusk = datetime.strptime(str(row_values[26]), "%m/%d/%Y")

            if ReportExcel.objects.filter(well=well, timestamp=timestamp).exists():
                report = ReportExcel.objects.get(well=well, timestamp=timestamp)
            else:
                report = ReportExcel.objects.create(well=well, timestamp=timestamp)
            report.operating_type = row_values[2]
            try:
                float(row_values[3])
                report.thp = float(row_values[3])
            except:
                pass
            try:
                float(row_values[4])
                report.annulus = float(row_values[4])
            except:
                pass
            try:
                float(row_values[5])
                report.flow_line = float(row_values[5])
            except:
                pass
            try:
                float(row_values[6])
                report.tyct = float(row_values[6])
            except:
                pass
            try:
                float(row_values[7])
                report.choke_size = float(row_values[7])
            except:
                pass
            report.replacement = replacement
            try:
                float(row_values[9])
                report.operated_time = float(row_values[9])
            except:
                pass
            try:
                float(row_values[10])
                report.emir_oil = float(row_values[10])
            except:
                pass
            report.otbivka = otbivka
            try:
                float(row_values[12])
                report.fluid = float(row_values[12])
            except:
                pass
            try:
                float(row_values[13])
                report.fluid_tonn = float(row_values[13])
            except:
                pass
            try:
                float(row_values[14])
                report.teh_rej_water = float(row_values[14])
            except:
                pass
            try:
                float(row_values[15])
                report.oil = float(row_values[15])
            except:
                pass
            try:
                float(row_values[16])
                report.oil_tonn = float(row_values[16])
            except:
                pass
            try:
                float(row_values[17])
                report.daily_prod = float(row_values[17])
            except:
                pass
            try:
                float(row_values[18])
                report.gor = float(row_values[18])
            except:
                pass
            report.measurement = measurement
            try:
                float(row_values[20])
                report.water_drainage = float(row_values[20])
            except:
                pass
            report.stop_time = row_values[21]
            report.stop_date = stop_date
            report.stop_reason = row_values[23]
            report.research = row_values[24]
            report.result = row_values[25]
            report.spusk = spusk
            try:
                float(row_values[27])
                report.tool_depth = float(row_values[27])
            except:
                pass
            report.comments = row_values[28]
            report.save()

        # except Exception as e: print(e)
        except:
            pass

    return HttpResponse("OK")
