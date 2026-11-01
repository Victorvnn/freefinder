"""USGS factual product metadata. Never treats country-of-map as a shipping country."""
import re
import hashlib
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
from ..domain import now, canonical_url

def parse_product(url,html):
    soup=BeautifulSoup(html,'html.parser')
    main=soup.find('main') or soup
    for tag in main(['script','style','nav','footer','header']): tag.decompose()
    title=main.find('h1')
    if not title: return None
    text=main.get_text(' ',strip=True)
    if not re.search(r'Media\s*:?\s*Paper\b',text,re.I): return None
    # First product price before Product Details; other products/recommendations are ignored.
    pricing=text.split('Product Details')[0]
    price=re.search(r'\$\s*([0-9,]+\.\d{2})',pricing)
    if not price or float(price[1].replace(',',''))!=0: return None
    charges=re.search(r'\$\s*([0-9]+\.\d{2})\s*USD\s+handling charge',text,re.I)
    fee=float(charges[1]) if charges else None
    stamp=now(); url=canonical_url(url)
    sold=bool(re.search(r'\b(out of stock|unavailable|not available)\b',pricing,re.I))
    return dict(id=hashlib.sha256(url.encode()).hexdigest()[:24],name=title.get_text(' ',strip=True)[:220],description='Publicación física de USGS anunciada a precio cero. Transporte y elegibilidad territorial pendientes.',brand='USGS',category='office',platform='USGS Store',url=url,image_url=None,regular_price=None,promo_price=0.0,currency='USD',kind='promotion',shipping_es='unknown',shipping_ad='unknown',shipping_cost_es=None,shipping_cost_ad=None,additional_charges_es=fee,additional_charges_ad=fee,residency=None,requirements=['Se anuncia un cargo de gestión por pedido; no se ha comprobado el carrito.','Disponibilidad indicada por la página; solicitud no realizada.'],starts_at=None,ends_at=None,discovered_at=stamp,checked_at=stamp,status='sold_out' if sold else 'pending',purchase_required=False,keepable=True,confidence=0.35,rejection_reason=None,risk_reasons=['Existen gastos de gestión además del transporte.'] if fee else [],evidence=[dict(field='promo_price',source=url,checked_at=stamp,method='public_html',sha256=hashlib.sha256(html.encode()).hexdigest(),note='Precio cero y soporte Paper observados; destinos y existencias no confirmados en carrito.')])

class UsgsConnector:
    def __init__(self,source,http):self.source=source;self.http=http
    def collect(self):
        queue=[(u,0) for u in self.source['seeds']]; seen=set(); found=[]
        while queue and len(seen)<20:
            url,depth=queue.pop(0)
            if url in seen: continue
            seen.add(url); html=self.http.get(url)
            if re.search(r'/product/\d+',url):
                p=parse_product(url,html)
                if p: found.append(p)
                continue
            if depth>2: continue
            for a in BeautifulSoup(html,'html.parser').select('a[href]'):
                link=canonical_url(urljoin(url,a['href']))
                if urlsplit(link).hostname not in self.http.hosts: continue
                path=urlsplit(link).path
                if re.search(r'/product/\d+',path) or (depth<2 and re.search(r'educational|water|geology|other-products|natural-hazards',path,re.I)):
                    if link not in seen and len(queue)<80: queue.append((link,depth+1))
        return found
