from django import template

register = template.Library()

@register.simple_tag
def is_shelter(user):
    """
    Returns True if the user is a Shelter, False otherwise.
    """
    return user.is_authenticated and getattr(user, 'type_user', None) == 'Shelter'

@register.simple_tag
def is_adopter(user):
    """
    Returns True if the user is an Adopter, False otherwise.
    """
    return user.is_authenticated and getattr(user, 'type_user', None) == 'Adopter'


@register.filter
def is_adopter(user):
    return user.is_authenticated and user.type_user == "Adopter"

@register.filter
def is_shelter(user):
    return user.is_authenticated and user.type_user == "Shelter"

# @register.filter
# def has_permission(user, perm_name):
#     return user.has_perm(perm_name)