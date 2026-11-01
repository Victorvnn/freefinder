import os
os.environ['DATABASE_URL']='sqlite://'
os.environ['ADMIN_TOKEN']='test-secret-token'
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app import db
from app.domain import parse_campaign

def client():
    db.engine=create_engine('sqlite://',connect_args={'check_same_thread':False},poolclass=StaticPool)
    db.Session.configure(bind=db.engine)
    from app.main import app
    db.init_db()
    return TestClient(app)

def test_empty_catalog_and_admin_auth():
    c=client()
    assert c.get('/v1/offers').json()['items']==[]
    assert c.post('/v1/refresh').status_code==401
    assert c.get('/health').status_code==200

def test_filters_unknown_destination_and_total():
    c=client()
    o=parse_campaign('https://example.org/p','<h1>Muestra gratis de papel</h1><p>Solicita tu muestra</p>','Example')
    with db.Session() as s:
        db.upsert(s,o); s.commit()
    assert len(c.get('/v1/offers').json()['items'])==1
    assert c.get('/v1/offers?country=AD').json()['items']==[]
    assert c.get('/v1/offers?max_shipping=0').json()['items']==[]
    assert c.get('/v1/offers?category=office').json()['total']==1
    assert c.get('/v1/offers?category=clothing').json()['total']==0
    assert c.get('/v1/offers?kind=giveaway').json()['total']==0
    assert c.get('/v1/offers/'+o['id']).json()['total_es'] is None

def test_upsert_deduplicates_and_records_changes():
    c=client()
    o=parse_campaign('https://example.org/p','<h1>Muestra gratis de papel</h1><p>Solicita tu muestra</p>','Example')
    with db.Session() as s:
        db.upsert(s,o); s.commit()
        o=dict(o,status='sold_out'); db.upsert(s,o); s.commit()
    assert c.get('/v1/offers').json()['total']==1
    assert len(c.get('/v1/offers/'+o['id']+'/history').json())==2

def test_query_validation():
    c=client()
    assert c.get('/v1/offers?country=XX').status_code==422
    assert c.get('/v1/offers?limit=10000').status_code==422
