from django import template

register = template.Library()

@register.filter(name='get_option')
def get_option(question_dict, correct_option_key):
    """
    Usage: {{ question|get_option:question.correctoption }}
    """
    return question_dict.get(f"option{correct_option_key}", "")

@register.filter(name='dict_sum')
def dict_sum(dict):
    s=0;
    for value in dict.keys():
        s+=value
