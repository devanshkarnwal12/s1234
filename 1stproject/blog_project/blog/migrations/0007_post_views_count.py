# Generated by Django 5.1.3 on 2024-11-11 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_post_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='views_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
