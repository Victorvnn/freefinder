import pytest
from app.connectors.bemz import extract_samples, BemzConnector, TERMS_URL

URL = 'https://bemz.com/es-es/fabrics'
TERMS = '<p>Bemz te ofrece la posibilidad de recibir hasta tres muestras de telas sin cargo alguno.</p>'

def card(code='ABC1', name='Linen', color='Blue', marker='Añadir muestra gratuita'):
    return f'<a href="/es-es/products/SWA1-{code}"><div><img src="copyright.jpg"><button>{marker}</button></div><div><div>{name}</div><div>{color}</div></div></a>'

def test_extracts_real_sample_names_without_images_or_prose():
    result = extract_samples(URL, card(), TERMS)
    assert len(result) == 1
    item = result[0]
    assert item['name'] == 'Muestra de tela: Linen Blue'
    assert item['category'] == 'home' and item['kind'] == 'sample'
    assert item['image_url'] is None and item['promo_price'] == 0
    assert item['status'] == 'conditional' and item['shipping_es'] == 'unknown'
    assert 'cinco' in item['requirements'][0] and 'tres' in item['requirements'][0]
    assert item['purchase_required'] is False
    assert len(item['evidence']) == 2
    assert 'copyright.jpg' not in str(item)

def test_requires_individual_free_sample_claim_and_valid_product_url():
    assert not extract_samples(URL, card(marker='Comprar'), TERMS)
    assert not extract_samples(URL, card().replace('SWA1-', 'SOFA-'), TERMS)
    assert not extract_samples(URL, card().replace('/es-es/products/', 'https://evil.org/es-es/products/'), TERMS)
    assert not extract_samples('https://evil.org/', card(), TERMS)

def test_caps_collection_and_deduplicates():
    result = extract_samples(URL, card()*3 + ''.join(card(f'A{i}') for i in range(40)), TERMS)
    assert len(result) == 12 and len({x['url'] for x in result}) == 12

def test_disappearing_cards_are_not_seeded():
    assert extract_samples(URL, '<h1>Telas</h1>', TERMS) == []
    with pytest.raises(ValueError): extract_samples(URL, card(), 'Conditions changed')
    with pytest.raises(PermissionError): extract_samples(URL, card(), TERMS+' Automated access prohibited')

def test_collect_gets_live_collection_and_terms_only():
    class HTTP:
        calls = []
        def get(self, url):
            self.calls.append(url)
            return TERMS if url == TERMS_URL else card()
    http = HTTP()
    assert len(BemzConnector({'seeds':[URL]}, http).collect()) == 1
    assert http.calls == [TERMS_URL, URL]
