# Generated by Django 3.1.2 on 2020-10-14 16:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_broadcast'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Creation date.')),
                ('updated', models.DateTimeField(auto_now=True, help_text='Date of last update.')),
                ('text', models.CharField(max_length=500)),
            ],
            options={
                'verbose_name': 'message',
                'verbose_name_plural': 'messages',
                'db_table': 'messages',
            },
        ),
        migrations.AddField(
            model_name='broadcast',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name='broadcast',
            index=models.Index(fields=['created'], name='broadcasts_created_c465e9_idx'),
        ),
        migrations.AddField(
            model_name='message',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='messages', to=settings.AUTH_USER_MODEL, verbose_name='author'),
        ),
        migrations.AddField(
            model_name='message',
            name='broadcast',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.broadcast', verbose_name='broadcast'),
        ),
        migrations.AddField(
            model_name='message',
            name='deleter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='deleter'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['created'], name='messages_created_1499d8_idx'),
        ),
    ]
