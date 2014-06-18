

class activityAgent:
    def __init__(self, activityId, module, setting, money=0, weight=0):
        self.activityId = activityId
        self.money = money
        self.weight = weight
        self.auctionRT = module.trainingTree(setting)

    def __str__(self):
        return self.activityId

    def bid(self, curFeature):
        price = self.money * self.getWinProb(curFeature)
        return int(round(price))

    def getWinProb(self, curFeature):
        #print(self.auctionRT.predict([curFeature])[0])
        return self.auctionRT.predict([curFeature])[0]

    def addMoney(self, added):
        self.money += added

    def reduceMoney(self, reduced):
        self.money -= reduced
