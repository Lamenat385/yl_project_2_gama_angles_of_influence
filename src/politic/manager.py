import numpy as np


class Manager:
    def __init__(self, mapp):
        self.groups_set = set()
        self.id_to_build = {}
        self.world_map = mapp
        self.current_id = 0

    def new_build(self, build):
        self.current_id += 1
        build.id=f"#{self.current_id}"
        self.id_to_build[f"#{self.current_id}"] = build

    def new_link(self, link):
        t = []
        for i in self.groups_set:
            id_list=[j.id for j in i.builds_set]
            if link[0] in id_list and link[1] in id_list:
                i.links_set.add(link)
                break
            elif link[0] in id_list or link[1] in id_list:
                t.append(i)
        self.groups_set.remove(t[0])
        self.groups_set.remove(t[1])
        self.groups_set.add(t[0].unification(t[1], link))

    def delete_link(self, link):
        for i in self.groups_set:
            if link in i.links_set:
                self.groups_set.remove(i)
                self.groups_set = self.groups_set | i.delete_link()
                break