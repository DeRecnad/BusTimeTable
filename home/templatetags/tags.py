from django.http import HttpResponse
from django import template

register = template.Library()


@register.simple_tag
def submit():
    return 1
