from database import session, User, Intervals


def get_user_by_tg_id(tg_id: int) -> User:
    user = (session.query(User).filter(User.tg_id == str(tg_id)).first())
    return user



