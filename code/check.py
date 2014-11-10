from hypergraphs import *
from itertools import product, repeat
INF = FixedPoint

def permutation(*cycles):
    """Generate a permutation with given cycles"""
    perm = {}
    for points in cycles:
        for i in range(len(points)):
            perm[points[i-1]] = points[i]
    return perm


def check_decomposition(K, *args):
    """Given a set of base blocks and permutations on the vertex sets,
    check that the orbits give a decomposition of the hypergraph K."""
    all_blocks = []
    for base_blocks, permutations in zip(args[::2], args[1::2]):
        this_orbit = list(base_blocks)
        for block in this_orbit:
            for p in permutations:
                new = block.copy([p.get(v,v) for v in block.vertices])
                if new not in this_orbit:
                    this_orbit.append(new)
        all_blocks.extend(this_orbit)

    edges = []
    for block in all_blocks:
        edges.extend(block.edges)

    # Sort all the edges and all the vertices within each edge.
    edges = sorted(map(sorted, edges))
    required = sorted(map(sorted, K.edges))

    if edges == required:
        print("OK")
        return True


    # There was something wrong with the decomposition.
    # Tell the user what was wrong.

    # Check if the right number of edges were covered.
    if len(edges) != len(required):
        print("ERROR - expected {} edges, got {}"
               .format(len(required), len(edges)))
        print()
    else:
        print("ERROR:")
        print()

    # Check if there were edges missed
    print("Edges not covered:")
    missed = {tuple(e) for e in required
              if edges.count(e) < required.count(e)}
    total = 0
    for e in sorted(map(list, missed)):
        diff = required.count(e) - edges.count(e)
        if diff == 1:
            print(e)
        else:
            print(e, '*', diff)
        total += diff
    print("Total:", total, end="\n\n")

    # Check if there were any edges gained or duplicated
    print("Unwanted edges:")
    missed = {tuple(e) for e in edges
              if required.count(e) < edges.count(e)}
    total = 0
    for e in sorted(map(list, missed)):
        diff = edges.count(e) - required.count(e)
        if diff == 1:
            print(e)
        else:
            print(e, '*', diff)
        total += diff
    print("Total:", total, end="\n\n")

    return False
