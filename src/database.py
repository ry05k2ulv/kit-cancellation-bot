import argparse
from pprint import pprint

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
    posted = Column(Boolean)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_dict(self) -> dict[str, str]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_info_dict(self) -> dict[str, str]:
        return {
            "program": self.program,
            "course": self.course,
            "instructor": self.instructor,
            "date": self.date,
            "day_of_week": self.day_of_week,
            "period": self.period,
            "remarks": self.remarks,
            "published_at": self.published_at,
        }


def create_database(database_filename: str) -> Session:
    engine = create_engine(f"sqlite:///{database_filename}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def select_cancellation_list_by_date(
    session: Session,
    date: str,
) -> list[Cancellation]:
    return session.query(Cancellation).filter_by(date=date).all()


def select_cancellation_list_by_posted(
    session: Session,
    posted: bool,
) -> list[Cancellation]:
    return session.query(Cancellation).filter_by(posted=posted).all()


def insert_cancellation_list_if_not_exist(
    session: Session,
    cancellation_list: list[Cancellation],
):
    for c in cancellation_list:
        first = session.query(Cancellation).filter_by(**c.to_info_dict()).first()
        if first is None:
            session.add(c)
    session.commit()


def update_cancellation_list_posted(
    session: Session,
    cancellation_list: list[Cancellation],
    posted: bool,
):
    for c in cancellation_list:
        session.query(Cancellation).filter_by(id=c.id).update({"posted": posted})
    session.commit()
    for c in cancellation_list:
        session.refresh(c)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=str, default="cancellations.db")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    session = create_database(args.database)
    pprint([c.to_dict() for c in session.query(Cancellation).all()])
    session.close()
