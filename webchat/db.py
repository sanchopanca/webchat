import hashlib

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from webchat import config

Session = sessionmaker()
engine = create_engine('sqlite:///{0}'.format(config.DB_FILE), echo=False)
Session.configure(bind=engine)


session = Session()


from models import Channel, User, Message


def channel_create(channel_name, owner):
    channel = Channel(channel_name, owner)
    session.add(channel)
    session.commit()


def channel_get_by_id(channel_id):
    return session.query(Channel).filter(Channel.id == channel_id).first()


def channel_get_by_name(name):
    try:
        return session.query(Channel).filter(Channel.name == name).first()
    except:
        return None


def channels_get_all():
    return session.query(Channel).all()


def channels_search(substring):
    s = '%{0}%'.format(substring)
    return session.query(Channel).filter(Channel.name.like(s)).all()


def message_add(text, user_id, channel_name):
    user = user_get_by_id(user_id)
    message = Message(text, user)
    channel = channel_get_by_name(channel_name)
    channel.messages.append(message)
    session.add(message)
    session.commit()
    return message


def messages_search(channel_name, substring):
    s = '%{0}%'.format(substring)
    messages = session.query(Message).\
        filter(Message.text.like(s)).all()
    return [m for m in messages if m.channel.name == channel_name]


def user_add(login, password):
    u = User(login, password)
    session.add(u)
    session.commit()


def user_get_by_id(user_id):
    return session.query(User).filter(User.id == user_id).first()


def user_get_by_login_and_password(login, password):
    password_hash = hashlib.sha1(password).hexdigest()
    return session.query(User).filter(User.login == login).\
        filter(User.password_hash == password_hash).first()


def user_is_login_free(login):
    return session.query(User).filter(User.login == login).all() == []
