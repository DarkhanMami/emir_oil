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


class OrderShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class FeedbackShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'


class FeedbackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'


class NewsKZMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsKZMedia
        fields = ['file']


class NewsKZVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsKZVideo
        fields = ['file']


class NewsKZShortSerializer(serializers.ModelSerializer):
    media = serializers.SerializerMethodField('get_news_media')
    video = serializers.SerializerMethodField('get_video_media')

    def get_news_media(self, newsKZ):
        result = NewsKZMedia.objects.filter(newsKZ=newsKZ)
        medias = list()
        for res in result:
            medias.append(NewsKZMediaSerializer(instance=res).data)
        return medias

    def get_video_media(self, newKZ):
        result = NewsKZVideo.objects.filter(newKZ=newKZ)
        medias = list()
        for res in result:
            medias.append(NewsKZVideoSerializer(instance=res).data)
        return medias

    class Meta:
        model = NewsKZ
        fields = '__all__'


class NewsKZJsonSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsKZ
        fields = ['title', 'description', 'link', 'timestamp']
