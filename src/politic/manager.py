import numpy as np

from src.politic.groups.group import Group
from src.politic.territory.territory_manadger import Territory_manager


class Manager:
    def __init__(self, mapp, fossils):
        self.groups_set = set()
        self.bots_set = set()
        self.nations_set = set()
        self.id_to_build = {}
        self.world_map = mapp
        self.current_id = 0
        self.fossils = fossils
        self.terrain_manager = Territory_manager(self)

    def new_bot(self, bot):
        self.bots_set.add(bot)

    def new_build(self, build):
        self.current_id += 1
        build.id = f"#{self.current_id}"
        self.id_to_build[f"#{self.current_id}"] = build
        R = Group(self, [(build.id, build.id)])
        build.group = R
        self.groups_set.add(R)

    def new_link(self, link):
        t = []
        k = False
        for i in self.groups_set:
            id_list = [j.id for j in i.builds_set]
            if link[0] in id_list and link[1] in id_list:
                i.links_set.add(link)
                break
            elif link[0] in id_list or link[1] in id_list:
                k = True
                t.append(i)
        if k:
            self.groups_set.remove(t[0])
            self.groups_set.remove(t[1])
            R = t[0].unification(t[1], link)
            for i in t[0].builds_set:
                i.group = R
            for i in t[1].builds_set:
                i.group = R
            self.groups_set.add(R)

    def delete_link(self, link):
        for i in self.groups_set:
            if link in i.links_set:
                self.groups_set.remove(i)
                self.groups_set = self.groups_set | i.delete_link()
                break

    def update(self):
        self.terrain_manager.update()
        for i in self.groups_set:
            i.update(self.world_map, self.fossils)
        # for i in self.bots_set:
        #     i.choice()

