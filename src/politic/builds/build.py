import json


class Build:
    def __init__(self, coords, nation, type_data,id=None):
        self.id=id
        self.coordinats = coords
        self.nation = nation
        self.type_data=type_data
        with open(f"src/politic/builds_data/{self.type_data}.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        self.out_resources = data["out_resources"]
        self.resources_for_build = data["resources_for_build"]
        self.need_resources = data["need_resources"]

    def OUT_resources(self, resources_level):
        out = dict()
        for key in self.need_resources.keys():
            if self.need_resources[key] != 0:
                out[key] = self.out_resources[key] * 0.1 + self.out_resources[key] * 0.9 * (
                            resources_level[key] / self.need_resources[key])
            else:
                out[key] = 0
        return out

class FM_Build(Build):
    def get_fruitfulness(self, mapp):
        return 0
    def OUT_resources(self, resources_level,mapp):
        fruitfulness=self.get_fruitfulness(mapp)
        out = dict()
        for key in self.need_resources.keys():
            if self.need_resources[key] != 0:
                out[key] = self.out_resources[key] * 0.1 * fruitfulness + self.out_resources[key] * 0.9 * fruitfulness * (
                            resources_level[key] / self.need_resources[key])
            else:
                out[key] = 0
        return out
