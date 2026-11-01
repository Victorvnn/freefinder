from app import db
from app import worker
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

def test_client_initialization_failure_is_recorded(monkeypatch):
    db.engine=create_engine('sqlite://',connect_args={'check_same_thread':False},poolclass=StaticPool)
    db.Session.configure(bind=db.engine);db.init_db()
    monkeypatch.setattr(worker,'load_sources',lambda:[dict(id='test',enabled=True,policy_reviewed='2026-11-01',hosts=['example.org'],adapter='html')])
    def failure(*a,**k):raise RuntimeError('fixture construction failure')
    monkeypatch.setattr(worker,'SafeHTTP',failure)
    assert worker.run_once()[0]['status']=='error'
    with db.Session() as s: assert s.query(db.Run).one().status=='error'
