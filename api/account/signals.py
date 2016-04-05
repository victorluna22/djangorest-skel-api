# -*- coding: utf-8 -*-
from django.dispatch.dispatcher import Signal



def pre_save_address_receiver(sender, instance, **kwargs):
    from .models import Address
    from django.contrib.gis.geos import GEOSGeometry

    addr = u'%s %s, %s %s - %s' % (instance.street, instance.number, instance.neighborhood, instance.city.name, instance.city.state.name)
    result = Address.objects.geocodeGoogle(addr.encode('utf8'))
    if result['results']:
        location = result['results'][0]['geometry']['location']
        point = GEOSGeometry('POINT(%s %s)' % (location['lat'], location['lng']), srid=4326)
        instance.location = point

def pos_save_forgot_password(sender, instance, created, **kwargs):
    from .models import SendMail
    from django.conf import settings

    if created:
        context = "{'hash': '%s', 'name': '%s'}" % (instance.hash, instance.user.get_short_name())
        SendMail.objects.create(email_from=settings.EMAIL_FROM, to=instance.user.email, subject='[Stepbox] Esqueci minha senha', template='email/forgot_password.html', context=context)


def pos_save_sendmail(sender, instance, created, **kwargs):
    from django.template import Context
    from django.template.loader import render_to_string, get_template
    from django.core.mail import EmailMessage
    import ast

    if created:
        context = {}
        if instance.context:
            context = ast.literal_eval(instance.context)
        message = get_template(instance.template).render(Context(context))
        msg = EmailMessage(instance.subject, message, to=[instance.to], from_email=instance.email_from)
        msg.content_subtype = 'html'
        msg.send()


