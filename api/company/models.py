# encoding: utf-8

from django.db import models
from django.db.models import Avg
from account.models import Address, ConsumerUser
from django.utils.translation import ugettext_lazy as _


class Company(models.Model):
    name = models.CharField('Nome', max_length=255)
    cnpj = models.CharField('CNPJ', max_length=18, null=True, blank=True)
    company_name = models.CharField(u'Razão social', max_length=255, null=True, blank=True)
    email = models.EmailField(verbose_name=_(u'Email'), max_length=255, null=True, blank=True)
    address = models.ForeignKey(Address, verbose_name=u'Endereço', blank=True, null=True)
    phone1 = models.CharField(u'Telefone 1', max_length=15, null=True, blank=True)
    phone2 = models.CharField(u'Telefone 2', max_length=15, null=True, blank=True)
    active = models.BooleanField('Ativo', default=1)
    total = models.DecimalField(decimal_places=2, max_digits=30, verbose_name=u'total', default=0)
    deleted = models.BooleanField('Deletado', default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _(u'Empresa')
        verbose_name_plural = _(u'Empresas')

    def __unicode__(self):
        return self.name

    def get_rating(self):
        try:
            return "%.2f" % self.ratings.all().aggregate(Avg('vote'))['vote__avg']
        except:
            return 0


class Review(models.Model):
    company = models.ForeignKey(Company, related_name='ratings')
    user = models.ForeignKey(ConsumerUser)
    vote = models.IntegerField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)