from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from timermute.db.base import Base
from timermute.db.model import MuteUser
from timermute.util import now


class MuteUserDB(Base):
    def __init__(self, db_fullpath: str = "mute.db") -> None:
        super().__init__(db_fullpath)

    def select(self) -> list[MuteUser]:
        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()
        result = session.query(MuteUser).all()
        session.close()
        return result

    def upsert(self, record: str | MuteUser) -> int:
        if isinstance(record, str):
            screen_name = str(record)
            record = MuteUser(screen_name, "muted", now(), now(), "")

        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()
        res = -1

        try:
            q = session.query(MuteUser).filter(MuteUser.screen_name == record.screen_name).with_for_update()
            p = q.one()
        except NoResultFound:
            # INSERT
            session.add(record)
            res = 0
        else:
            # UPDATE
            # id以外を更新する
            p.screen_name = record.screen_name
            p.status = record.status
            p.created_at = record.created_at
            p.updated_at = record.updated_at
            p.unmuted_at = record.unmuted_at
            res = 1

        session.commit()
        session.close()
        return res

    def delete(self, key_screen_name) -> None:
        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()

        target = session.query(MuteUser).filter(MuteUser.screen_name == key_screen_name).one()
        session.delete(target)

        session.commit()
        session.close()
        return

    def mute(self, key_screen_name, unmuted_at) -> None:
        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()

        target = session.query(MuteUser).filter(MuteUser.screen_name == key_screen_name).one()
        target.status = "muted"
        target.updated_at = now()
        target.unmuted_at = unmuted_at

        session.commit()
        session.close()
        return

    def unmute(self, key_screen_name) -> None:
        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()

        target = session.query(MuteUser).filter(MuteUser.screen_name == key_screen_name).one()
        target.status = "unmuted"
        target.updated_at = now()
        target.unmuted_at = ""

        session.commit()
        session.close()
        return
