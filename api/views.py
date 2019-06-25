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
from api.serializers import UserSerializer
from main import models
from main.serializers import RoomShortSerializer, OrderShortSerializer, OrderCreateSerializer, FeedbackShortSerializer,\
    FeedbackCreateSerializer, NewsKZShortSerializer
from . import serializers
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


class RoomViewSet(mixins.RetrieveModelMixin,  mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('name', 'type', 'lake_view')
    queryset = models.Room.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        # if self.request.user.type == User.TEACHER:
        #     return models.Course.objects.filter(teacher=self.request.user)
        # return models.Course.objects.filter(students=self.request.user).distinct()
        return models.Room.objects.all()

    def get_serializer_class(self):
        return RoomShortSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        # if self.action == "add_lesson":
        #     permission_classes = [IsAuthenticated, IsTeacher]
        return [permission() for permission in permission_classes]


class FeedbackViewSet(mixins.RetrieveModelMixin,  mixins.ListModelMixin, GenericViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('isShown', 'type')

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return None

    def get_serializer_class(self):
        return FeedbackShortSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False)
    def get_stat_all(self, request, *args, **kwargs):
        with open('json_data/birge.json') as json_file:
            params = json.load(json_file)

        return Response(params)

    @action(methods=['get'], detail=False)
    def get_length(self, request, *args, **kwargs):
        return Response(len(models.Feedback.objects.all()))

    @action(methods=['post'], detail=False)
    def create_feedback(self, request, *args, **kwargs):
        # recaptcha_response = request.POST.get('g-recaptcha-response')
        recaptcha_response = request.data["g-recaptcha-response"]
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        data = urllib.parse.urlencode(values).encode()
        req = urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())

        if result['success']:
            feedback = models.Feedback.objects.create(author=request.data["author"],
                                                      contact=request.data["contact"],
                                                      # age=request.data["age"],
                                                      # iin=request.data["iin"],
                                                      location=request.data["location"],
                                                      career=request.data["career"],
                                                      wish_type=request.data["wish_type"],
                                                      # wish_type2=request.data["wish_type2"],
                                                      body=request.data["body"],
                                                      type=request.data["type"])
            return Response(FeedbackCreateSerializer(instance=feedback).data, status=status.HTTP_201_CREATED)
        else:
            return Response("Обращение не создано", status=status.HTTP_429_TOO_MANY_REQUESTS)


