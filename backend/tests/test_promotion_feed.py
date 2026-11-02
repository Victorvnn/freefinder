from datetime import datetime, timezone
import pytest
from app.connectors.promotion_feed import extract_announcements
AT=datetime(2026,11,1,22,tzinfo=timezone.utc)
def feed(title='Marca sortea 4 espumadores SOGO',link='https://regalosymuestrasgratis.com/espumadores.html',description='Participación sujeta a bases.'):
    return f'<rss><channel><item><title>{title}</title><link>{link}</link><pubDate>Sun, 01 Nov 2026 12:00:00 +0000</pubDate><description>{description}</description></item></channel></rss>'
def test_real_named_physical_announcement_is_not_verified_free_product():
    o=extract_announcements(feed(),AT)[0]
    assert o['kind']=='giveaway' and o['category']=='appliances'
    assert o['status']=='pending' and o['promo_price'] is None and o['shipping_ad']=='unknown'
    assert o['image_url'] is None and o['keepable'] is None
@pytest.mark.parametrize('title',['Marca sortea un viaje','Marca sortea tarjeta regalo','Marca sortea una lavadora por comprar detergente','Marca sortea una suscripción de belleza'])
def test_nonphysical_and_purchase_promotions_excluded(title):assert extract_announcements(feed(title=title),AT)==[]
def test_purchase_requirement_in_body_excluded():assert extract_announcements(feed(description='Hay que subir el ticket de compra'),AT)==[]
def test_unknown_category_old_items_and_malicious_urls_excluded():
    assert extract_announcements(feed(title='Marca sortea algo misterioso'),AT)==[]
    assert extract_announcements(feed(link='https://evil.example/product.html'),AT)==[]
    assert extract_announcements(feed().replace('2026','2025'),AT)==[]
def test_entities_rejected():
    with pytest.raises(ValueError):extract_announcements('<!DOCTYPE rss><rss/>',AT)


def test_blocked_announcement_pages_are_not_reported_as_success(monkeypatch):
    import app.connectors.promotion_feed as m
    candidates=m.extract_announcements(feed(),AT)
    monkeypatch.setattr(m,'extract_announcements',lambda xml:candidates)
    class HTTP:
        def get(self,url):
            if url==m.FEED:return '<rss/>'
            raise PermissionError('Blocked by robots')
    with pytest.raises(ValueError,match='could not be confirmed'):
        m.PromotionFeedConnector({},HTTP()).collect()
