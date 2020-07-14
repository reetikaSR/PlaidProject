# Generated by Django 3.0.8 on 2020-07-14 15:40

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('plaid_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='plaidtoken',
            name='institution_id',
            field=models.CharField(default='', max_length=64),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='plaidtoken',
            name='item_id',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterUniqueTogether(
            name='plaidtoken',
            unique_together={('user', 'institution_id')},
        ),
        migrations.AlterIndexTogether(
            name='plaidtoken',
            index_together={('user', 'institution_id')},
        ),
    ]