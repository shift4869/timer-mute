from datetime import datetime

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from timermute.db.base import Base
from timermute.db.model import MuteUser
from timermute.util import Result, now


class MuteUserDB(Base):
    def __init__(self, db_fullpath: str = "mute.db") -> None:
        super().__init__(db_fullpath)

    def select(self) -> list[MuteUser]:
        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()
        result = session.query(MuteUser).all()
        session.close()
        return result

    def upsert(self, record: MuteUser) -> Result:
        if not isinstance(record, MuteUser):
            raise ValueError("record must be MuteUser.")

        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()

        try:
            q = session.query(MuteUser).filter(MuteUser.screen_name == record.screen_name).with_for_update()
            p = q.one()
        except NoResultFound:
            # INSERT
            session.add(record)
        else:
            # UPDATE
            # id以外を更新する
            p.screen_name = record.screen_name
            p.status = record.status
            p.created_at = record.created_at
            p.updated_at = record.updated_at
            p.unmuted_at = record.unmuted_at

        session.commit()
        session.close()
        return Result.SUCCESS

    def delete(self, key_screen_name: str) -> Result:
        if not isinstance(key_screen_name, str):
            raise ValueError("key_screen_name must be str.")

        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()

        target = session.query(MuteUser).filter(MuteUser.screen_name == key_screen_name).one()
        session.delete(target)

        session.commit()
        session.close()
        return Result.SUCCESS

    def mute(self, key_screen_name: str, unmuted_at: str) -> Result:
        if not isinstance(key_screen_name, str):
            raise ValueError("key_screen_name must be str.")
        if not isinstance(unmuted_at, str):
            raise ValueError("unmuted_at must be str.")

        if unmuted_at:
            destination_format = "%Y-%m-%d %H:%M:%S"
            _ = datetime.strptime(unmuted_at, destination_format)

        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()

        target = session.query(MuteUser).filter(MuteUser.screen_name == key_screen_name).one()
        target.status = "muted"
        target.updated_at = now()
        target.unmuted_at = unmuted_at

        session.commit()
        session.close()
        return Result.SUCCESS

    def unmute(self, key_screen_name: str) -> Result:
        if not isinstance(key_screen_name, str):
            raise ValueError("key_screen_name must be str.")

        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()

        target = session.query(MuteUser).filter(MuteUser.screen_name == key_screen_name).one()
        target.status = "unmuted"
        target.updated_at = now()
        target.unmuted_at = ""

        session.commit()
        session.close()
        return Result.SUCCESS
