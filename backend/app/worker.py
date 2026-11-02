"""Run exactly one worker process. Database records all attempts; no simulated catalog."""
import argparse
import os
import time
from datetime import datetime, timezone
from . import db
from .domain import now
from .connectors.images import enrich_image
from .connectors.registry import load_sources
from .connectors.safe_http import SafeHTTP
from .connectors.html import HtmlConnector
from .connectors.usgs import UsgsConnector
from .connectors.agrisera import AgriseraConnector
from .connectors.bemz import BemzConnector
from .connectors.mgl import MglConnector
from .connectors.kvik import KvikConnector
from .connectors.promotion_feed import PromotionFeedConnector

def reconcile_source(session, source_id, seen):
    """A missing link or failed scan is not proof of expiry or stock."""
    for row in session.query(db.Offer).all():
        if row.payload.get('source_id')!=source_id: continue
        if seen is not None and row.id in seen: continue
        payload=dict(row.payload)
        payload['source_status']='unreachable' if seen is None else 'missing'
        if payload.get('status') not in {'expired','sold_out','rejected'}:
            payload['status']='pending'
        # Preserve checked_at: no offer verification was completed.
        db.upsert(session,payload)

def _run_locked(force=False):
    db.init_db();results=[]
    for source in load_sources():
        if not source.get('enabled') or not source.get('policy_reviewed'): continue
        with db.Session() as s:
            last=s.query(db.Run).filter_by(source=source['id']).order_by(db.Run.id.desc()).first()
            # Force requests never bypass source limits.
            interval=max(source.get('minimum_hours',24),float(os.getenv('SCAN_HOURS','6')))
            if last and (datetime.now(timezone.utc)-datetime.fromisoformat(last.started_at)).total_seconds()<interval*3600:
                results.append(dict(source=source['id'],status='not_due'));continue
            run=db.Run(source=source['id'],started_at=now(),status='running',count=0);s.add(run);s.commit();rid=run.id
        http=None
        try:
            http=SafeHTTP(source['hosts'])
            adapter={'usgs':UsgsConnector,'agrisera':AgriseraConnector,'html':HtmlConnector,'mgl':MglConnector,'bemz':BemzConnector,'kvik':KvikConnector,'promotion_feed':PromotionFeedConnector}[source['adapter']]
            offers=adapter(source,http).collect()
            with db.Session() as s:
                seen={o['id'] for o in offers}
                for o in offers:
                    o.update(source_id=source['id'],source_status='current')
                    db.upsert(s,enrich_image(o))
                reconcile_source(s,source['id'],seen)
                run=s.get(db.Run,rid);run.status='ok';run.count=len(offers);run.finished_at=now();s.commit()
            results.append(dict(source=source['id'],status='ok',count=len(offers)))
        except Exception as e:
            with db.Session() as s:
                reconcile_source(s,source['id'],None)
                run=s.get(db.Run,rid);run.status='error';run.error=f'{type(e).__name__}: {str(e)[:400]}';run.finished_at=now();s.commit()
            results.append(dict(source=source['id'],status='error',error=type(e).__name__))
        finally:
            if http is not None: http.close()
    return results

def run_once(force=False):
    from filelock import FileLock, Timeout
    try:
        with FileLock(os.getenv('LOCK_FILE','./freefinder-worker.lock'),timeout=0):
            return _run_locked(force)
    except Timeout:
        return [dict(status='busy')]

def main():
    p=argparse.ArgumentParser();p.add_argument('--once',action='store_true');args=p.parse_args()
    while True:
        print(run_once(),flush=True)
        if args.once:break
        time.sleep(60)
if __name__=='__main__':main()
