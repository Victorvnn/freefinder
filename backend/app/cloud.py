"""Finite cloud job: restore public metadata, scan once, export static Android endpoints.

No phone records, environment values, credentials or raw HTML are exported.
The files under public/ are data snapshots, not a live API or source verification.
"""
import argparse
import html
import json
import os
from pathlib import Path
from urllib.parse import urlsplit, parse_qsl
from sqlalchemy import func, select
from . import db
from .domain import now, total_cost
from .connectors.images import enrich_image

MAX_OFFERS=10_000
PUBLIC_OFFER_FIELDS=set('id source_id source_status name description brand category platform url request_url image_url image_credit image_license image_license_url regular_price promo_price currency kind shipping_es shipping_ad shipping_cost_es shipping_cost_ad additional_charges_es additional_charges_ad residency requirements starts_at ends_at published_at discovered_at checked_at status purchase_required keepable confidence rejection_reason risk_reasons evidence'.split())

def public_url(url):
    p=urlsplit(url)
    if p.scheme!='https' or not p.hostname or p.username or p.password or p.port not in (None,443) or p.fragment:
        raise ValueError('Public catalog requires credential-free HTTPS URLs')
    if any(k.lower() not in {'id','product_id','sku','variant'} for k,v in parse_qsl(p.query)):
        raise ValueError('URL query not approved for public export')
    return url

def public_offer(payload):
    result={k:v for k,v in payload.items() if k in PUBLIC_OFFER_FIELDS}
    result['url']=public_url(result['url'])
    for key in ('image_url','request_url','image_license_url'):
        if result.get(key):result[key]=public_url(result[key])
    result['evidence']=[{k:(public_url(v) if k=='source' else v) for k,v in e.items() if k in {'field','source','checked_at','method','sha256','note'}} for e in result.get('evidence',[])]
    return result

def restore_state(session_factory,state):
    if not isinstance(state,dict) or state.get('schema_version')!=1:
        raise ValueError('Unsupported public state format; refusing to reset history')
    for key in ('offers','runs','revisions'):
        if not isinstance(state.get(key),list):raise ValueError('Missing state collection: '+key)
    if len(state['offers'])>MAX_OFFERS:raise ValueError('Catalog too large')
    # A dedicated, fresh job database is required, never a replacement of an existing one.
    with session_factory() as s:
        if s.query(db.Offer).first() or s.query(db.Run).first():raise ValueError('Restore target must be empty')
        for payload in state['offers']:
            if not isinstance(payload,dict) or not payload.get('id') or not payload.get('url','').startswith('https://'):
                raise ValueError('Invalid offer in public state')
            s.add(db.Offer(id=payload['id'],payload=payload))
        for r in state['runs']:s.add(db.Run(**r))
        for r in state['revisions']:s.add(db.Revision(**r))
        s.commit()

def _run_dict(r):
    # Public errors keep the failure category, not details that could contain credentials.
    return dict(id=r.id,source=r.source,started_at=r.started_at,finished_at=r.finished_at,status=r.status,count=r.count,error=r.error.split(':',1)[0] if r.error else None)

