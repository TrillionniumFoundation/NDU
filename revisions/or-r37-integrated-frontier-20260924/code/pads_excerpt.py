"""Offline ConcaveMinima excerpt from David Eppstein's PADS SMAWK.py.

Source mirror: https://github.com/silky/PADS-mirror
Pinned commit: a6f82ff6f2d60d52a02f7b816ae7b1dfc431b5d9
Original SMAWK.py Git blob: 0a94e9e685130f7f79262c52761414c33226214d
Original license: ABOUT-PADS.txt, blob af71e1c36786aef6226d34e3999787051343ee9a
The executable offline function below is retained without algorithmic changes.
Only its docstring, comments, and surrounding file have been shortened; this
is an excerpt, not a claim of byte identity with the full 7,700-byte source.
ConcaveMinima returns COLUMN minima. Our adapter transposes its interface.
The independent search still uses the same contractual cost oracle.

Copyright (c) 2002-2015, David Eppstein

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""


def ConcaveMinima(RowIndices, ColIndices, Matrix):
    """Column minima, with ties resolved in favor of earlier rows."""
    if not ColIndices:
        return {}
    stack = []
    for r in RowIndices:
        while len(stack) >= 1 and \
                Matrix(stack[-1], ColIndices[len(stack)-1]) \
                > Matrix(r, ColIndices[len(stack)-1]):
            stack.pop()
        if len(stack) != len(ColIndices):
            stack.append(r)
    RowIndices = stack
    minima = ConcaveMinima(RowIndices,
                          [ColIndices[i] for i in range(1, len(ColIndices), 2)],
                          Matrix)
    r = 0
    for c in range(0, len(ColIndices), 2):
        col = ColIndices[c]
        row = RowIndices[r]
        if c == len(ColIndices) - 1:
            lastrow = RowIndices[-1]
        else:
            lastrow = minima[ColIndices[c+1]][1]
        pair = (Matrix(row, col), row)
        while row != lastrow:
            r += 1
            row = RowIndices[r]
            pair = min(pair, (Matrix(row, col), row))
        minima[col] = pair
    return minima
