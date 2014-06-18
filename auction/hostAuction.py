import sys
import datetime
from activityAgent import activityAgent

sys.path.append('../')
import db
import angel_agent
import devil_agent
import auctioneer


class hostAuction:
    def __init__(self, setting, buyers):
        self.auctionRT = auctioneer.trainingTree(setting)
        self.buyers = buyers
        self.lastAuctionTime = None
        self.curFeature = None

    def wantToAuction(self, session, user, curTime):
        coder = auctioneer.genActivityEncoder(session, user)
        self.curFeature = auctioneer.genFeatures(session, user, curTime, coder)
        #get diff
        diff = 360
        if self.lastAuctionTime is not None:
            diff = curTime - self.lastAuctionTime
            diff = diff.total_seconds() / 60
        self.curFeature.append(diff)
        print(self.curFeature)
        #print(self.auctionRT.predict([self.curFeature])[0])
        return (self.auctionRT.predict([self.curFeature])[0] > 0.5)

    def startAuction(self, session, user, curTime, thres=0):
        #everyone bid
        winner = None
        for i in self.buyers:
            tmpBid = i.bid(self.curFeature)
            print("{} Agent bids  {}".format(i, tmpBid))
            if tmpBid > thres and tmpBid <= i.money:
                thres = tmpBid
                winner = i
        self.lastAuctionTime = curTime
        print("Highest Price: {}, ".format(thres)),
        print("{} Agent Get".format(winner))
        if winner is not None:
            winner.reduceMoney(thres)

    def supplyMoney(self, basic):
        print("ooooooooooooooooooooooooooooooooooooo")
        for i in self.buyers:
            i.addMoney(basic*i.weight)
            print("{} Agent 's money increase {}".format(i, basic*i.weight))

    def reportMoney(self):
        print("Current Money: "),
        for i in self.buyers:
            print("( {}:{} ) ".format(i, i.money)),
        print("")


def main():

    TEST_Y = 2014
    TEST_M = 6
    TEST_D = 17

    AngelMoney = 100
    DevilMoney = 100
    AngelW = 0.6
    DevilW = 0.4
    BasicRate = 50

    import argparse
    desc = 'test Auction Result'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--setting', default='setting',
                        help='Setting file (default: setting)')
    args = parser.parse_args()
    setting = auctioneer.load_setting(args.setting)

    aAgentsList = []
    workA = activityAgent('Working', angel_agent, setting, AngelMoney, AngelW)
    playA = activityAgent('Leisure', devil_agent, setting, DevilMoney, DevilW)
    aAgentsList.append(workA)
    aAgentsList.append(playA)
    a = hostAuction(setting, aAgentsList)
    session = db.session(setting['dbserver'], setting['dbname'],
                         setting['dbaccount'], setting['dbpasswd'])

    print("")
    print("")
    print("***********START SIMULATION***********")
    a.reportMoney()
    print("")
    print("")

    for hour in range(0, 24, 1):
        for minute in range(0, 31, 30):
            curTime = datetime.datetime(TEST_Y, TEST_M, TEST_D, hour, minute)
            curTimeStr = curTime.strftime('%Y-%m-%d %H:%M')
            print("===  {}".format(curTimeStr))
            if a.wantToAuction(session, setting['user'], curTime):
                print("!!!!! START auction")
                a.startAuction(session, setting['user'], curTime)
            else:
                print("...... NO auction")
            a.supplyMoney(BasicRate)
            a.reportMoney()
            print("")
            print("")


if __name__ == '__main__':
    main()