def export_snapshot(session_factory,output,sources,previous_state=None):
    output=Path(output);(output/'v1').mkdir(parents=True,exist_ok=True)
    with session_factory() as s:
        rows=s.query(db.Offer).order_by(db.Offer.id).limit(MAX_OFFERS+1).all()
        if len(rows)>MAX_OFFERS:raise ValueError('Refusing to publish a truncated catalog')
        offers=[public_offer(enrich_image(dict(row.payload))) for row in rows]
        runs=[_run_dict(r) for r in s.query(db.Run).order_by(db.Run.id.desc()).limit(100)]
        # Keep latest attempt of every source, even if absent from display history.
        last_ids=select(func.max(db.Run.id)).group_by(db.Run.source)
        checkpoints=[_run_dict(r) for r in s.query(db.Run).filter(db.Run.id.in_(last_ids))]
        state_runs=sorted({r['id']:r for r in runs+checkpoints}.values(),key=lambda r:r['id'],reverse=True)
        revisions=[dict(id=r.id,offer_id=r.offer_id,at=r.at,payload=public_offer(r.payload)) for r in s.query(db.Revision).order_by(db.Revision.id.desc()).limit(1000)]
    successes=[r['finished_at'] for r in state_runs if r['status']=='ok' and r['finished_at']]
    prior=(previous_state or {}).get('last_successful_scan')
    if prior:successes.append(prior)
    last_success=max(successes,default=None)
    stamp=now()
    from .source_directory import merge_directory
    safe_sources=merge_directory(sources)
    state=dict(schema_version=1,generated_at=stamp,last_successful_scan=last_success,offers=offers,runs=state_runs,revisions=revisions)
    items=[]
    for o in offers:
        p=dict(o)
        for c in ('es','ad'):p['total_'+c]=total_cost(p.get('promo_price'),p.get('shipping_cost_'+c),p.get('additional_charges_'+c))
        items.append(p)
    responses={'v1/offers':dict(items=items,total=len(items),offset=0),'v1/runs':runs,'v1/sources':safe_sources,'snapshot.json':state,'health':dict(status='ok',mode='static_snapshot',catalog_is_live_search=False,generated_at=stamp,last_successful_scan=last_success)}
    for relative,payload in responses.items():
        target=output/relative
        temp=target.with_name(target.name+'.tmp')
        temp.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8');temp.replace(target)
    (output/'.nojekyll').write_text('',encoding='utf-8')
    summary='No hay productos importados. Revisa las fuentes y el historial.' if not items else f'{len(items)} oportunidades observadas. Consulta las condiciones originales.'
    errors=' · '.join(html.escape(r['source']+': '+r['status']) for r in runs[:5]) or 'Sin ejecuciones registradas.'
    page='''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FreeFinder · estado del catálogo</title><style>body{font:17px system-ui;background:#f4f8f5;color:#173c30;max-width:760px;margin:60px auto;padding:24px;line-height:1.6}main{background:white;border-radius:20px;padding:30px}a{color:#166c53}code{overflow-wrap:anywhere}</style><main><h1>FreeFinder</h1><p>Catálogo automático alojado en GitHub Pages.</p><p>SUMMARY</p><p>Última exportación: STAMP</p><p>Última revisión de fuente completada: LAST</p><h2>Conectar la app</h2><p>Copia la dirección de esta página en Ajustes → URL del backend y guarda. Después sincroniza.</p><p>La app conserva tus favoritos y notas en el teléfono. Esta página no los recibe.</p><h2>Últimos intentos</h2><p>ERRORS</p><p><a href="v1/runs">Historial JSON</a> · <a href="health">Estado JSON</a></p><p>La exportación no acredita stock, transporte o solicitud verificada. Las tareas programadas pueden retrasarse.</p></main></html>'''
    page=page.replace('SUMMARY',html.escape(summary)).replace('STAMP',html.escape(stamp)).replace('LAST',html.escape(last_success or 'Ninguna')).replace('ERRORS',errors)
    if (output/'downloads/freefinder-0.4.0.apk').is_file():
        page=page.replace('<h2>Conectar la app</h2>', '<p><a href="downloads/freefinder-0.4.0.apk">Descargar FreeFinder 0.4.0 para Android 14+</a></p><p>Versión de prueba instalada como FreeFinder 0.4, junto a la anterior. No desinstales la original: conserva sus favoritos y notas allí. Los datos personales no se transfieren automáticamente.</p><h2>Conectar la app</h2>')
    (output/'index.html').write_text(page,encoding='utf-8')
    return state

def main():
    p=argparse.ArgumentParser();p.add_argument('--state',required=True);p.add_argument('--output',required=True);p.add_argument('--export-only',action='store_true');args=p.parse_args()
    if not os.getenv('DATABASE_URL'):raise SystemExit('DATABASE_URL must point to a fresh job database')
    db.init_db();state_path=Path(args.state)
    previous=None
    if state_path.is_file():
        previous=json.loads(state_path.read_text(encoding='utf-8'))
        restore_state(db.Session,previous)
    if not args.export_only:
        from .worker import run_once
        print(json.dumps(run_once()),flush=True)
    from .connectors.registry import load_sources
    state=export_snapshot(db.Session,Path(args.output),load_sources(),previous_state=previous)
    state_path.parent.mkdir(parents=True,exist_ok=True)
    tmp=state_path.with_name(state_path.name+'.tmp');tmp.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(state_path)
    print(json.dumps(dict(mode='static_snapshot',offers=len(state['offers']),generated_at=state['generated_at'],last_successful_scan=state['last_successful_scan'])),flush=True)
if __name__=='__main__':main()
