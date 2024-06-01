import uuid

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.db import IntegrityError, models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        email = email.lower()
        user = self.model(email=email, **extra_fields)
        
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(_('email address'), unique=True)
    full_name = models.CharField(_('full name'), max_length=255, null=True, blank=True)
    turkish_id_number = models.CharField(_("turkish_id_number"), max_length=11)
    phone_number = models.CharField(_("phone_number"), max_length=13)
    sms_notification = models.BooleanField(_("sms_notification"), default=False)
    email_notification = models.BooleanField(_("email_notification"), default=False)

    REQUIRED_FIELDS = ['email', 'phone_number', 'password', 'turkish_id_number', 'first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return str(self.username) 

    def save(self, *args, **kwargs):
        if not self.id: 
            self.username = uuid.uuid4()
            self.full_name = self.first_name + " " + self.last_name
            
        super().save(*args, **kwargs)


class UserRole(models.Model):
    name = models.CharField(_("name"), max_length=250)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    modified_at = models.DateTimeField(_('modified at'), auto_now=True)
    is_deleted = models.BooleanField(_("is deleted"), default=False)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name = _('User Role')
        verbose_name_plural = _('User Roles')
        ordering = ('created_at',)
