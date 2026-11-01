import os
from sqlalchemy import create_engine, String, Text, DateTime, JSON, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

class Base(DeclarativeBase): pass
class Offer(Base):
    __tablename__='offers'
    id: Mapped[str]=mapped_column(String(64),primary_key=True)
    payload: Mapped[dict]=mapped_column(JSON)
class Revision(Base):
    __tablename__='revisions'
    id: Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    offer_id: Mapped[str]=mapped_column(String(64),index=True)
    at: Mapped[str]=mapped_column(String(40))
    payload: Mapped[dict]=mapped_column(JSON)
class Run(Base):
    __tablename__='runs'
    id: Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    started_at: Mapped[str]=mapped_column(String(40))
    finished_at: Mapped[str | None]=mapped_column(String(40),nullable=True)
    source: Mapped[str]=mapped_column(String(100))
    status: Mapped[str]=mapped_column(String(30))
    count: Mapped[int]=mapped_column(Integer,default=0)
    error: Mapped[str | None]=mapped_column(Text,nullable=True)

url=os.getenv('DATABASE_URL','sqlite:///./freefinder.db')
engine=create_engine(url,connect_args={'check_same_thread':False} if url.startswith('sqlite') else {},pool_pre_ping=True)
Session=sessionmaker(engine,expire_on_commit=False)
def init_db(): Base.metadata.create_all(engine)

def upsert(session, data):
    from .domain import now
    old=session.get(Offer,data['id'])
    if old:
        data['discovered_at']=old.payload['discovered_at']
        a={k:v for k,v in old.payload.items() if k not in ('checked_at','evidence')}
        b={k:v for k,v in data.items() if k not in ('checked_at','evidence')}
        if a!=b: session.add(Revision(offer_id=old.id,at=now(),payload=old.payload))
        old.payload=data
    else:
        session.add(Offer(id=data['id'],payload=data))
        session.add(Revision(offer_id=data['id'],at=now(),payload=data))
