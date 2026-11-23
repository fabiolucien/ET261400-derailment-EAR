import warnings; warnings.filterwarnings("ignore")
from scipy import sparse
from scipy.stats import rankdata
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from joblib import Parallel, delayed
SEED = 42
C0 = pd.read_csv(f"{PROC}/11_celulas_1km.csv", low_memory=False)
C = C0[~C0["sentido"].astype(str).str.contains("Interromp")].sort_values(["ferrovia", "linha", "km_a"]).reset_index(drop=True); gate("células em operação", len(C), 20936, source="notebook 11")
E = pd.read_csv(f"{PROC}/11_eventos_celulas.csv"); E = E[E["cel_id"].isin(C["cel_id"])].copy(); E["ano"] = E["ano"].astype(int); EV = E[E["via"]]; gate("descarrilamentos por via", len(EV), 2681, source="notebook 11")
N = len(C); idx = pd.Series(np.arange(N), index=C["cel_id"].values)
def matriz(ev):
    M_ = np.zeros((15, N))
    for k in range(15):
        s = ev[ev["ano"] == 2011 + k].groupby("cel_id").size(); M_[k, idx[s.index].values] = s.values
    return M_
CV_, CA_ = matriz(EV), matriz(E); gate("soma da matriz ano x célula", int(CV_.sum()), 2681, source="partição por ano")
ANOS = np.arange(2011, 2026)
def conta(M_, anos): return M_[np.isin(ANOS, anos)].sum(0)
NUM = ["dmin_patio", "dmin_amv", "frac_zona_patio"] + [f"f16p{j}" for j in range(5)] + [f"f16a{j}" for j in range(5)] + ["rmin_geo"] + [f"fr_lt{l}" for l in (300, 400, 500, 600, 800)] + ["rampa_max_pct", "carga_eixo_t", "taxa_dorm", "gab_vert_m", "gab_horiz_m", "cap_vinc", "dias_op", "raio_min_m", "vma_carregado"]
CAT = ["dormente", "perfil_trilho", "fixacao", "sinalizacao", "controle_circ", "bitola", "sentido", "n_linhas"]
for c in NUM: C[c] = pd.to_numeric(C[c], errors="coerce")
for c in CAT: C[c] = C[c].astype(str).str.strip().replace({"nan": "NA", "": "NA"})
Xn = C[NUM].copy(); med = Xn.median().fillna(0.0)
for c in NUM: Xn[c + "_na"] = Xn[c].isna().astype(float); Xn[c] = Xn[c].fillna(med[c])
X0 = StandardScaler().fit_transform(pd.concat([Xn, pd.get_dummies(C[CAT], dtype=float)], axis=1).values.astype(float))   # padronização só usa atributos, nunca a resposta
FERC = pd.factorize(C["ferrovia"])[0]; LINC = pd.factorize(C["ferrovia"].astype(str) + "|" + C["linha"].astype(str))[0]; SEGC = pd.factorize(C["seg_id"].astype(str))[0]; KM = ((C["km_a"] + C["km_b"]) / 2).values; LN = C["len_km"].values
ri, ci = [], []
for l in range(LINC.max() + 1):
    i = np.where(LINC == l)[0]; k = KM[i]; M_ = (np.abs(k[:, None] - k[None, :]) <= 20) & ~np.eye(len(i), dtype=bool); a, b = np.where(M_); ri.append(i[a]); ci.append(i[b])
W = sparse.csr_matrix((np.ones(sum(len(a) for a in ri)), (np.concatenate(ri), np.concatenate(ci))), shape=(N, N)); nviz = np.asarray(W.sum(1)).ravel()
def historico(anos):
    """Histórico de acidentes com os anos informados (todos anteriores ao período conferido), por ano de observação."""
    n = max(len(anos), 1); hv = conta(CV_, anos); ha = conta(CA_, anos); b = (hv > 0).astype(float); d = pd.DataFrame({"b": b, "hv": hv})
    return np.column_stack([hv / n, ha / n, b, (W @ b) / np.maximum(nviz, 1), (W @ hv) / np.maximum(nviz, 1) / n, d.groupby(SEGC)["b"].transform("mean").values, d.groupby(LINC)["b"].transform("mean").values, d.groupby(FERC)["b"].transform("mean").values, d.groupby(FERC)["hv"].transform("mean").values / n])
