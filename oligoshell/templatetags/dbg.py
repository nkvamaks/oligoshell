from django import template
register = template.Library()


@register.simple_tag(takes_context=True)
def set_breakpoint(context):
    breakpoint()
