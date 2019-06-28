from django.db.models import QuerySet
from rest_framework import serializers

from api.serializers import UserSerializer
from main.models import *


class EmptySerializer(serializers.Serializer):
    pass


class RoomMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomMedia
        fields = ['file']


class RoomShortSerializer(serializers.ModelSerializer):
    media = serializers.SerializerMethodField('get_room_media')

    def get_room_media(self, room):
        result = RoomMedia.objects.filter(room=room)
        medias = list()
        for res in result:
            medias.append(RoomMediaSerializer(instance=res).data)
        return medias

    class Meta:
        model = Room
        fields = '__all__'


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