import hashlib
import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from flask_login import UserMixin

Base = declarative_base()


user_channel = Table('user_channel', Base.metadata,
                     Column('user_id',
                            Integer,
                            ForeignKey('users.id')),
                     Column('channel_id',
                            Integer,
                            ForeignKey('channels.id')))


class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    login = Column(String)
    password_hash = Column(String)
    channels = relationship('Channel', secondary=user_channel)

    def __init__(self, login, password):
        self.login = login
        self.password_hash = hashlib.sha1(password).hexdigest()

    def subscribe(self, channel):
        self.channels.append(channel)

    def unsubscribe(self, channel_id):
        for i, channel in enumerate(self.channels[:]):
            if channel.id == channel_id:
                self.channels.pop(i)
                return


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    text = Column(Text)
    when = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User')
    channel_id = Column(Integer, ForeignKey('channels.id'))

    def __init__(self, text, user):
        self.user = user
        self.text = text
        self.when = datetime.datetime.now()

    def when_str(self):
        return self.when.strftime('[%d-%m-%Y %H:%M:%S]')


class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship('User')
    messages = relationship('Message', backref='channel')

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner


if __name__ == '__main__':
    import db
    Base.metadata.create_all(db.engine)