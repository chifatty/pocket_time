import sys
import datetime

sys.path.append('.')

from rescuetime.api.service.Service import Service
from rescuetime.api.access.AnalyticApiKey import AnalyticApiKey
from rescuetime.api.model.ResponseData import ResponseData
from sqlalchemy import Column, DateTime, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class RescueTime(Base):
    __tablename__ = 'rescueTime'
    user = Column(String, primary_key=True)
    time = Column(DateTime)
    timeSpent = Column(Integer)
    activity = Column(String)
    category = Column(String)
    productivity = Column(Integer)


def dump_to_db(setting):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine('mysql://{0}:{1}@{2}/{3}?charset=utf8&use_unicode=1'
                           .format(setting['dbaccount'],
                                   setting['dbpasswd'],
                                   setting['dbserver'],
                                   setting['dbname']))

    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)
    s = session()

    rescuetime_service = Service()
    key = AnalyticApiKey(setting['api_key'], rescuetime_service)
    conf = {
        'op': 'select',
        'vn': 0,
        'pv': 'interval',
        'rb': setting['rb'],
        're': setting['re']
    }
    response = ResponseData(key, **conf)
    response.sync()
    if response.object['rows'] is not None:
        for record in response.object['rows']:
            if len(record) != 6:
                return
            time = datetime.datetime.strptime(record[0],
                                              '%Y-%m-%dT%H:%M:%S')
            data = {
                'user': setting['user'],
                'time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'timeSpent': record[1],
                'activity': ''.join(map(chr, map(ord, record[3]))),
                'category': record[4],
                'productivity': record[5]
            }
            entry = RescueTime(**data)
            s.add(entry)
            s.commit()


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
    dump_to_db(setting)
    #test1()


if __name__ == '__main__':
    main()
