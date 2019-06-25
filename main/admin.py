from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group

from main import models
from main.models import Feedback, NewsKZ, NewsKZMedia, NewsKZVideo, Field, Well, WellMatrix, FieldBalance


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


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('author', 'contact', 'location', 'career', 'wish_type', 'body', 'timestamp', 'isShown', 'type')
    list_filter = ('isShown', 'type')
    search_fields = ('location', )

    def has_module_permission(self, request):
        if request.user.is_authenticated and (request.user.type == "Менеджер" or request.user.type == "Администратор"):
            return True
        else:
            return False


class NewsKZImage(admin.StackedInline):
    model = NewsKZMedia
    extra = 1


class NewsKZVideo(admin.StackedInline):
    model = NewsKZVideo
    extra = 1


@admin.register(NewsKZ)
class NewsKZAdmin(admin.ModelAdmin):
    list_display = ('link', 'title', 'description', 'timestamp')
    search_fields = ('title',)
    inlines = [NewsKZImage, NewsKZVideo]

    def has_module_permission(self, request):
        if request.user.is_authenticated and (request.user.type == "Журналист" or request.user.type == "Администратор"):
            return True
        else:
            return False


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Well)
class WellAdmin(admin.ModelAdmin):
    list_display = ('field', 'name')
    search_fields = ('name',)
    list_filter = ('field',)


@admin.register(WellMatrix)
class WellMatrixAdmin(admin.ModelAdmin):
    list_display = ('well', 'fluid', 'teh_rej_fluid', 'teh_rej_oil', 'teh_rej_water', 'timestamp')
    search_fields = ('well',)


@admin.register(FieldBalance)
class WellMatrixAdmin(admin.ModelAdmin):
    list_display = ('field', 'transport_balance', 'ansagan_balance', 'timestamp')
    list_filter = ('field',)