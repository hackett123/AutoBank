# Generated by Django 3.2.5 on 2021-07-11 18:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_recurring'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recurring',
            name='purchase_type',
        ),
    ]
