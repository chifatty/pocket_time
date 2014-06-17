from sqlalchemy import Column, DateTime, String, Integer
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserLog(Base):
    __tablename__ = 'userLog'
    actionID = Column(Integer, primary_key=True)
    userName = Column(String)
    timeStamp = Column(DateTime)

    def __repr__(self):
        user = self.userName.encode('UTF-8')
        time = self.timeStamp
        return "<UserLog(userName:{}, timeStamp:{})>".format(user, time)


class ActionLog(Base):
    __tablename__ = 'actionLog'
    actionID = Column(Integer, ForeignKey(UserLog.actionID))
    label = Column(String)
    data = Column(String)
    __table_args__ = (PrimaryKeyConstraint(actionID, label),)

    def __repr__(self):
        return "<ActionLog(label:{}, data:{})>".format(self.label, self.data)


class RescueTime(Base):
    __tablename__ = 'rescueTime'
    user = Column(String)
    time = Column(DateTime)
    timeSpent = Column(Integer)
    activity = Column(String)
    category = Column(String)
    productivity = Column(Integer)
    __table_args__ = (PrimaryKeyConstraint(user, time, activity),)

    def __repr__(self):
        user = self.user.encode('UTF-8')
        category = self.category.encode('UTF-8')
        activity = self.activity.encode('UTF-8')
        line1 = "name={}, time={}, timeSpent={}"
        line1 = line1.format(user, self.time, self.timeSpent)
        line2 = "activity={}, category={}, productivity={}"
        line2 = line2.format(activity, category, self.productivity)
        return "<Log({},\n\t {})>".format(line1, line2)


def session(server, db, account, passwd):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine('mysql://{0}:{1}@{2}/{3}?charset=utf8&use_unicode=1'
                           .format(account, passwd, server, db))

    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)
    return session
