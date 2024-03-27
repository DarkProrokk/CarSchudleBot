from sqlalchemy import create_engine, text, Column, Integer, String, DateTime, Boolean, Time, ForeignKey, Date
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# Создаем подключение к базе данных
engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost:5433/carschedule')
Base = declarative_base()


class Intervals(Base):
    __tablename__ = "intervals"

    id = Column(Integer, primary_key=True)
    time_start = Column(Time)
    time_finish = Column(Time)
    busy = Column(Boolean, default=False)
    day = Column(Integer, ForeignKey('days.id'), nullable=False)
    user = Column(Integer, ForeignKey('user.id'), nullable=True)
    is_selected = Column(Boolean, default=False)
    departure_point = Column(String)
    finish_point = Column(String)
    group_id = Column(Integer, ForeignKey('intervalgroup.id'), nullable=True)


class Days(Base):
    __tablename__ = 'days'
    id = Column(Integer, primary_key=True)
    date = Column(Date)


class IntervalGroup(Base):
    __tablename__ = 'intervalgroup'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    tg_id = Column(String)
    tg_username = Column(String)
    is_admin = Column(Boolean, default=False)
    surname = Column(String, default=None, nullable=True)


# Создаем сессию для взаимодействия с базой данных
Session = sessionmaker(bind=engine)
session = Session()
