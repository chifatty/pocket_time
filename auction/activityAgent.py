import random

class activityAgent:
    def __init__(self, activityId, money=0, weight=0):
        self.activityId = activityId
        self.money = money
        self.weight = weight

    def bid(self):
        return int(round(self.money * self.getWinProb()))

    def getWinProb(self):
        return random.random()

    def addMoney(self, added):
        self.money += added

    def reduceMoney(self, reduced):
        self.money -= reduced
        
