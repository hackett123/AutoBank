# Generated by Django 3.2.5 on 2021-07-03 16:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='purchase_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to='main.purchasetype'),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='purchased_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='purchasetype',
            name='type',
            field=models.CharField(max_length=200),
        ),
    ]