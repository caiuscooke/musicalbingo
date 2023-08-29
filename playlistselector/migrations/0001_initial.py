# Generated by Django 4.2.4 on 2023-08-21 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccessToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.CharField(max_length=255, unique=True)),
                ('token_type', models.CharField(max_length=255)),
                ('expires_at', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('playlist_url', models.URLField(max_length=255, unique=True)),
                ('playlist_uri', models.CharField(max_length=255, unique=True)),
            ],
        ),
    ]