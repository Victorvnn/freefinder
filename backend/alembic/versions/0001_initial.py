"""Initial schema, with extensible JSON offer facts and append-only change snapshots."""
from alembic import op
import sqlalchemy as sa
revision='0001'
down_revision=None
branch_labels=None
depends_on=None

def upgrade():
    op.create_table('offers',sa.Column('id',sa.String(64),primary_key=True),sa.Column('payload',sa.JSON(),nullable=False))
    op.create_table('revisions',sa.Column('id',sa.Integer(),primary_key=True,autoincrement=True),sa.Column('offer_id',sa.String(64),nullable=False),sa.Column('at',sa.String(40),nullable=False),sa.Column('payload',sa.JSON(),nullable=False))
    op.create_index('ix_revisions_offer_id','revisions',['offer_id'])
    op.create_table('runs',sa.Column('id',sa.Integer(),primary_key=True,autoincrement=True),sa.Column('started_at',sa.String(40),nullable=False),sa.Column('finished_at',sa.String(40),nullable=True),sa.Column('source',sa.String(100),nullable=False),sa.Column('status',sa.String(30),nullable=False),sa.Column('count',sa.Integer(),nullable=False),sa.Column('error',sa.Text(),nullable=True))
def downgrade():
    op.drop_table('runs');op.drop_index('ix_revisions_offer_id',table_name='revisions');op.drop_table('revisions');op.drop_table('offers')
