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


class Field(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True, db_index=True, verbose_name=_('Название'))
    density = models.FloatField(default=0.8, verbose_name=_('Плотность'))

    class Meta:
        verbose_name = _("Месторождение")
        verbose_name_plural = _("Месторождения")

    def __str__(self):
        return self.name


class Well(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True, db_index=True, verbose_name=_('Название'))
    field = models.ForeignKey(Field, blank=False, null=False, on_delete=models.CASCADE, related_name='fields')

    class Meta:
        verbose_name = _("Скважина")
        verbose_name_plural = _("Скважины")

    def __str__(self):
        return self.name


class WellMatrix(models.Model):
    well = models.ForeignKey(Well, blank=False, null=False, on_delete=models.CASCADE, related_name='wells')
    fluid = models.FloatField(default=0, verbose_name=_('Замерная жидкость'))
    teh_rej_fluid = models.FloatField(default=0, verbose_name=_('Техрежим жидкости'))
    teh_rej_oil = models.FloatField(default=0, verbose_name=_('Техрежим нефти'))
    teh_rej_water = models.FloatField(default=0, verbose_name=_('Обводненность'))
    gas = models.FloatField(default=0, verbose_name=_('Газ'))
    timestamp = models.DateTimeField(blank=False, verbose_name=_('Дата замера'))

    class Meta:
        verbose_name = _("Матрица скважины")
        verbose_name_plural = _("Матрица скважин")


class FieldBalance(models.Model):
    field = models.ForeignKey(Field, blank=False, null=False, on_delete=models.CASCADE, related_name='bal_fields')
    transport_balance = models.FloatField(default=0, verbose_name=_('Автомобильные весы (жидкость)'))
    ansagan_balance = models.FloatField(default=0, verbose_name=_('Весы по Ансаган (жидкость)'))
    transport_brutto = models.FloatField(default=0, verbose_name=_('Автомобильные весы (брутто)'))
    ansagan_brutto = models.FloatField(default=0, verbose_name=_('Весы по Ансаган (брутто)'))
    transport_netto = models.FloatField(default=0, verbose_name=_('Автомобильные весы (нетто)'))
    ansagan_netto = models.FloatField(default=0, verbose_name=_('Весы по Ансаган (нетто)'))
    transport_density = models.FloatField(default=0, verbose_name=_('Автомобильные весы (плотность)'))
    ansagan_density = models.FloatField(default=0, verbose_name=_('Весы по Ансаган (плотность)'))

    agzu_fluid = models.FloatField(default=0, verbose_name=_('Замер жидкости по скважинам'))
    agzu_oil = models.FloatField(default=0, verbose_name=_('Замер нефти по скважинам'))
    teh_rej_fluid = models.FloatField(default=0, verbose_name=_('Замер по Тех. жидкости'))
    teh_rej_oil = models.FloatField(default=0, verbose_name=_('Замер по Тех. нефти'))

    timestamp = models.DateField(blank=False, verbose_name=_('Дата замера'))

    class Meta:
        verbose_name = _("Баланс по месторождению")
        verbose_name_plural = _("Баланс по месторождениям")


class Production(models.Model):
    well = models.ForeignKey(Well, blank=False, null=False, on_delete=models.CASCADE, related_name='rev_wells')
    calc_time = models.FloatField(default=0, verbose_name=_('Время замера'))
    teh_rej_fluid = models.FloatField(default=0, verbose_name=_('Техрежим жидкости'))
    teh_rej_oil = models.FloatField(default=0, verbose_name=_('Техрежим нефти'))
    teh_rej_water = models.FloatField(default=0, verbose_name=_('Обводненность'))
    fluid = models.FloatField(default=0, verbose_name=_('Замерная жидкость'))
    gas = models.FloatField(default=0, verbose_name=_('Газ'))
    density = models.FloatField(default=0, verbose_name=_('Плотность'))
    stop_time = models.FloatField(default=0, verbose_name=_('Простои'))
    timestamp = models.DateField(blank=False, verbose_name=_('Дата'))

    class Meta:
        verbose_name = _("Замерная добыча")
        verbose_name_plural = _("Замерные добычи")


class ParkProduction(models.Model):
    field = models.ForeignKey(Field, blank=False, null=False, on_delete=models.CASCADE, related_name='park_fields')
    fluid_beg = models.FloatField(default=0, verbose_name=_('Жидкость на начало'))
    fluid_end = models.FloatField(default=0, verbose_name=_('Жидкость на конец'))
    teh_rej_water = models.FloatField(default=0, verbose_name=_('Обводненность'))
    fluid_brutto = models.FloatField(default=0, verbose_name=_('Добыча по весам (брутто)'))
    needs = models.FloatField(default=0, verbose_name=_('Собственные нужды'))
    pump = models.FloatField(default=0, verbose_name=_('Откачки воды'))
    timestamp = models.DateField(blank=False, verbose_name=_('Дата'))

    class Meta:
        verbose_name = _("Замерная добыча")
        verbose_name_plural = _("Замерные добычи")


# class ReverseCalculation(models.Model):
#     field = models.ForeignKey(Field, blank=False, null=False, on_delete=models.CASCADE, related_name='rev_fields')
#     fluid = models.FloatField(default=0, verbose_name=_('Замерная жидкость'))
#     oil = models.FloatField(default=0, verbose_name=_('Замерная нефть'))
#     park_fluid = models.FloatField(default=0, verbose_name=_('Парковая жидкость'))
#     park_oil = models.FloatField(default=0, verbose_name=_('Парковая нефть'))
#     coeff_fluid = models.FloatField(default=0, verbose_name=_('Парковый коэф. жидкости'))
#     coeff_oil = models.FloatField(default=0, verbose_name=_('Парковый коэф. нефти'))
#     timestamp = models.DateField(blank=False, verbose_name=_('Дата'))
#
#     class Meta:
#         verbose_name = _("Обратный расчет")
#         verbose_name_plural = _("Обратные расчеты")

