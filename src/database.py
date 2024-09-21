from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm.session import Session

Base = declarative_base()


class Cancellation(Base):
    __tablename__ = "cancellations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    program = Column(String)
    course = Column(String)
    instructor = Column(String)
    date = Column(String)
    day_of_week = Column(String)
    period = Column(String)
    remarks = Column(String)
    published_at = Column(String)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_dict_without_id(self):
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
            if c.name != "id"
        }


def create_database(database_filename: str) -> Session:
    engine = create_engine(f"sqlite:///{database_filename}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def select_cancellation_list_by_date(session: Session, date: str) -> list[Cancellation]:
    return session.query(Cancellation).filter_by(date=date).all()


def insert_cancellation_if_not_exist(
    session: Session, cancellation: Cancellation
) -> bool:
    # id 以外の属性が一致する休講情報が存在するかどうか
    exist = (
        session.query(Cancellation)
        .filter_by(**cancellation.to_dict_without_id())
        .first()
    )
    if exist:
        return False
    session.add(cancellation)
    session.commit()
    return True


def update_cancellation_list(session: Session, cancellation_list: list[Cancellation]):
    for c in cancellation_list:
        session.query(Cancellation).filter_by(id=c.id).update(c)
    session.commit()
