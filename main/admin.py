from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group

from main import models
from main.models import Field, Well, WellMatrix, FieldBalance, Production, ParkProduction


class CustomUserCreationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

    class Meta(UserCreationForm.Meta):
        model = models.User
        fields = '__all__'


class CustomUserChangeForm(UserChangeForm):

    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)

    class Meta(UserChangeForm.Meta):
        model = models.User
        fields = '__all__'


@admin.register(models.User)
class UserAdmin(BaseUserAdmin):

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ('email', 'is_admin')
    list_filter = ('is_admin', 'type')
    fieldsets = (
        (None, {'fields': ('email', 'name', 'password', 'type')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'email', 'type', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

    def has_module_permission(self, request):
        if request.user.is_authenticated and (request.user.type == "Администратор"):
            return True
        else:
            return False


admin.site.unregister(Group)


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'density')


@admin.register(Well)
class WellAdmin(admin.ModelAdmin):
    list_display = ('field', 'name')
    search_fields = ('name',)
    list_filter = ('field',)


@admin.register(WellMatrix)
class WellMatrixAdmin(admin.ModelAdmin):
    list_display = ('well', 'fluid', 'gas', 'teh_rej_fluid', 'teh_rej_oil', 'teh_rej_water', 'gas', 'timestamp')
    search_fields = ('well',)


@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    list_display = ('well', 'calc_time', 'fluid', 'teh_rej_fluid', 'teh_rej_oil', 'teh_rej_water',
                    'density', 'stop_time', 'timestamp', 'stop_init', 'stop_reason', 'status')
    search_fields = ('well',)


@admin.register(ParkProduction)
class ParkProductionAdmin(admin.ModelAdmin):
    list_display = ('field', 'fluid_beg', 'fluid_end', 'fluid_brutto', 'fluid_netto', 'teh_rej_water', 'needs', 'pump', 'timestamp')
    list_filter = ('field',)


@admin.register(FieldBalance)
class FieldBalanceAdmin(admin.ModelAdmin):
    list_display = ('field', 'transport_balance', 'ansagan_balance', 'transport_brutto', 'ansagan_brutto',
                    'transport_netto', 'ansagan_netto', 'transport_density', 'ansagan_density',
                    'agzu_fluid', 'agzu_oil', 'teh_rej_fluid', 'teh_rej_oil', 'timestamp')
    list_filter = ('field',)