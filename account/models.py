from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField


class CustomUserManager(UserManager):
    def create_user(self, email, first_name, last_name, password=None,  **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password, **extra_fields):
        user = self.create_user(email, first_name, last_name, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def create_staff(self, email, first_name, last_name, password, **extra_fields):
        user = self.create_user(email, first_name, last_name, password, **extra_fields)
        user.is_staff = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(
        unique=True, help_text=_("Required. Unique User email address.")
    )
    first_name = models.CharField(
        max_length=100, help_text=_("Required. Designates first name of the user.")
    )
    last_name = models.CharField(
        max_length=100, help_text=_("Required. Designates last name of the user."),
        blank=True,
        null=True,
    )
    address = models.CharField(
        max_length=100, help_text=_("Not Required. Designates address of the user."),
        blank=True,
        null=True,
    )
    city = models.CharField(
        max_length=100, help_text=_("Not Required. Designates city of residence."),
        blank=True,
        null=True,
    )
    phone_number = PhoneNumberField(
        help_text=_(
        "Not Required. Designates phone number of the user.\n"
        "Format: +2348123456789"
        ),
        null=True,
        blank=True,
    )
    country = CountryField(
        help_text=_("Not Required. Designates country of the user."),
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

    def get_phone_number(self):
        return self.phone_number

    def get_country(self):
        return self.country
