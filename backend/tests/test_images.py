from app.connectors.agrisera import extract_posters

def test_poster_requires_physical_free_claim_and_request_condition():
    html='<main><h1>Educational poster collection</h1><p>Sign up for our newsletter to receive hard copies of the posters, free of charge!</p><p>Using graphics is allowed for non-commercial educational purposes with citation.</p><a href="/dokument/Poster1.pdf">Poster 1: Synthetic photosynthesis</a></main>'
    offers=extract_posters('https://www.agrisera.com/en/info/educational-posters.html',html)
    assert len(offers)==1
    p=offers[0]
    assert p['status']=='conditional' and p['kind']=='promotion'
    assert p['shipping_es']=='unknown' and p['shipping_cost_es'] is None
    assert p['requirements'] and p['image_url'] is None
    assert extract_posters('https://www.agrisera.com/p','<main>Download free PDF <a href="/Poster.pdf">Poster 1: test</a></main>')==[]


def test_image_reference_is_only_added_for_reviewed_exact_product():
    from app.connectors.images import enrich_image
    assert enrich_image(dict(url='https://store.usgs.gov/product/999999')) .get('image_url') is None
    offer=enrich_image(dict(url='https://store.usgs.gov/product/208284'))
    assert offer['image_url'].endswith('vhp_img1052.jpg')
    assert offer['image_license']=='Public domain'
    assert offer['evidence'][0]['method']=='editorial_rights_review'


def test_agrisera_links_remain_distinct_and_do_not_copy_restricted_images():
    html='<main><p>Subscribe for hard copies of the posters free of charge</p><h3><a href="/a.pdf">Poster 1: A</a><img src="/restricted.jpg"></h3><a href="/b.pdf">Poster 2: B</a><a href="https://evil.example/c.pdf">Poster 3: C</a></main>'
    offers=extract_posters('https://www.agrisera.com/en/info/educational-posters.html',html)
    assert len(offers)==2 and len({o['id'] for o in offers})==2
    assert all(o['image_url'] is None and o['request_url'].endswith('educational-posters.html') for o in offers)


def test_source_failure_does_not_fake_expiry_or_new_verification():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app import db
    from app.worker import reconcile_source
    engine=create_engine('sqlite://')
    db.Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as s:
        db.upsert(s,dict(id='poster',url='https://www.agrisera.com/a.pdf',source_id='agrisera_posters',status='conditional',checked_at='old',discovered_at='old'))
        reconcile_source(s,'agrisera_posters',set())
        s.commit()
        p=s.get(db.Offer,'poster').payload
        assert p['status']=='pending' and p['source_status']=='missing' and p['checked_at']=='old'
        reconcile_source(s,'agrisera_posters',None)
        s.commit()
        assert s.get(db.Offer,'poster').payload['source_status']=='unreachable'


def test_licensed_poster_image_requires_exact_reviewed_url_and_has_attribution():
    from app.connectors.images import REVIEWED_IMAGES,enrich_image
    reviewed=[(u,v) for u,v in REVIEWED_IMAGES.items() if 'agrisera.com' in u]
    assert len(reviewed)>=8
    for url,metadata in reviewed:
        item=enrich_image(dict(url=url))
        assert item['image_license']=='CC BY 4.0'
        assert '10.6084/' in item['image_credit']
        assert item['evidence'][0]['source'].startswith('https://api.figshare.com/v2/articles/')
        assert len(enrich_image(item)['evidence'])==1
