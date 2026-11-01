"""Conservative extraction. HTML evidence is an observation, never a successful claim."""
import hashlib
import re
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from bs4 import BeautifulSoup

CATEGORIES = ['electronics','computing','appliances','home','tools','clothing','shoes','accessories','beauty','hygiene','food','pets','sport','automotive','office','garden','children','other']
TYPES = ['free_shipping','shipping_only','sample','keep_trial','selection','cashback','promotion','giveaway','private_gift','loan']
STATUSES = ['verified','conditional','pending','sold_out','expired','rejected']

def now(): return datetime.now(timezone.utc).isoformat()

def canonical_url(url):
    p = urlsplit(url)
    q = sorted((k,v) for k,v in parse_qsl(p.query) if not k.lower().startswith('utm_') and k.lower() not in ('fbclid','gclid'))
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path or '/', urlencode(q), ''))

def total_cost(price, shipping, charges):
    return None if any(v is None for v in (price,shipping,charges)) else round(price+shipping+charges,2)

def classify(text):
    t = text.lower()
    purchase = bool(re.search(r'(con (?:cualquier |tu |una )?compra|al comprar|compra mínima|junto (?:a|con) (?:un|tu) pedido)',t))
    if re.search(r'préstamo|debe[s]? devolver|devolución obligatoria',t): kind='loan'
    elif re.search(r'reembolso.{0,12}100\s*%|cashback',t): kind='cashback'
    elif 'sorteo' in t: kind='giveaway'
    elif 'seleccionad' in t: kind='selection'
    elif 'muestra' in t: kind='sample'
    elif 'conservar' in t: kind='keep_trial'
    elif 'recogida' in t: kind='private_gift'
    elif re.search(r'(solo|únicamente).{0,15}(envío|transporte)',t): kind='shipping_only'
    elif 'envío gratis' in t or 'envío gratuito' in t: kind='free_shipping'
    else: kind='promotion'
    return kind,purchase

def parse_campaign(url, html, platform):
    soup=BeautifulSoup(html,'html.parser')
    for tag in soup(['script','style','nav','footer','header','noscript']): tag.decompose()
    main=soup.find('main') or soup
    text=main.get_text(' ',strip=True)
    t=text.lower()
    if not re.search(r'gratis|gratuit|reembolso.{0,12}100\s*%', t): return None
    title=main.find(['h1','h2']) or soup.find('title')
    name=title.get_text(' ',strip=True) if title else ''
    # Require an actual sample/item claim and a request action; generic program directories excluded.
    if not re.search(r'muestra|pack|paquete|regalo|sorteo|préstamo|reembolso',t): return None
    if not re.search(r'solicit|rellena|pide|recibe|particip|registr|formulario',t): return None
    if not name or (re.search(r'programa de pruebas|nuestros programas',name.lower())): return None
    kind,purchase=classify(text)
    explicit_zero=bool(re.search(r'(?:muestras?|packs?|paquetes?|productos?|regalos?)\s+(?:totalmente\s+)?(?:gratis|gratuit[oa]s?)|(?:gratis|gratuit[oa]s?)\s+(?:muestras?|packs?|paquetes?|productos?)',t))
    if not explicit_zero and kind not in ('cashback','giveaway','selection','loan'): return None
    ident=hashlib.sha256(canonical_url(url).encode()).hexdigest()[:24]
    # All monetary and territorial facts remain unknown until field-specific parsing is implemented.
    return dict(id=ident,name=name[:220],description='Campaña anunciada por la fuente. Consulta las condiciones originales antes de solicitar.',brand=None,category='office' if re.search(r'fundas|plastific|papel',t) else 'children' if 'bebé' in t else 'other',platform=platform,url=canonical_url(url),image_url=None,regular_price=None,promo_price=0.0 if explicit_zero and kind!='cashback' else None,currency='EUR',kind=kind,shipping_es='unknown',shipping_ad='unknown',shipping_cost_es=None,shipping_cost_ad=None,additional_charges_es=None,additional_charges_ad=None,residency=None,requirements=['Consulta las condiciones originales; solicitud no comprobada'],starts_at=None,ends_at=None,discovered_at=now(),checked_at=now(),status='pending',purchase_required=purchase,keepable=None,confidence=0.25,rejection_reason=None,risk_reasons=[],evidence=[dict(field='campaign_observed',source=url,checked_at=now(),method='public_html',sha256=hashlib.sha256(html.encode()).hexdigest(),note='Texto de campaña detectado; formulario, existencias y destinos no comprobados')])
