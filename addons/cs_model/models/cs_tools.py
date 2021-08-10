# -*- coding: utf-8 -*-
import re


# Todo, mover a un repositorio global.
# Convierte un texto html en texto plano.
def html2text(html):

    if not html or len(html)<=0:
        return ""

    """
    Remove HTML from the text.

    html = re.sub(r'(?i)&nbsp;', ' ', html)
    html = re.sub(r'(?i)<br[ \\]*?>', '\n', html)
    html = re.sub(r'(?m)<!--.*?--\s*>', '', html)
    html = re.sub(r'(?i)<ref[^>]*>[^>]*<\/ ?ref>', '', html)
    html = re.sub(r'(?m)<.*?>', '', html)
    html = re.sub(r'(?i)&amp;', '&', html)


    """
    html = re.sub(r'(?i)&nbsp;', ' ', html)
    html = re.sub(r'(?i)</h2>', '. </h2>', html)
    html = re.sub(r'(?m)<.*?>', '', html)
    html = re.sub(r'(?i)<br>', '', html)
    html = re.sub(r'(?i)<br[ \\]*?>', '', html)

    html = html.replace("\n",'')
    html = html.replace("\r",'')

    return html


# Extraer los parrafos de un texto
def extract_paragraphs_from_text(text, n = None, long = 250):
    try:
        text = text[:long+1 ]
        datos = text.split('.')
        datos = datos[:len(datos)-1]

        if n:
            text = '.'.join(datos[0:n])
            text = text

        else:
            text = '.'.join(datos)

    except Exception:
        text = ""

    return text

# Extraer los parrafos de un html
def extract_paragraphs_from_html(html, n = None,long = 250):
    return self.extract_paragraphs_from_text(self.html2text(html),n)
