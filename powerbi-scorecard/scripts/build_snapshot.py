#!/usr/bin/env python3
"""Genera snapshot.json (valores, RAG, tendencia y sparkline del último mes
completo) que consume build_preview.py. Depende de model.json (build_model.py)."""
import json, collections, sys, os

SCRATCH = os.path.dirname(os.path.abspath(__file__))
MODEL = os.environ.get("MODEL_JSON", os.path.join(os.getcwd(), "model.json"))
m = json.load(open(MODEL))
kpis = {k["KPI_ID"]: k for k in m["dim_kpi"]}
fx = collections.defaultdict(dict)
for c, dt, n, d in m["fact"]:
    fx[c][dt] = (n, d)

def val(code, dt):
    if dt not in fx[code]:
        return None
    n, d = fx[code][dt]
    vt = kpis[code]["Value_Type"]
    if vt in ("PCT", "RATIO"):
        return n / d if (d not in (None, 0) and n is not None) else None
    if vt == "RATE1000":
        return n / d * 1000 if (d not in (None, 0) and n is not None) else None
    return n  # COUNT / CURRENCY

# Último mes "cerrado": el más reciente con >=10 KPIs de ratio con num Y den y
# SIN porcentajes imposibles (>100,1%), que delatan un mes aún en carga.
counts = collections.Counter()
anomaly = set()
for c in kpis:
    vt = kpis[c]["Value_Type"]
    if vt in ("PCT", "RATE1000", "RATIO"):
        for dt, (n, d) in fx[c].items():
            if n is not None and d not in (None, 0):
                counts[dt] += 1
                if vt == "PCT" and n / d > 1.001:   # % que supera el 100% -> datos parciales
                    anomaly.add(dt)
complete = sorted([dt for dt, c in counts.items() if c >= 10 and dt not in anomaly])
cur = sys.argv[1] if len(sys.argv) > 1 else complete[-1]
allm = sorted({dt for c in fx for dt in fx[c]})
prev = allm[allm.index(cur) - 1]

def rag(code, v):
    k = kpis[code]; t = k["Target"]; dirc = k["Direction"]
    if v is None or t in (None, "") or dirc == "N":
        return "none"
    t = float(t)
    if dirc == "H":
        return "green" if v >= t else ("amber" if v >= t * 0.95 else "red")
    return "green" if v <= t else ("amber" if v <= t * 1.05 else "red")

def trend(code, v, vp, dirc):
    if v is None or vp is None:
        return ("", "none")
    if vp == 0:
        return ("→", "none")
    pct = (v - vp) / abs(vp)
    if abs(pct) < 0.005:
        return ("→", "none")
    fav = (v > vp and dirc == "H") or (v < vp and dirc == "L")
    return (("↗" if v > vp else "↘"), "up" if fav else "down")

snap = []
idx = allm.index(cur)
window = allm[max(0, idx - 11):idx + 1]
for code, k in kpis.items():
    v = val(code, cur); vp = val(code, prev)
    if v is None:
        continue
    ar, tc = trend(code, v, vp, k["Direction"])
    spark = [val(code, mth) for mth in window]
    snap.append(dict(code=code, persp=k["Perspective"], measure=k["Measure"], process=k["Process"],
                     vt=k["Value_Type"], unit=k["Unit"], dir=k["Direction"], target=k["Target"],
                     value=v, prev=vp, rag=rag(code, v), arrow=ar, trendc=tc,
                     spark=spark, defn=k["Definition"]))
cnts = dict(collections.Counter(s["rag"] for s in snap))
out = os.path.join(os.getcwd(), "snapshot.json")
json.dump({"cur": cur, "prev": prev, "snap": snap, "counts": cnts}, open(out, "w"))
print(f"snapshot -> {out} | mes={cur} | KPIs={len(snap)} | RAG={cnts}")
