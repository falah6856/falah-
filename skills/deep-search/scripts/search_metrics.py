#!/usr/bin/env python3
"""Search coverage toolkit for the deep-search skill.

Input: JSON Lines, one result per line with any of:
  title, url, source, query, rank (1-based), round (int)

Commands:
  fuse        dedupe + Reciprocal Rank Fusion ranking
  saturation  new unique items per round
  recapture   Chapman capture-recapture estimate between two sources
  recall      recall against a known-item list (one title or URL per line)
"""
import argparse, json, math, re, sys, unicodedata
from urllib.parse import urlsplit, parse_qsl, urlencode

TRACKING = re.compile(r"^(utm_|fbclid$|gclid$|ref$|ref_src$|mc_)")


def norm_url(u):
    if not u:
        return ""
    s = urlsplit(u.strip())
    host = s.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    path = s.path.rstrip("/")
    q = urlencode(sorted((k, v) for k, v in parse_qsl(s.query) if not TRACKING.match(k)))
    return f"{host}{path}" + (f"?{q}" if q else "")


def norm_title(t):
    if not t:
        return ""
    t = unicodedata.normalize("NFKC", t).casefold()
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def key(row):
    return norm_url(row.get("url")) or "t:" + norm_title(row.get("title"))


def fuse(rows, k=60):
    items = {}
    for r in rows:
        kk = key(r)
        if not kk or kk == "t:":
            continue
        it = items.setdefault(kk, {"title": r.get("title"), "url": r.get("url"),
                                   "score": 0.0, "hits": 0, "sources": set(), "queries": set()})
        rank = r.get("rank")
        if isinstance(rank, (int, float)) and rank >= 1:
            it["score"] += 1.0 / (k + rank)
        it["hits"] += 1
        if r.get("source"):
            it["sources"].add(r["source"])
        if r.get("query"):
            it["queries"].add(r["query"])
        if not it["title"] and r.get("title"):
            it["title"] = r["title"]
    out = sorted(items.values(), key=lambda x: (-x["score"], -x["hits"]))
    for it in out:
        it["sources"] = sorted(it["sources"])
        it["queries"] = sorted(it["queries"])
    return out


def saturation(rows):
    seen, rep = set(), []
    rounds = sorted({r.get("round", 1) for r in rows})
    for rd in rounds:
        batch = {key(r) for r in rows if r.get("round", 1) == rd} - {"", "t:"}
        new = batch - seen
        seen |= batch
        rep.append({"round": rd, "returned": len(batch), "new": len(new),
                    "new_pct": round(100 * len(new) / len(batch), 1) if batch else 0.0,
                    "cumulative": len(seen)})
    return rep


def chapman(n1, n2, m):
    N = (n1 + 1) * (n2 + 1) / (m + 1) - 1
    var = (n1 + 1) * (n2 + 1) * (n1 - m) * (n2 - m) / ((m + 1) ** 2 * (m + 2))
    se = math.sqrt(max(var, 0))
    observed = n1 + n2 - m
    return {"n1": n1, "n2": n2, "overlap": m, "observed": observed, "N": N,
            "low": max(observed, N - 1.96 * se), "high": N + 1.96 * se,
            "coverage_pct": round(100 * observed / N, 1) if N > 0 else None,
            "warning": m < 3}


def wilson(found, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = found / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def recall(rows, known):
    urls = {norm_url(r.get("url")) for r in rows} - {""}
    titles = [norm_title(r.get("title")) for r in rows if r.get("title")]
    found, missing = 0, []
    for k in known:
        k = k.strip()
        if not k:
            continue
        if k.startswith("http"):
            hit = norm_url(k) in urls
        else:
            nk = norm_title(k)
            hit = any(nk and (nk in t or t in nk) for t in titles)
        found += hit
        if not hit:
            missing.append(k)
    n = found + len(missing)
    lo, hi = wilson(found, n)
    return {"found": found, "n": n, "recall": found / n if n else 0.0,
            "ci_low": lo, "ci_high": hi, "missing": missing}


def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fuse"); f.add_argument("file"); f.add_argument("--top", type=int, default=50); f.add_argument("--k", type=int, default=60)
    s = sub.add_parser("saturation"); s.add_argument("file")
    rc = sub.add_parser("recapture"); rc.add_argument("file"); rc.add_argument("--a", required=True); rc.add_argument("--b", required=True)
    rl = sub.add_parser("recall"); rl.add_argument("file"); rl.add_argument("known")
    a = p.parse_args(argv)
    rows = load(a.file)

    if a.cmd == "fuse":
        fused = fuse(rows, a.k)
        print(f"raw={len(rows)} unique={len(fused)}")
        for i, it in enumerate(fused[: a.top], 1):
            print(f"{i:>3}. {it['score']:.4f} hits={it['hits']} [{','.join(it['sources'])}] {it['title'] or ''} {it['url'] or ''}")
    elif a.cmd == "saturation":
        for r in saturation(rows):
            print(f"round {r['round']}: returned={r['returned']} new={r['new']} ({r['new_pct']}%) cumulative={r['cumulative']}")
    elif a.cmd == "recapture":
        A = {key(r) for r in rows if r.get("source") == a.a} - {""}
        B = {key(r) for r in rows if r.get("source") == a.b} - {""}
        e = chapman(len(A), len(B), len(A & B))
        print(json.dumps(e, ensure_ascii=False, indent=2))
        if e["warning"]:
            print("WARNING: overlap < 3 — estimate unreliable; search more before trusting it.", file=sys.stderr)
        print("NOTE: assumes the two sources are independent; shared popularity bias makes N an underestimate.", file=sys.stderr)
    elif a.cmd == "recall":
        with open(a.known, encoding="utf-8") as fh:
            rep = recall(rows, fh.readlines())
        print(f"recall={rep['found']}/{rep['n']} = {100*rep['recall']:.0f}%  (95% Wilson CI {100*rep['ci_low']:.0f}–{100*rep['ci_high']:.0f}%)")
        for m in rep["missing"]:
            print("  missing:", m)


if __name__ == "__main__":
    main()
