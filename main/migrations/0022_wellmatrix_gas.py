# Generated by Django 2.1 on 2019-07-04 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_auto_20190701_2132'),
    ]

    operations = [
        migrations.AddField(
            model_name='wellmatrix',
            name='gas',
            field=models.FloatField(db_index=True, default=0, verbose_name='Газ'),
        ),
    ]
