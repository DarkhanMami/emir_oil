from datetime import timedelta, datetime
from django.conf import settings
import urllib
import json
from django.db.models import Q

from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import generics, mixins, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.authtoken.models import Token

from api import serializers
from api.serializers import UserSerializer
from main import models
from main.models import WellMatrix
from main.serializers import WellMatrixCreateSerializer, WellMatrixSerializer, WellSerializer, FieldSerializer, \
    FieldBalanceSerializer
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
                                                                                  "timestamp": dt})
            return Response(self.get_serializer(wellmatrix, many=False).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FieldBalanceViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('field',)
    queryset = models.FieldBalance.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return models.FieldBalance.objects.all()

    def get_serializer_class(self):
        if self.action == 'create_balance':
            return WellMatrixCreateSerializer
        return FieldBalanceSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['post'], detail=False)
    def create_balance(self, request, *args, **kwargs):
        serializer = WellMatrixCreateSerializer(data=request.data)
        if serializer.is_valid():
            well = models.Well.objects.get(name=request.data["well"])
            dt = datetime.now()
            wellmatrix = WellMatrix.objects.update_or_create(well=well, defaults={"fluid": request.data["fluid"],
                                                                                  "teh_rej_fluid": request.data["teh_rej_fluid"],
                                                                                  "teh_rej_oil": request.data["teh_rej_oil"],
                                                                                  "teh_rej_water": request.data["teh_rej_water"],
                                                                                  "timestamp": dt})
            return Response(self.get_serializer(wellmatrix, many=False).data)
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
        if self.action == "add_lesson":
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
        if self.action == "add_lesson":
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]