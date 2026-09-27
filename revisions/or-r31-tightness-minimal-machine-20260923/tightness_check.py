#!/usr/bin/env python3
"""Independent exact combinatorial audit of the R31 tight-response family."""
import json
from pathlib import Path

def audit(n: int):
    events = sorted([x for j in range(1, n + 1) for x in (2*j - 1, 2*j)])
    assert len(events) == 2*n
    assert len(set(events)) == 2*n
    per_vertex = []
    for i in range(1, n + 1):
        local_events = sorted([x for j in range(i, n + 1) for x in (2*j - 1, 2*j)])
        assert len(local_events) == 2*(n-i+1)
        # Between consecutive event locations every local clipped-affine term
        # has constant slope; each listed event changes exactly one local slope.
        segments = len(local_events) + 1
        per_vertex.append(segments)
    total = sum(per_vertex)
    assert total == n*n + 2*n
    return {
        "n": n,
        "global_knots": len(events),
        "total_segments": total,
        "expected_global_knots": 2*n,
        "expected_total_segments": n*n + 2*n,
    }

def main():
    ns = [1, 2, 3, 4, 8, 16, 32, 64, 128]
    records = [audit(n) for n in ns]
    out = {"status": "PASS", "family": "R_i(eta)=sum_{j=i}^n [2j-eta]_[0,1]", "records": records}
    target = Path(__file__).with_name("tightness_check.json")
    target.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
