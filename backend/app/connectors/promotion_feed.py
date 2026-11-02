"""Bounded personal RSS reader: factual announcement metadata, never article copies.

Public syndication feed. No photographs, prose, affiliate links, comments or
personal data are republished. Organizer eligibility/stock is NOT verified.
"""
import hashlib
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup
from ..domain import now

HOST='regalosymuestrasgratis.com'
FEED='https://regalosymuestrasgratis.com/feed/'
MAX_ITEMS=8

def extract_announcements(xml, at=None):
    if re.search(r'<!DOCTYPE|<!ENTITY',xml,re.I):raise ValueError('XML declarations forbidden')
    root=ET.fromstring(xml)
    current=at or datetime.now(timezone.utc)
    out=[]
    for item in root.findall('./channel/item'):
        title=item.findtext('title','').strip();url=item.findtext('link','').strip()
        p=urlsplit(url)
        if p.scheme!='https' or p.hostname!=HOST or p.username or p.password or p.query or p.fragment or not p.path.endswith('.html'):continue
        try:published=parsedate_to_datetime(item.findtext('pubDate','')).astimezone(timezone.utc)
        except (ValueError,TypeError,OverflowError):continue
        if not 0<=(current-published).total_seconds()<=10*86400:continue
        html=item.findtext('{http://purl.org/rss/1.0/modules/content/}encoded','') or item.findtext('description','')
        text=BeautifulSoup(html,'html.parser').get_text(' ',strip=True)
        # Only narrowly identified physical prizes/samples. No trips, tickets,
        # vouchers, digital services, subscriptions or purchase-linked entries.
        if not re.search(r'sortea[n]?|muestras? gratis',title,re.I):continue
        if re.search(r'compr[ae]|comprando|ticket|factura|suscripci[oó]n|viaje|entradas?|tarjeta regalo|vale de|descuento',title,re.I):continue
        if re.search(r'(?:por comprar|tras comprar|compra obligatoria|ticket de compra|sube.{0,30}ticket|registrar.{0,30}compra)',text,re.I):continue
        words=title+' '+text[:500]
        category=next((key for key,rx in [
            ('appliances',r'espumador|lavadora|cafetera|batidora|freidora'),
            ('electronics',r'auriculares|altavoz|smartwatch|smartphone|televisor'),
            ('pets',r'mascota|perro|gato|pienso'),
            ('beauty',r'belleza|crema|perfume|cosm[eé]tic|maquillaje|nelly|rosalique'),
            ('food',r'conservas|chocolate|golosinas|aliment|galletas|bebidas'),
            ('home',r'l[aá]mpara|macetero|decoraci[oó]n')]
            if re.search(rx,words,re.I)),None)
        if not category:continue
        kind='giveaway' if re.search(r'sortea[n]?',title,re.I) else 'sample'
        # Strip announcement verbs, retaining factual brand/item names.
        name=re.sub(r'\bsortea[n]?\b','·',title,flags=re.I)[:220]
        stamp=now()
        out.append(dict(id=hashlib.sha256(url.encode()).hexdigest()[:24],name=name,
            description='Anuncio descubierto en un feed público de promociones. Las bases del organizador, la vigencia y los destinos todavía no se han comprobado.',
            brand=None,category=category,platform='Regalos y Muestras Gratis · RSS',url=url,request_url=url,image_url=None,
            regular_price=None,promo_price=None,currency='EUR',kind=kind,
            shipping_es='unknown',shipping_ad='unknown',shipping_cost_es=None,shipping_cost_ad=None,
            additional_charges_es=None,additional_charges_ad=None,residency=None,
            requirements=['Anuncio de una fuente secundaria: confirmar bases, fechas, requisitos y ausencia de compra con el organizador.',
                          'Si es un sorteo, participar no garantiza recibir el producto. No se ha participado ni comprobado el envío.'],
            starts_at=None,ends_at=None,published_at=published.isoformat(),discovered_at=stamp,checked_at=stamp,
            status='pending',purchase_required=None,keepable=None,confidence=0.15,rejection_reason=None,
            risk_reasons=['Bases y disponibilidad del organizador sin verificar.'],
            evidence=[dict(field='announcement',source=FEED,checked_at=stamp,method='public_rss',
                           sha256=hashlib.sha256(xml.encode()).hexdigest(),
                           note='Solo se ha observado el anuncio en RSS; no acredita precio, stock, participación ni transporte.')]))
        if len(out)>=MAX_ITEMS:break
    return out

class PromotionFeedConnector:
    def __init__(self,source,http):self.source,self.http=source,http
    def collect(self):
        xml=self.http.get(FEED)
        candidates=extract_announcements(xml)
        found=[]
        for offer in candidates:
            try:
                page=self.http.get(offer['url'])
                heading=BeautifulSoup(page,'html.parser').find('h1')
                if not heading:continue
                title=heading.get_text(' ',strip=True)
                if re.search(r'finalizad|caducad|terminad',title,re.I):continue
                normalize=lambda value:re.sub(r'\W+',' ',re.sub(r'\bsortea[n]?\b',' ',value,flags=re.I)).strip().casefold()
                if normalize(title)!=normalize(offer['name']):continue
                offer['evidence'].append(dict(field='announcement_page',source=offer['url'],checked_at=now(),method='public_html',sha256=hashlib.sha256(page.encode()).hexdigest(),note='Artículo con título coincidente accesible; no acredita bases, stock ni envío del organizador.'))
                found.append(offer)
            except Exception:
                # Individual missing/blocked announcement pages are not offers.
                continue
        if candidates and not found:raise ValueError('Announcement pages could not be confirmed; source requires review')
        return found
