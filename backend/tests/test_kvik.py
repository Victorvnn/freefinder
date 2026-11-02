from app.connectors.kvik import extract_colour_samples

URL='https://www.kvik.es/'
HTML='''<main><p>Te enviaremos muestras de color Mano gratuitas directamente a tu hogar.</p>
<div><div><div>Muestras de color Mano</div><p>Descubre los colores.</p><div>Gratis</div><button>Pide tus muestras de color</button></div></div></main>'''

def test_named_physical_sample_campaign_from_page():
    item=extract_colour_samples(URL, HTML)[0]
    assert item['name']=='Muestras de color Mano'
    assert item['category']=='home' and item['kind']=='sample'
    assert item['image_url'] is None and item['status']=='conditional'
    assert item['purchase_required'] is False and item['shipping_es']=='unknown'

def test_fails_closed_if_offer_disappears_or_purchase_required():
    assert not extract_colour_samples(URL,HTML.replace('Gratis','Precio 10 €'))
    assert not extract_colour_samples(URL,HTML.replace('gratuitas directamente a tu hogar','de pago'))
    assert not extract_colour_samples(URL,HTML.replace('Descubre los colores.','Gratis al comprar tu cocina.'))
    assert not extract_colour_samples('https://evil.org/',HTML)

def test_unrelated_free_appliance_promotion_is_not_sample():
    assert not extract_colour_samples(URL,'<h2>Gratis 5 electrodomésticos con tu compra</h2>')
