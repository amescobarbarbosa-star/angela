#!/usr/bin/env python3
"""Genera la maqueta HTML del informe Power BI a partir del snapshot real."""
import json, collections, html, os

m = json.load(open("model.json"))
snap = json.load(open("snapshot.json"))
kpis = {k["KPI_ID"]: k for k in m["dim_kpi"]}
rows = {r["code"]: r for r in snap["snap"]}
cur = snap["cur"]
counts = snap["counts"]

MONTHS_ES = {1:"enero",2:"febrero",3:"marzo",4:"abril",5:"mayo",6:"junio",
             7:"julio",8:"agosto",9:"septiembre",10:"octubre",11:"noviembre",12:"diciembre"}
cy, cm = int(cur[:4]), int(cur[5:7])
month_label = f"{MONTHS_ES[cm].capitalize()} {cy}"

PERSP_ORDER = ["1. Efficient and Scalable","2. Customer Focused",
               "3. Robust Control and Compliance","4. Excellent People and Technology",
               "5. Continuous Improvement"]
PERSP_SHORT = {
    "1. Efficient and Scalable":"Eficiente y escalable",
    "2. Customer Focused":"Orientado al cliente",
    "3. Robust Control and Compliance":"Control y cumplimiento",
    "4. Excellent People and Technology":"Personas y tecnología",
    "5. Continuous Improvement":"Mejora continua",
}
PERSP_ICON = {  # inline svg path drawn in a small badge
    "1. Efficient and Scalable":"M3 13h4v6H3zM10 7h4v12h-4zM17 3h4v16h-4z",
    "2. Customer Focused":"M12 12a4 4 0 100-8 4 4 0 000 8zM4 20a8 8 0 0116 0z",
    "3. Robust Control and Compliance":"M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6z",
    "4. Excellent People and Technology":"M9 11a3 3 0 100-6 3 3 0 000 6zM2 20a7 7 0 0114 0zM17 8h5M19.5 5.5v5",
    "5. Continuous Improvement":"M4 12a8 8 0 018-8 8 8 0 016.9 4M20 12a8 8 0 01-8 8 8 0 01-6.9-4M18 3v5h-5M6 21v-5h5",
}

def fmt(vt, v):
    if v is None: return "–"
    if vt == "PCT":      return f"{v*100:.1f}%"
    if vt == "RATE1000": return f"{v:,.1f}"
    if vt == "RATIO":    return f"{v:,.0f}" if v>=100 else f"{v:,.2f}"
    if vt == "CURRENCY": return f"{v:,.0f}"
    return f"{v:,.0f}"

def fmt_target(vt, t):
    if t in (None,""): return "—"
    t=float(t)
    if vt=="PCT": return f"{t*100:.0f}%"
    return f"{t:,.0f}"

