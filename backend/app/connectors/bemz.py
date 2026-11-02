"""Bounded factual sample discovery for personal, noncommercial use only.

Reviewed 2026-11-01: /robots.txt permits catalog access (checkout excluded).
Terms reserve content reuse to personal noncommercial use. We retain names,
URLs, observed price/conditions and response hashes only, never images or prose.
The conflicting catalog (five) / terms (three) limits remain visible to users.
"""
import hashlib
import re
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
from ..domain import now

TERMS_URL = 'https://bemz.com/es-es/information/terminos-y-condiciones'
MAX_SAMPLES = 12


def extract_samples(url, html, terms_html):
    if urlsplit(url).hostname != 'bemz.com':
        return []
    soup = BeautifulSoup(html, 'html.parser')
    terms = BeautifulSoup(terms_html, 'html.parser').get_text(' ', strip=True)
    # An explicit future automation prohibition requires a fresh source review.
    if re.search(r'(?:scraping|web scraping|automated access|acceso automatizado|robots? de rastreo)', terms, re.I):
        raise PermissionError('Bemz terms mention automation; source requires review')
    if not re.search(r'hasta tres muestras de telas sin cargo', terms, re.I):
        raise ValueError('Bemz sample terms changed; source requires review')
    stamp = now()
    evidence = [dict(field='conditions', source=source, checked_at=stamp,
                     method='public_html', sha256=hashlib.sha256(body.encode()).hexdigest(),
                     note=note) for source, body, note in [
                         (url, html, 'Individual catalog cards advertise a free physical fabric sample; stock and request not tested.'),
                         (TERMS_URL, terms_html, 'Terms allow three samples without charge; catalog advertises five. Personal noncommercial metadata use only.')]]
    offers = {}
    for card in soup.select('a[href]'):
        target = urljoin(url, card['href'])
        parsed = urlsplit(target)
        if parsed.scheme != 'https' or parsed.hostname != 'bemz.com' or parsed.query or parsed.fragment:
            continue
        if not re.fullmatch(r'/es-es/products/SWA1-[A-Za-z0-9]+', parsed.path):
            continue
        if not re.search(r'Añadir muestra gratuita', card.get_text(' ', strip=True), re.I):
            continue
        # The final direct div is the factual fabric/colour label, separate
        # from marketing badges, photographs and action controls.
        parts = card.find_all('div', recursive=False)
        if len(parts) < 2:
            continue
        label = parts[-1].get_text(' ', strip=True)
        if not label or len(label) > 180 or re.search(r'gratuit|comprar|%|€', label, re.I):
            continue
        offers[target] = dict(
            id=hashlib.sha256(target.encode()).hexdigest()[:24], name=f'Muestra de tela: {label}',
            description='Muestra física de tejido anunciada gratuitamente por Bemz. Solicitud y existencias no comprobadas.',
            brand='Bemz', category='home', platform='Bemz', url=target, request_url=target,
            image_url=None, regular_price=None, promo_price=0.0, currency='EUR', kind='sample',
            shipping_es='unknown', shipping_ad='unknown', shipping_cost_es=None, shipping_cost_ad=None,
            additional_charges_es=None, additional_charges_ad=None, residency=None,
            requirements=['Hay una contradicción: el catálogo anuncia cinco muestras y las condiciones permiten tres sin cargo. Confirmar antes de solicitar.',
                          'Por encima del límite pueden cobrarse portes. Destinos, gastos finales, existencias y solicitud sin comprobar.'],
            starts_at=None, ends_at=None, discovered_at=stamp, checked_at=stamp, status='conditional',
            purchase_required=False, keepable=True, confidence=0.55, rejection_reason=None,
            risk_reasons=['Límite de muestras contradictorio entre catálogo y condiciones.'], evidence=evidence)
        if len(offers) >= MAX_SAMPLES:
            break
    return list(offers.values())


class BemzConnector:
    def __init__(self, source, http):
        self.source, self.http = source, http

    def collect(self):
        terms = self.http.get(TERMS_URL)
        offers = {}
        for url in self.source['seeds']:
            for offer in extract_samples(url, self.http.get(url), terms):
                offers[offer['url']] = offer
                if len(offers) >= MAX_SAMPLES:
                    return list(offers.values())
        if not offers:
            raise ValueError('No current free fabric sample cards; source requires review')
        return list(offers.values())
