from django.db import models, transaction
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from common.models import ULIDField
import ulid


class AccountManager(BaseUserManager):
    def create_user(self, request_data, **kwargs):
        now = timezone.now()
        if not request_data['username']:
            raise ValueError('Users must have an username.')

        user = self.model(
            username=request_data['username'],
            email=self.normalize_email(request_data['email']),
            is_active=True,
            last_login=now,
        )

        user.set_password(request_data['password'])
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        request_data = {
            'username': username,
            'email': email,
            'password': password
        }
        user = self.create_user(request_data)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    id = ULIDField(default=ulid.new, primary_key=True, unique=True, editable=False)
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    display_name = models.CharField(_('display name'), max_length=30, blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    balance = models.IntegerField(_('balance'), default=0)

    objects = AccountManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    @classmethod
    def deposit(cls, pk, amount):
        with transaction.atomic():
            account = (cls.objects.select_for_update().get(id=pk))
            account.balance += amount
            account.save()

        return account

    @classmethod
    def withdraw(cls, pk, amount):
        with transaction.atomic():
            account = (cls.objects.select_for_update().get(id=pk))

            if account.balance < amount:
                raise ValueError(_('Insufficient funds'))

            account.balance -= amount
            account.save()

        return account


class Idm(models.Model):
    idm = models.CharField(
        _('IDm Number'),
        max_length=16,
        unique=True,
        error_messages={
            'unique': _("This card is already registered"),
        },)
    name = models.CharField(_('card name'), max_length=255, blank=True, null=True)
    account = models.ForeignKey(Account, verbose_name=_('account'), on_delete=models.CASCADE)
