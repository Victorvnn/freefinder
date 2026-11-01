from app.connectors.usgs import parse_product

def test_paper_product_zero_price_has_disclosed_handling():
    html='<main><h1>TEST PAPER POSTER</h1><p>$0.00</p><p>Available</p><h2>Product Details</h2><p>Media Paper</p><p>For all orders a $7.50 USD handling charge is applied.</p></main>'
    p=parse_product('https://store.usgs.gov/product/123',html)
    assert p['promo_price']==0
    assert p['currency']=='USD'
    assert p['shipping_cost_es'] is None
    assert p['additional_charges_es']==7.5
    assert p['shipping_es']=='unknown'
    assert p['status']=='pending'
    assert p['name']=='TEST PAPER POSTER'

def test_paid_physical_and_free_digital_excluded():
    assert parse_product('https://store.usgs.gov/product/1','<main><h1>TEST MAP</h1><p>$12.00 Available Product Details Media Paper</p></main>') is None
    assert parse_product('https://store.usgs.gov/product/2','<main><h1>TEST PDF</h1><p>$0.00 Available Product Details Media PDF</p></main>') is None

def test_empty_discovery_is_not_a_successful_catalog_scan():
    import pytest
    from app.connectors.usgs import UsgsConnector
    class EmptyHTTP:
        hosts={'store.usgs.gov'}
        def get(self,url):return '<html><h1>Educational products</h1><p>Unavailable catalog</p></html>'
    with pytest.raises(ValueError):UsgsConnector({'seeds':['https://store.usgs.gov/educational-products']},EmptyHTTP()).collect()
