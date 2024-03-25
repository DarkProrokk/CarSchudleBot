from database import session, User, Intervals


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