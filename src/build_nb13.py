# -*- coding: utf-8 -*-
"""Gera notebooks/13_mvp_mapa_nacional.ipynb: posiciona as células das 13 malhas no eixo da ANTT e gera o mapa nacional do MVP."""
import nbformat as nbf
from nb_common import HEADER_RULE, SETUP_CODE, DECLARACAO_IA
cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s))
code = lambda s: cells.append(nbf.v4.new_code_cell(s))
md(f"""# 13 · MVP nacional: mapa das 13 malhas e resultado por malha

{HEADER_RULE}

**O que este notebook acrescenta.** A análise do notebook 11 já é nacional (20.936 células, 13 malhas); só o mapa era da FCA. Aqui as células de todas as malhas são posicionadas no eixo público da ANTT (camada Linha-Estação, mar/2026) e o mapa passa a mostrar o país. A tabela por malha mostra em quantas malhas a medida contínua dos critérios do EAR supera a regra por faixas.

**Regra de posicionamento (declarada antes do código).** (1) Para cada segmento da Declaração de Rede, procurar no eixo o trecho cuja estação final tem o mesmo nome do pátio final (ou inicial) e o mesmo km, com tolerância de 1 km; (2) o código de ferrovia de cada malha é o mais votado entre os seus segmentos pareados; (3) cada linha da Declaração de Rede fica com os códigos de linha do eixo que os seus segmentos pareados indicaram; (4) a célula é posicionada pelo km do seu ponto médio dentro do trecho do eixo que contém esse km. Células de linhas sem pareamento ficam fora do mapa e são contadas; nenhuma métrica depende do mapa.

**Gates.** As 13 malhas recebem 13 códigos de ferrovia distintos; a FCA recebe o código 8 (notebook 03); as posições das células da FCA coincidem com as do notebook 11 (mediana da diferença de até 1 km); todas as posições caem dentro do território brasileiro; o escore do sorteio 0 reproduz a captura de 20% do notebook 11 para o mesmo sorteio.""")
code(SETUP_CODE)
code(r'''import warnings; warnings.filterwarnings("ignore")
import geopandas as gpd
from shapely.ops import linemerge
from shapely.geometry import Point
from scipy.stats import rankdata
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
SHP = f"{RAW}/antt_shp/ShapeFile mar-2026"
def norm(s): return re.sub(r"\s+", " ", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper().strip())
lin = gpd.read_file(f"{SHP}/LinhaEsta#U00e7#U00e3o2026.shp"); est = gpd.read_file(f"{SHP}/Esta#U00e7#U00e3o2026.shp")
n0 = len(lin); lin = lin[lin.geometry.notna() & (lin["NumeroExte"] > 0) & lin["CodigoFerr"].notna() & lin["CodigoLi_1"].notna()].reset_index(drop=True); print("trechos do eixo:", n0, "| com geometria e extensão:", len(lin))
est["nome"] = est["NomeEstaca"].map(norm); EP = dict(zip(est["CodigoEsta"], est.geometry))
lin = lin.merge(est[["CodigoEsta", "nome"]].drop_duplicates("CodigoEsta"), on="CodigoEsta", how="left"); lin["ki"] = lin["NumeroQuil"] - lin["NumeroExte"]
C0 = pd.read_csv(f"{PROC}/11_celulas_1km.csv")
C = C0[~C0["sentido"].astype(str).str.contains("Interromp")].sort_values(["ferrovia", "linha", "km_a"]).reset_index(drop=True)
gate("células em operação", len(C), 20936, source="notebook 11")
S = pd.read_csv(f"{RAW}/matriz_segmentos.csv", usecols=["seg_id", "ferrovia", "linha", "patio_a", "patio_b", "km_ini", "km_fim"]); S = S[S["seg_id"].isin(C["seg_id"])]
V = []
for _, s in S.iterrows():
    for nome, km in ((norm(s["patio_b"]), s["km_fim"]), (norm(s["patio_a"]), s["km_ini"])):
        c = lin[(lin["nome"] == nome) & ((lin["NumeroQuil"] - km).abs() <= 1.0)]
        for _, t in c.iterrows(): V.append((s["ferrovia"], s["linha"], int(t["CodigoFerr"]), int(t["CodigoLi_1"])))
V = pd.DataFrame(V, columns=["ferrovia", "linha", "cf", "cl"]); print("votos de pareamento:", len(V), "| segmentos:", len(S))
FER = V.groupby("ferrovia")["cf"].agg(lambda x: x.value_counts().idxmax()); display(FER.to_frame("CodigoFerr").T)
gate("malhas com código de ferrovia", len(FER), 13, source="13 malhas do notebook 11"); gate("códigos de ferrovia distintos", int(FER.nunique()), 13, source="cada malha é uma concessão"); gate("código da FCA", int(FER["FCA"]), 8, source="notebook 03")
V = V[V["cf"] == V["ferrovia"].map(FER)]; LC = V.groupby(["ferrovia", "linha"])["cl"].agg(lambda x: list(x.value_counts().index)).to_dict()
def linha_geom(g):
    g = linemerge(g) if g.geom_type == "MultiLineString" else g
    return g if g.geom_type == "LineString" else max(g.geoms, key=lambda q: q.length)
lin["g"] = lin.geometry.map(linha_geom); TR = {k: d for k, d in lin.groupby(["CodigoFerr", "CodigoLi_1"])}
def ponto(fer, linha, km):
    for cl in LC.get((fer, linha), []):
        d = TR.get((float(FER[fer]), cl)) if (float(FER[fer]), cl) in TR else TR.get((FER[fer], cl))
        if d is None: continue
        t = d[(d["ki"] <= km) & (d["NumeroQuil"] >= km)]
        if not len(t): continue
        t = t.iloc[0]; g = t["g"]; fr = float(np.clip((km - t["ki"]) / (t["NumeroQuil"] - t["ki"]), 0, 1)); pe = EP.get(t["CodigoEsta"])
        if pe is not None and Point(g.coords[0]).distance(pe) < Point(g.coords[-1]).distance(pe): fr = 1 - fr
        p = g.interpolate(fr, normalized=True); return (p.x, p.y)
    return (np.nan, np.nan)
xy = np.array([ponto(f, l, (a + b) / 2) for f, l, a, b in zip(C["ferrovia"], C["linha"], C["km_a"], C["km_b"])]); C["lon"], C["lat"] = xy[:, 0], xy[:, 1]; C["pos"] = C["lon"].notna()
cob = C.groupby("ferrovia").agg(celulas=("pos", "size"), posicionadas=("pos", "sum"), atingidas=("nv_1125", lambda x: int((x > 0).sum()))); cob["pct_posicionadas"] = (100 * cob["posicionadas"] / cob["celulas"]).round(1); display(cob)
print(f"células posicionadas no eixo: {int(C['pos'].sum())} de {len(C)} ({100 * C['pos'].mean():.1f}%); eventos nas células posicionadas: {int(C.loc[C['pos'], 'nv_1125'].sum())} de {int(C['nv_1125'].sum())}")
gate_between("posições dentro do território brasileiro (fração)", float((C.loc[C["pos"], "lon"].between(-74.1, -34.7) & C.loc[C["pos"], "lat"].between(-33.8, 5.3)).mean()), 1.0, 1.0, source="extremos do território brasileiro (IBGE)")
ref = pd.read_csv(f"{TAB}/11_mvp_fca_celulas_escore.csv", usecols=["cel_id", "x", "y"]).merge(C.loc[C["pos"], ["cel_id", "lon", "lat"]], on="cel_id")
PROJ = "+proj=poly +lat_0=0 +lon_0=-54 +ellps=GRS80 +units=m +no_defs"
pp = gpd.GeoSeries(gpd.points_from_xy(ref["lon"], ref["lat"]), crs=4674).to_crs(PROJ); dkm = np.hypot(pp.x.values - ref["x"].values, pp.y.values - ref["y"].values) / 1000
print("FCA: células em comum com o notebook 11:", len(ref), "| diferença de posição, mediana e percentil 95 (km):", round(float(np.median(dkm)), 3), round(float(np.percentile(dkm, 95)), 3))
gate_between("FCA: mediana da diferença de posição contra o notebook 11 (km)", float(np.median(dkm)), 0.0, 1.0, source="notebook 11, mesma regra de interpolação")
C[["cel_id", "ferrovia", "linha", "km_a", "km_b", "lon", "lat", "pos"]].to_csv(f"{PROC}/13_celulas_posicao.csv", index=False)
log_ia("13.1 posicionamento nacional", "Claude", "FOCUS: parear segmentos da DR ao eixo por nome de pátio e km; posicionar células pelo km; contar o que fica de fora", "13_celulas_posicao.csv", "gates de código de ferrovia, território e coincidência com a FCA do notebook 11")''')
md("""---
## Escore do MVP (sorteio 0), mapa nacional e resultado por malha

O escore é o do modelo M2 do notebook 11 (logística com critérios do EAR contínuos e atributos declarados), sempre com o segmento da célula fora do ajuste. A tabela por malha usa 10 sorteios (sementes 42 a 51).""")
code(r'''SEED, KF = 42, 5
DIST = ["dmin_patio", "dmin_amv", "frac_zona_patio"] + [f"f16p{j}" for j in range(5)] + [f"f16a{j}" for j in range(5)]
CURV = ["rmin_geo"] + [f"fr_lt{l}" for l in (300, 400, 500, 600, 800)]
NUM = ["rampa_max_pct", "carga_eixo_t", "taxa_dorm", "gab_vert_m", "gab_horiz_m", "cap_vinc", "dias_op", "raio_min_m", "vma_carregado"]
CAT = ["dormente", "perfil_trilho", "fixacao", "sinalizacao", "controle_circ", "bitola", "sentido", "n_linhas"]
for c in NUM + DIST + CURV: C[c] = pd.to_numeric(C[c], errors="coerce")
for c in CAT: C[c] = C[c].astype(str).str.strip().replace({"nan": "NA", "": "NA"})
def design(df, num, cat):
    X = df[num].copy(); med = X.median().fillna(0.0)
    for c in num: X[c + "_na"] = X[c].isna().astype(float); X[c] = X[c].fillna(med[c])
    D = pd.get_dummies(df[cat], dtype=float) if cat else pd.DataFrame(index=df.index)
    return pd.concat([X, D], axis=1).values
y = (C["nv_1125"] > 0).astype(int).values; ev = C["nv_1125"].values.astype(float); LN = C["len_km"].values; fer = C["ferrovia"].values; SEG = C["seg_id"].astype(str).values
def cls16(d): return np.select([d <= 300, d <= 600, d <= 1200, d <= 1800], [4, 3, 2, 1], 0)
def rcls16(r): return np.select([r < 500, r < 1200, r < 2300], [3, 2, 1], 0)
B2 = (0.5 * cls16(C["dmin_patio"].fillna(1e9)) / 4 + 0.5 * rcls16(C["rmin_geo"].fillna(1e6)) / 3).astype(float)
X1, X2 = design(C, DIST + CURV, []), design(C, DIST + CURV + NUM, CAT)
def auc(yy, s):
    n1 = yy.sum(); n0 = len(yy) - n1; return float((rankdata(s)[yy == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))
def captura(s, p):
    o = np.lexsort((np.random.default_rng(SEED).random(len(s)), -s)); cum = np.cumsum(LN[o]) / LN.sum(); return float(ev[o][cum <= p].sum() / ev.sum())
def folds_por(grupo, seed, k=KF):
    u = np.unique(grupo); f = dict(zip(u, np.random.default_rng(seed).permutation(len(u)) % k)); return np.array([f[g] for g in grupo])
def oof(X, fo):
    s = np.zeros(len(C))
    for k in np.unique(fo):
        te = fo == k; tr = ~te; st = StandardScaler().fit(X[tr]); s[te] = LogisticRegression(C=0.5, max_iter=3000).fit(st.transform(X[tr]), y[tr]).predict_proba(st.transform(X[te]))[:, 1]
    return s
S1, S2 = [], []
for r in range(10):
    fo = folds_por(SEG, SEED + r); S1.append(oof(X1, fo)); S2.append(oof(X2, fo))
ref11 = pd.read_csv(f"{TAB}/11_metricas_por_sorteio.csv"); r0 = ref11[(ref11["sorteio"] == 0) & ref11["metodo"].str.startswith("M2")]["captura20"].iloc[0]
cap_m2, cap_b2 = captura(S2[0], 0.20), captura(B2, 0.20)
gate("captura em 20% do M2 no sorteio 0 reproduz o notebook 11", round(cap_m2, 4), round(float(r0), 4), tol=0.005, source="11_metricas_por_sorteio.csv")
print(f"País, sorteio 0: 20% da extensão de maior escore concentram {cap_m2:.1%} dos descarrilamentos por via (regra do EAR: {cap_b2:.1%})")
L = []
for f in np.unique(fer):
    i = fer == f; h = int(y[i].sum())
    if h < 5: L.append(dict(malha=f, celulas=int(i.sum()), atingidas=h, auc_regra_ear=np.nan, auc_criterios_continuos=np.nan, auc_com_atributos=np.nan)); continue
    L.append(dict(malha=f, celulas=int(i.sum()), atingidas=h, auc_regra_ear=auc(y[i], B2[i]), auc_criterios_continuos=float(np.mean([auc(y[i], s[i]) for s in S1])), auc_com_atributos=float(np.mean([auc(y[i], s[i]) for s in S2]))))
PM = pd.DataFrame(L); PM["ganho_continuo_menos_regra"] = PM["auc_criterios_continuos"] - PM["auc_regra_ear"]; PM = PM.sort_values("atingidas", ascending=False).round(3); display(PM); PM.to_csv(f"{TAB}/13_resultado_por_malha.csv", index=False)
v = PM.dropna(subset=["auc_regra_ear"]); print(f"malhas com pelo menos 5 células atingidas: {len(v)}; a medida contínua supera a regra em {int((v['ganho_continuo_menos_regra'] > 0).sum())} delas; essas malhas somam {int(v.loc[v['ganho_continuo_menos_regra'] > 0, 'atingidas'].sum())} das {int(v['atingidas'].sum())} células atingidas")
log_ia("13.2 escore e resultado por malha", "Claude", "FOCUS: mesmo modelo e split do notebook 11; AUC por malha para a regra e para os critérios contínuos", "13_resultado_por_malha.csv", "gate de reprodução da captura do sorteio 0")''')
code(r'''import matplotlib; matplotlib.use("Agg") if not IN_COLAB else None
import matplotlib.pyplot as plt
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
INK, ACC, BLU, CIN, BG = "#16191C", "#BD4B2C", "#1F4E79", "#C9CCD1", "#FBFAF7"
uf = gpd.read_file(f"{SHP}/UF2026.shp")
o = np.argsort(-S2[0]); cum = np.cumsum(LN[o]) / LN.sum(); top = np.zeros(len(C), bool); top[o[cum <= 0.20]] = True; hit = y == 1; P = C["pos"].values
fig = plt.figure(figsize=(9.6, 5.0), facecolor=BG); ax = fig.add_axes([0.0, 0.03, 0.60, 0.86]); ax2 = fig.add_axes([0.70, 0.15, 0.285, 0.65], facecolor=BG)
uf.boundary.plot(ax=ax, color="#DDD9CF", linewidth=0.5, zorder=0); gpd.GeoSeries(lin["g"]).plot(ax=ax, color="#9AA0A8", linewidth=0.7, zorder=1)
m = P & top & ~hit; ax.scatter(C.loc[m, "lon"], C.loc[m, "lat"], s=1.8, color="#E9B3A3", zorder=3, label="classe muito alta, sem descarrilamento")
m = P & ~top & hit; ax.scatter(C.loc[m, "lon"], C.loc[m, "lat"], s=5, facecolors="none", edgecolors=INK, linewidths=0.4, zorder=4, label="descarrilamento fora da classe muito alta")
m = P & top & hit; ax.scatter(C.loc[m, "lon"], C.loc[m, "lat"], s=5, color=ACC, zorder=5, label="descarrilamento na classe muito alta")
import matplotlib.patheffects as pe
ROT = {"EFC": (-46.9, -1.0), "FNSTN": (-46.9, -8.6), "FTL": (-42.6, -1.2), "FCA": (-42.3, -15.4), "EFVM": (-39.9, -19.2), "MRS": (-43.6, -24.3), "RMP": (-50.3, -19.7), "RMS": (-55.2, -27.6),
       "RMO": (-56.6, -21.9), "RMN": (-56.4, -16.4), "RMC": (-52.3, -13.6), "EFPO": (-55.6, -24.4), "FTC": (-48.3, -29.6)}   # posição dos rótulos, fora dos traçados
for f, (lo, la) in ROT.items(): ax.text(lo, la, f, fontsize=9, color="#22272E", fontweight="bold", zorder=6, path_effects=[pe.withStroke(linewidth=2.2, foreground=BG)])
ax.set_xlim(-68.5, -34.2); ax.set_ylim(-33.5, 0.5); ax.set_aspect(1 / np.cos(np.deg2rad(16))); ax.axis("off")
h_, l_ = ax.get_legend_handles_labels(); fig.legend(h_, l_, loc="upper left", bbox_to_anchor=(0.004, 0.875), fontsize=9.5, frameon=False, markerscale=2.2, handletextpad=0.3)
fig.text(0.012, 0.955, "(a) 13 malhas: classe muito alta e descarrilamentos por via", fontsize=11.5, color=INK)
cap_m2_30 = float(ref11[ref11["metodo"].str.startswith("M2")]["captura20"].mean())
fig.text(0.012, 0.915, f"Classe muito alta: {cap_m2_30:.0%} dos descarrilamentos (regra: {cap_b2:.0%})", fontsize=11.5, color=ACC, fontweight="bold")
gr = np.linspace(0, 1, 101)
def curva(s): return [100 * np.mean([captura(q, p) for q in s]) for p in gr]
ax2.plot(100 * gr, curva([B2]), color=INK, ls="--", lw=1.4, label="Regra do EAR (sem IA)")
B1 = []
for r in range(3):
    fo = folds_por(SEG, SEED + r); b = np.zeros(len(C))
    for k in np.unique(fo):
        te = fo == k; tx = pd.Series(y[~te]).groupby(fer[~te]).mean(); b[te] = pd.Series(fer[te]).map(tx).fillna(y[~te].mean()).values
    B1.append(b)
ax2.plot(100 * gr, curva(B1), color="#8A929C", ls="-.", lw=1.4, label="Dummy: taxa média da malha")
ax2.plot(100 * gr, curva(S1[:3]), color=BLU, lw=1.5, label="Critérios do EAR contínuos"); ax2.plot(100 * gr, curva(S2[:3]), color=ACC, lw=1.6, label="EAR calibrado (+ atributos da via)")
ax2.plot([0, 100], [0, 100], color=CIN, lw=0.8, label="ao acaso"); ax2.axvline(20, color=CIN, lw=0.7)
ax2.set_xlabel("extensão acumulada (%)".replace(",", "."), fontsize=10.5); ax2.set_ylabel("descarrilamentos por via acumulados (%)", fontsize=10.5); ax2.set_xlim(0, 100); ax2.set_ylim(0, 100)
ax2.legend(fontsize=8.2, frameon=False, loc="lower right", borderaxespad=0.1); ax2.spines[["top", "right"]].set_visible(False); ax2.tick_params(labelsize=10)
fig.text(0.69, 0.955, "(b) Curva de taxa de predição", fontsize=11.5, color=INK); fig.text(0.69, 0.915, "Chung e Fabbri (2003); 3 sorteios", fontsize=9.5, color="#4A4F57")
fig.text(0.012, 0.008, f"Fontes: ANTT (RAAF 2011 a 2025, Declarações de Rede 2025, eixo de mar/2026). Mapa: escore de um sorteio; {100 * C['pos'].mean():.0f}% das células posicionadas no eixo.", fontsize=8.5, color="#4A4F57")
plt.savefig(f"{FIG}/13_mvp_mapa_nacional.png", dpi=260, facecolor=BG); plt.show()
log_ia("13.3 mapa nacional", "Claude", "FOCUS: mapa das 13 malhas com os 20% priorizados e os descarrilamentos; curva de captura nacional", "13_mvp_mapa_nacional.png", "valores do título lidos do escore com gate")
exportar_registros("13")''')
md(f"""---
## Limites

O mapa depende do pareamento por nome de pátio e km entre a Declaração de Rede e o eixo; as células de linhas não pareadas ficam fora do mapa e estão contadas na tabela de cobertura. As métricas não dependem do mapa. A posição do evento tem a precisão do quilômetro do RAAF (notebook 12).

{DECLARACAO_IA}""")
nb = nbf.v4.new_notebook(); nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"}, "colab": {"name": "13_mvp_mapa_nacional.ipynb"}}
nbf.write(nb, "13_mvp_mapa_nacional.ipynb"); print("ok 13")
