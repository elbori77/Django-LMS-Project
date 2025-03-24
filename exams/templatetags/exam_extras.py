from django import template

register = template.Library()

@register.filter
def get_option(question, letter):
    return getattr(question, f"option_{letter.lower()}", "")
