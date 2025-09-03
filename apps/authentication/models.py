import datetime
from random import random
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, Group, PermissionsMixin
import uuid
from PIL import Image
import io
from django.core.files.base import ContentFile


class PrefixedUUIDField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 39)  # 3 (prefix) + 29 (UUID) = 32
        kwargs['unique'] = True
        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        self.model = cls
        self.prefix = model_name_prefix(cls.__name__)

    def pre_save(self, model_instance, add):
        if add and not getattr(model_instance, self.attname):
            value = f"{self.prefix}{uuid.uuid4()}"
            setattr(model_instance, self.attname, value)
            return value
        return super().pre_save(model_instance, add)


def model_name_prefix(model_name):
    prefixes = {
        'User': '0US',
    }
    return prefixes.get(model_name, '0EX')


class UserManager(BaseUserManager):
    def create_user(self, email, first_name=None, last_name=None, phone=None, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = PrefixedUUIDField(primary_key=True)

    email = models.EmailField(verbose_name='email', max_length=255, unique=True)

    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    avatar_color = models.CharField(max_length=7, default='#000000')
    user_avatar = models.ImageField(upload_to='avatars', blank=True)


    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email & Password are required by default.

    def get_full_name(self):
        # The user is identified by their email address
        return str(self.first_name) + " " + str(self.last_name)

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return str(self.first_name) + " " + str(self.last_name)

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        if self.is_active and (self.is_superuser or super().has_perm(perm, obj)):
            return True
        return False

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        if self.is_active and (self.is_superuser or super().has_module_perms(app_label)):
            return True
        return False

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        return self.staff

    @property
    def is_admin(self):
        """Is the user a admin member?"""
        return self.admin

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def redirect_after_edit(self):
        return f'/user/view/{self.id}'

    def is_admin_or_manager(self):
        return self.is_superuser or self.groups.filter(name='Kierownik').exists()

    objects = UserManager()
