from sqlalchemy import Column, Integer, String, create_engine
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
    created_at = Column(String)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def create_database(database_filename: str) -> Session:
    engine = create_engine(f"sqlite:///{database_filename}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def get_cancellation_list_by_date(session: Session, date: str) -> list[Cancellation]:
    return session.query(Cancellation).filter_by(date=date).all()
