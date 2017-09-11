from pulp import *

edges = {
    (1, 2): (1, 10),
    (1, 3): (10, 3),
    (2, 4): (1, 1),
    (2, 5): (2, 3),
    (3, 2): (1, 2),
    (3, 4): (5, 7),
    (3, 5): (12, 3),
    (4, 5): (10, 1),
    (4, 6): (1, 7),
    (5, 6): (2, 2)
}

G_adjR = {}  # G_adjR: a graph represented by adjacency lists
for (i, j) in edges:
    G_adjR.setdefault(i, []).append(j)


def get_all_paths(G_adjR, fn, tn, path=[]):
    #
    # fn: node from
    # tn: node to
    #
    path = path[:] + [fn]
    if fn == tn:
        return [path]
    if not fn in G_adjR:
        return []
    paths = []
    for an in G_adjR[fn]:
        if an not in path:
            for newpath in get_all_paths(G_adjR, an, tn, path):
                paths.append(newpath)
    return paths

print(get_all_paths(G_adjR, 1, 6))

A = set(edges.keys())
c_ij = {(i, j): inputs[0] for (i, j), inputs in edges.items()}
t_ij = {(i, j): inputs[1] for (i, j), inputs in edges.items()}

x_ij = {(i, j): LpVariable('x(%d,%d)' % (i, j), cat='Binary') for (i, j) in A}


prob = LpProblem("constrainedShortestPathProblem", LpMinimize)
# Objective
prob += lpSum([c_ij[i, j] * x_ij[i, j] for (i, j) in A])

# Constraints
prob += lpSum([x_ij[i, j] for (i, j) in A if i == 1]) == 1, 'sourceFlow'
for i in range(2, 6):
    prob += lpSum([x_ij[i0, j] for (i0, j) in A if i0 == i]) == lpSum([x_ij[j, i0] for (j, i0) in A if i0 == i]), 'fc(%d)' % i
prob += lpSum([x_ij[i, j] for (i, j) in A if j == 6]) == 1, 'sinkFlow'
prob += lpSum([t_ij[i, j] * x_ij[i, j] for (i, j) in A]) <= 14, 'timeResource'

prob.writeLP("CSP_Model.lp")
prob.solve()
print("Status:", LpStatus[prob.status])
for v in prob.variables():
    print(v.name, "=", v.varValue)

print("Obj = ", value(prob.objective))