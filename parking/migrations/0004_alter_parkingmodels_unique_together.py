# Generated by Django 4.0.6 on 2022-07-16 11:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parking', '0003_alter_parkingmodels_departure_time'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='parkingmodels',
            unique_together={('plate', 'departure_time')},
        ),
    ]
