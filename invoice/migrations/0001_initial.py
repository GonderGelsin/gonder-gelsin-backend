# Generated by Django 4.2.7 on 2024-10-04 13:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BillingAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_line_1', models.CharField(max_length=255, verbose_name='address line 1')),
                ('address_line_2', models.CharField(blank=True, max_length=255, null=True, verbose_name='address line 2')),
                ('city', models.CharField(max_length=100, verbose_name='city')),
                ('state', models.CharField(max_length=100, verbose_name='state')),
                ('postal_code', models.CharField(max_length=20, verbose_name='postal code')),
                ('country', models.CharField(max_length=100, verbose_name='country')),
                ('is_default', models.BooleanField(default=False, verbose_name='default address')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='billing_addresses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Billing Address',
                'verbose_name_plural': 'Billing Addresses',
            },
        ),
    ]