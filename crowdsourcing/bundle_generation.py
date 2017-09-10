from random import seed, choice, random, randint


class node(object):
    def __init__(self, nid, i=None, j=None):
        self.nid = nid
        self.i, self.j = i, j
        self.edges = []

    def __repr__(self):
        return str(self.nid)


class path(object):
    def __init__(self, ori, dest, w):
        self.ori, self.dest, self.w = ori, dest, w

    def __repr__(self):
        return '%s->%s;%.03f' % (self.ori, self.dest, self.w)


class task(object):
    def __init__(self, tid, pp, dp, r):
        self.tid, self.pp, self.dp, self.r = tid, pp, dp, r

    def __repr__(self):
        return 't%d(%s->%s;%.03f)' % (self.tid, self.pp, self.dp, self.r)


class bundle(object):
    def __init__(self, n2n_distance, paths, max_detour, max_ntb, bid, t0):
        self.n2n_distance, self.paths, self.max_detour, self.max_ntb = n2n_distance, paths, max_detour, max_ntb
        self.bid = bid
        self.tasks = {}
        self.tasks[t0.tid] = t0
        seq = ['p%d' % t0.tid, 'd%d' % t0.tid]
        self.path_pd_seq, self.path_detour = {}, {}
        path_ws = 0
        for p in self.paths:
            self.path_pd_seq[p] = seq[:]
            self.path_detour[p] = self.n2n_distance[p.ori, t0.pp] + self.n2n_distance[t0.pp, t0.dp] + self.n2n_distance[t0.dp, p.dest]
            if self.path_detour[p] > self.max_detour:
                self.path_detour[p] = 1e400
            else:
                path_ws += p.w
        self.bundle_attr = t0.r * path_ws

    def __repr__(self):
        return 'b%d(ts:%s)' % (self.bid, ','.join(['t%d' % t.tid for t in self.tasks.itervalues()]))

    def display_detour_seq(self):
        for p in self.paths:
            print '\t', self.path_detour[p], '(%s->%s->%s)' % (p.ori, '->'.join(self.path_pd_seq[p]), p.dest)


    def get_point(self, pd_name):
        t = self.tasks[int(pd_name[len('p'):])]
        if pd_name.startswith('p'):
            return t.pp
        else:
            assert pd_name.startswith('d')
            return t.dp

    def simul_greedy_insertion(self, t1):
        path_insertion_estimation = {}
        for p in self.paths:
            pd_seq = self.path_pd_seq[p]
            least_ad, i0, j0 = 1e400, None, None
            for i in range(len(pd_seq)):
                if i == len(pd_seq) - 1:
                    j = i
                    p0 = self.get_point(pd_seq[i])
                    p1 = p.dest
                    additional_detour = self.n2n_distance[p0, t1.pp] + \
                             self.n2n_distance[t1.pp, t1.dp] + \
                             self.n2n_distance[t1.dp, p1]
                    if additional_detour < least_ad:
                        least_ad, i0, j0 = additional_detour, i, j
                else:
                    for j in range(i, len(pd_seq)):
                        if i == j:
                            #
                            # task t1's pick-up is just before t1's delivery
                            #
                            if i == 0:
                                p0 = p.ori
                                p1 = self.get_point(pd_seq[i])
                            else:
                                p0 = self.get_point(pd_seq[i])
                                p1 = self.get_point(pd_seq[i+1])
                            additional_detour = self.n2n_distance[p0, t1.pp] + \
                                     self.n2n_distance[t1.pp, t1.dp] + \
                                     self.n2n_distance[t1.dp, p1]
                        else:
                            #
                            # task t1's pick-up is not just before t1's delivery
                            #
                            if i == 0:
                                #
                                # Insert a new pick-up task before the first pick-up task
                                #
                                p0 = p.ori
                                p1 = self.get_point(pd_seq[i])
                            else:
                                p0 = self.get_point(pd_seq[i])
                                p1 = self.get_point(pd_seq[i + 1])
                            #
                            if j == len(pd_seq) - 1:
                                #
                                # Insert a new delivery task after the last delivery task
                                #
                                p2 = self.get_point(pd_seq[j])
                                p3 = p.dest
                            else:
                                p2 = self.get_point(pd_seq[j])
                                p3 = self.get_point(pd_seq[j + 1])
                            #
                            additional_detour = self.n2n_distance[p0, t1.pp] + \
                                     self.n2n_distance[t1.pp, p1] + \
                                     self.n2n_distance[p2, t1.dp] + \
                                     self.n2n_distance[t1.dp, p3]
                        if additional_detour < least_ad:
                            least_ad, i0, j0 = additional_detour, i, j
            assert least_ad != 1e400
            path_insertion_estimation[p] = (least_ad, i0, j0)
        return path_insertion_estimation

    def estimate_bundle_attr(self, t1):
        if len(self.tasks) + 1 == self.max_ntb:
            return -1e400, None
        else:
            path_insertion_estimation = self.simul_greedy_insertion(t1)
            path_ws = 0
            for p, (additional_detour, _, _) in path_insertion_estimation.iteritems():
                if self.path_detour[p] + additional_detour < self.max_detour:
                    path_ws += p.w
            bundle_attr = (sum(t.r for t in self.tasks.itervalues()) + t1.r) * path_ws
            return bundle_attr, path_insertion_estimation

    def insert_task(self, t1, path_insertion_estimation):
        self.tasks[t1.tid] = t1
        path_ws = 0
        for p, (additional_detour, i0, j0) in path_insertion_estimation.iteritems():
            if self.path_detour[p] + additional_detour < self.max_detour:
                path_ws += p.w
                self.path_detour[p] += additional_detour
                self.path_pd_seq[p].insert(i0, 'p%d' % t1.tid)
                self.path_pd_seq[p].insert(j0 + 1, 'd%d' % t1.tid)
            else:
                self.path_detour[p] = 1e400
        self.bundle_attr = sum(t.r for t in self.tasks.itervalues()) * path_ws


