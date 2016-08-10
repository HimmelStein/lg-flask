from app import db
from sqlalchemy.dialects.postgresql import JSON


class ChBible(db.Model):
    __tablename__ = 'chbible'

    id = db.Column(db.Integer, primary_key=True)
    bbid = db.Column(db.String())
    snt = db.Column(db.String())
    snt_lg = db.Column(JSON)
    snt_sdg = db.Column(JSON)

    def __init__(self, bbid, snt, snt_lg, snt_sdg):
        self.url = bbid
        self.snt = snt
        self.snt_lg = snt_lg
        self.snt_sdg = snt_sdg

    def __repr__(self):
        return '<id {0}>  <{1}>  {2}\n'.format(self.id, self.bbid, self.snt)
