"""Extract current physical colour-sample campaigns from Kvik's public page.

2026-11-01: robots permits these paths. Terms index, store and webshop terms
reviewed; no automated-access prohibition found. Factual metadata only.
"""
import hashlib
import re
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from ..domain import now


def extract_colour_samples(url, html):
    if urlsplit(url).hostname != 'www.kvik.es':
        return []
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
        tag.decompose()
    text = soup.get_text(' ', strip=True)
    results = {}
    for label in soup.find_all(string=re.compile(r'^Muestras de color\s+\w', re.I)):
        name = label.strip()
        if len(name) > 100:
            continue
        # An item-specific free sample delivery statement is required as well
        # as a zero-price request card. Unrelated free-appliance promos fail.
        material = name[len('Muestras de color'):].strip()
        if not re.search(r'muestras de color\s+' + re.escape(material) + r'\s+gratuitas directamente a tu hogar', text, re.I):
            continue
        card = label.parent
        for _ in range(4):
            if not card:
                break
            content = card.get_text(' ', strip=True)
            if len(content) < 900 and re.search(r'\bGratis\b', content, re.I) and re.search(r'Pide tus muestras de color', content, re.I):
                if re.search(r'al comprar|con tu compra|compra mínima', content, re.I):
                    break
                stamp = now()
                identity = url + '#' + name.casefold()
                results[name] = dict(
                    id=hashlib.sha256(identity.encode()).hexdigest()[:24], name=name,
                    description='Muestras físicas de color anunciadas gratuitamente para recibir en casa. Solicitud y existencias sin comprobar.',
                    brand='Kvik', category='home', platform='Kvik', url=url, request_url=url,
                    image_url=None, regular_price=None, promo_price=0.0, currency='EUR', kind='sample',
                    shipping_es='unknown', shipping_ad='unknown', shipping_cost_es=None, shipping_cost_ad=None,
                    additional_charges_es=None, additional_charges_ad=None, residency=None,
                    requirements=['La página anuncia entrega en casa; destinos, posibles portes y condiciones del formulario pendientes de confirmar.',
                                  'Abre la página oficial y busca el botón de muestras de color; no se ha enviado ninguna solicitud.'],
                    starts_at=None, ends_at=None, discovered_at=stamp, checked_at=stamp,
                    status='conditional', purchase_required=False, keepable=True, confidence=0.5,
                    rejection_reason=None, risk_reasons=[],
                    evidence=[dict(field='conditions', source=url, checked_at=stamp, method='public_html',
                                   sha256=hashlib.sha256(html.encode()).hexdigest(),
                                   note='Matched named physical colour samples, free claim, home delivery and request card; no form submitted.')])
                break
            card = card.parent
    return list(results.values())


class KvikConnector:
    def __init__(self, source, http):
        self.source, self.http = source, http

    def collect(self):
        offers = []
        for url in self.source['seeds']:
            offers.extend(extract_colour_samples(url, self.http.get(url)))
        if not offers:
            raise ValueError('No current free physical colour-sample campaign; source requires review')
        return offers