def run_test():
    #
    # Inputs
    #
    n2n_distance, paths, tasks, max_detour, max_ntb, max_num_bundle = ex1()
    #
    # Generate bundles
    #
    from time import time
    start_time = time()
    bundles = run_heuristic(n2n_distance, paths, tasks, max_detour, max_ntb, max_num_bundle)
    for b in bundles:
        print b
        b.display_detour_seq()
    print 'It takes %f sec' % (time() - start_time)


def run_heuristic(n2n_distance, paths, tasks, max_detour, max_ntb, max_num_bundle):
    bundles = []
    while tasks:
        t = tasks.pop()
        if not bundles:
            bundles += [bundle(n2n_distance, paths, max_detour, max_ntb, len(bundles), t)]
            continue
        max_attr_bun, best_bun, best_path_insertion_estimation = -1e400, None, None
        for b in bundles:
            bundle_attr, path_insertion_estimation = b.estimate_bundle_attr(t)
            if max_attr_bun < bundle_attr:
                max_attr_bun, best_bun, best_path_insertion_estimation = bundle_attr, b, path_insertion_estimation
        #
        # Try to generate a new bundle
        #
        if len(bundles) < max_num_bundle:
            b = bundle(n2n_distance, paths, max_detour, max_ntb, len(bundles), t)
            if b.bundle_attr > max_attr_bun:
                bundles += [b]
            else:
                best_bun.insert_task(t, best_path_insertion_estimation)
        else:
            assert max_attr_bun != -1e400, 'infeasible'
            best_bun.insert_task(t, best_path_insertion_estimation)
    return bundles



def ex1():
    seed(0)
    #
    # Generate nodes (pick-up and delivery points)
    #
    nodes = {}
    nid = 0
    for i in range(1, 4):
        for j in range(1, 4):
            nid += 1
            nodes[nid] = node(nid, i, j)

    n2n_distance = {}
    for n0 in nodes.itervalues():
        for n1 in nodes.itervalues():
            n2n_distance[n0.nid, n1.nid] = abs(n0.i - n1.i) + abs(n0.j - n1.j)
    #
    # Generate paths
    #
    # num_paths = 100
    num_paths = 4
    paths = []
    weights = [random() for _ in xrange(num_paths)]
    for i in xrange(num_paths):
        n0 = choice(nodes.values())
        n1 = choice(nodes.values())
        while n0 == n1:
            n1 = choice(nodes.values())
        paths += [path(n0.nid, n1.nid, weights[i] / sum(weights))]
    #
    # Generate tasks
    #
    # num_tasks = 1000
    num_tasks = 10
    tasks = []
    for i in xrange(num_tasks):
        n0 = choice(nodes.values())
        n1 = choice(nodes.values())
        while n0 == n1:
            n1 = choice(nodes.values())
        tasks += [task(i, n0.nid, n1.nid, random())]
    #
    # Set max_detour
    #
    max_detour = sum(n2n_distance.values()) / float(len(n2n_distance.values())) * 5
    max_ntb = 4
    max_num_bundle = 400
    assert max_num_bundle * max_ntb > num_tasks
    tasks.sort(key=lambda t: t.r)
    return n2n_distance, paths, tasks, max_detour, max_ntb, max_num_bundle


if __name__ == '__main__':
    n2n_distance, paths, tasks, max_detour, max_ntb, max_num_bundle = ex1()
    print n2n_distance
    print paths
    print tasks
    print max_detour
    # run()