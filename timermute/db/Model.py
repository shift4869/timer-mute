from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base

Base = declarative_base()


class MuteWord(Base):
    """ミュートワードモデル

        [id] INTEGER NOT NULL UNIQUE,
        [keyword] TEXT NOT NULL,
        [status] TEXT,
        [created_at] TEXT,
        [updated_at] TEXT,
        [unmuted_at] TEXT,
        PRIMARY KEY([id])
    """

    __tablename__ = "MuteWord"

    id = Column(Integer, primary_key=True)
    keyword = Column(String(256), nullable=False)
    status = Column(String(128), default="unmuted")
    created_at = Column(String(256))
    updated_at = Column(String(256))
    unmuted_at = Column(String(256))

    def __init__(self, *args, **kwargs):
        super(Base, self).__init__(*args, **kwargs)

    def __init__(self, keyword, status, created_at, updated_at, unmuted_at):
        # self.id = id
        self.keyword = keyword
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        self.unmuted_at = unmuted_at

    def __repr__(self):
        return "<MuteWord(id='{}', keyword='{}')>".format(self.id, self.keyword)

    def __eq__(self, other):
        return isinstance(other, MuteWord) and other.keyword == self.keyword

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "keyword": self.keyword,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "unmuted_at": self.unmuted_at,
        }

    def to_muted_table_list(self) -> list[str]:
        # {
        #     "id": self.id,
        #     "keyword": self.keyword,
        #     "updated_at": self.updated_at,
        #     "unmuted_at": self.unmuted_at,
        # }
        # -> [id, keyword, updated_at, unmuted_at]
        d = self.to_dict()
        return [
            d.get("id"),
            d.get("keyword"),
            d.get("updated_at"),
            d.get("unmuted_at"),
        ]

    def to_unmuted_table_list(self) -> list[str]:
        # {
        #     "id": self.id,
        #     "keyword": self.keyword,
        #     "updated_at": self.updated_at,
        #     "created_at": self.created_at,
        # }
        # -> [id, keyword, updated_at, created_at]
        d = self.to_dict()
        return [
            d.get("id"),
            d.get("keyword"),
            d.get("updated_at"),
            d.get("created_at"),
        ]


class MuteUser(Base):
    """ミュートアカウントモデル

        [id] INTEGER NOT NULL UNIQUE,
        [screen_name] TEXT NOT NULL,
        [status] TEXT,
        [created_at] TEXT,
        [updated_at] TEXT,
        [unmuted_at] TEXT,
        PRIMARY KEY([id])
    """

    __tablename__ = "MuteUser"

    id = Column(Integer, primary_key=True)
    screen_name = Column(String(256), nullable=False)
    status = Column(String(128), default="unmute")
    created_at = Column(String(256))
    updated_at = Column(String(256))
    unmuted_at = Column(String(256))

    def __init__(self, *args, **kwargs):
        super(Base, self).__init__(*args, **kwargs)

    def __init__(self, screen_name, status, created_at, updated_at, unmuted_at):
        # self.id = id
        self.screen_name = screen_name
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        self.unmuted_at = unmuted_at

    def __repr__(self):
        return "<MuteUser(id='{}', screen_name='{}')>".format(self.id, self.screen_name)

    def __eq__(self, other):
        return isinstance(other, MuteUser) and other.keyword == self.screen_name

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "screen_name": self.screen_name,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "unmuted_at": self.unmuted_at,
        }

    def to_muted_table_list(self) -> list[str]:
        # {
        #     "id": self.id,
        #     "screen_name": self.screen_name,
        #     "updated_at": self.updated_at,
        #     "unmuted_at": self.unmuted_at,
        # }
        # -> [id, screen_name, updated_at, unmuted_at]
        d = self.to_dict()
        return [
            d.get("id"),
            d.get("screen_name"),
            d.get("updated_at"),
            d.get("unmuted_at"),
        ]

    def to_unmuted_table_list(self) -> list[str]:
        # {
        #     "id": self.id,
        #     "screen_name": self.screen_name,
        #     "updated_at": self.updated_at,
        #     "created_at": self.created_at,
        # }
        # -> [id, screen_name, updated_at, created_at]
        d = self.to_dict()
        return [
            d.get("id"),
            d.get("screen_name"),
            d.get("updated_at"),
            d.get("created_at"),
        ]


if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    engine = create_engine("sqlite:///test_DB.db", echo=True)
    Base.metadata.create_all(engine)

    session = Session(engine)
    session.query(MuteWord).delete()

    mute_word_list = [
        ("test_word_1", "unmuted", "2023-04-08 00:01:00", "2023-04-08 00:02:00"),
        ("test_word_2", "unmuted", "2023-04-08 00:01:00", "2023-04-08 00:02:00"),
        ("test_word_3", "unmuted", "2023-04-08 00:01:00", "2023-04-08 00:02:00"),
        ("test_word_4", "unmuted", "2023-04-08 00:01:00", "2023-04-08 00:02:00"),
    ]

    for i, data in enumerate(mute_word_list):
        mute_word_record = MuteWord(
            # id=i,
            keyword=data[0],
            status=data[1],
            created_at=data[2],
            updated_at=data[3]
        )
        session.add(mute_word_record)
    session.commit()

    result = session.query(MuteWord).all()[:10]
    for f in result:
        print(f)

    session.query(MuteUser).delete()

    mute_word_list = [
        ("test_account_1", "unmuted", "2023-04-08 00:01:00", "2023-04-08 00:02:00"),
        ("test_account_2", "unmuted", "2023-04-08 00:01:00", "2023-04-08 00:02:00"),
        ("test_account_3", "unmuted", "2023-04-08 00:01:00", "2023-04-08 00:02:00"),
        ("test_account_4", "unmuted", "2023-04-08 00:01:00", "2023-04-08 00:02:00"),
    ]

    for i, data in enumerate(mute_word_list):
        mute_word_record = MuteUser(
            # id=i,
            screen_name=data[0],
            status=data[1],
            created_at=data[2],
            updated_at=data[3]
        )
        session.add(mute_word_record)
    session.commit()

    result = session.query(MuteUser).all()[:10]
    for f in result:
        print(f)

    session.close()
