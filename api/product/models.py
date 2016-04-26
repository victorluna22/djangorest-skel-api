# encoding: utf-8
from django.db import models
from company.models import Company
from django.contrib.gis.db import models as gis_models
from django.utils.translation import ugettext_lazy as _


class Product(models.Model):
    name = models.CharField('Nome', max_length=255)
    company = models.ForeignKey(Company, verbose_name = u'Empresa')
    price = models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name=u'Preço')
    manufacturer = models.CharField('Fabricante', max_length=255, blank=True, null=True)
    available = models.BooleanField(u'Disponível', default=1)
    obs = models.TextField(u'Observações', blank=True, null=True)
    image = models.CharField(u'Imagem', max_length=255, blank=True, null=True)
    products_related = models.ManyToManyField('self')
    active = models.BooleanField('Ativo', default=1)
    deleted = models.BooleanField('Deletado', default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = gis_models.GeoManager()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u'Produto')
        verbose_name_plural = _(u'Produtos')








