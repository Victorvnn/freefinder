import pytest
from app.connectors.safe_http import validate_url
from app.connectors.html import discover_links

def test_ssrf_private_ip_and_hosts_blocked():
    for u in ['http://127.0.0.1/a','https://169.254.169.254/','https://user:pass@example.org/','https://example.org:444/','file:///etc/passwd','https://evil.org/']:
        with pytest.raises(ValueError): validate_url(u,{'example.org'})

def test_discovery_deduplicates_and_restricts_domain():
    html='<a href="/muestras/papel">Muestra gratis</a><a href="/muestras/papel#x">Solicita</a><a href="https://evil.org/muestra">Gratis</a><a href="/compra">Compra</a>'
    assert discover_links('https://example.org/',html,{'example.org'})==['https://example.org/muestras/papel']

def test_redirect_into_disallowed_path_is_blocked(monkeypatch):
    import httpx
    import app.connectors.safe_http as net
    monkeypatch.setattr(net,'validate_url',lambda url,hosts: url)
    client=net.SafeHTTP({'example.org'},delay=0)
    client.delay=0
    requested=[]
    def route(request):
        requested.append(request.url.path)
        if request.url.path=='/robots.txt':return httpx.Response(200,text='User-agent: *\nDisallow: /private*')
        if request.url.path=='/start':return httpx.Response(302,headers={'location':'/private/data'})
        return httpx.Response(200,text='not allowed')
    client.client.close();client.client=httpx.Client(transport=httpx.MockTransport(route))
    try:
        with pytest.raises(PermissionError): client.get('https://example.org/start')
        assert '/private/data' not in requested
    finally:client.close()
