import ipaddress
import socket
import time
from urllib.parse import urlsplit, urljoin
from protego import Protego
import httpx

AGENT='FreeFinder/0.1 (personal product discovery; no forms)'

def validate_url(url, hosts, resolve=True):
    p=urlsplit(url)
    if p.scheme!='https' or p.hostname not in hosts or p.username or p.password or p.port not in (None,443):
        raise ValueError('URL outside approved HTTPS hosts')
    if resolve:
        addresses=socket.getaddrinfo(p.hostname,443,type=socket.SOCK_STREAM)
        if not addresses or any(not ipaddress.ip_address(x[4][0]).is_global for x in addresses):
            raise ValueError('Non-public IP blocked')
    return url

class SafeHTTP:
    def __init__(self,hosts,delay=3):
        self.hosts=set(hosts); self.delay=max(3,delay); self.last=0; self.robots={}
        self.client=httpx.Client(timeout=20,follow_redirects=False,headers={'User-Agent':AGENT},limits=httpx.Limits(max_connections=2))
    def close(self): self.client.close()
    def raw(self,url,respect_robots=False):
        for _ in range(4):
            validate_url(url,self.hosts)
            if respect_robots: self.allowed(url)
            time.sleep(max(0,self.delay-(time.monotonic()-self.last)))
            self.last=time.monotonic()
            with self.client.stream('GET',url) as r:
                if r.is_redirect:
                    url=urljoin(url,r.headers['location']); continue
                r.raise_for_status()
                chunks=[]; size=0
                for c in r.iter_bytes():
                    size+=len(c)
                    if size>2_000_000: raise ValueError('Response too large')
                    chunks.append(c)
                return b''.join(chunks).decode('utf-8',errors='replace')
        raise ValueError('Too many redirects')
    def allowed(self,url):
        p=urlsplit(url); origin=f'https://{p.netloc}'
        if origin not in self.robots:
            robots=self.raw(origin+'/robots.txt')
            self.robots[origin]=Protego.parse(robots)
        parser=self.robots[origin]
        if not parser.can_fetch(url,AGENT): raise PermissionError('robots.txt disallows URL')
        crawl=parser.crawl_delay(AGENT)
        if crawl: self.delay=max(self.delay,float(crawl))
    def get(self,url):
        return self.raw(url,respect_robots=True)
