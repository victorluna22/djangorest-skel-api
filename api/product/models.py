# encoding: utf-8
from django.db import models
from company.models import Company
from django.contrib.gis.db import models as gis_models
from django.utils.translation import ugettext_lazy as _

NO_TYPE = 'nenhum';PILL = 'pilula';DROPS = 'gotas';CAPSULE = 'capsula';GEL = 'gel';SPRAY = 'spray';CREAM = 'creme';
PRODUCT_TYPES = (
    (NO_TYPE, u"Nenhum"),
    (PILL, u"Pílula"),
    (DROPS, u"Gotas"),
    (CAPSULE, u"Capsula"),
    (GEL, u"Gel"),
    (SPRAY, u"Spray"),
    (CREAM, u"Creme"),
    )

GENERIC = 'generico';SIMILAR = 'similar';BRANDED = 'de-marca';
MEDICAMENT_TYPES = (
    (NO_TYPE, u"Nenhum"),
    (GENERIC, u"Genérico"),
    (SIMILAR, u"Similar"),
    (BRANDED, u"De marca"),
    )


class Product(models.Model):
    name = models.CharField('Nome', max_length=255)
    company = models.ForeignKey(Company, verbose_name = u'Empresa')
    price = models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name=u'Preço')
    type = models.CharField('Tipo', max_length=100, choices=PRODUCT_TYPES, default=NO_TYPE, db_index=True)
    medicament_type = models.CharField('Tipo do medicamento', max_length=100, choices=MEDICAMENT_TYPES, default=NO_TYPE, db_index=True)
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




class ProductBase(models.Model):
    principio_ativo = models.CharField(u'Princípio ativo', max_length=255, null=True, blank=True)
    cnpj = models.CharField(u'CNPJ', max_length=40, null=True, blank=True)
    laboratorio = models.CharField(u'Laboratório', max_length=255, null=True, blank=True)
    codigo_ggrem = models.CharField(u'Código GGREM', max_length=255, null=True, blank=True)
    registro = models.CharField(u'Registro', max_length=255, null=True, blank=True)
    ean = models.CharField(u'EAN', max_length=255, null=True, blank=True)
    produto = models.CharField(u'Produto', max_length=255, null=True, blank=True)
    apresentacao = models.CharField(u'Apresentação', max_length=255, null=True, blank=True)
    classe_terapeutica = models.CharField(u'Classe Terapeutica', max_length=255, null=True, blank=True)
    pf0 = models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name=u'PF 0%')
    pf12 = models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name=u'PF 12%')
    pf17 = models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name=u'PF 17%')
    pf18 = models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name=u'PF 18%')
    pf19 = models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name=u'PF 19%')
    pf17_manaus = models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name=u'PF 17 MANAUS')
    pmc0 = models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name=u'PMC 0%')
    pmc12 = models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name=u'PMC 12%')
    pmc17 = models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name=u'PMC 17%')
    pmc18 = models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name=u'PMC 18%')
    pmc19 = models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name=u'PMC 19%')
    pmc17_manaus = models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name=u'PMC 17 MANAUS')
    restricao_hospitalar = models.BooleanField('Restrição Hospitalar', default=0)
    cap = models.BooleanField('CAP', default=0)
    confaz_87 = models.BooleanField('CONFAZ 87', default=0)
    analise_recursal = models.CharField(u'Análise Recursal', max_length=255, null=True, blank=True)
    ultima_alteracao = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = _(u'Produto Base')
        verbose_name_plural = _(u'Produtos Base')








