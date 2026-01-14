from src.politic.nation import Nation
class Player:
    def __init__(self,name,manager,ptype,coords):
        self.nation = Nation(manager,name,ptype,coords)
        self.current_choice = None