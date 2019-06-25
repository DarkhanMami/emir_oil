import uuid

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

from django.utils.translation import gettext as _
from tinymce.models import HTMLField


def uploaded_filename(instance, filename):
    """
    Scramble / uglify the filename of the uploaded file, but keep the files extension (e.g., .jpg or .png)
    :param instance:
    :param filename:
    :return:
    """
    extension = filename.split(".")[-1]
    return "{}/{}.{}".format(instance.pk, uuid.uuid4(), extension)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError(_('Users must have an email address'))

        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name=_('Email адрес'),
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=1024, blank=True, default="")
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    DISPATCHER = "Диспетчер"
    ADMINISTRATOR = "Администратор"

    TYPE_CHOICES = (
        (DISPATCHER, _('Диспетчер')),
        (ADMINISTRATOR, _('Администратор')),
    )

    type = models.CharField(choices=TYPE_CHOICES, default=ADMINISTRATOR, max_length=100, db_index=True, verbose_name=_("Тип пользователя"))

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class Room(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True, db_index=True, verbose_name=_('Название'))
    description = models.TextField(max_length=255 * 10, blank=True, default="", verbose_name=_('Описание'))
    price = models.IntegerField(default=1, db_index=True, verbose_name=_('Цена'))
    prior_price = models.IntegerField(default=1, db_index=True, verbose_name=_('Высокая цена'))
    lake_view = models.BooleanField(default=False, verbose_name=_('Вид на озеро'))

    ECONOMY = "Эконом"
    BUSINESS = "Бизнес"
    PREMIUM = "Премиум"

    ROOM_CHOICES = (
        (ECONOMY, _('Эконом')),
        (BUSINESS, _('Бизнес')),
        (PREMIUM, _('Премиум')),
    )

    type = models.CharField(choices=ROOM_CHOICES, default=ECONOMY, max_length=100, db_index=True, verbose_name=_("Тип"))
    count = models.IntegerField(default=1, db_index=True, verbose_name=_("Количество"))

    class Meta:
        verbose_name = _("Комната")
        verbose_name_plural = _("Комнаты")

    def __str__(self):
        return self.name


