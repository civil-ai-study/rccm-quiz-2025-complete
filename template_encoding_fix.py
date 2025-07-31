
from flask import make_response, render_template

def render_template_utf8(template_name, **context):
    """UTF-8エンコーディングを保証するrender_template"""
    response = make_response(render_template(template_name, **context))
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response

# 使用例:
# return render_template_utf8('index.html', data=data)
