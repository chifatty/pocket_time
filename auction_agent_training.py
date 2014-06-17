import sys
from sqlalchemy import Column, DateTime, String, Integer
from sqlalchemy import and_
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import timedelta
from sklearn import tree
from sklearn import preprocessing
from sklearn.externals.six import StringIO
import pydot

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

    label = {"yes": 0, "no": 1}
    training_data = []
    query1 = session.query(UserLog)
    query1 = query1.filter(UserLog.userName == setting['user'])
    for userLog in query1.all():
        query2 = session.query(ActionLog)
        query2 = query2.filter(and_(ActionLog.actionID == userLog.actionID,
                                    ActionLog.label == 'annoyed'))
        query2 = query2.order_by(ActionLog.actionID.asc())
        for actionLog in query2.all():
            sample = {
                'time': userLog.timeStamp,
                'label': label[actionLog.data]
            }
            training_data.append(sample)
    activity_label = {'None': 1}
    for index, sample in enumerate(training_data):
        # insert features
        features = []
        # hours of date
        features.append(sample["time"].hour)
        features.append(sample["time"].weekday())
        # time between last success notification
        diff = 360
        for i in range(index - 1, -1, -1):
            if training_data[i]["label"] == 1:
                diff = (sample["time"] - training_data[i]["time"])
                diff = diff.total_seconds() / 60
                break
        features.append(diff)
        # time between last unsuccess notification
        diff = 360
        for i in range(index - 1, -1, -1):
            if training_data[i]["label"] == 0:
                diff = (sample["time"] - training_data[i]["time"])
                diff = diff.total_seconds() / 60
                break
        features.append(diff)
        # features from rescuetime log
        delta = timedelta(hours=3)
        query3 = session.query(RescueTime)
        query3 = query3.filter(and_(RescueTime.user == setting["user"],
                                    RescueTime.time < sample['time'],
                                    RescueTime.time > sample['time'] - delta))
        query3 = query3.order_by(RescueTime.timeSpent.desc())
        productivity = 0
        activities = ['None', 'None', 'None', 'None', 'None']
        index = 0
        for log in query3[0:5]:
            activities[index] = log.category.encode('UTF-8')
            activity_label[activities[index]] = 1
            productivity += log.timeSpent * log.productivity
            index += 1
        features.append(productivity)
        sample["activities"] = activities
        sample["features"] = features
    # Learning regression tree
    activity_label = sorted(activity_label.keys())
    print(activity_label)
    le = preprocessing.LabelEncoder()
    le.fit(activity_label)
    X = []
    y = []
    for sample in training_data:
        features = sample['features']
        features += le.transform(sample["activities"]).tolist()
        X.append(features)
        y.append(sample['label'])
    clf = tree.DecisionTreeRegressor(max_depth=5)
    clf = clf.fit(X, y)
    dot_data = StringIO()
    tree.export_graphviz(clf, out_file=dot_data)
    graph = pydot.graph_from_dot_data(dot_data.getvalue())
    graph.write_pdf("aution_agent_{}.pdf".format(setting["user"]))
    # print(training_data)

    # for log in query.order_by(RescueTime.time.desc()).all():
    #     print(log)
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
