from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, full_name, password=None, **extra_fields):
        if not full_name:
            raise ValueError(_('The Full Name field must be set'))
        extra_fields.setdefault('is_active', True)
        user = self.model(full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(full_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    full_name = models.CharField(max_length=100, unique=True, verbose_name=_("Full Name"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    is_staff = models.BooleanField(default=False, verbose_name=_("Is Staff"))

    objects = UserManager()

    USERNAME_FIELD = 'full_name'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name}"

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name.split()[0]
