# Generated by Django 2.1 on 2019-10-20 10:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0034_auto_20191001_2336'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParkOil',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ttn', models.IntegerField(default=0, verbose_name='Номер ТТН')),
                ('contractor', models.CharField(blank=True, max_length=20, null=True, verbose_name='Подрядчик')),
                ('gos_num', models.CharField(blank=True, max_length=20, null=True, verbose_name='Гос.номер')),
                ('driver', models.CharField(blank=True, max_length=20, null=True, verbose_name='Ф.И.О. водителя')),
                ('fluid_brutto', models.FloatField(default=0, verbose_name='Добыча по весам (брутто)')),
                ('go_to', models.TimeField(verbose_name='Время заезда на ГУ')),
                ('go_out', models.TimeField(verbose_name='Время выезда из ГУ')),
                ('start', models.TimeField(verbose_name='Начало налива')),
                ('end', models.TimeField(verbose_name='Конец налива')),
                ('timestamp', models.DateField(verbose_name='Дата')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='oil_fields', to='main.Field')),
            ],
            options={
                'verbose_name': 'Журнал сдачи нефти',
                'verbose_name_plural': 'Журнал сдачи нефти',
            },
        ),
    ]