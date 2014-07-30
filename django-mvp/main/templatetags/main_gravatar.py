from django import template
from urllib.parse import urlencode
import hashlib

register = template.Library()

@register.simple_tag
def gravatar_img(email, size=140):
    url = get_url(email, size)
    return '''<img class="img-circle" src="%s" height="%s" width="%s" alt="user.avatar" />''' % (url, size, size)
  
def get_url(email, size=140):
    default = 'http://img1.wikia.nocookie.net/__cb20091118055536/starwars/images/e/e2/SwKOTOR25cropped.jpg'
    query_params = urlencode([('s', str(size)), ('d', default)])
    
    return ('http://www.gravatar.com/avatar/' +
            hashlib.md5(email.lower().encode('utf-8')).hexdigest() +
            '?' + query_params)