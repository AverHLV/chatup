# Generated by Django 3.1.7 on 2021-03-17 16:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_auto_20210316_1733'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='broadcast',
            name='watchers',
        ),
        migrations.DeleteModel(
            name='BroadcastToUser',
        ),
    ]
