from database import session, User, Intervals, IntervalGroup
from datetime import datetime
from typing import List
from datetime import date, timedelta


def get_user_by_tg_id(tg_id: int) -> User:
    user = (session.query(User).filter(User.tg_id == str(tg_id)).first())
    return user


def interval_validator(interval: List[Intervals]):
    for interval1, interval2 in zip(interval, interval[1:]):
        if not (interval1.time_finish == interval2.time_start):
            return False
    return True


def interval_cancaller(intervals):
    for interval in intervals:
        interval.is_selected = False
        interval.user = None
        interval.departure_point = None
        interval.finish_point = None
        interval.group_id = None
    session.commit()


def interval_combiner(intervals):
    """Скомбинировать интервалы по группе.

    Эта функция комбинирует(или правильнее сказать группирует)
    переданные интервалы, добавления им одинаковую группу
    Args:
         intervals (List[Interval]): Список интервалов, которые необходимо сгруппировать
    Returns:
        None
    """
    group = IntervalGroup(created_at=datetime.now())
    session.add(group)
    session.commit()
    for interval in intervals:
        interval.group_id = group.id
    session.commit()


def interval_decliner_by_group(group_id):
    intervals = session.query(Intervals).filter(Intervals.group_id == group_id).all()
    for interval in intervals:
        interval.busy = False
        interval.user = None
        interval.group_id = None
        interval.finish_point = None
        interval.departure_point = None
    session.commit()


def get_intervals_by_group_choices(call):
    group_id = int(call.data.split('_')[1])
    interval = (session.query(Intervals.departure_point,
                              Intervals.finish_point)
                .select_from(Intervals)
                .join(User, Intervals.user == User.id)  # Join the Intervals and User tables
                .filter(Intervals.group_id == group_id)
                .first())
    return interval


def get_current_date() -> date:
    now = datetime.now()
    if now.hour >= 18:
        return date.today() + timedelta(days=1)
    else:
        return date.today()


def get_next_date() -> date:
    return date.today() + timedelta(days=1)
