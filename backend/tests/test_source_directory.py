import json
import pytest
from app.source_directory import merge_directory
from app.connectors.registry import load_sources


def test_directory_covers_requested_names_without_claiming_integration():
    rows=merge_directory(load_sources())
    expected={'Amazon','AliExpress','Alibaba','SHEIN','Temu','eBay','Miravia','Banggood','DHgate','Joom','Geekbuying','Amazon Vine','SHEIN Free Trial','Influenster','Sampleo','Kuvut','The Insiders','Home Tester Club','Philips Product Tester','ReviewClub','bopki','youzz','trnd','Freecycle'}
    by_name={r['name']:r for r in rows}
    assert expected<=by_name.keys()
    assert len({r['id'] for r in rows})==len(rows)
    for name in expected:
        r=by_name[name]
        assert r['enabled'] is False
        assert r['mode']!='automated'
        assert r['url'].startswith('https://') and r['categories'] and r['policy_note']
    assert by_name['Amazon Vine']['mode']=='invitation'
    assert {r['id'] for r in rows if r['mode']=='automated'}=={r['id'] for r in load_sources() if r.get('enabled')}


def test_scanner_registry_not_expanded_by_directory():
    assert not any(r['id']=='amazon' for r in load_sources())
    assert all('adapter' not in r and 'seeds' not in r for r in merge_directory(load_sources()))


def test_source_public_projection_and_strict_url_rules():
    source={'id':'fixture','name':'Fixture','enabled':True,'seeds':['https://example.org/'],'headers':{'secret':'NEVER'},'token':'NEVER','password':'NEVER'}
    row=merge_directory([source])[0]
    assert row['mode']=='automated' and row['url']=='https://example.org/'
    assert 'NEVER' not in json.dumps(row)
    for url in ['https://user:secret@example.org/','https://example.org/?token=secret','https://example.org/#secret','http://example.org/']:
        with pytest.raises(ValueError):merge_directory([{**source,'seeds':[url]}])


def test_directory_does_not_mutate_scanner_config_and_real_ids_take_precedence():
    source={'id':'amazon','name':'Configured','enabled':False,'seeds':['https://example.org/']}
    original=json.dumps(source)
    rows=merge_directory([source])
    assert [r for r in rows if r['id']=='amazon'][0]['name']=='Configured'
    assert json.dumps(source)==original
