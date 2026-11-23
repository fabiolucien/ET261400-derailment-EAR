import warnings; warnings.filterwarnings("ignore")
from scipy import sparse
from scipy.stats import rankdata
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import matplotlib; matplotlib.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})
import matplotlib.pyplot as plt
SEED = 42
C0 = pd.read_csv(f"{PROC}/11_celulas_1km.csv", low_memory=False)
C = C0[~C0["sentido"].astype(str).str.contains("Interromp")].sort_values(["ferrovia", "linha", "km_a"]).reset_index(drop=True); gate("células em operação", len(C), 20936, source="notebook 11")
E = pd.read_csv(f"{PROC}/11_eventos_celulas.csv"); E = E[E["cel_id"].isin(C["cel_id"])].copy(); E["ano"] = E["ano"].astype(int); EV = E[E["via"]]; gate("descarrilamentos por via", len(EV), 2681, source="notebook 11")
N = len(C); idx = pd.Series(np.arange(N), index=C["cel_id"].values); ANOS = np.arange(2011, 2026)
def matriz(ev):
    M_ = np.zeros((15, N))
    for k in range(15):
        s = ev[ev["ano"] == 2011 + k].groupby("cel_id").size(); M_[k, idx[s.index].values] = s.values
    return M_
CV_, CA_ = matriz(EV), matriz(E)
def conta(M_, a0, a1): return M_[(ANOS >= a0) & (ANOS <= a1)].sum(0)
EARN = ["dmin_patio", "dmin_amv", "frac_zona_patio"] + [f"f16p{j}" for j in range(5)] + [f"f16a{j}" for j in range(5)] + ["rmin_geo"] + [f"fr_lt{l}" for l in (300, 400, 500, 600, 800)]
NUM = EARN + ["rampa_max_pct", "carga_eixo_t", "taxa_dorm", "gab_vert_m", "gab_horiz_m", "cap_vinc", "dias_op", "raio_min_m", "vma_carregado"]
CAT = ["dormente", "perfil_trilho", "fixacao", "sinalizacao", "controle_circ", "bitola", "sentido", "n_linhas"]
for c in NUM: C[c] = pd.to_numeric(C[c], errors="coerce")
for c in CAT: C[c] = C[c].astype(str).str.strip().replace({"nan": "NA", "": "NA"})
def design(num, cat):
    X = C[num].copy(); med = X.median().fillna(0.0)
    for c in num: X[c + "_na"] = X[c].isna().astype(float); X[c] = X[c].fillna(med[c])
    X = pd.concat([X, pd.get_dummies(C[cat], dtype=float)], axis=1) if cat else X; return StandardScaler().fit_transform(X.values.astype(float))
X0, XE = design(NUM, CAT), design(EARN, [])
FERC = pd.factorize(C["ferrovia"])[0]; LINC = pd.factorize(C["ferrovia"].astype(str) + "|" + C["linha"].astype(str))[0]; SEGC = pd.factorize(C["seg_id"].astype(str))[0]; KM = ((C["km_a"] + C["km_b"]) / 2).values; LN = C["len_km"].values
ri, ci = [], []
for l in range(LINC.max() + 1):
    i = np.where(LINC == l)[0]; k = KM[i]; M_ = (np.abs(k[:, None] - k[None, :]) <= 20) & ~np.eye(len(i), dtype=bool); a, b = np.where(M_); ri.append(i[a]); ci.append(i[b])
W = sparse.csr_matrix((np.ones(sum(len(a) for a in ri)), (np.concatenate(ri), np.concatenate(ci))), shape=(N, N)); nviz = np.asarray(W.sum(1)).ravel()
def historico(a0, a1):
    n = a1 - a0 + 1; hv = conta(CV_, a0, a1); ha = conta(CA_, a0, a1); b = (hv > 0).astype(float); d = pd.DataFrame({"b": b, "hv": hv})
    return np.column_stack([hv / n, ha / n, b, (W @ b) / np.maximum(nviz, 1), (W @ hv) / np.maximum(nviz, 1) / n, d.groupby(SEGC)["b"].transform("mean").values, d.groupby(LINC)["b"].transform("mean").values, d.groupby(FERC)["b"].transform("mean").values, d.groupby(FERC)["hv"].transform("mean").values / n])
