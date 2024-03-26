from database import session, User, Intervals, IntervalGroup
from datetime import datetime


def get_user_by_tg_id(tg_id: int) -> User:
    user = (session.query(User).filter(User.tg_id == str(tg_id)).first())
    return user


def interval_validator(intreval: Intervals):
    for interval1, interval2 in zip(intreval, intreval[1:]):
        if not (interval1.time_finish == interval2.time_start):
            return False
    return True


def interval_cansalled(intervals):
    for interval in intervals:
        interval.is_selected = False
        interval.user = None
    session.commit()


def interval_combiner(intervals):
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
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