class RoomMedia(models.Model):
    file = models.FileField(upload_to=uploaded_filename, blank=True, null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room')


class Order(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, db_index=True, verbose_name=_('ФИО'))
    room = models.ForeignKey(Room, blank=False, null=False, on_delete=models.CASCADE, related_name='orders')
    date_from = models.DateField(blank=False, null=False, verbose_name=_('Дата начала'))
    date_to = models.DateField(blank=False, null=False, verbose_name=_('Дата окончания'))
    children_num = models.IntegerField(default=0, db_index=True, verbose_name=_('Кол-во детей'))
    with_meal = models.BooleanField(default=False, verbose_name=_('Питание'))
    guest_num = models.IntegerField(default=1, db_index=True, verbose_name=_('Кол-во гостей'))
    final_cost = models.IntegerField(default=1, db_index=True, verbose_name=_('Окончательная цена'))
    prepayment = models.IntegerField(default=0, db_index=True, verbose_name=_('Предоплата'))
    email = models.CharField(max_length=255, blank=False, null=False, db_index=True)
    telephone = models.CharField(max_length=15, db_index=True, verbose_name=_('Телефон'))

    class Meta:
        verbose_name = _("Бронирование")
        verbose_name_plural = _("Бронирования")
        ordering = ['room', 'date_from', 'date_to']

    def __str__(self):
        return str(self.date_from) + " " + str(self.date_to) + " " + str(self.room)


class Feedback(models.Model):
    author = models.CharField(max_length=255, blank=False, null=False, verbose_name=_('Автор'))
    contact = models.CharField(max_length=255, blank=True, verbose_name=_('Контакт'))
    # age = models.IntegerField(default=0, db_index=True, verbose_name=_('Возраст'))
    # iin = models.CharField(max_length=255, verbose_name=_('ИИН'))

    GNUR = 'г. Нур-Султан'
    GALM = 'г. Алматы'
    GSHY = 'г. Шымкент'
    AKM = 'Акмолинская'
    AKT = 'Актюбинская'
    ALM = 'Алматинская'
    ATY = 'Атырауская'
    VOS = 'Восточно-Казахстанская'
    ZHA = 'Жамбылская'
    ZAP = 'Западно-Казахстанская'
    KAR = 'Карагандинская'
    KOS = 'Костанайская'
    KYZ = 'Кызылординская'
    MAN = 'Мангистауская'
    PAV = 'Павлодарская'
    SEV = 'Северо-Казахстанская'
    TUR = 'Туркестанская'

    LOCATION_CHOICES = (
        (GNUR, _('г. Нур-Султан')),
        (GALM, _('г. Алматы')),
        (GSHY, _('г. Шымкент')),
        (AKM, _('Акмолинская')),
        (AKT, _('Актюбинская')),
        (ALM, _('Алматинская')),
        (ATY, _('Атырауская')),
        (VOS, _('Восточно-Казахстанская')),
        (ZHA, _('Жамбылская')),
        (ZAP, _('Западно-Казахстанская')),
        (KAR, _('Карагандинская')),
        (KOS, _('Костанайская')),
        (KYZ, _('Кызылординская')),
        (MAN, _('Мангистауская')),
        (PAV, _('Павлодарская')),
        (SEV, _('Северо-Казахстанская')),
        (TUR, _('Туркестанская')),
    )

    # location = models.CharField(choices=LOCATION_CHOICES, default=GNUR, max_length=255, blank=False, null=False, verbose_name=_('Место жительства'))
    location = models.CharField(max_length=255, blank=False, null=False, verbose_name=_('Место жительства'))
    career = models.CharField(max_length=255, blank=True, verbose_name=_('Род деятельности'))
    wish_type = models.CharField(max_length=255, blank=False, null=False, verbose_name=_('Пожелание/Предложение'))
    # wish_type2 = models.CharField(max_length=255, verbose_name=_('Подтип №2'))
    body = models.TextField(max_length=255 * 10, blank=False, null=False, verbose_name=_('Текст'))
    timestamp = models.DateTimeField(blank=False, auto_now_add=True, verbose_name=_('Дата создания'))
    isShown = models.BooleanField(default=False, verbose_name=_('Показать на сайте'))
    WISH = "Пожелание"
    OFFER = "Предложение"
    # APPEAL = "Обращение"

    FEEDBACK_CHOICES = (
        (WISH, _('Пожелание')),
        (OFFER, _('Предложение')),
        # (APPEAL, _('Обращение')),
    )

    type = models.CharField(choices=FEEDBACK_CHOICES, default=WISH, max_length=100, db_index=True, verbose_name=_("Тип"))

    class Meta:
        verbose_name = _("Пожелание")
        verbose_name_plural = _("Пожелания")

    def __str__(self):
        return self.author


class NewsKZ(models.Model):
    link = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Ссылка'))
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Название'))
    description = models.TextField(max_length=140, blank=True, null=True, verbose_name=_('Описание'))
    body = HTMLField(blank=True, null=True, verbose_name=_('Текст'))
    timestamp = models.DateTimeField(blank=False, auto_now_add=True, verbose_name=_('Дата создания'))

    class Meta:
        verbose_name = _("Новость (Kaz)")
        verbose_name_plural = _("Новости (Kaz)")

    def __str__(self):
        return self.link


class NewsKZMedia(models.Model):
    file = models.FileField(upload_to=uploaded_filename, blank=True, null=True)
    newsKZ = models.ForeignKey(NewsKZ, on_delete=models.CASCADE, related_name='newsKZ')

    class Meta:
        verbose_name = _("Фото")
        verbose_name_plural = _("Фото")


class NewsKZVideo(models.Model):
    file = models.FileField(upload_to=uploaded_filename, blank=True, null=True)
    newKZ = models.ForeignKey(NewsKZ, on_delete=models.CASCADE, related_name='newKZ')

    class Meta:
        verbose_name = _("Видео")
        verbose_name_plural = _("Видео")


class Field(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True, db_index=True, verbose_name=_('Название'))

    class Meta:
        verbose_name = _("Месторождение")
        verbose_name_plural = _("Месторождения")


class Well(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True, db_index=True, verbose_name=_('Название'))
    field = models.ForeignKey(Field, blank=False, null=False, on_delete=models.CASCADE, related_name='fields')

    class Meta:
        verbose_name = _("Скважина")
        verbose_name_plural = _("Скважины")


class WellMatrix(models.Model):
    well = models.ForeignKey(Well, blank=False, null=False, on_delete=models.CASCADE, related_name='wells')
    fluid = models.FloatField(default=0, db_index=True, verbose_name=_('Замерная жидкость'))
    teh_rej_fluid = models.FloatField(default=0, db_index=True, verbose_name=_('Техрежим жидкости'))
    teh_rej_oil = models.FloatField(default=0, db_index=True, verbose_name=_('Техрежим нефти'))
    teh_rej_water = models.FloatField(default=0, db_index=True, verbose_name=_('Обводненность'))
    timestamp = models.DateTimeField(blank=False, verbose_name=_('Дата замера'))

    class Meta:
        verbose_name = _("Матрица скважины")
        verbose_name_plural = _("Матрица скважин")


class FieldBalance(models.Model):
    field = models.ForeignKey(Field, blank=False, null=False, on_delete=models.CASCADE, related_name='bal_fields')
    transport_balance = models.FloatField(default=0, db_index=True, verbose_name=_('Автомобильные весы'))
    ansagan_balance = models.FloatField(default=0, db_index=True, verbose_name=_('Весы по Ансаган'))
    timestamp = models.DateTimeField(blank=False, verbose_name=_('Дата замера'))

    class Meta:
        verbose_name = _("Баланс по месторождению")
        verbose_name_plural = _("Баланс по месторождениям")
