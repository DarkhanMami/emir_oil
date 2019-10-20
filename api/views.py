from datetime import timedelta, datetime
from django.db.models.aggregates import Sum, Count
from django.conf import settings
import urllib
import json
from django.db.models import Q

from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import generics, mixins, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.authtoken.models import Token

from api import serializers
from api.serializers import UserSerializer
from main import models
from main.models import WellMatrix
from main.serializers import WellMatrixCreateSerializer, WellMatrixSerializer, WellSerializer, FieldSerializer, \
    FieldBalanceSerializer, FieldBalanceCreateSerializer, ProductionSerializer, ParkProductionSerializer, \
    ReportExcelSerializer, ParkOilSerializer
from datetime import date, datetime
from django.core.mail import EmailMessage


class AuthView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })


class ListUser(generics.ListCreateAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer


class DetailUser(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer


class WellMatrixViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('well',)
    queryset = models.WellMatrix.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        # if self.request.user.type == User.CLIENT:
        #     return models.Application.objects.filter(user=self.request.user)
        return models.WellMatrix.objects.all()

    def get_serializer_class(self):
        if self.action == 'create_wellmatrix':
            return WellMatrixCreateSerializer
        return WellMatrixSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False)
    def get_by_field(self, request, *args, **kwargs):
        field = models.Field.objects.get(name=request.GET.get("field"))
        result = models.WellMatrix.objects.filter(well__field=field)
        return Response(WellMatrixSerializer(result, many=True).data)

    @action(methods=['post'], detail=False)
    def create_wellmatrix(self, request, *args, **kwargs):
        serializer = WellMatrixCreateSerializer(data=request.data)
        if serializer.is_valid():
            well = models.Well.objects.get(name=request.data["well"])
            dt = datetime.now()
            wellmatrix = WellMatrix.objects.update_or_create(well=well, defaults={"fluid": request.data["fluid"],
                                                                                  "teh_rej_fluid": request.data["teh_rej_fluid"],
                                                                                  "teh_rej_oil": request.data["teh_rej_oil"],
                                                                                  "teh_rej_water": request.data["teh_rej_water"],
                                                                                  "gas": request.data["gas"],
                                                                                  "timestamp": dt})
            return Response(self.get_serializer(wellmatrix, many=False).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductionViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('well',)
    queryset = models.Production.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return None

    def get_serializer_class(self):
        return ProductionSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False)
    def get_by_month(self, request, *args, **kwargs):
        result = models.Production.objects.filter(timestamp__year__gte=2019,
                                                  timestamp__month__gte=request.GET.get("month"),
                                                  timestamp__year__lte=2019,
                                                  timestamp__month__lte=request.GET.get("month"))
        return Response(ProductionSerializer(result, many=True).data)

    @action(methods=['get'], detail=False)
    def get_all(self, request, *args, **kwargs):
        with open('json_data/production.json') as json_file:
            params = json.load(json_file)
        return Response(params)

    @action(methods=['post'], detail=False)
    def update_table(self, request, *args, **kwargs):
        data = request.data["data"]
        for item in data:
            if models.Well.objects.filter(name=item[2]).exists():
                well = models.Well.objects.get(name=item[2])
                dt = datetime.strptime(item[0], '%Y-%m-%d')
                models.Production.objects.update_or_create(well=well, timestamp=dt, defaults={"calc_time": item[3],
                                                                                            "fluid": item[4],
                                                                                            "teh_rej_fluid": item[5],
                                                                                            "teh_rej_oil": item[6],
                                                                                            "teh_rej_water": item[7]})
                if models.WellMatrix.objects.filter(well=well).exists():
                    matrix = models.WellMatrix.objects.get(well=well)
                    matrix.fluid = item[4]
                    matrix.teh_rej_fluid = item[5]
                    matrix.teh_rej_oil = item[6]
                    matrix.teh_rej_water = item[7]
                    matrix.save()
            else:
                    pass
        return Response("OK")

    @action(methods=['post'], detail=False)
    def update_stop(self, request, *args, **kwargs):
        data = request.data["data"]
        for item in data:
            if models.Well.objects.filter(name=item[2]).exists():
                well = models.Well.objects.get(name=item[2])
                dt = datetime.strptime(item[0], '%Y-%m-%d')
                models.Production.objects.update_or_create(well=well, timestamp=dt, defaults={"stop_time": item[3],
                                                                                              "stop_init": item[4],
                                                                                              "stop_reason": item[5],
                                                                                              "status": item[6]})
            else:
                pass
        return Response("OK")

    @action(methods=['post'], detail=False)
    def add_today_data(self, request, *args, **kwargs):
        last_day = models.Production.objects.order_by('-timestamp').first().timestamp
        cur_day = last_day + timedelta(days=1)
        while cur_day <= date.today():
            if models.Production.objects.filter(timestamp=cur_day).exists():
                pass
            else:
                data = models.Production.objects.filter(timestamp=last_day)
                for item in data:
                    if models.WellMatrix.objects.filter(well=item.well).exists():
                        matrix = models.WellMatrix.objects.get(well=item.well)
                        matrix.fluid = item.fluid
                        matrix.teh_rej_fluid = item.teh_rej_fluid
                        matrix.teh_rej_oil = item.teh_rej_oil
                        matrix.teh_rej_water = item.teh_rej_water
                        matrix.gas = item.gas
                        matrix.save()
                    item.pk = None
                    item.timestamp = cur_day
                    item.save()
                data = models.ParkProduction.objects.filter(timestamp=last_day)
                for item in data:
                    item.pk = None
                    item.timestamp = cur_day
                    item.save()
            cur_day = cur_day + timedelta(days=1)
        return Response("Success")


class ParkProductionViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('field',)
    queryset = models.ParkProduction.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return None

    def get_serializer_class(self):
        return ParkProductionSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False)
    def get_by_month(self, request, *args, **kwargs):
        result = models.ParkProduction.objects.filter(timestamp__year__gte=2019,
                                                      timestamp__month__gte=request.GET.get("month"),
                                                      timestamp__year__lte=2019,
                                                      timestamp__month__lte=request.GET.get("month"))
        return Response(ParkProductionSerializer(result, many=True).data)

    @action(methods=['get'], detail=False)
    def get_all(self, request, *args, **kwargs):
        with open('json_data/park_production.json') as json_file:
            params = json.load(json_file)
        return Response(params)

    @action(methods=['post'], detail=False)
    def update_table(self, request, *args, **kwargs):
        data = request.data["data"]
        for item in data:
            if models.Field.objects.filter(name=item[1]).exists():
                field = models.Field.objects.get(name=item[1])
                dt = datetime.strptime(item[0], '%Y-%m-%d')
                models.ParkProduction.objects.update_or_create(field=field, timestamp=dt,
                                                               defaults={"fluid_beg": item[2],
                                                                         "fluid_end": item[3],
                                                                         "teh_rej_water": item[4],
                                                                         "fluid_brutto": item[5],
                                                                         "fluid_netto": item[6],
                                                                         "needs": item[7],
                                                                         "pump": item[8]})
        else:
            pass
        return Response("OK")


class FieldBalanceViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('field',)

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return None

    def get_serializer_class(self):
        if self.action == 'create_balance':
            return FieldBalanceCreateSerializer
        return FieldBalanceSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False)
    def get_by_field(self, request, *args, **kwargs):
        field = models.Field.objects.get(name=request.GET.get("field"))
        result = models.FieldBalance.objects.filter(field=field, timestamp__year__gte=2019,
                                                    timestamp__month__gte=request.GET.get("month"),
                                                    timestamp__year__lte=2019,
                                                    timestamp__month__lte=request.GET.get("month"))
        return Response(FieldBalanceSerializer(result, many=True).data)

    @action(methods=['get'], detail=False)
    def get_total(self, request, *args, **kwargs):
        result = models.FieldBalance.objects.filter(timestamp__year__gte=2019,
                                                    timestamp__month__gte=request.GET.get("month"),
                                                    timestamp__year__lte=2019,
                                                    timestamp__month__lte=request.GET.get("month")).values('timestamp')\
            .annotate(transport_balance=Sum('transport_balance'), ansagan_balance=Sum('ansagan_balance'),
                      transport_brutto=Sum('transport_brutto'), ansagan_brutto=Sum('ansagan_brutto'),
                      transport_netto=Sum('transport_netto'), ansagan_netto=Sum('ansagan_netto'),
                      transport_density=Sum('transport_density'), ansagan_density=Sum('ansagan_density'),
                      agzu_fluid=Sum('agzu_fluid'), agzu_oil=Sum('agzu_oil'),
                      teh_rej_fluid=Sum('teh_rej_fluid'), teh_rej_oil=Sum('teh_rej_oil'))
        return Response(FieldBalanceSerializer(result, many=True).data)

    @action(methods=['post'], detail=False)
    def create_balance(self, request, *args, **kwargs):
        serializer = FieldBalanceCreateSerializer(data=request.data)
        if serializer.is_valid():
            field = models.Field.objects.get(name=request.data["field"])
            dt = datetime.now()
            balance = models.FieldBalance.objects.update_or_create(field=field, timestamp=dt,
                                                   defaults={"transport_balance": request.data["transport_balance"],
                                                             "transport_brutto": request.data["transport_brutto"],
                                                             "transport_netto": request.data["transport_netto"],
                                                             "transport_density": request.data["transport_density"]})
                                                             # "agzu_fluid": request.data["agzu_fluid"],
                                                             # "agzu_oil": request.data["agzu_oil"],
                                                             # "teh_rej_fluid": request.data["teh_rej_fluid"],
                                                             # "teh_rej_oil": request.data["teh_rej_oil"]})
            return Response(self.get_serializer(balance, many=False).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WellViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('name',)
    queryset = models.Well.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return models.Well.objects.all()

    def get_serializer_class(self):
        return WellSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False)
    def get_by_field(self, request, *args, **kwargs):
        field = models.Field.objects.get(name=request.GET.get("field"))
        wells = models.Well.objects.filter(field=field)
        return Response(WellSerializer(wells, many=True).data)


class FieldViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('name',)
    queryset = models.Field.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return models.Field.objects.all()

    def get_serializer_class(self):
        return FieldSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class ParkOilViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('field',)
    queryset = models.ParkOil.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return models.ParkOil.objects.all()

    def get_serializer_class(self):
        return ParkOilSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False)
    def get_by_month(self, request, *args, **kwargs):
        result = models.ParkOil.objects.filter(timestamp__year__gte=2019,
                                               timestamp__month__gte=request.GET.get("month"),
                                               timestamp__year__lte=2019,
                                               timestamp__month__lte=request.GET.get("month"))
        return Response(ParkOilSerializer(result, many=True).data)


class ReportExcelViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('well',)
    queryset = models.ReportExcel.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return None

    def get_serializer_class(self):
        return ReportExcelSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False)
    def get_by_day(self, request, *args, **kwargs):
        dt = datetime.strptime(request.GET.get("date"), '%Y-%m-%d')
        result = models.ReportExcel.objects.filter(timestamp__exact=dt)
        return Response(ReportExcelSerializer(result, many=True).data)


@api_view(['GET'])
def add_today_data(request):
    last_day = models.Production.objects.order_by('-timestamp').first().timestamp
    cur_day = last_day + timedelta(days=1)
    while cur_day <= date.today():
        if models.Production.objects.filter(timestamp=cur_day).exists():
            pass
        else:
            data = models.Production.objects.filter(timestamp=last_day)
            for item in data:
                if models.WellMatrix.objects.filter(well=item.well).exists():
                    matrix = models.WellMatrix.objects.get(well=item.well)
                    matrix.fluid = item.fluid
                    matrix.teh_rej_fluid = item.teh_rej_fluid
                    matrix.teh_rej_oil = item.teh_rej_oil
                    matrix.teh_rej_water = item.teh_rej_water
                    matrix.gas = item.gas
                    matrix.save()
                item.pk = None
                item.timestamp = cur_day
                item.save()
            data = models.ParkProduction.objects.filter(timestamp=last_day)
            for item in data:
                item.pk = None
                item.timestamp = cur_day
                item.save()
        cur_day = cur_day + timedelta(days=1)
    return Response({
        "info": "New data is added"
    })

