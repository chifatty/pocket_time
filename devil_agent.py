import sys
from sqlalchemy import and_, or_
from datetime import timedelta
from sklearn import tree
from sklearn.externals.six import StringIO
import pydot
import db
from db import ActionLog
from db import UserLog
from db import RescueTime


def genLabel(session, actionID):
    query = session.query(ActionLog)
    query = query.filter(ActionLog.actionID == actionID)
    query = query.filter(or_(ActionLog.label == "activity",
                             ActionLog.label == "change"))
    value = {"activity": {"working": 0, "leisure": 1},
             "change": {"yes": 1, "no": 0}}
    result = 0
    for actionLog in query.all():
        label = actionLog.label.encode("UTF8")
        data = actionLog.data.encode("UTF8")
        result ^= value[label][data]
    return result


def genFeatures(session, user, timestamp, activityEncoder):
    features = []
    features.append(timestamp.hour)
    features.append(timestamp.weekday())
    bound = timedelta(hours=3)
    query = session.query(RescueTime)
    query = query.filter(and_(RescueTime.user == user,
                              RescueTime.time < timestamp,
                              RescueTime.time > timestamp - bound))
    query = query.order_by(RescueTime.timeSpent.desc())
    productivity = 0
    activities = ['None'] * 5
    for i, log in enumerate(query[0:5]):
        activities[i] = log.category.encode('UTF-8')
        productivity += log.timeSpent * log.productivity
    features.append(productivity)
    features += activityEncoder.transform(activities).tolist()
    return features


def genActivityEncoder(session, user):
    from sklearn import preprocessing
    query = session.query(RescueTime)
    query = query.filter(RescueTime.user == user)
    categories = {"None": 1}
    for log in query.all():
        category = log.category.encode('UTF-8')
        categories[category] = 1
    le = preprocessing.LabelEncoder()
    le.fit(sorted(categories.keys()))
    return le


def genTrainingData(session, user):
    training_data = []
    query = session.query(UserLog)
    query = query.filter(UserLog.userName == user)
    query = query.order_by(UserLog.timeStamp.asc())
    X = []
    y = []
    for userLog in query.all():
        sample = {
            'time': userLog.timeStamp,
            'label': genLabel(session, userLog.actionID)
        }
        training_data.append(sample)

    activityEncoder = genActivityEncoder(session, user)
    for index, sample in enumerate(training_data):
        features = genFeatures(session, user,
                               sample['time'], activityEncoder)
        # time between last success notification
        diff = 360
        for i in range(index - 1, -1, -1):
            if training_data[i]["label"] == 1:
                diff = (sample["time"] - training_data[i]["time"])
                diff = diff.total_seconds() / 60
                break
        features.append(diff)
        X.append(features)
        y.append(sample['label'])
    return (X, y)


def trainingTree(setting):
    session = db.session(setting['dbserver'], setting['dbname'],
                         setting['dbaccount'], setting['dbpasswd'])

    (X, y) = genTrainingData(session, setting['user'])
    clf = tree.DecisionTreeRegressor(max_depth=4)
    clf = clf.fit(X, y)
    dot_data = StringIO()
    tree.export_graphviz(clf, out_file=dot_data)
    graph = pydot.graph_from_dot_data(dot_data.getvalue())
    graph.write_pdf("devil_agent_{}.pdf".format(setting["user"]))
    return clf


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
    trainingTree(setting)
    print("0: hour, 1: day, 2: productivity, 3~7:app, 8: last_auction")


if __name__ == '__main__':
    main()
