from django import template

#register custom template
register = template.Library()

@register.filter
def get_data(dict, key):
    return dict[key]