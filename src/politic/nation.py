import json
from src.politic.groups.group import Group
from src.politic.builds.classes import City


class Nation:
    def __init__(self, manager, name, ptype, coords):
        self.manager = manager
        self.manager.nations_set.add(self)
        self.name = name
        self.ptype = ptype
        with open(f"src/politic/nation_data/tech.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        self.tech = data
        self.capital = City(coords, self,"city1")
        self.manager.new_build(self.capital)
        self.capital.group.resources = {
            "food": 300,
            "population": 1000,
            "electry": 100,
            "tree": 0,
            "stone": 100,
            "iron": 60,
            "copper": 30,
            "uran": 0,
            "oil": 500,
            "comp_t1": 10,
            "comp_t2": 0,
            "comp_t3": 0,
        }
        self.area=None