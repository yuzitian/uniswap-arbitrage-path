graph = {1:[2, 3, 4], 2:[1, 3, 4], 3:[1, 2, 4], 4:[1, 2, 3]}
paths = []

for a in graph.keys():
    for b in graph[a]:
        for c in graph[b]:
            path = []
            if a in graph[c]:
                path.append(a)
                path.append(b)
                path.append(c)
                path.append(a)
                paths.append(path)


print(paths)
print(len(paths))