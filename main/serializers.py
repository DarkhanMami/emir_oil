from django.db.models import QuerySet
from rest_framework import serializers

from api.serializers import UserSerializer
from main.models import *


class EmptySerializer(serializers.Serializer):
    pass


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = ['name', 'density']


class WellSerializer(serializers.ModelSerializer):
    field = FieldSerializer(many=False, read_only=True)

    class Meta:
        model = Well
        fields = ['name', 'field']


class WellMatrixSerializer(serializers.ModelSerializer):
    well = WellSerializer(many=False, read_only=True)

    class Meta:
        model = WellMatrix
        fields = ['well', 'fluid', 'gas', 'teh_rej_fluid', 'teh_rej_oil', 'teh_rej_water', 'gas', 'timestamp']


class ProductionSerializer(serializers.ModelSerializer):
    well = WellSerializer(many=False, read_only=True)

    class Meta:
        model = Production
        fields = ['well', 'calc_time', 'fluid', 'teh_rej_fluid', 'teh_rej_oil', 'teh_rej_water',
                  'density', 'stop_time', 'timestamp', 'stop_init', 'stop_reason', 'status']


class ParkProductionSerializer(serializers.ModelSerializer):
    field = FieldSerializer(many=False, read_only=True)

    class Meta:
        model = ParkProduction
        fields = ['field', 'fluid_beg', 'fluid_end', 'fluid_brutto', 'fluid_netto', 'teh_rej_water', 'needs', 'pump', 'timestamp']


class WellMatrixCreateSerializer(serializers.ModelSerializer):
    well = WellSerializer(many=False, read_only=True)

    class Meta:
        model = WellMatrix
        fields = ['well', 'fluid', 'teh_rej_fluid', 'teh_rej_oil', 'teh_rej_water', 'gas']


class FieldBalanceSerializer(serializers.ModelSerializer):
    field = FieldSerializer(many=False, read_only=True)

    class Meta:
        model = FieldBalance
        fields = ['field', 'transport_balance', 'ansagan_balance', 'transport_brutto', 'ansagan_brutto',
                  'transport_netto', 'ansagan_netto', 'transport_density', 'ansagan_density',
                  'agzu_fluid', 'agzu_oil', 'teh_rej_fluid', 'teh_rej_oil', 'timestamp']


class FieldBalanceCreateSerializer(serializers.ModelSerializer):
    field = FieldSerializer(many=False, read_only=True)

    class Meta:
        model = FieldBalance
        fields = ['field', 'transport_balance', 'transport_brutto', 'transport_netto', 'transport_density']


class ReportExcelSerializer(serializers.ModelSerializer):
    well = WellSerializer(many=False, read_only=True)

    class Meta:
        model = ReportExcel
        fields = ['well', 'operating_type', 'thp', 'annulus', 'flow_line', 'tyct', 'choke_size', 'replacement',
                  'operated_time', 'emir_oil', 'otbivka', 'fluid', 'fluid_tonn', 'teh_rej_water', 'oil', 'oil_tonn',
                  'daily_prod', 'gor', 'measurement', 'water_drainage', 'stop_time', 'stop_date', 'stop_reason',
                  'research', 'result', 'spusk', 'tool_depth', 'comments', 'timestamp']


class ParkOilSerializer(serializers.ModelSerializer):
    field = FieldSerializer(many=False, read_only=True)

    class Meta:
        model = ParkOil
        fields = ['field', 'ttn', 'contractor', 'gos_num', 'driver', 'fluid_brutto',
                  'go_to', 'start', 'end', 'go_out', 'timestamp']
