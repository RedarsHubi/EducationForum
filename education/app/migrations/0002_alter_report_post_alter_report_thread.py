# Generated by Django 5.0.3 on 2024-07-12 16:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='post',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='app.post'),
        ),
        migrations.AlterField(
            model_name='report',
            name='thread',
            field=models.ForeignKey(default=4, on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='app.thread'),
        ),
    ]