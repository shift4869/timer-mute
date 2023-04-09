# coding: utf-8
import re

from sqlalchemy import asc, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from timermute.db.Base import Base
from timermute.db.Model import MuteWord


class MuteWordDB(Base):
    def __init__(self, db_fullpath: str = "mute.db"):
        super().__init__(db_fullpath)

    def select(self) -> list[MuteWord]:
        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()
        result = session.query(MuteWord).all()
        session.close()
        return result

    def upsert(self, record: str | MuteWord):
        if isinstance(record, str):
            keyword = str(record)
            record = MuteWord(keyword, "muted", self.now(), self.now(), "")

        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()
        res = -1

        try:
            q = session.query(MuteWord).filter(MuteWord.keyword == record.keyword).with_for_update()
            p = q.one()
        except NoResultFound:
            # INSERT
            session.add(record)
            res = 0
        else:
            # UPDATE
            # id以外を更新する
            p.keyword = record.keyword
            p.status = record.status
            p.created_at = record.created_at
            p.updated_at = record.updated_at
            p.unmuted_at = record.unmuted_at
            res = 1

        session.commit()
        session.close()
        return res

    def delete(self, key):
        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()
        res = -1

        target = session.query(MuteWord).filter(MuteWord.keyword == key).first()
        session.delete(target)
        res = 0

        session.commit()
        session.close()
        return res

    def mute(self, key, unmuted_at):
        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()
        res = -1

        target = session.query(MuteWord).filter(MuteWord.keyword == key).first()
        target.status = "muted"
        target.updated_at = self.now()
        target.unmuted_at = unmuted_at
        res = 0

        session.commit()
        session.close()
        return res

    def unmute(self, key):
        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()
        res = -1

        target = session.query(MuteWord).filter(MuteWord.keyword == key).first()
        target.status = "unmuted"
        target.updated_at = self.now()
        target.unmuted_at = ""
        res = 0

        session.commit()
        session.close()
        return res
