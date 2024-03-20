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


class Days(Base):
    __tablename__ = 'days'
    id = Column(Integer, primary_key=True)
    date = Column(Date)


class Schedule(Base):
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.now)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    tg_id = Column(String)
    tg_username = Column(String)


Base.metadata.create_all(engine)

# Создаем сессию для взаимодействия с базой данных
Session = sessionmaker(bind=engine)
session = Session()
#
# # Пример добавления нового пользователя в базу данных
# new_user = User(name='Alice')
# session.add(new_user)
# session.commit()
#
# # Пример запроса пользователей из базы данных
# users = session.query(User).all()
# for user in users:
#     print(user.name, user.created_at)

# Закрываем сессию
session.close()
