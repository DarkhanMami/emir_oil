from django.db.models import QuerySet
from rest_framework import serializers

from api.serializers import UserSerializer
from main.models import *


class EmptySerializer(serializers.Serializer):
    pass


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = ['name']


class WellSerializer(serializers.ModelSerializer):
    field = FieldSerializer(many=False, read_only=True)

    class Meta:
        model = Well
        fields = ['name', 'field']


class WellMatrixSerializer(serializers.ModelSerializer):
    well = WellSerializer(many=False, read_only=True)

    class Meta:
        model = WellMatrix
        fields = ['well', 'fluid', 'teh_rej_fluid', 'teh_rej_oil', 'teh_rej_water', 'timestamp']


class WellMatrixCreateSerializer(serializers.ModelSerializer):
    well = WellSerializer(many=False, read_only=True)

    class Meta:
        model = WellMatrix
        fields = ['well', 'fluid', 'teh_rej_fluid', 'teh_rej_oil', 'teh_rej_water']


class FieldBalanceSerializer(serializers.ModelSerializer):
    field = FieldSerializer(many=False, read_only=True)

    class Meta:
        model = FieldBalance
        fields = ['field', 'transport_balance', 'ansagan_balance', 'timestamp']


class FieldBalanceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldBalance
        fields = ['__all__']