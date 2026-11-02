"""Bounded discovery of complete, zero-price outreach coins (not samples).

Public collection is the seed, never individual product IDs. Reviewed 2026-11-01:
robots permits collection/product pages with Crawl-delay:20. No terms link was
published in the inspected catalog; /terms-and-conditions/ returned 404.
Only factual titles, numeric prices, stock observations and hashes are retained.
"""
import hashlib
import re
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
from ..domain import now

HOST = 'mgl-southasian.com'
MAX_DETAILS = 3


def discover_free_coins(url, html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(' ', strip=True)
    if not re.search(r'\$0\.00.{0,70}FREE\s+GRANT', text, re.I):
        raise ValueError('Free grant terms missing; review source')
    links = []
    for card in soup.select('li.product.instock'):
        title = card.select_one('h3 a[href]')
        price = card.select_one('.price')
        if not title or not price or not re.fullmatch(r'\$\s*0\.00', price.get_text(' ', strip=True)):
            continue
        name = title.get_text(' ', strip=True)
        if not re.fullmatch(r'Gospel coins?\s*\([^()]+\)', name, re.I):
            continue
        target = urljoin(url, title['href'])
        p = urlsplit(target)
        if p.scheme == 'https' and p.hostname == HOST and re.fullmatch(r'/product/[a-z0-9-]+/', p.path) and not p.query and not p.fragment and target not in links:
            links.append(target)
        if len(links) >= MAX_DETAILS:
            break
    return links


def parse_free_coin(url, html, collection_url, collection_html):
    if urlsplit(url).hostname != HOST:
        return None
    soup = BeautifulSoup(html, 'html.parser')
    item = soup.select_one('div.product.product-type-simple.instock')
    if not item:
        return None
    summary = item.select_one('.summary')
    if not summary:
        return None
    title, price, stock = summary.select_one('h1.product_title'), summary.select_one('p.price'), summary.select_one('p.stock.in-stock')
    if not title or not price or not stock or not summary.select_one('button.single_add_to_cart_button'):
        return None
    name = title.get_text(' ', strip=True)
    if not re.fullmatch(r'Gospel coins?\s*\([^()]+\)', name, re.I) or not re.fullmatch(r'\$\s*0\.00', price.get_text(' ', strip=True)):
        return None
    if re.search(r'with purchase|minimum purchase|gift with|sample|digital|download|deposit|quote', summary.get_text(' ', strip=True), re.I):
        return None
    stamp = now()
    return dict(id=hashlib.sha256(url.encode()).hexdigest()[:24], name=name,
                description='Moneda física de divulgación religiosa ofrecida como producto completo a precio cero. No es una muestra. Concesión y pedido sujetos a la fuente.',
                brand='MGL Multilingual', category='other', platform='MGL Multilingual', url=url, request_url=url,
                image_url=None, regular_price=None, promo_price=0.0, currency='USD', kind='promotion',
                shipping_es='unknown', shipping_ad='unknown', shipping_cost_es=None, shipping_cost_ad=None,
                additional_charges_es=None, additional_charges_ad=None, residency=None,
                requirements=['La fuente puede limitar la cantidad y pide explicar el uso previsto de las monedas para divulgación religiosa.',
                              'Precio del artículo cero; transporte, destinos, impuestos y aprobación del pedido sin confirmar.',
                              'La página indica existencias en la revisión; no se ha solicitado ni reservado el producto.'],
                starts_at=None, ends_at=None, discovered_at=stamp, checked_at=stamp, status='conditional',
                purchase_required=False, keepable=True, confidence=0.6, rejection_reason=None, risk_reasons=[],
                evidence=[dict(field=field, source=source, checked_at=stamp, method='public_html',
                               sha256=hashlib.sha256(body.encode()).hexdigest(), note=note)
                          for field, source, body, note in [
                              ('price_stock', url, html, 'Complete physical outreach coin, zero numeric price, in-stock marker and order action observed.'),
                              ('conditions', collection_url, collection_html, 'Free grant catalog: quantities may be limited and intended-use explanation requested. No shipping promise.')]])


class MglConnector:
    def __init__(self, source, http):
        self.source, self.http = source, http

    def collect(self):
        offers = []
        checked = set()
        for seed in self.source['seeds']:
            catalog = self.http.get(seed)
            for url in discover_free_coins(seed, catalog):
                if url in checked:
                    continue
                checked.add(url)
                offer = parse_free_coin(url, self.http.get(url), seed, catalog)
                if offer:
                    offers.append(offer)
                if len(checked) >= MAX_DETAILS:
                    return offers
        return offers
