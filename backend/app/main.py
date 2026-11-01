import os
import secrets
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from typing import Literal
from fastapi import FastAPI, HTTPException, Query, Request, Header
from . import db
from .domain import CATEGORIES, TYPES, total_cost

@asynccontextmanager
async def lifespan(app):
    db.init_db()
    yield

app=FastAPI(title='FreeFinder API',version='0.1.0',lifespan=lifespan)
limits=defaultdict(deque)
@app.middleware('http')
async def rate_limit(request:Request, call_next):
    from starlette.responses import JSONResponse
    host=request.client.host if request.client else 'unknown'
    q=limits[host]; t=time.monotonic()
    while q and q[0]<t-60: q.popleft()
    if len(q)>=120: return JSONResponse({'detail':'Rate limit'},429)
    q.append(t)
    if len(limits)>10000:
        for k in list(limits):
            if not limits[k] or limits[k][-1]<t-60: del limits[k]
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    return response

def output(o):
    p=dict(o.payload)
    p['total_es']=total_cost(p['promo_price'],p['shipping_cost_es'],p['additional_charges_es'])
    p['total_ad']=total_cost(p['promo_price'],p['shipping_cost_ad'],p['additional_charges_ad'])
    return p

@app.get('/health')
def health(): return {'status':'ok','catalog_is_live_search':False}

@app.get('/v1/categories')
def categories(): return CATEGORIES

@app.get('/v1/offers')
def offers(q:str=Query('',max_length=200),category:str|None=None,kind:str|None=None,country:Literal['ES','AD','both','pickup']|None=None,status:str|None=None,platform:str|None=None,brand:str|None=None,max_shipping:float|None=Query(None,ge=0),min_value:float|None=Query(None,ge=0),keepable:bool=False,include_conditional_purchase:bool=False,sort:Literal['newest','ending','total','value','confidence']='newest',limit:int=Query(50,ge=1,le=100),offset:int=Query(0,ge=0)):
    with db.Session() as s: rows=[output(o) for o in s.query(db.Offer).all()]
    def matches(p):
        if q and q.casefold() not in (p['name']+' '+p['description']+' '+(p['brand'] or '')).casefold(): return False
        for key,val in [('category',category),('kind',kind),('status',status),('platform',platform),('brand',brand)]:
            if val and p[key]!=val: return False
        if p['purchase_required'] and not include_conditional_purchase: return False
        if keepable and p['keepable'] is not True: return False
        if country in ('ES','AD') and p['shipping_'+country.lower()]!='confirmed': return False
        if country=='both' and not all(p['shipping_'+c]=='confirmed' for c in ('es','ad')): return False
        if country=='pickup' and p['kind']!='private_gift': return False
        costs=[p['shipping_cost_'+c] for c in (['ad'] if country=='AD' else ['es','ad'] if country=='both' else ['es'])]
        if max_shipping is not None and any(c is None or c>max_shipping for c in costs): return False
        if min_value is not None and (p['regular_price'] is None or p['regular_price']<min_value): return False
        return True
    rows=[p for p in rows if matches(p)]
    if sort=='newest': rows.sort(key=lambda p:p['discovered_at'],reverse=True)
    elif sort=='ending': rows.sort(key=lambda p:p['ends_at'] or '9999')
    elif sort=='value': rows.sort(key=lambda p:p['regular_price'] if p['regular_price'] is not None else -1,reverse=True)
    elif sort=='confidence': rows.sort(key=lambda p:p['confidence'],reverse=True)
    else: rows.sort(key=lambda p:p['total_ad' if country=='AD' else 'total_es'] if p['total_ad' if country=='AD' else 'total_es'] is not None else float('inf'))
    return {'items':rows[offset:offset+limit],'total':len(rows),'offset':offset}

@app.get('/v1/offers/{offer_id}')
def detail(offer_id:str):
    with db.Session() as s:
        o=s.get(db.Offer,offer_id)
        if not o: raise HTTPException(404,'Offer not found')
        return output(o)

@app.get('/v1/offers/{offer_id}/history')
def history(offer_id:str):
    with db.Session() as s:
        return [{'at':r.at,'offer':r.payload} for r in s.query(db.Revision).filter_by(offer_id=offer_id).order_by(db.Revision.id.desc()).limit(100)]

@app.get('/v1/runs')
def runs():
    with db.Session() as s:
        return [dict(id=r.id,source=r.source,started_at=r.started_at,finished_at=r.finished_at,status=r.status,count=r.count,error=r.error) for r in s.query(db.Run).order_by(db.Run.id.desc()).limit(100)]

@app.get('/v1/sources')
def sources():
    from .connectors.registry import load_sources
    return [{k:v for k,v in x.items() if k not in ('headers','token')} for x in load_sources()]

@app.post('/v1/refresh')
def refresh(authorization:str|None=Header(None)):
    token=os.getenv('ADMIN_TOKEN','')
    if not token or not secrets.compare_digest(authorization or '',f'Bearer {token}'):
        raise HTTPException(401,'Administrator token required')
    from .worker import run_once
    return run_once(force=True)
