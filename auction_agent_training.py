import sys
from sqlalchemy import Column, DateTime, String, Integer
from sqlalchemy import and_
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


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
        # line1 = u"name='%s', time='%s', timeSpent='%d'" % (
        #     self.user, self.time, self.timeSpent)
        # line2 = u"activity='%s', category='%s', productivity='%d'" % (
        #     self.activity.encode("UTF-8"), self.category, self.productivity)
        # return u"<Log({},\n\t {})>".format % (line1, line2)
        # return self.activity.encode('UTF-8')


def training(setting):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine('mysql://{0}:{1}@{2}/{3}?charset=utf8&use_unicode=1'
                           .format(setting['dbaccount'],
                                   setting['dbpasswd'],
                                   setting['dbserver'],
                                   setting['dbname']))

    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)
    query = session.query(RescueTime)
    for log in query.order_by(RescueTime.time.desc()).all():
        print(log)
    # for log in query.filter(and_(RescueTime.user == 'idleHao',
    #                              RescueTime.time < '2014-06-11 13:00:00')).order_by(RescueTime.time.desc()).all():

    #     print(log)
    # response = stmt.execute()
    # for row in response:
    #     print(row)


def load_setting(file_name):
    import ConfigParser
    parser = ConfigParser.ConfigParser()
    parser.read(file_name)
    setting = {}
    try:
        setting['user'] = parser.get('rescuetime', 'user')
        setting['api_key'] = parser.get('rescuetime', 'api_key')
        setting['rb'] = parser.get('rescuetime', 'rb')
        setting['re'] = parser.get('rescuetime', 're')
        setting['dbserver'] = parser.get('db', 'server')
        setting['dbname'] = parser.get('db', 'dbname')
        setting['dbaccount'] = parser.get('db', 'account')
        setting['dbpasswd'] = parser.get('db', 'passwd')
    except Exception as e:
        print(e)
        sys.exit(1)
    return setting


def main():
    import argparse

    desc = 'Read data from Recuetime and write to db'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--setting', default='setting',
                        help='Setting file (default: setting)')
    args = parser.parse_args()
    setting = load_setting(args.setting)
    training(setting)
    #test1()


if __name__ == '__main__':
    main()
