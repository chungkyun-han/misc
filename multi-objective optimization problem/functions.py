from gurobipy import *
import plotly.plotly as py
from plotly.graph_objs import *


def powerset(s):
    x = len(s)
    return [[s[j] for j in range(x) if (i & (1 << j))] for i in range(1 << x)]


def get_GUB_GLB(c):
    try:
        numPairs = len(c)
        GLB_GUB = []
        for objDirect in [GRB.MINIMIZE, GRB.MAXIMIZE]:
            m = Model('')
            m.setParam('OutputFlag', False )
            #
            dv = {}
            for i in range(numPairs):
                for j in range(numPairs):
                    dv[i, j] = m.addVar(vtype=GRB.BINARY, name='x_(%d,%d)' % (i, j))
            m.update()
            #
            obj = LinExpr()
            for i in range(numPairs):
                for j in range(numPairs):
                    obj += c[i][j] * dv[i, j]
            m.setObjective(obj, objDirect);
            #
            for i in range(numPairs):
                m.addConstr(quicksum(dv[i,j] for j in range(numPairs)) == 1)
            for j in range(numPairs):
                m.addConstr(quicksum(dv[i,j] for i in range(numPairs)) == 1)
            #
            m.optimize()
            assert m.status == GRB.Status.OPTIMAL, 'Errors while optimization'
            GLB_GUB += [m.objVal]
        return GLB_GUB
    except GurobiError:
        print 'Error reported'


def draw_3D(Xn, Yn, Zn, labels, colors, Xe, Ye, Ze, title):
    bs=Scatter3d(x=Xe,
                   y=Ye,
                   z=Ze,
                   mode='lines',
                   line=Line(color='rgb(125,125,125)', width=1),
                   hoverinfo='none'
                   )
    bps = Scatter3d(x=Xn, y=Yn, z=Zn,
                   mode='markers', name='actors',
                   marker=Marker(symbol='dot',
                                 size=6,
                                 color=colors,
                                 colorscale='Viridis',
                                 line=Line(color='rgb(50,50,50)', width=0.5)
                                 ),
                   text=labels, hoverinfo='text')
    axis_info = {}
    for i in range(1, 4):
        axis_info['f%d' % i] = axis=dict(showbackground=False, showline=False, zeroline=False, showgrid=False,
                                          title='f%d' % i)

    layout = Layout(
             title=title,
             width=1000, height=1000,showlegend=False,
             scene=Scene(
                 xaxis=XAxis(axis_info['f1']),
                 yaxis=YAxis(axis_info['f2']),
                 zaxis=ZAxis(axis_info['f3']),
                        ),
         margin=Margin(t=100), hovermode='closest')

    data=Data([bs, bps])
    fig=Figure(data=data, layout=layout)

    return py.iplot(fig, filename=title)