# encoding: utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _
from account.models import ConsumerUser, Employee
# Create your models here.

class FormMessage(models.Model):
	user = models.ForeignKey(ConsumerUser, related_name='form_messages')
	subject = models.CharField('Assunto', max_length=255)
	message = models.TextField('Mensagem')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = _(u'Fale conosco')
		verbose_name_plural = _(u'Fale conosco')


class FormCompanyMessage(models.Model):
	company = models.ForeignKey(Employee, related_name='form_messages')
	subject = models.CharField('Assunto', max_length=255)
	message = models.TextField('Mensagem')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = _(u'Fale conosco')
		verbose_name_plural = _(u'Fale conosco')