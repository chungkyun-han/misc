import sys

import cplex
from cplex.exceptions import CplexError

costs = [  [99, 19, 74, 55, 41],
       [23, 81, 93, 39, 49],
       [66, 21, 63, 24, 38],
       [65, 41, 7, 39, 66],
       [93, 30, 5, 4, 13]  ]


numPairs = len(costs)



try:
    c = cplex.Cplex()
    c.objective.set_sense(c.objective.sense.maximize)
    dv = ['x_%d,%d' % (i, j) for j in xrange(numPairs) for i in xrange(numPairs)]
    obj = [costs[i][j] for j in xrange(numPairs) for i in xrange(numPairs)]
    c.variables.add(obj=obj, names=dv, types='B' * len(dv))

    for i in xrange(numPairs):
        ind = ['x_%d,%d' % (i, j) for j in xrange(numPairs)]
        val = [1] * numPairs
        row = [[ind, val]]
        c.linear_constraints.add(lin_expr=row, senses=["L"], rhs=[1])
    # ind = ['x_%d,%d' % (i, j) for j in xrange(numPairs) for i in xrange(numPairs)]
    # c.linear_constraints.add(lin_expr=[SparsePair(ind=inside,
    #                                               val=consumption[i])
    #                                    for i in range(len(consumption))],
    #                          senses=["L" for i in consumption],
    #                          rhs=capacity,
    #                          names=["capacity_" + str(i)
    #                                 for i in range(nbResources)])

    #
    for j in xrange(numPairs):
        ind = ['x_%d,%d' % (i, j) for i in xrange(numPairs)]
        val = [1] * numPairs
        row = [[ind, val]]
        c.linear_constraints.add(lin_expr=row, senses=["L"], rhs=[1])
    #
    c.solve()
    print ''
    print "Solution status = ", c.solution.get_status()
    print "cost: " + str(c.solution.get_objective_value())
    for i in xrange(numPairs):
        for j in xrange(numPairs):
            x = 'x_%d,%d' % (i, j)
            print x, c.solution.get_values(x)

except CplexError as exc:
    print exc
