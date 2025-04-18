import re
from flask import current_app
from jinja2 import Environment

def regex_findall(pattern, string):
    """
    Custom Jinja2 filter to find all occurrences of a regex pattern in a string
    """
    return re.findall(pattern, string)

def now():
    """
    Return the current datetime
    """
    from datetime import datetime
    return datetime.now()

# Register custom filters
def register_filters(app):
    app.jinja_env.filters['regex_findall'] = regex_findall
    app.jinja_env.globals['now'] = now
