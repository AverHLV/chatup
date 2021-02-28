# Generated by Django 3.1.7 on 2021-02-28 13:49

import apps.chat.models
from django.conf import settings
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('watchtime', models.PositiveIntegerField(default=0, help_text='Total time of the watched broadcasts (seconds).')),
                ('username_color', models.CharField(default='000000', help_text='Username color in chat, hex format.', max_length=6, validators=[django.core.validators.RegexValidator('^(?:[0-9a-fA-F]{3}){2}$')])),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'db_table': 'users',
            },
            managers=[
                ('objects', apps.chat.models.CustomUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Broadcast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Creation date.')),
                ('updated', models.DateTimeField(auto_now=True, help_text='Date of last update.')),
                ('title', models.CharField(max_length=200, unique=True)),
                ('description', models.CharField(blank=True, max_length=1000, null=True)),
                ('is_active', models.BooleanField(default=False, help_text='Whether broadcast is active now.')),
                ('source_link', models.URLField(help_text='Link to broadcast source.', verbose_name='source link')),
                ('streamer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='broadcasts', to=settings.AUTH_USER_MODEL, verbose_name='streamer')),
            ],
            options={
                'verbose_name': 'broadcast',
                'verbose_name_plural': 'broadcasts',
                'db_table': 'broadcasts',
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('name_ru', models.CharField(max_length=500)),
                ('sid', models.CharField(choices=[('user', 'User'), ('vip', 'VIP'), ('moderator', 'Moderator'), ('administrator', 'Administrator'), ('streamer', 'Streamer')], max_length=20, unique=True)),
            ],
            options={
                'verbose_name': 'role',
                'verbose_name_plural': 'roles',
                'db_table': 'roles',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Creation date.')),
                ('updated', models.DateTimeField(auto_now=True, help_text='Date of last update.')),
                ('text', models.CharField(max_length=500)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='messages', to=settings.AUTH_USER_MODEL, verbose_name='author')),
                ('broadcast', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.broadcast', verbose_name='broadcast')),
                ('deleter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='deleter')),
            ],
            options={
                'verbose_name': 'message',
                'verbose_name_plural': 'messages',
                'db_table': 'messages',
            },
        ),
        migrations.CreateModel(
            name='BroadcastToUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('broadcast', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.broadcast')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'broadcasts_to_users',
            },
        ),
        migrations.AddField(
            model_name='broadcast',
            name='watchers',
            field=models.ManyToManyField(through='chat.BroadcastToUser', to=settings.AUTH_USER_MODEL, verbose_name='watchers'),
        ),
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='users', to='chat.role', verbose_name='role'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['created'], name='messages_created_1499d8_idx'),
        ),
        migrations.AddIndex(
            model_name='broadcast',
            index=models.Index(fields=['created'], name='broadcasts_created_c465e9_idx'),
        ),
    ]
