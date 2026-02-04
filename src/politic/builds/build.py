import json


class Build:
    def __init__(self, coords, nation, type_data, id=None,group=None):
        self.id = id
        self.group = group
        self.coordinates = coords
        self.nation = nation
        self.type_data = type_data
        with open(f"src/politic/builds_data/{self.type_data}.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        self.out_resources = data["out_resources"]
        self.resources_for_build = data["resources_for_build"]
        self.need_resources = data["need_resources"]

    def OUT_resources(self, resources_level, mapp=None):
        out = dict()
        c = []
        for key in self.need_resources.keys():
            if self.need_resources[key] != 0:
                c.append(resources_level[key])
        c = sum(c) / len(c)
        for key in self.need_resources.keys():
            out[key] = c * self.out_resources[key]
        return out


class FM_Build(Build):
    def get_fruitfulness(self, mapp):
        return 0

    def OUT_resources(self, resources_level, mapp=None):
        fruitfulness = self.get_fruitfulness(mapp)
        out = dict()
        c = []
        for key in self.need_resources.keys():
            if self.need_resources[key] != 0:
                c.append(resources_level[key])
        c=sum(c)/len(c)
        for key in self.need_resources.keys():
            out[key] = c * self.out_resources[key] * fruitfulness
        print(out)
        return out
