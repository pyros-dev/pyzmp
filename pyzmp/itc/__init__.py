

"""
Interval Tree Clocks

These are used to check if all PAST known messages have been received by one node.
We can therefore decide to enforce causality conservation if/when needed.

Ref : https://github.com/ricardobcl/Interval-Tree-Clocks
Ref : http://haslab.uminho.pt/cbm/files/itc.pdf

Maybe we could represent these here with a CRDT ? Maybe there is some kind of equivalence ?
"""