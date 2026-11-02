from app.connectors.mgl import discover_free_coins, parse_free_coin

SEED='https://mgl-southasian.com/product-category/free-products/'
URL='https://mgl-southasian.com/product/gospel-coin-greek/'
CAT='''<p>Any listing of $0.00 is available as a FREE GRANT</p><ul><li class="product instock"><h3><a href="/product/gospel-coin-greek/">Gospel coin (Greek)</a></h3><span class="price">$ 0.00</span></li></ul>'''
ITEM='''<div class="product product-type-simple instock"><div class="summary"><h1 class="product_title">Gospel coin (Greek)</h1><p class="price">$ 0.00</p><p class="stock in-stock">175 in stock</p><button class="single_add_to_cart_button">Add to cart</button></div></div>'''

def test_discovers_complete_coin_from_collection_then_checks_live_price_stock():
    assert discover_free_coins(SEED,CAT)==[URL]
    item=parse_free_coin(URL,ITEM,SEED,CAT)
    assert item['kind']=='promotion' and item['promo_price']==0
    assert item['category']=='other' and item['currency']=='USD'
    assert item['status']=='conditional' and item['shipping_es']=='unknown'
    assert item['image_url'] is None and not item['purchase_required']

def test_rejects_price_changes_stock_loss_purchase_gifts_and_noncoins():
    assert not parse_free_coin(URL,ITEM.replace('0.00','1.00'),SEED,CAT)
    assert not parse_free_coin(URL,ITEM.replace('instock','onbackorder'),SEED,CAT)
    assert not parse_free_coin(URL,ITEM.replace('175 in stock','Gift with purchase only'),SEED,CAT)
    assert not discover_free_coins(SEED,CAT.replace('Gospel coin (Greek)','Download PDF'))
    assert not discover_free_coins(SEED,CAT.replace('/product/gospel-coin-greek/','https://evil.org/product/gospel-coin-greek/'))
