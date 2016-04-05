# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.gis.db import models as gis_models
from datetime import datetime
import re
import base64
import urllib
import json
import uuid
from geopy.geocoders import Nominatim
from gcm.models import AbstractDevice
from django.db.models.signals import pre_save, post_save
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from rest_framework.exceptions import APIException
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from .signals import pre_save_address_receiver, pos_save_forgot_password, pos_save_sendmail

try:
    from django.utils.timezone import now as datetime_now
except ImportError:
    datetime_now = datetime.now

SHA1_RE = re.compile('^[a-f0-9]{40}$')

GENDER_CHOICES = (('M', _(u'Masculino')),
                  ('F', _(u'Feminino')),)

PROVIDER_CHOICES = (
    (u'facebook', u'Facebook'),
)


CONSUMER = 1
COMPANY = 2
ADM = 3

USER_TYPES = (
    (CONSUMER, "Consumidor"),
    (COMPANY, u"Empresa"),
    (ADM, "Administrador"),
    )


class StepUserManager(BaseUserManager):
    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()

        if email:
            # raise ValueError(_(u'É necessário um email válido.'))
            email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True,
                                 **extra_fields)

    def validate_hash_activate(self, hash):
        try:
            string = base64.b64decode(hash)
            id, email = string.split('!@#')
            if self.filter(id=id, email=email).exists():
                return self.get(id=id)
            return None
        except:
            return None


class StepAbstractUser(AbstractBaseUser, PermissionsMixin):
    """
    A fully featured User model with admin-compliant permissions that uses
    a full-length email field as the username.

    Email and password are required. Other fields are optional.
    """
    # TODO: make full_name obligatory
    full_name = models.CharField(verbose_name=_(u'Nome'), max_length=120, blank=True, null=True)
    username = models.CharField(blank=True, null=True, max_length=120)
    email = models.EmailField(verbose_name=_(u'Email'), max_length=254, unique=True, db_index=True, null=True, blank=True)
    is_staff = models.BooleanField(verbose_name=_(u'Membro da equipe'), default=False,
                                   help_text=_(u'Designa se este usuário pode acessar este site admin.'))
    is_active = models.BooleanField(verbose_name=_(u'Ativo'), default=True,
                                    help_text=_(u'Designa se este usuário está ativo.'
                                                u'Desmarque esta opção ao invés de deletar a conta.'))
    date_joined = models.DateTimeField(verbose_name=_(u'Criado em'), auto_now_add=True)
    deleted = models.BooleanField('Deletado', default=0)
    objects = StepUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = _(u'usuário do Stepbox')
        verbose_name_plural = _(u'usuários do Stepbox')


    def is_consumer(self):
        try:
            if self.consumeruser:
                return True
        except:
            return False

    def is_company(self):
        try:
            if self.companyuser:
                return True
        except:
            return False

    def is_adm(self):
        try:
            if self.admuser:
                return True
        except:
            return False

    def get_user(self):
        if self.is_consumer():
            return self.consumeruser
        elif self.is_company():
            return self.companyuser
        elif self.is_adm():
            return self.admuser


    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.email)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        return self.full_name.strip().title() if self.full_name else self.email

    def get_hash_activate(self):
        return base64.b64encode("%s!@#%s" % (self.id, self.email))


    def get_short_name(self):
        """
        Returns the short name for the user.
        """

        return self.full_name.split()[0] if self.full_name else self.email


    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, 'email@domain.com', [self.email])

# class Country(models.Model):
#     name = models.CharField(max_length=100)
#     acronym = models.CharField(max_length=6)
#     acronym3 = models.CharField(max_length=6)

#     def __unicode__(self):
#         return self.name

#     class Meta:
#         verbose_name = _(u'País')
#         verbose_name_plural = _(u'Países')

class State(models.Model):
    name = models.CharField(max_length=100)
    acronym = models.CharField(max_length=2)
    def __unicode__(self):
        return u'%s-%s' % (self.name, self.acronym)

    class Meta:
        verbose_name = _(u'Estado')
        verbose_name_plural = _(u'Estados')

class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State)
    def __unicode__(self):
        return u'%s - %s' % (self.name, self.state.acronym)

    class Meta:
        verbose_name = _(u'Cidade')
        verbose_name_plural = _(u'Cidades')


