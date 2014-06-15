import random
from activityAgent import activityAgent

class auctioneer:
    def __init__(self, buyers):
        self.buyers = buyers

    def wantToAuction(self):
        if random.randint(0,1) == 0:
            return True
        else:
            return False

    def hostAuction(self, thres=0):
        winner = activityAgent('None')
        for i in self.buyers:
            tmpBid = i.bid()
            print i.activityId, "Agent bids ", tmpBid
            if tmpBid > thres and tmpBid <= i.money:
                thres = tmpBid
                winner = i

        winner.reduceMoney(thres);
        if winner.activityId == 'None':
            print "No Agent Get"
        else:
            print "By", thres, ",", winner.activityId, "Agent Get"

    def supplyMoney(self):
        for i in self.buyers:
            i.addMoney(i.weight)

    def reportMoney(self):
        print "Current Money: ",
        for i in self.buyers:
            print "(", i.activityId, i.money, ") ",
        print ""


if __name__ == '__main__':
    aAgentsList = []
    aAgentsList.append(activityAgent('Working',100,2))
    aAgentsList.append(activityAgent('Leisure',100,5))
    a = auctioneer(aAgentsList)
    
    for hour in range(0, 24, 1):
        for minute in range(0, 60, 1):
            if a.wantToAuction():
                print "===== ", str(hour).zfill(2), ":", str(minute).zfill(2), ", START an auction"
                a.hostAuction()
            else:
                print "===== ", str(hour).zfill(2), ":", str(minute).zfill(2), ", NO auction"

            a.supplyMoney()
            a.reportMoney()
            print ""
