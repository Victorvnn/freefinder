import pytest
from app.domain import classify, canonical_url, total_cost, parse_campaign

def test_unknown_shipping_never_becomes_free():
    assert total_cost(0, None, 0) is None
    assert total_cost(0, 0, None) is None
    assert total_cost(0, 0, 0) == 0

def test_classification_keeps_purchase_outside_catalog():
    assert classify('Muestra gratis con cualquier compra') == ('sample', True)
    assert classify('Sorteo gratis de un reloj') == ('giveaway', False)
    assert classify('Reembolso del 100 %') == ('cashback', False)
    assert classify('Préstamo gratuito, debes devolverlo') == ('loan', False)

def test_canonical_dedup_preserves_product_query():
    assert canonical_url('https://example.org/p?id=2&utm_source=x#top') == 'https://example.org/p?id=2'

def test_active_page_is_not_verified():
    o = parse_campaign('https://example.org/muestra', '<main><h1>Muestra gratis de papel</h1><p>Solicita tu muestra gratuita.</p></main>', 'Example')
    assert o['status'] == 'pending'
    assert o['shipping_ad'] == 'unknown'
    assert o['shipping_es'] == 'unknown'
    assert o['shipping_cost_es'] is None
    assert o['image_url'] is None

def test_generic_program_is_not_a_product():
    assert parse_campaign('https://example.org/', '<h1>Programa de pruebas</h1><p>Descubre productos gratis</p>', 'Example') is None

def test_no_free_claim_no_offer():
    assert parse_campaign('https://example.org/p', '<h1>Pack de papel</h1><p>Compra por 10 euros</p>', 'Example') is None

def test_free_shipping_does_not_invent_zero_product_price():
    assert parse_campaign('https://example.org/p', '<main><h1>Pack de papel</h1><p>20 euros; envío gratis. Pide aquí.</p></main>', 'Example') is None

def test_cashback_does_not_invent_zero_upfront_price():
    p=parse_campaign('https://example.org/p', '<main><h1>Reembolso del 100 %</h1><p>Participa en el reembolso del 100 %.</p></main>', 'Example')
    assert p['promo_price'] is None

def test_nearby_free_shipping_cannot_be_used_as_product_price():
    assert parse_campaign('https://example.org/p', '<main><h1>Pack</h1><p>20€ envío gratis. Pide aquí.</p></main>', 'Example') is None