dp = C["dmin_patio"].fillna(1e9).values; rg = C["rmin_geo"].fillna(1e6).values
B2 = 0.5 * np.select([dp <= 300, dp <= 600, dp <= 1200, dp <= 1800], [4, 3, 2, 1], 0) / 4 + 0.5 * np.select([rg < 500, rg < 1200, rg < 2300], [3, 2, 1], 0) / 3
def auc(y, s):
    n1 = y.sum(); n0 = len(y) - n1; return float((rankdata(s)[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))
def auc_dentro(s, y):
    a, w = [], []
    for f in range(FERC.max() + 1):
        i = FERC == f
        if 5 <= y[i].sum() < i.sum(): a.append(auc(y[i], s[i])); w.append(y[i].sum())
    return float(np.average(a, weights=w))
def lr(Xtr, ytr, Xte): return LogisticRegression(C=0.5, max_iter=3000).fit(Xtr, ytr).predict_proba(Xte)[:, 1]
DES = np.random.default_rng(SEED).random(N)
DES = np.random.default_rng(SEED).random(N)
log_ia("23.1 dados e funções", "Claude", "FOCUS: mesmas funções do notebook 18", "design, auc, lr", "2 gates de contagem")

# 1. Teste geral: todos os descarrilamentos por via de 2011 a 2025, sem recorte de tempo
n15 = conta(CV_, 2011, 2025); y = (n15 > 0).astype(int); gate("quilômetros com descarrilamento por via em 2011 a 2025", int(y.sum()), 2123, source="notebook 11")
gate("regra do EAR no período inteiro (não depende de sorteio)", round(auc(y, B2), 3), 0.588, tol=0.002, source="notebook 11")
KF = 5
def folds_por(grupo, seed, k=KF):
    u = np.unique(grupo); f = dict(zip(u, np.random.default_rng(seed).permutation(len(u)) % k)); return np.array([f[g] for g in grupo])
def fora_do_ajuste(fo, yy):
    """Nota de cada célula dada por um modelo que não a viu: uma linha por método."""
    S = {m: np.zeros(N) for m in ("Dummy: taxa da malha", "Critérios do EAR em medida contínua", "EAR calibrado (atributos da via)")}
    for k in range(KF):
        te = fo == k; tr = ~te
        t = pd.Series(yy[tr]).groupby(FERC[tr]).mean(); S["Dummy: taxa da malha"][te] = pd.Series(FERC[te]).map(t).fillna(yy[tr].mean()).values
        S["Critérios do EAR em medida contínua"][te] = lr(XE[tr], yy[tr], XE[te]); S["EAR calibrado (atributos da via)"][te] = lr(X0[tr], yy[tr], X0[te])
    S["Regra do EAR por faixas"] = B2; return S
def topo(s, yy):
    o = np.lexsort((DES, -s)); top = np.zeros(N, bool); top[o[(np.cumsum(LN[o]) / LN.sum()) <= 0.20]] = True; return float(yy[top].sum() / yy.sum())
DESENHOS = [("G1 trechos entre pátios inteiros fora do ajuste", SEGC, 30), ("G2 linhas inteiras fora do ajuste", LINC, 10), ("G0 células sorteadas ao acaso (referência otimista)", np.arange(N), 10)]
L, GUARDA = [], {}
for nome, grupo, R in DESENHOS:
    for r in range(R):
        fo = folds_por(grupo, SEED + r)
        if not nome.startswith("G0"): assert all(len(set(fo[grupo == g])) == 1 for g in np.unique(grupo)[:50]), "grupo dividido entre ajuste e conferência"
        S = fora_do_ajuste(fo, y); GUARDA[(nome, r)] = S
        for m, s in S.items(): L.append(dict(desenho=nome, sorteio=r, metodo=m, auc=auc(y, s), auc_dentro=0.5 if m.startswith("Dummy") else auc_dentro(s, y), classe_muito_alta=topo(s, y)))
    print(nome, "concluído:", R, "sorteios", flush=True)
RES = pd.DataFrame(L); RES.to_csv(f"{TAB}/23_teste_geral_por_sorteio.csv", index=False)
T = RES.groupby(["desenho", "metodo"])[["auc", "auc_dentro", "classe_muito_alta"]].agg(["mean", "std"]).round(3); display(T); T.to_csv(f"{TAB}/23_teste_geral_resumo.csv")
m1 = RES[RES.desenho.str.startswith("G1")].groupby("metodo")["auc"].mean()
gate("G1, EAR calibrado: AUC (notebook 11, 30 sorteios)", round(float(m1["EAR calibrado (atributos da via)"]), 3), 0.761, tol=0.005, source="notebook 11")
gate("G1, critérios contínuos: AUC", round(float(m1["Critérios do EAR em medida contínua"]), 3), 0.634, tol=0.005, source="notebook 11")
gate("G1, Dummy da malha: AUC", round(float(m1["Dummy: taxa da malha"]), 3), 0.693, tol=0.005, source="notebook 11")
log_ia("23.2 teste geral", "Claude", "FOCUS: período inteiro; validação cruzada em blocos espaciais (trecho e linha); células ao acaso só como referência otimista", "23_teste_geral_resumo.csv", "5 gates contra o notebook 11")

# 2. Intervalo de 95% por reamostragem de linhas inteiras (G1, 10 primeiros sorteios, 300 reamostragens) e teste de vazamento
rng = np.random.default_rng(SEED); Lu = np.unique(LINC); ix = {l: np.where(LINC == l)[0] for l in Lu}; B = 300; nome1 = DESENHOS[0][0]
BOOT = {m: np.zeros(B) for m in ("Regra do EAR por faixas", "Dummy: taxa da malha", "Critérios do EAR em medida contínua", "EAR calibrado (atributos da via)")}; DIF = np.zeros(B)
for b in range(B):
    i = np.concatenate([ix[l] for l in rng.choice(Lu, len(Lu))])
    if y[i].sum() < 50: continue
    for m in BOOT: BOOT[m][b] = np.mean([auc(y[i], GUARDA[(nome1, r)][m][i]) for r in range(10)])
    DIF[b] = BOOT["EAR calibrado (atributos da via)"][b] - BOOT["Regra do EAR por faixas"][b]
IC = pd.DataFrame({m: dict(media=float(m1[m]), ic95_inf=float(np.percentile(v[v > 0], 2.5)), ic95_sup=float(np.percentile(v[v > 0], 97.5))) for m, v in BOOT.items()}).T.round(3); display(IC); IC.to_csv(f"{TAB}/23_teste_geral_ic95.csv")
print("EAR calibrado menos regra, IC 95%:", round(float(np.percentile(DIF[DIF != 0], 2.5)), 3), "a", round(float(np.percentile(DIF[DIF != 0], 97.5)), 3))
emb = []
for r in range(20):
    ye = np.random.default_rng(1000 + r).permutation(y); emb.append(auc(ye, fora_do_ajuste(folds_por(SEGC, SEED + r), ye)["EAR calibrado (atributos da via)"]))
gate_between("teste de vazamento (média de 20 embaralhamentos dos rótulos)", round(float(np.mean(emb)), 3), 0.45, 0.55, source="acaso")
log_ia("23.3 intervalo e vazamento", "Claude", "FOCUS: reamostragem de linhas inteiras; rótulos embaralhados devem dar 0,5", "23_teste_geral_ic95.csv", "gate de vazamento")

# 3. Os três modos de conferir, lado a lado: geral, ano a ano e três anos à frente
import os
linhas = [dict(conferencia="Geral: 2011 a 2025, trechos inteiros fora do ajuste (30 sorteios)", **{m: round(float(m1[m]), 3) for m in m1.index})]
if os.path.exists(f"{TAB}/21_validacao_temporal_por_avaliacao.csv"):
    V = pd.read_csv(f"{TAB}/21_validacao_temporal_por_avaliacao.csv"); V = V[V.desenho.str.startswith("D1")]
    for rot, nome in (("H=1", "No tempo: ano a ano (11 anos conferidos, 2015 a 2025)"), ("H=3", "No tempo: três anos à frente"), ("H=5", "No tempo: cinco anos à frente")):
        g = V[V.rotulo == rot].groupby("metodo")["auc"].mean(); linhas.append(dict(conferencia=nome, **{m: round(float(g[m]), 3) for m in m1.index if m in g.index}))
LADO = pd.DataFrame(linhas).set_index("conferencia"); display(LADO); LADO.to_csv(f"{TAB}/23_geral_e_no_tempo_lado_a_lado.csv")
exportar_registros("23")
