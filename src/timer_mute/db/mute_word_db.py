from datetime import datetime

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from timer_mute.db.base import Base
from timer_mute.db.model import MuteWord
from timer_mute.util import Result, now


class MuteWordDB(Base):
    def __init__(self, db_fullpath: str = "mute.db") -> None:
        super().__init__(db_fullpath)

    def select(self) -> list[MuteWord]:
        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()
        result = session.query(MuteWord).all()
        session.close()
        return result

    def upsert(self, record: MuteWord) -> Result:
        if not isinstance(record, MuteWord):
            raise ValueError("record must be MuteWord.")

        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()

        try:
            q = session.query(MuteWord).filter(MuteWord.keyword == record.keyword).with_for_update()
            p = q.one()
        except NoResultFound:
            # INSERT
            session.add(record)
        else:
            # UPDATE
            # id以外を更新する
            p.keyword = record.keyword
            p.status = record.status
            p.created_at = record.created_at
            p.updated_at = record.updated_at
            p.unmuted_at = record.unmuted_at

        session.commit()
        session.close()
        return Result.success

    def delete(self, keyword: str) -> Result:
        if not isinstance(keyword, str):
            raise ValueError("keyword must be str.")

        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()

        target = session.query(MuteWord).filter(MuteWord.keyword == keyword).one()
        session.delete(target)

        session.commit()
        session.close()
        return Result.success

    def mute(self, keyword: str, unmuted_at: str) -> Result:
        if not isinstance(keyword, str):
            raise ValueError("keyword must be str.")
        if not isinstance(unmuted_at, str):
            raise ValueError("unmuted_at must be str.")

        if unmuted_at:
            destination_format = "%Y-%m-%d %H:%M:%S"
            _ = datetime.strptime(unmuted_at, destination_format)

        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()

        target = session.query(MuteWord).filter(MuteWord.keyword == keyword).one()
        target.status = "muted"
        target.updated_at = now()
        target.unmuted_at = unmuted_at

        session.commit()
        session.close()
        return Result.success

    def unmute(self, keyword: str) -> Result:
        if not isinstance(keyword, str):
            raise ValueError("keyword must be str.")
        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()

        target = session.query(MuteWord).filter(MuteWord.keyword == keyword).one()
        target.status = "unmuted"
        target.updated_at = now()
        target.unmuted_at = ""

        session.commit()
        session.close()
        return Result.success
