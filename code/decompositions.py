a#!/usr/bin/env python3

import itertools
import functools
import sys

from hypergraphs import *


#################
# Algorithm 3.1 #
#################

def get_complete_types(v, n):
    """Return the set of all orbit types of the complete 3-uniform
    hypergraph."""
    if not v - 2 <= n <= v:
        raise ValueError("Can't have more than two fixed points")

    orbits = set()

    for a in range(1, n // 2 + 1):
        for b in range(1, n // 2 + 1):
            if a + b < (n + 1) // 2:
                # (a, b, c) s.t. a + b = c
                c = a + b
                orbits.add((a, b, c))
            elif a + b < n:
                # (a, b, c) s.t. a + b + c = n
                # (b, c, a) and (c, a, b) are also triples;
                # take the lexicographically smallest.
                c = n - (a + b)
                if (a, b, c) <= (b, c, a) and (a, b, c) <= (c, a, b):
                    orbits.add((a, b, c))

    # Do some sanity checking on the number of triples
    if n % 3 == 0:
        assert len(orbits) == n * (n - 3) / 6 + 1, n
    else:
        assert len(orbits) == (n - 1) * (n - 2) / 6, n

    if n <= v - 1:
        for j in range(1, (n + 1)//2):
            for i in range(v-n):
                orbits.add((FixedPoint(i + 1), j))
    if n == v - 2:
        # Add the pair (infty1, infty2)
        orbits.add((FixedPoint(1), FixedPoint(2)))

    # Check we have the correct number of orbit types
    assert len(orbits) == v * (v - 1) * (v - 2) // 6 / n

    return sorted(orbits)


#################
# Algorithm 3.2 #
#################

def get_complete_orbits(block, v, n):
    """For a given H-block, compute the orbit
    types which its edges include."""
    covered = []

    for e in block.edges:
        u, v, w = sorted(e)
        if isinstance(u, int):      # No fixed points
            # Get the distances and normalise
            a, b, c = v-u, w-v, n-(w-u)
            if a > n // 2: a = n - a
            if b > n // 2: b = n - b
            if c > n // 2: c = n - c

            if a + b + c == n:
                edge_type = min((a,b,c), (b,c,a), (c,a,b))
            elif a + b == c:
                edge_type = (a, b, c)
            elif b + c == a:
                edge_type = (b, c, a)
            elif c + a == b:
                edge_type = (c, a, b)
            else:
                raise RuntimeError("Unreachable")

        elif isinstance(v, int):    # One fixed point
            diff = abs(v-w)
            diff = min(diff, n-diff)
            edge_type = (u, diff)

        else:   # Two fixed points
            edge_type = (u, v)

        covered.append(edge_type)

    return covered


#################
# Algorithm 3.3 #
#################

def get_admissible(H, K, get_orbits, *args):
    """For each admissible set B, find a corresponding H-block.

    Return a mapping {admissible sets} -> {corresponding H-blocks}
    """
    coverings = {}

    for V in itertools.permutations(K.vertices, len(H.vertices)):
        # A small optimisation
        if get_orbits != get_complete_orbits and ('u', 0) not in V:
            continue

        block = H.copy(V)

        if K.contains(block):
            B = get_orbits(block, *args)
            B = tuple(sorted(set(B)))
            if B not in coverings and len(B) == len(H.edges):
                coverings[B] = block

    return coverings


#################
# Algorithm 3.4 #
#################

def find_decomposition(H, K, get_types, get_orbits, *args):
    """Given hypergraphs H and K, find an H-decomposition of K,
    if one exists."""
    orbits = tuple(get_types(*args))
    possible_blocks = get_admissible(H, K, get_orbits, *args)

    @functools.lru_cache(maxsize=None)
    def find_partition(orbits, depth=0):
        """Solve the subproblem of finding only the given edge orbits"""
        if not orbits:
            return []
        for block in itertools.combinations(orbits, len(H.edges)):
            if tuple(sorted(block)) in possible_blocks:
                print("| "*depth+"Try", block)
                remain = tuple(x for x in orbits if x not in block)
                rest = find_partition(remain, depth+1)
                if rest is not None:
                    return [(block, possible_blocks[block])] + rest
        return None

    return find_partition(orbits)


#################
# Algorithm 3.5 #
#################

def get_candelabra_types(m, epsilon):
    """Get the set of orbit types of L_{m,m,[epsilon]}"""
    orbits = set()
    for a, b in itertools.combinations(range(m), 2):
        orbits.add(('u', a, b))
        orbits.add(('v', a, b))

    for d in range(m):
        for k in range(epsilon):
            orbits.add((FixedPoint(k+1), d))

    return sorted(orbits)


#################
# Algorithm 3.6 #
#################

def get_candelabra_orbits(block, m, epsilon):
    """For a given H-block, find the orbit types it covers."""
    covered = []

    for e in block.edges:
        x, y, z = sorted(e)
        if isinstance(x, FixedPoint):
            assert y[0] == 'u' and z[0] == 'v'
            dist = (z[1] - y[1]) % m
            edge_type = (x, dist)
        else:
            assert x[0] == 'u' and z[0] == 'v'
            if y[0] == 'u':
                # z is by itself
                d1, d2 = sorted([(_[1] - z[1]) % m for _ in [x, y]])
            elif y[0] == 'v':
                # x is by itself
                d1, d2 = sorted([(_[1] - x[1]) % m for _ in [y, z]])
            edge_type = (y[0], d1, d2)

        covered.append(edge_type)

    return covered


#################
# Algorithm 3.7 #
#################

def get_gdd_types(m):
    """Get the set of orbit types of K_{m,m,m}"""
    orbits = set()
    for a in range(m):
        for b in range(m):
            orbits.add((a, b))

    return sorted(orbits)


#################
# Algorithm 3.7 #
#################

def get_gdd_orbits(block, m):
    """For a given H-block, find the orbit types it covers."""
    covered = []

    for e in block.edges:
        x, y, z = e
        assert x[0] == 'u' and y[0] == 'v' and z[0] == 'w'
        edge_type = ((y[1] - x[1]) % m, (z[1] - x[1]) % m)

        covered.append(edge_type)

    return covered


######################################################################
# Helper functions to run the above methods

def find_complete_decomposition(H, v):
    """Find a complete decomposition of a hypergraph H of order v"""
    # First, find the parameter `n`, the length of the orbit
    num_edges = v * (v - 1) * (v - 2) // 6
    if num_edges % len(H.edges) != 0:
        raise ValueError("v={}, |E(H)|={} does not satisfy "
                         "obvious necessary conditions"
                         .format(v, len(H.edges)))
    num_blocks = num_edges // len(H.edges)

    n = max(i for i in range(v-2, v+1) if num_blocks % i == 0)

    K = complete_hypergraph(list(range(n)) +
                            [FixedPoint(i+1) for i in range(v-n)])

    return find_decomposition(H, K, get_complete_types,
                              get_complete_orbits, v, n)


def find_candelabra_decomposition(H, m, epsilon):
    parts = [[(c, i) for i in range(m)] for c in 'uv']
    stem = [FixedPoint(i+1) for i in range(epsilon)]

    K = candelabra(parts, stem)
    return find_decomposition(H, K, get_candelabra_types,
                              get_candelabra_orbits, m, epsilon)


def find_gdd_decomposition(H, m):
    parts = [[(c, i) for i in range(m)] for c in 'uvw']
    K = multipartite(parts)
    return find_decomposition(H, K, get_gdd_types, get_gdd_orbits, m)


######################################################################


def output(result):
    print()
    if result is None:
        print("No Solution\n")
        return

    for orbits, block in result:
        print("{!r:<50}  covers orbit types {}"
              .format(block.vertices, orbits))
    print()
    print()


H32 = Hypergraph([1,2,3,4,5,6,7,8], [[1,2,3],[1,4,5],[6,7,8]])
H33 = Hypergraph([1,2,3,4,5,6,7], [[1,2,3],[1,2,4],[5,6,7]])
H34 = Hypergraph([1,2,3,4,5,6,7], [[1,2,3],[1,4,5],[1,6,7]])
H35 = Hypergraph([1,2,3,4,5,6,7], [[1,2,3],[1,4,5],[4,6,7]])

H39 = Hypergraph([1,2,3,4,5], [[1,2,3],[1,2,4],[1,2,5]])


def main():
    # Find complete decompositions:
    for v in [9, 10, 11]:
        print("H39-decomposition of K_{{{}}}^3".format(v))
        output(find_complete_decomposition(H39, v))

    # Find candelabra systems
    for epsilon in [0, 1, 2]:
        print("H39-decomposition of L_{{9,9,[{}]}}^3".format(epsilon))
        output(find_candelabra_decomposition(H39, 9, epsilon))

    # Find group divisible designs
    print("H39-decomposition of K_{9,9,9}^3")
    output(find_gdd_decomposition(H39, 9))


if __name__ == '__main__':
    main()