class AddressManager(models.Manager):
    def geocodeCorreios(self, cep):
        url = 'https://viacep.com.br/ws/%s/json/' % cep.replace('-', '')
        data = urllib.urlopen(url).read()
        try:
            result = json.loads(data)
            result['address'] = '%s, %s %s - %s' % (result['logradouro'], result['bairro'], result['localidade'], result['uf'])
            return result
        except:
            raise APIException('No results')
        

    def geocodeGoogle(self, location):
        location = urllib.quote_plus(location)
        request = "http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false" % (location)
        data = urllib.urlopen(request).read()
        result = json.loads(data)
        return result

    def geocoderGeoPyLatLon(self, lat, lon):
        geolocator = Nominatim()
        if lat and lon:
            coord = "%s, %s" % (lat, lon)
            location = geolocator.reverse(coord)
            if location.raw:
                return location.raw['address']
            return None

class Address(models.Model):
    street = models.CharField('Rua', max_length=255, null=True, blank=True)
    number = models.CharField(u'Número', max_length=30, null=True, blank=True)
    complement = models.CharField('Complemento', max_length=100, null=True, blank=True)
    neighborhood = models.CharField('Bairro', max_length=255, null=True, blank=True)
    city = models.ForeignKey(City, verbose_name='Cidade')
    cep = models.CharField('CEP', max_length=9, null=True, blank=True)
    location = gis_models.PointField(u"longitude/latitude", geography=True, blank=True, null=True)
    deleted = models.BooleanField('Deletado', default=0)

    objects = AddressManager()
    class Meta:
        verbose_name = _(u'Endereço')
        verbose_name_plural = _(u'Endereços')

    # def save(self, *args, **kwargs):
    #     data = self.objects.geocodeGoogle('%s %s, %s %s - %s' % (self.street, self.number, self.neighborhood, self.city.name, self.city.state.name))
    #     import pdb;pdb.set_trace()
    #     return super(Address, self).save(*args, **kwargs)



class ConsumerUser(StepAbstractUser):
    birthday = models.DateField(verbose_name=_(u'Data de nascimento'), blank=True, null=True,
                                help_text=_(u'Insira sua data de nascimento.'))
    gender = models.CharField(verbose_name=_(u'Sexo'), max_length=1, blank=True, null=True, choices=GENDER_CHOICES)
    phone = models.CharField('Telefone', max_length=15, blank=True, null=True)
    facebook = models.CharField(max_length=255, blank=True, null=True)
    newsletter = models.BooleanField(default=1)
    address = models.ManyToManyField(Address, verbose_name=u'Endereços', through='AddressConsumerUser')
    objects = StepUserManager()

    class Meta:
        verbose_name = _(u'Usuário consumidor')
        verbose_name_plural = _(u'Usuários consumidores')
        

class AddressConsumerUser(models.Model):
    address = models.ForeignKey(Address)
    user = models.ForeignKey(ConsumerUser)
    active = models.BooleanField(default=0)


class Employee(StepAbstractUser):
    company = models.ForeignKey('company.Company', related_name='employees')
    is_admin = models.BooleanField(default=0)
    objects = StepUserManager()

    class Meta:
        verbose_name = _(u'Usuário da empresa')
        verbose_name_plural = _(u'Usuários da empresa')

class AdmUser(StepAbstractUser):
    objects = StepUserManager()

    class Meta:
        verbose_name = _(u'Usuário administrador')
        verbose_name_plural = _(u'Usuários administradores')


class DeviceUser(AbstractDevice):
    user = models.ForeignKey(ConsumerUser, related_name='devices')

class File(models.Model):
    image = models.ImageField(u'Imagem', upload_to='images/')


class UserForgotPassword(models.Model):
    user = models.ForeignKey(ConsumerUser, related_name='requests_forgot')
    hash = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)


class SendMail(models.Model):
    email_from = models.EmailField(max_length=150)
    to = models.EmailField(max_length=150)
    subject = models.CharField(max_length=255)
    body = models.TextField(null=True, blank=True)
    template = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    result = models.TextField(null=True, blank=True)
    context = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)




pre_save.connect(pre_save_address_receiver, sender=Address, dispatch_uid='stepbox.account.signals.pre_save_address')
post_save.connect(pos_save_forgot_password, sender=UserForgotPassword, dispatch_uid='stepbox.account.signals.pos_save_forgot_password')
post_save.connect(pos_save_sendmail, sender=SendMail, dispatch_uid='stepbox.account.signals.pos_save_sendmail')




