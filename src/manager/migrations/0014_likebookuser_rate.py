# Generated by Django 3.1.4 on 2020-12-15 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0013_comment_likes'),
    ]

    operations = [
        migrations.AddField(
            model_name='likebookuser',
            name='rate',
            field=models.PositiveIntegerField(default=5),
        ),
    ]