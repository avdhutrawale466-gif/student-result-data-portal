from django import template


register = template.Library()


@register.filter
def get_item(dictionary, key):
    try:
        return dictionary.get(key)
    except:
        return None


@register.filter
def get_sgpa(dictionary, key):
    try:
        data = dictionary.get(key)

        if data:
            return data.get("sgpa", 0)

        return 0

    except:
        return 0