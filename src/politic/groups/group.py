from collections import Counter


def check_graph_integrity(edges):
    # Строим граф в виде словаря смежности
    graph = {}
    for v1, v2 in edges:
        if v1 != v2:
            graph.setdefault(v1, []).append(v2)
            graph.setdefault(v2, []).append(v1)

    # Поиск в глубину для нахождения компонент связности
    visited = set()
    components = []

    def dfs(node, component):
        stack = [node]
        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                component.append(current)
                stack.extend(neighbor for neighbor in graph.get(current, [])
                             if neighbor not in visited)

    # Находим все компоненты связности
    for node in graph:
        if node not in visited:
            component = []
            dfs(node, component)
            components.append(component)

    # Если граф цельный (одна компонента связности)
    if len(components) == 1:
        return [edges]

    # Разделяем рёбра по компонентам связности
    result = []
    for component in components:
        comp_set = set(component)
        comp_edges = []
        for edge in edges:
            if edge[0] in comp_set and edge[1] in comp_set:
                comp_edges.append(edge)
        result.append(comp_edges)

    return result


class Group:
    def __init__(self, manager, links):
        self.manager = manager
        self.new_builds=[]
        self.links_set = set(links)
        items = set()
        self.builds_set = set()
        for i in links:
            items.add(i[0])
            items.add(i[1])
        for i in items:
            self.builds_set.add(self.manager.id_to_build[i])
        self.needs = None
        self.resources = {
            "food": 0,
            "population": 0,
            "electry": 0,
            "tree": 0,
            "stone": 0,
            "iron": 0,
            "copper": 0,
            "uran": 0,
            "oil": 0,
            "comp_t1": 0,
            "comp_t2": 0,
            "comp_t3": 0,
        }
        self.resources_level = {
            "food": 0,
            "population": 0,
            "electry": 0,
            "tree": 0,
            "stone": 0,
            "iron": 0,
            "copper": 0,
            "uran": 0,
            "oil": 0,
            "comp_t1": 0,
            "comp_t2": 0,
            "comp_t3": 0,
        }

    def update(self, mapp, fossils):
        sub = lambda a, b: {k: max(0, a[k] - b[k]) for k in a}
        res_in = Counter()
        for i in self.builds_set:
            res_in.update(i.need_resources)
        self.needs = dict(res_in)
        for key in self.needs.keys():
            try:
                self.resources_level[key] = int(self.resources[key]) / int(self.needs[key])
            except Exception:
                self.resources_level[key] = 1.0
            self.resources_level[key] = min(1.0, self.resources_level[key])
        res_out = Counter(self.resources)
        for i in self.builds_set:
            if i.type_data[:-1] == "mine":
                res_out.update(i.OUT_resources(self.resources_level, fossils))
            else:
                res_out.update(i.OUT_resources(self.resources_level, mapp))
        self.resources = sub(dict(res_out),self.needs)

    def delete_build(self, id):
        for i in self.links_set:
            if id in i:
                self.links_set.remove(i)
        for i in self.builds_set:
            if id == i.id:
                self.builds_set.remove(i)
        result = set()
        for i in check_graph_integrity(self.links_set):
            result.add(Group(self.manager, i))
        return result

    def delete_link(self, link):
        self.links_set.remove(link)
        result = []
        for i in check_graph_integrity(self.links_set):
            result.append(Group(self.manager, i))
        return result

    def unification(self, other, link):
        add = lambda a, b: {k: a[k] + b[k] for k in a}
        R=Group(self.manager, list(self.links_set) + list(other.links_set) + [link])
        R.resources =add(self.resources,other.resources)
        return R
