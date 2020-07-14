# Generated by Django 3.0.8 on 2020-07-14 15:19

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_id', models.CharField(max_length=128)),
                ('account_owner', models.CharField(max_length=128, null=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('transaction_id', models.CharField(max_length=128, unique=True)),
                ('transaction_date', models.DateTimeField()),
                ('category_id', models.CharField(max_length=64)),
                ('category', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=64), default=list, size=None)),
            ],
        ),
        migrations.CreateModel(
            name='PlaidToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.CharField(max_length=128)),
                ('item_id', models.CharField(max_length=128, unique=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LogEvents',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=64)),
                ('link_session_id', models.CharField(max_length=64, null=True)),
                ('request_id', models.CharField(max_length=64)),
                ('message', models.TextField()),
                ('code', models.CharField(max_length=64)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('available_balance', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('current_balance', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('type', models.CharField(max_length=64)),
                ('sub_type', models.CharField(max_length=64)),
                ('plaid_token', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='plaid_app.PlaidToken')),
            ],
        ),
    ]