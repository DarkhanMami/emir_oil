from django.db.models import QuerySet
from rest_framework import serializers

from api.serializers import UserSerializer
from main.models import *


class EmptySerializer(serializers.Serializer):
    pass


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = ['__all__']


class WellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Well
        fields = ['__all__']


class WellMatrixSerializer(serializers.ModelSerializer):
    class Meta:
        model = WellMatrix
        fields = ['__all__']


class WellMatrixCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WellMatrix
        fields = ['well', 'fluid', 'teh_rej_fluid', 'teh_rej_oil', 'teh_rej_water']


class FieldBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldBalance
        fields = ['__all__']


class FieldBalanceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldBalance
        fields = ['__all__']