"""A model for 3-uniform Hypergraphs"""
import itertools as _itertools


class Hypergraph(object):
    def __init__(self, vertices, edges):
        self._vertices = list(vertices)
        self._edges = [sorted(e) for e in edges]
        self._edge_set = set(tuple(e) for e in self._edges)

    vertices = property(lambda self: list(self._vertices))
    edges = property(lambda self: [list(e) for e in self._edges])

    @classmethod
    def from_edges(self, edges):
        vertices = []
        for e in edges:
            for v in e:
                if v not in vertices:
                    vertices.append(v)
        return Hypergraph(vertices, edges)

    def copy(self, vertices):
        """Return an isomorphic copy of the graph on the given vertex list."""
        # Explicitly construct the isomorphism, then apply it to each edge.
        isom = dict(zip(self._vertices, vertices))
        edges = [[isom[_] for _ in e] for e in self._edges]
        return Hypergraph(vertices, edges)

    def copy_edges(self, new_edges):
        """Return a copy of the graph onto the new edge set"""
        new_vertices = list(set(sum(new_edges, [])))
        new_edges = list(map(sorted, new_edges))
        # Try and find the appropriate vertex mapping
        for f in _itertools.permutations(new_vertices):
            isom = dict(zip(self._vertices, f))
            edges = [sorted(map(isom.get, e)) for e in self._edges]
            if edges == new_edges:
                return Hypergraph(f, edges)
        raise ValueError("Edge sets do not correspond")

    def __str__(self):
        return "(V = {}, E = {})".format(self.vertices, self.edges)

    def __repr__(self):
        return "Hypergraph({!r}, {!r})".format(self.vertices, self.edges)

    def __eq__(self, other):
        return (sorted(self._vertices) == sorted(other._vertices) and
                sorted(self._edges) == sorted(other._edges))

    def regular(self):
        """Return True if all vertices have the same degree."""
        degs = {len([e for e in self._edges if x in e]) for x in self._vertices}
        return len(degs) == 1

    def isomorphic(self, other):
        """Return True if the two hypergraphs are isomorphic."""
        # This is not at all a smart way of doing it.
        if len(self._vertices) != len(other._vertices) or len(self._edges) != len(other._edges):
            return False
        for f in _itertools.permutations(other.vertices):
            # Does f describe an isomorphism onto `self`?
            if self.copy(f) == other:
                return True
        return False

    def contains(self, H):
        """Return True if H is a sub-hypergraph of this graph"""
        return all(tuple(e) in self._edge_set for e in H._edges)

    def subgraphs(self, H, copy=None):
        """Yield subgraphs isomorphic to H"""
        length = len(H._edges)
        if copy is None:
            copy = [None for i in range(length)]

        def agree(e, f):
            """Return True if there is a maping  e -> f  such that for each edge
            e' in E(H) and corresponding f' in `copy`, the mapping extends to a
            mapping e+e' -> f+f'."""
            for f_order in _itertools.permutations(f):
                e_to_f = {a: b for a, b in zip(e, f_order)}
                f_to_e = {b: a for a, b in zip(e, f_order)}
                for e2, f2 in zip(H._edges, copy):
                    if f2 is None:
                        return True
                    if any(v in e and e_to_f[v] not in f2 for v in e2):
                        break
                    if any(v in f and f_to_e[v] not in e2 for v in f2):
                        break
                else:
                    return True
            return False

        # Try and construct a copy of H out of edges of `self`:
        i = copy.index(None)
        for e in self._edges:
            # Check whether e can be used as edge number i of H:
            if agree(H._edges[i], e):
                copy[i] = e
                if i == length - 1:
                    yield H.copy_edges(copy)
                else:
                    yield from self.subgraphs(H, copy)
            copy[i] = None

    def __sub__(self, other, keep_isolated=False):
        assert all(e in self._edges for e in other._edges)
        edges = [e for e in self._edges if e not in other._edges]
        vertices = [v for v in self._vertices
                    if keep_isolated or any(v in e for e in edges)]
        return Hypergraph(vertices, edges)

    def __add__(self, other):
        vertices = self._vertices + [v for v in other._vertices if v not in self._vertices]
        return Hypergraph(vertices, self._edges + other._edges)

    def __mul__(self, factor):
        return Hypergraph(self._vertices, self._edges * factor)

    def __rmul__(self, factor):
        return Hypergraph(self._vertices, self._edges * factor)


def complete_hypergraph(vertices):
    """Return a complete 3-uniform hypergraph on a given vertex set"""
    return Hypergraph(vertices, _itertools.combinations(vertices, 3))


def multipartite(parts):
    """Return a complete 3-uniform 3-partite hypergraph on a given set of parts"""
    vertices = sum(parts, [])
    assert len(vertices) == len(set(vertices))
    edges = _itertools.product(*parts)
    return Hypergraph(vertices, edges)


def candelabra(parts, stem=None):
    """Return the 3-uniform hypergraph L_{V1,...,Vm,[W]} for given parts/stem."""
    if stem is None:
        stem = []

    vertices = sum(parts, []) + stem
    assert len(vertices) == len(set(vertices))
    H = complete_hypergraph(vertices)
    rest = Hypergraph([],[])
    for p in parts:
        rest += complete_hypergraph(p + stem)
    return H - rest


class FixedPoint(object):
    "An element which is not moved by cycles"
    def __init__(self, num):
        self.num = num

    def __str__(self):
        return "\\infty_{{{}}}".format(self.num)

    def __unicode__(self):
        return u"\u221e_{{{}}}".format(self.num)

    def __repr__(self):
        return "INF({})".format(self.num)

    def __eq__(self, other):
        return isinstance(other, FixedPoint) and self.num == other.num

    def __lt__(self, other):
        return not isinstance(other, FixedPoint) or self.num < other.num

    def __le__(self, other):
        return not isinstance(other, FixedPoint) or self.num <= other.num

    def __gt__(self, other):
        return not (self <= other)

    def __ge__(self, other):
        return not (self < other)

    def __hash__(self):
        return hash(self.num)
