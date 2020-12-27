from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
Session = sessionmaker()


class User(Base):
    __tablename__ = 'users'
    user_id = Column(String, primary_key=True)

    def __init__(self, user_id):
        self.user_id = user_id

    def __repr__(self):
        return f'<User({self.user_id})>'


class TimetableRecord(Base):
    __tablename__ = 'timetable_records'

    record_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'))
    weekday = Column(String)
    time = Column(String)
    lecturer = Column(String)
    subject = Column(String)
    place = Column(String)

    def __init__(self, user_id, weekday, time, subject, lecturer, place):
        self.user_id = user_id
        self.weekday = weekday
        self.time = time
        self.subject = subject
        self.lecturer = lecturer
        self.place = place

    def __repr__(self):
        return f'<TimetableRecord({self.user_id}, {self.weekday}, {self.time}, {self.subject}, {self.lecturer})>'


class Database:

    def __init__(self, url: str):
        self.engine = create_engine(url)

        Base.metadata.create_all(self.engine)
        Session.configure(bind=self.engine)

        self.session = Session()
