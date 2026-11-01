import re
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
from ..domain import canonical_url, parse_campaign

def discover_links(base,html,hosts):
    urls=[]
    for a in BeautifulSoup(html,'html.parser').select('a[href]'):
        href=canonical_url(urljoin(base,a['href']))
        label=a.get_text(' ',strip=True)+' '+href
        if urlsplit(href).hostname in hosts and re.search(r'muestra|sample|gratis|free-trial|freeorder',label,re.I) and href not in urls:
            urls.append(href)
    return urls

class HtmlConnector:
    def __init__(self,source,http): self.source=source; self.http=http
    def collect(self):
        found=[]; visited=set()
        for seed in self.source['seeds']:
            html=self.http.get(seed)
            links=discover_links(seed,html,self.http.hosts)
            for url in [seed]+links[:8]:
                if url in visited: continue
                visited.add(url)
                body=html if url==seed else self.http.get(url)
                o=parse_campaign(url,body,self.source['name'])
                if o: found.append(o)
        return found