class OrderViewSet(mixins.RetrieveModelMixin,  mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('date_from', 'date_to')
    queryset = models.Order.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return models.Order.objects.all()

    def get_serializer_class(self):
        return OrderShortSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False)
    def get_free_rooms(self, request, *args, **kwargs):
        start_date = request.GET.get("date_from")
        end_date = request.GET.get("date_to")
        guest_num = int(request.GET.get("guest_num"))
        with_meal = str(request.GET.get("with_meal"))
        guest_num_tmp = guest_num
        children_num = int(request.GET.get("children_num"))
        prior_start_date = datetime(year=2019, month=6, day=30)
        prior_end_date = datetime(year=2019, month=8, day=15)
        dt_start = datetime.strptime(start_date, '%Y-%m-%d')
        dt_end = datetime.strptime(end_date, '%Y-%m-%d')
        diff = (dt_end - dt_start).days
        if diff < 1:
            diff = 1

        discount = 1
        today = datetime.today()
        discount_date = datetime(year=2019, month=5, day=1)
        if today < discount_date:
            discount = 0.7

        records_list = models.Order.objects.filter(date_from__gte=start_date, date_from__lte=end_date)
        records_list2 = models.Order.objects.filter(date_to__gte=start_date, date_to__lte=end_date)
        records_list = records_list | records_list2

        result = list()

        for room in models.Room.objects.all():
            if room.type == 'Эконом':
                if guest_num < 2:
                    guest_num_tmp = 2
            elif room.type == 'Бизнес':
                if guest_num < 3:
                    guest_num_tmp = 3
            elif room.type == 'Премиум':
                if guest_num < 4:
                    guest_num_tmp = 4

            res = dict()
            free_rooms = room.count - len(records_list.filter(room=room))
            if free_rooms < 0:
                free_rooms = 0
            res["room"] = RoomShortSerializer(room).data
            res["free_rooms"] = free_rooms
            if prior_start_date < dt_start < prior_end_date and prior_start_date < dt_end < prior_end_date:
                order_price = (guest_num_tmp * room.prior_price) + (children_num * 5000)
                if with_meal.lower() == 'false':
                    order_price -= (guest_num * 2000) + (children_num * 2000)
            else:
                order_price = (guest_num_tmp * room.price) + (children_num * 5000)
                if with_meal.lower() == 'false':
                    order_price -= (guest_num * 2000) + (children_num * 2000)

            order_price = order_price * diff
            if room.lake_view:
                order_price += diff * 3000
            order_price = order_price * discount
            res["order_price"] = order_price
            result.append(res)
        return Response(result)

    @action(methods=['post'], detail=False)
    def create_order(self, request, *args, **kwargs):
        start_date = request.data["date_from"]
        end_date = request.data["date_to"]
        guest_num = int(request.data["guest_num"])
        with_meal = str(request.data["with_meal"])
        guest_num_tmp = guest_num
        children_num = int(request.data["children_num"])
        dt_start = datetime.strptime(start_date, '%Y-%m-%d')
        dt_end = datetime.strptime(end_date, '%Y-%m-%d')
        diff = (dt_end - dt_start).days
        if diff < 1:
            diff = 1

        discount = 1
        today = datetime.today()
        discount_date = datetime(year=2019, month=5, day=1)
        if today < discount_date:
            discount = 0.7

        room = models.Room.objects.get(id=request.data["room_id"])
        if room.type == 'Эконом':
            if guest_num < 2:
                guest_num_tmp = 2
        elif room.type == 'Бизнес':
            if guest_num < 3:
                guest_num_tmp = 3
        elif room.type == 'Премиум':
            if guest_num < 4:
                guest_num_tmp = 4

        prior_start_date = datetime(year=2019, month=6, day=30)
        prior_end_date = datetime(year=2019, month=8, day=15)

        if prior_start_date < dt_start < prior_end_date and prior_start_date < dt_end < prior_end_date:
            order_price = (guest_num_tmp * room.prior_price) + (children_num * 5000)
            if with_meal.lower() == 'false':
                order_price -= (guest_num * 2000) + (children_num * 2000)
        else:
            order_price = (guest_num_tmp * room.price) + (children_num * 5000)
            if with_meal.lower() == 'false':
                order_price -= (guest_num * 2000) + (children_num * 2000)

        order_price = order_price * diff
        if room.lake_view:
            order_price += diff * 3000
        order_price = order_price * discount

        order = models.Order.objects.create(name=request.data["name"],
                                            date_from=start_date,
                                            date_to=end_date,
                                            children_num=children_num,
                                            with_meal=with_meal,
                                            guest_num=guest_num,
                                            final_cost=order_price,
                                            prepayment=request.data["prepayment"],
                                            email=request.data["email"],
                                            telephone=request.data["telephone"],
                                            room=room)
        return Response(OrderCreateSerializer(instance=order).data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False)
    def send_email(self, request, *args, **kwargs):
        subject = request.data["subject"]
        body = request.data['body']
        email = EmailMessage(subject, body, to=['poseidonalakol@gmail.com'])
        email.send()
        try:
            email.send()
            return Response("Сообщение отправлено", status=status.HTTP_200_OK)
        except:
            return Response("Сообщение не отправлено", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NewsKZViewSet(mixins.RetrieveModelMixin,  mixins.ListModelMixin, GenericViewSet):

    filter_backends = (filters.DjangoFilterBackend,)

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return None
        # return models.NewsKZ.objects.all().order_by('-timestamp')

    def get_serializer_class(self):
        return NewsKZShortSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False)
    def get_news(self, request, *args, **kwargs):
        serializer = self.get_serializer(models.NewsKZ.objects.filter(link__contains=request.GET.get("link")), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def get_all(self, request, *args, **kwargs):
        with open('json_data/kz_news.json') as json_file:
            params = json.load(json_file)
        return Response(params)
