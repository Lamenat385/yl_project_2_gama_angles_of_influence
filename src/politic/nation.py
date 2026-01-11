import json
from src.politic.groups.group import Group
from src.politic.builds.classes import City

class Nation:
    def __init__(self,manager,name,ptype,coords):
        self.manager=manager
        self.name=name
        self.ptype=ptype
        with open(f"src/politic/nation_data/tech.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        self.tech=data
        self.groups_set=set()
        self.capital=City(coords,self)
        self.manager.new_build(self.capital)
        self.groups_set.add(Group(self.manager,[(self.capital.id,self.capital.id)]))