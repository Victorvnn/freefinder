"""Synthetic fixtures only. No external products are seeded in deployments."""
import json
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from app import db
from app.domain import parse_campaign
from app.cloud import export_snapshot, restore_state

@pytest.fixture
def database():
    engine=create_engine('sqlite://',connect_args={'check_same_thread':False},poolclass=StaticPool)
    db.Base.metadata.create_all(engine)
    return db.sessionmaker(engine,expire_on_commit=False)

def test_snapshot_keeps_unknown_costs_and_existing_android_paths(database,tmp_path):
    o=parse_campaign('https://example.org/sample','<h1>Muestra gratis de papel</h1><p>Solicita tu muestra gratuita</p>','Synthetic fixture')
    with database() as s:
        db.upsert(s,o);s.add(db.Run(source='fixture',started_at='2026-01-01T00:00:00+00:00',finished_at='2026-01-01T00:00:01+00:00',status='ok',count=1));s.commit()
    state=export_snapshot(database,tmp_path,[])
    p=json.loads((tmp_path/'v1/offers').read_text())
    assert p['total']==1 and len(p['items'])==1
    assert p['items'][0]['total_es'] is None
    assert p['items'][0]['shipping_es']=='unknown'
    assert json.loads((tmp_path/'v1/runs').read_text())[0]['status']=='ok'
    assert state['last_successful_scan']=='2026-01-01T00:00:01+00:00'
    assert state['schema_version']==1
    assert (tmp_path/'.nojekyll').is_file()

def test_state_roundtrip_keeps_source_interval_and_history(database,tmp_path):
    o=parse_campaign('https://example.org/sample','<h1>Muestra gratis</h1><p>Solicita tu muestra</p>','Synthetic fixture')
    with database() as s:
        db.upsert(s,o);s.add(db.Run(source='fixture',started_at='2026-01-01T00:00:00+00:00',status='error',count=0,error='fixture error'));s.commit()
    state=export_snapshot(database,tmp_path,[])
    engine=create_engine('sqlite://',poolclass=StaticPool);db.Base.metadata.create_all(engine);other=db.sessionmaker(engine)
    restore_state(other,state)
    with other() as s:
        assert s.query(db.Offer).count()==1
        assert s.query(db.Revision).count()==1
        assert s.query(db.Run).one().status=='error'
    assert state['last_successful_scan'] is None

def test_invalid_state_does_not_erase_database(database):
    with database() as s:
        s.add(db.Run(source='existing',started_at='2026-01-01T00:00:00+00:00',status='error',count=0));s.commit()
    with pytest.raises(ValueError):restore_state(database,{'schema_version':99})
    with database() as s:assert s.query(db.Run).count()==1

def test_snapshot_never_exports_phone_or_environment_data(database,tmp_path,monkeypatch):
    monkeypatch.setenv('ADMIN_TOKEN','synthetic-secret-not-for-export')
    state=export_snapshot(database,tmp_path,[])
    assert state['offers']==[]
    assert 'synthetic-secret-not-for-export' not in (tmp_path/'snapshot.json').read_text()
    assert 'No hay productos' in (tmp_path/'index.html').read_text()

def test_static_http_query_contract_for_unchanged_apk(database,tmp_path):
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
    import threading
    import urllib.request
    import functools
    export_snapshot(database,tmp_path,[])
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self,*a): pass
    handler=functools.partial(QuietHandler,directory=str(tmp_path))
    server=ThreadingHTTPServer(('127.0.0.1',0),handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        base=f'http://127.0.0.1:{server.server_port}'
        with urllib.request.urlopen(base+'/v1/offers?limit=100&offset=0') as r:
            assert r.status==200 and r.geturl()==base+'/v1/offers?limit=100&offset=0'
            assert json.load(r)=={'items':[],'total':0,'offset':0}
        with urllib.request.urlopen(base+'/v1/runs') as r:assert json.load(r)==[]
    finally:server.shutdown();server.server_close();thread.join(timeout=2)

def test_source_checkpoint_survives_global_display_retention(database,tmp_path):
    with database() as s:
        s.add(db.Run(source='slow',started_at='2026-01-01T00:00:00+00:00',status='error',count=0));s.flush()
        for _ in range(105):s.add(db.Run(source='fast',started_at='2026-01-02T00:00:00+00:00',status='error',count=0))
        s.commit()
    state=export_snapshot(database,tmp_path,[])
    assert any(r['source']=='slow' for r in state['runs'])
    assert len(json.loads((tmp_path/'v1/runs').read_text()))==100

def test_prior_success_survives_display_retention(database,tmp_path):
    previous={'schema_version':1,'last_successful_scan':'2025-12-01T00:00:00+00:00'}
    state=export_snapshot(database,tmp_path,[],previous_state=previous)
    assert state['last_successful_scan']==previous['last_successful_scan']

def test_nonpublic_fields_removed_and_secret_urls_rejected(database,tmp_path):
    o=parse_campaign('https://example.org/sample','<h1>Muestra gratis</h1><p>Solicita tu muestra</p>','Synthetic fixture')
    o['private_note']='NEVER-PUBLISH'
    with database() as s:db.upsert(s,o);s.commit()
    export_snapshot(database,tmp_path,[])
    assert 'NEVER-PUBLISH' not in (tmp_path/'snapshot.json').read_text()
    o['url']='https://example.org/item?access_token=SYNTHETIC-SECRET'
    with database() as s:db.upsert(s,o);s.commit()
    with pytest.raises(ValueError):export_snapshot(database,tmp_path,[])
    assert 'SYNTHETIC-SECRET' not in (tmp_path/'snapshot.json').read_text()

def test_public_url_rejects_secret_fragments():
    from app.cloud import public_url
    with pytest.raises(ValueError):public_url('https://example.org/item#access_token=fixture')
