import random

from src.politic.nation import Nation


class Bot:
    def __init__(self,manager,expensive,aggressive,coords):
        self.manager = manager
        self.expensive = expensive
        self.aggressive = aggressive
        self.emotions={}
        self.nation = Nation(self.manager,"name",random.randint(0,3),coords)
    def update_emotions(self,events):
        for i in events:
            if not i["nation"] is self.nation:
                if i["type"]=="build":
                    if self.nation.area.contains(i["coordinates"]):
                        self.emotions[i["nation"]]+=self.expensive*(-20)
                    if i["data"]=="artillery":
                        self.emotions[i["nation"]]+=1/(self.aggressive*10)*(-10)+self.expensive*(-10)
                elif i["type"]=="attack":
                    if i["data"] is self.nation:
                        self.emotions[i["nation"]]+=-30-50*self.aggressive*self.expensive