dp = C["dmin_patio"].fillna(1e9).values; rg = C["rmin_geo"].fillna(1e6).values
B2 = 0.5 * np.select([dp <= 300, dp <= 600, dp <= 1200, dp <= 1800], [4, 3, 2, 1], 0) / 4 + 0.5 * np.select([rg < 500, rg < 1200, rg < 2300], [3, 2, 1], 0) / 3
def auc(y, s):
    n1 = y.sum(); n0 = len(y) - n1; return float((rankdata(s)[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)) if n1 >= 5 and n0 >= 5 else np.nan
def auc_dentro(s, y):
    a, w = [], []
    for f in range(FERC.max() + 1):
        i = FERC == f
        if 5 <= y[i].sum() < i.sum(): a.append(auc(y[i], s[i])); w.append(y[i].sum())
    return float(np.average(a, weights=w)) if a else np.nan
DES = np.random.default_rng(SEED).random(N)
def classe_muito_alta(s, c):
    """Fração dos descarrilamentos conferidos que cai no quintil superior da nota (classe muito alta, cinco classes por quantis da extensão)."""
    o = np.lexsort((DES, -s)); cum = np.cumsum(LN[o]) / LN.sum(); return float(c[o[cum <= 0.20]].sum() / c.sum())
def lr(Xtr, ytr, Xte): return LogisticRegression(C=0.5, max_iter=3000).fit(Xtr, ytr).predict_proba(Xte)[:, 1]
def avalia(desenho, cal, conf, com_historico=False, rotulo=""):
    """cal e conf: listas de anos, disjuntas. Devolve uma linha por método."""
    cal, conf = sorted(cal), sorted(conf); assert not set(cal) & set(conf), "janelas sobrepostas"
    ycal = (conta(CV_, cal) > 0).astype(int); cc = conta(CV_, conf); y = (cc > 0).astype(int)
    if ycal.sum() < 20 or y.sum() < 20: return []
    sentido = "para frente" if max(cal) < min(conf) else ("para trás" if min(cal) > max(conf) else "blocos (passado e futuro)")
    base = dict(desenho=desenho, rotulo=rotulo, calibra=f"{min(cal)}-{max(cal)}" + ("" if len(cal) == max(cal) - min(cal) + 1 else " (com lacuna)"), confere=f"{min(conf)}-{max(conf)}", anos_calibracao=len(cal), horizonte=len(conf), sentido=sentido, conf_ini=min(conf), conf_fim=max(conf), km_calibracao=int(ycal.sum()), km_conferidos=int(y.sum()))
    S = {"Regra do EAR por faixas": B2, "Dummy: taxa da malha": pd.Series(ycal).groupby(FERC).transform("mean").values, "EAR calibrado (atributos da via)": lr(X0, ycal, X0)}
    if com_historico and sentido == "para frente":
        H = len(conf); cal_h = [a for a in cal if a <= max(cal) - H]
        if len(cal_h) >= 2:
            alvo = [a for a in cal if a > max(cal) - H]; Htr = historico(cal_h); Hte = historico(cal); st = StandardScaler().fit(Htr); ytr = (conta(CV_, alvo) > 0).astype(int)
            if ytr.sum() >= 20: S["EAR calibrado + histórico de acidentes"] = lr(np.column_stack([X0, st.transform(Htr)]), ytr, np.column_stack([X0, st.transform(Hte)]))
    return [dict(base, metodo=m, auc=auc(y, s), auc_dentro=auc_dentro(s, y), classe_muito_alta=classe_muito_alta(s, cc)) for m, s in S.items()], (desenho, rotulo, tuple(cal), tuple(conf), y, S)
J = []
# D1: origem móvel, janela expansiva, para frente (Tashman, 2000); horizontes de 1 a 5 anos; mínimo de 4 anos de calibração
for H in (1, 2, 3, 4, 5):
    for T in range(2014, 2026 - H): J.append(("D1 origem móvel, janela expansiva", list(range(2011, T + 1)), list(range(T + 1, T + H + 1)), True, f"H={H}"))
# D2: origem móvel, janela fixa de 3, 5 e 7 anos, para frente
for Wd in (3, 5, 7):
    for H in (1, 3, 5):
        for T in range(2010 + Wd, 2026 - H): J.append(("D2 origem móvel, janela fixa", list(range(T - Wd + 1, T + 1)), list(range(T + 1, T + H + 1)), False, f"W={Wd}, H={H}"))
# D3: espelho para trás do D1 (robustez; não é previsão)
for H in (1, 3, 5):
    for T in range(2010 + H, 2023): J.append(("D3 espelho para trás", list(range(T + 1, 2026)), list(range(T - H + 1, T + 1)), False, f"H={H}"))
# D4: validação cruzada em blocos contíguos (Bergmeir e Benítez, 2012; Roberts et al., 2017): calibra em todos os outros blocos
for K, tam in ((3, 5), (5, 3), (15, 1)):
    for b in range(K):
        conf = list(range(2011 + b * tam, 2011 + (b + 1) * tam)); J.append(("D4 validação cruzada em blocos", [a for a in ANOS if a not in conf], conf, False, f"K={K} blocos de {tam} ano(s)"))
# D5: deixar um ano de fora com lacuna de um ano de cada lado (variante h-bloco: retira os vizinhos imediatos do ano conferido)
for a0 in ANOS: J.append(("D5 um ano de fora, com lacuna", [a for a in ANOS if abs(a - a0) > 1], [int(a0)], False, "lacuna de 1 ano"))
print("avaliações declaradas:", len(J)); gate_between("número de avaliações declaradas", float(len(J)), 150, 260, source="desenho")
