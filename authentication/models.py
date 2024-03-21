from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db import IntegrityError
from django.core.validators import MinLengthValidator
from django.conf import settings

# Create your models here.


class CustomUser(models.Model):
    name = models.CharField(_("name"), max_length=50)
    surname = models.CharField(_("surname"), max_length=50)
    phone = models.CharField(_("phone_number"), max_length=13)
    email = models.CharField(_("email"), max_length=50)
    address = models.CharField(_("address"), max_length=200)
    turkish_id_number = models.CharField(_("turkish_id_number"), max_length=11)
    password = models.CharField(_("password"), max_length=16, validators=[
                                MinLengthValidator(4)])