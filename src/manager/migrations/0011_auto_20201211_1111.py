# Generated by Django 3.1.4 on 2020-12-11 08:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0010_auto_20201209_1007'),
    ]

    operations = [
        migrations.RenameField(
            model_name='book',
            old_name='likes1',
            new_name='users_like',
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='likes2',
            new_name='users_like',
        ),
        migrations.AlterField(
            model_name='likebookuser',
            name='book',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='liked_user_table', to='manager.book'),
        ),
    ]