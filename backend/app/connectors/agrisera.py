"""Physical posters, discovered from Agrisera's public educational collection.

This parser withholds thumbnails. A separate reviewed-image registry adds only
images whose authors publish an explicit reusable license on Figshare. PDF URLs identify actual posters;
the separate request URL points to the publisher's physical-copy instructions.
"""
import hashlib
import re
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
from ..domain import now


def extract_posters(url, html):
    soup = BeautifulSoup(html, 'html.parser')
    main = soup.find('main') or soup
    text = main.get_text(' ', strip=True)
    if not re.search(r'hard copies.{0,120}free of charge', text, re.I):
        return []
    stamp = now()
    result = {}
    for a in main.select('a[href]'):
        title = a.get_text(' ', strip=True)
        target = urljoin(url, a['href'])
        p = urlsplit(target)
        if not re.match(r'Poster\s*\d+\s*:', title, re.I):
            continue
        if p.scheme != 'https' or p.hostname != 'www.agrisera.com' or not p.path.lower().endswith('.pdf') or p.query:
            continue
        result[target] = dict(
            id=hashlib.sha256(target.encode()).hexdigest()[:24], name=title[:220],
            description='Póster impreso educativo anunciado sin coste del producto. La página ofrece solicitar copias al suscribirse al boletín. No se ha realizado una solicitud.',
            brand='Agrisera', category='office', platform='Agrisera', url=target,
            request_url=url, image_url=None, regular_price=None, promo_price=0.0,
            currency='EUR', kind='promotion', shipping_es='unknown', shipping_ad='unknown',
            shipping_cost_es=None, shipping_cost_ad=None, additional_charges_es=None,
            additional_charges_ad=None, residency=None,
            requirements=['La página exige suscribirse al boletín para solicitar ejemplares impresos.',
                          'Disponibilidad de cada ejemplar y transporte pendientes de confirmar.',
                          'El enlace de referencia es el PDF del póster; Ver oferta abre las instrucciones de solicitud física.'],
            starts_at=None, ends_at=None, discovered_at=stamp, checked_at=stamp,
            status='conditional', purchase_required=False, keepable=True,
            confidence=0.4, rejection_reason=None, risk_reasons=[],
            evidence=[dict(field='conditions', source=url, checked_at=stamp,
                           method='public_html', sha256=hashlib.sha256(html.encode()).hexdigest(),
                           note='La página ofrece hard copies free of charge con suscripción al boletín; no se confirma solicitud, porte ni stock individual.')])
    return list(result.values())


class AgriseraConnector:
    def __init__(self, source, http):
        self.source, self.http = source, http

    def collect(self):
        offers = []
        for url in self.source['seeds']:
            offers.extend(extract_posters(url, self.http.get(url)))
        if not offers:
            raise ValueError('No physical free-copy claim found; source requires review')
        return offers