def sparkline(vals, color):
    pts=[v for v in vals if v is not None]
    if len(pts) < 2:
        return '<span class="spark-empty">—</span>'
    w,h,pad=104,30,3
    lo,hi=min(pts),max(pts)
    rng=(hi-lo) or 1
    n=len(vals)
    step=(w-2*pad)/(n-1)
    coords=[]
    for i,v in enumerate(vals):
        if v is None: continue
        x=pad+i*step
        y=h-pad-((v-lo)/rng)*(h-2*pad)
        coords.append((x,y))
    line=" ".join(f"{x:.1f},{y:.1f}" for x,y in coords)
    lx,ly=coords[-1]
    area=f"M{coords[0][0]:.1f},{h-pad} " + " ".join(f"L{x:.1f},{y:.1f}" for x,y in coords) + f" L{lx:.1f},{h-pad} Z"
    gid=f"g{abs(hash(tuple(pts)))%99999}"
    return (f'<svg class="spark" viewBox="0 0 {w} {h}" preserveAspectRatio="none" aria-hidden="true">'
            f'<defs><linearGradient id="{gid}" x1="0" x2="0" y1="0" y2="1">'
            f'<stop offset="0" stop-color="{color}" stop-opacity="0.22"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>'
            f'<path d="{area}" fill="url(#{gid})"/>'
            f'<polyline points="{line}" fill="none" stroke="{color}" stroke-width="1.6" '
            f'stroke-linejoin="round" stroke-linecap="round"/>'
            f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="2.4" fill="{color}"/></svg>')

RAG_LABEL={"green":"En objetivo","amber":"En riesgo","red":"Fuera de objetivo","none":"Sin objetivo"}

# group KPIs by perspective (all, ordered by code)
def code_key(c):
    parts=c.split("."); return (int(parts[0]), int(parts[1]) if len(parts)>1 else 0)
by_persp=collections.defaultdict(list)
for code,k in kpis.items():
    by_persp[k["Perspective"]].append(code)
for p in by_persp: by_persp[p].sort(key=code_key)

def kpi_row(code):
    k=kpis[code]; vt=k["Value_Type"]
    if code in rows:
        r=rows[code]
        rag=r["rag"]; v=r["value"]; arrow=r["arrow"]; tc=r["trendc"]; spark=r["spark"]
    else:
        rag="nodata"; v=None; arrow=""; tc="none"; spark=[]
    dot_cls={"green":"g","amber":"a","red":"r","none":"n","nodata":"x"}[rag]
    trend_cls={"up":"t-up","down":"t-down","none":"t-flat"}[tc]
    proc=k["Process"] or "All"
    spark_color={"green":"#2E7D32","amber":"#C98A12","red":"#C62828"}.get(rag,"#8B94A6")
    val_html = fmt(vt,v) if v is not None else '<span class="pend">pendiente</span>'
    return f'''<tr class="kpi {'nodata' if rag=='nodata' else ''}">
      <td class="c-dot"><span class="dot {dot_cls}" title="{RAG_LABEL.get(rag,'Sin datos')}"></span></td>
      <td class="c-code">{code}</td>
      <td class="c-meas"><span class="meas">{html.escape(k["Measure"])}</span><span class="obj">{html.escape(k["Objective"])}</span></td>
      <td class="c-proc"><span class="chip p-{proc.lower().replace(' ','')}">{proc}</span></td>
      <td class="c-val">{val_html}</td>
      <td class="c-tgt">{fmt_target(vt,k["Target"])}</td>
      <td class="c-trend"><span class="{trend_cls}">{arrow or '·'}</span></td>
      <td class="c-spark">{sparkline(spark,spark_color)}</td>
    </tr>'''

sections=[]
for p in PERSP_ORDER:
    codes=by_persp.get(p,[])
    with_data=sum(1 for c in codes if c in rows)
    obj=kpis[codes[0]]["Perspective_Objective"] if codes else ""
    body="\n".join(kpi_row(c) for c in codes)
    icon=PERSP_ICON.get(p,"")
    sections.append(f'''<section class="persp">
      <header class="persp-head">
        <span class="persp-badge"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="{icon}"/></svg></span>
        <div class="persp-titles">
          <h2>{html.escape(p)}</h2>
          <p>{html.escape(obj)}</p>
        </div>
        <span class="persp-count">{with_data}/{len(codes)} con datos</span>
      </header>
      <div class="twrap"><table class="scoretable">
        <thead><tr>
          <th></th><th>KPI</th><th>Indicador</th><th>Área</th>
          <th class="num">Valor</th><th class="num">Objetivo</th><th>Tend.</th><th>12 meses</th>
        </tr></thead>
        <tbody>{body}</tbody>
      </table></div>
    </section>''')

green=counts.get("green",0); amber=counts.get("amber",0); red=counts.get("red",0)
measured=green+amber+red+counts.get("none",0)
on_target=f"{(green/(green+amber+red)*100):.0f}%" if (green+amber+red) else "—"

HTML=f'''<title>DS Smith SSC · Balanced Scorecard — Vista previa Power BI</title>
<style>
:root{{
  --ground:#F5F7FA; --surface:#FFFFFF; --surface-2:#FBFCFE;
  --ink:#18202E; --ink-2:#5A667A; --ink-3:#8A94A6;
  --line:#E4E8EF; --line-2:#EEF1F6;
  --brand:#1F3864; --brand-2:#2E5F9A; --brand-ink:#FFFFFF;
  --green:#2E7D32; --green-bg:#E7F2E8;
  --amber:#B4790E; --amber-bg:#FBF0D8;
  --red:#C62828; --red-bg:#F9E5E5;
  --grey:#8A94A6; --grey-bg:#EDF0F5;
  --shadow:0 1px 2px rgba(24,32,46,.06),0 4px 16px rgba(24,32,46,.05);
  --radius:14px;
  --font:"Segoe UI",system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;
}}
@media (prefers-color-scheme:dark){{ :root:not([data-theme="light"]){{
  --ground:#0E131B; --surface:#161E2A; --surface-2:#1B2431;
  --ink:#E9EDF4; --ink-2:#A7B1C2; --ink-3:#727E92;
  --line:#26303F; --line-2:#202A38;
  --brand:#294B85; --brand-2:#4C7FCB; --brand-ink:#FFFFFF;
  --green:#5BB463; --green-bg:#16281A;
  --amber:#E0A83B; --amber-bg:#2C2412;
  --red:#E86A6A; --red-bg:#2E1717;
  --grey:#7E8798; --grey-bg:#1E2632;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 6px 20px rgba(0,0,0,.28);
}}}}
:root[data-theme="dark"]{{
  --ground:#0E131B; --surface:#161E2A; --surface-2:#1B2431;
  --ink:#E9EDF4; --ink-2:#A7B1C2; --ink-3:#727E92;
  --line:#26303F; --line-2:#202A38;
  --brand:#294B85; --brand-2:#4C7FCB; --brand-ink:#FFFFFF;
  --green:#5BB463; --green-bg:#16281A;
  --amber:#E0A83B; --amber-bg:#2C2412;
  --red:#E86A6A; --red-bg:#2E1717;
  --grey:#7E8798; --grey-bg:#1E2632;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 6px 20px rgba(0,0,0,.28);
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--ground);color:var(--ink);font-family:var(--font);
  font-size:14px;line-height:1.45;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1080px;margin:0 auto;padding:26px 22px 56px}}
.tabular{{font-variant-numeric:tabular-nums}}

/* Top bar */
.topbar{{background:linear-gradient(120deg,var(--brand),var(--brand-2));color:var(--brand-ink);
  border-radius:var(--radius);padding:20px 24px;display:flex;align-items:center;gap:18px;
  flex-wrap:wrap;box-shadow:var(--shadow)}}
.topbar .mark{{width:42px;height:42px;border-radius:10px;background:rgba(255,255,255,.16);
  display:grid;place-items:center;font-weight:700;font-size:17px;letter-spacing:.5px;flex:none}}
.topbar h1{{margin:0;font-size:18px;font-weight:650;letter-spacing:.2px}}
.topbar .sub{{margin:2px 0 0;font-size:12.5px;opacity:.85;font-weight:400}}
.topbar .spacer{{flex:1}}
.monthchip{{background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.25);
  border-radius:999px;padding:7px 15px;font-size:13px;font-weight:600;display:flex;
  align-items:center;gap:8px}}
.monthchip .cal{{width:14px;height:14px}}

/* Summary tiles */
.tiles{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin:18px 0 6px}}
@media(max-width:720px){{.tiles{{grid-template-columns:repeat(2,1fr)}}}}
.tile{{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
  padding:15px 16px;box-shadow:var(--shadow);position:relative;overflow:hidden}}
.tile .k{{font-size:11px;text-transform:uppercase;letter-spacing:.7px;color:var(--ink-3);font-weight:600}}
.tile .v{{font-size:30px;font-weight:680;margin-top:6px;letter-spacing:-.5px}}
.tile .stripe{{position:absolute;left:0;top:0;bottom:0;width:4px}}
.tile.on .stripe{{background:var(--brand-2)}} .tile.on .v{{color:var(--brand-2)}}
.tile.g .stripe{{background:var(--green)}} .tile.g .v{{color:var(--green)}}
.tile.a .stripe{{background:var(--amber)}} .tile.a .v{{color:var(--amber)}}
.tile.r .stripe{{background:var(--red)}} .tile.r .v{{color:var(--red)}}
.tile.m .stripe{{background:var(--grey)}}

/* Perspective sections */
.persp{{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
  box-shadow:var(--shadow);margin-top:18px;overflow:hidden}}
.persp-head{{display:flex;align-items:center;gap:14px;padding:15px 20px;
  border-bottom:1px solid var(--line-2);background:var(--surface-2)}}
.persp-badge{{width:34px;height:34px;border-radius:9px;background:var(--brand);color:#fff;
  display:grid;place-items:center;flex:none}}
.persp-badge svg{{width:19px;height:19px}}
.persp-titles{{flex:1;min-width:0}}
.persp-titles h2{{margin:0;font-size:15px;font-weight:650}}
.persp-titles p{{margin:1px 0 0;font-size:12px;color:var(--ink-2)}}
.persp-count{{font-size:11.5px;color:var(--ink-3);white-space:nowrap;font-weight:600;
  background:var(--grey-bg);padding:4px 10px;border-radius:999px}}

.twrap{{overflow-x:auto}}
.scoretable{{width:100%;border-collapse:collapse;min-width:640px}}
.scoretable thead th{{font-size:10.5px;text-transform:uppercase;letter-spacing:.6px;
  color:var(--ink-3);font-weight:600;text-align:left;padding:9px 12px;border-bottom:1px solid var(--line)}}
.scoretable thead th.num{{text-align:right}}
.scoretable td{{padding:10px 12px;border-bottom:1px solid var(--line-2);vertical-align:middle}}
.kpi:hover{{background:var(--surface-2)}}
.kpi.nodata{{opacity:.62}}
.c-dot{{width:26px}}
.dot{{width:11px;height:11px;border-radius:50%;display:inline-block}}
.dot.g{{background:var(--green);box-shadow:0 0 0 3px var(--green-bg)}}
.dot.a{{background:var(--amber);box-shadow:0 0 0 3px var(--amber-bg)}}
.dot.r{{background:var(--red);box-shadow:0 0 0 3px var(--red-bg)}}
.dot.n,.dot.x{{background:var(--grey);box-shadow:0 0 0 3px var(--grey-bg)}}
.c-code{{font-weight:650;color:var(--ink-2);width:44px;font-size:13px}}
.c-meas .meas{{display:block;font-weight:550;color:var(--ink);line-height:1.3}}
.c-meas .obj{{display:block;font-size:11px;color:var(--ink-3);margin-top:1px}}
.chip{{font-size:10.5px;font-weight:650;padding:2.5px 8px;border-radius:6px;
  background:var(--grey-bg);color:var(--ink-2);white-space:nowrap}}
.chip.p-ap{{background:#E7EFFA;color:#2E5F9A}}
.chip.p-ar{{background:#EDE9FA;color:#6146C6}}
.chip.p-r2r{{background:#E7F2E8;color:#2E7D32}}
.c-val{{text-align:right;font-weight:680;font-size:15px;font-variant-numeric:tabular-nums;white-space:nowrap}}
.c-tgt{{text-align:right;color:var(--ink-2);font-variant-numeric:tabular-nums}}
.pend{{font-size:11px;font-weight:500;color:var(--ink-3);font-style:italic}}
.c-trend{{text-align:center;font-size:16px;font-weight:700}}
.t-up{{color:var(--green)}} .t-down{{color:var(--red)}} .t-flat{{color:var(--ink-3)}}
.c-spark{{width:112px}}
.spark{{width:104px;height:30px;display:block}}
.spark-empty{{color:var(--ink-3)}}

.legend{{display:flex;gap:18px;flex-wrap:wrap;margin:16px 2px 0;font-size:12px;color:var(--ink-2)}}
.legend .li{{display:flex;align-items:center;gap:7px}}
.footer{{margin-top:26px;padding:16px 18px;border:1px dashed var(--line);border-radius:var(--radius);
  font-size:12px;color:var(--ink-2);background:var(--surface-2)}}
.footer b{{color:var(--ink)}}
.note{{margin:6px 2px 0;font-size:11.5px;color:var(--ink-3)}}
</style>

<div class="wrap">
  <div class="topbar">
    <div class="mark">DS</div>
    <div>
      <h1>Shared Service Centre · Balanced Scorecard</h1>
      <p class="sub">DE Pack · Maqueta del informe Power BI — datos reales del fichero de grupo</p>
    </div>
    <div class="spacer"></div>
    <div class="monthchip"><svg class="cal" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="4" width="18" height="17" rx="2"/><path d="M3 9h18M8 2v4M16 2v4"/></svg>{month_label}</div>
  </div>

  <div class="tiles">
    <div class="tile on"><div class="stripe"></div><div class="k">En objetivo</div><div class="v tabular">{on_target}</div></div>
    <div class="tile g"><div class="stripe"></div><div class="k">Verde</div><div class="v tabular">{green}</div></div>
    <div class="tile a"><div class="stripe"></div><div class="k">Ámbar</div><div class="v tabular">{amber}</div></div>
    <div class="tile r"><div class="stripe"></div><div class="k">Rojo</div><div class="v tabular">{red}</div></div>
    <div class="tile m"><div class="stripe"></div><div class="k">KPIs medidos</div><div class="v tabular">{measured}</div></div>
  </div>
  <div class="legend">
    <span class="li"><span class="dot g"></span> En objetivo</span>
    <span class="li"><span class="dot a"></span> En riesgo (±5%)</span>
    <span class="li"><span class="dot r"></span> Fuera de objetivo</span>
    <span class="li"><span class="dot n"></span> Sin objetivo / memo</span>
    <span class="li">↗ ↘ tendencia favorable/desfavorable vs mes anterior</span>
  </div>

  {"".join(sections)}

  <div class="footer">
    <b>Fuente:</b> 2026_AP07_DE_DSS_Balanced_Scorecard_SSC (modelo de grupo, hoja Data_DE_Pack) · histórico may-2019 → dic-2026.<br>
    <b>Reconciliación:</b> los 11 KPIs de porcentaje verificables coinciden al 100% con el valor calculado del Excel original.<br>
    Esta página es una <b>maqueta de diseño</b> del informe que se construye en Power BI Desktop con el modelo de esta carpeta (Dim_KPI · Dim_Date · Fact_Scorecard) y las medidas DAX. El estado RAG y las tendencias son dinámicos en Power BI.
  </div>
  <p class="note">Valores mostrados a fecha de {month_label}. Los KPIs marcados como “pendiente” están en el catálogo del modelo, listos para rellenar cuando lleguen sus datos.</p>
</div>'''

out="/home/user/angela/powerbi-scorecard/preview/scorecard_preview.html"
os.makedirs(os.path.dirname(out),exist_ok=True)
open(out,"w",encoding="utf-8").write(HTML)
print("Escrito",out,len(HTML),"bytes")
