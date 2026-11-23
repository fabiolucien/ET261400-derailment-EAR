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

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import average_precision_score
log_ia("24.1 dados e funções", "Claude", "FOCUS: mesmas funções e mesma matriz do notebook 23", "design, auc, lr", "gates de contagem")

# 0. Resposta e protocolo: iguais ao notebook 23 e à dissertação (trechos inteiros entre pátios fora do ajuste, 5 grupos, 30 sorteios)
n15 = conta(CV_, 2011, 2025); y = (n15 > 0).astype(int); gate("quilômetros com descarrilamento por via em 2011 a 2025", int(y.sum()), 2123, source="notebook 11")
gate("regra do EAR no período inteiro", round(auc(y, B2), 3), 0.588, tol=0.002, source="notebook 11 e dissertação v4")
KF, R = 5, 30
def folds_por(grupo, seed, k=KF):
    u = np.unique(grupo); f = dict(zip(u, np.random.default_rng(seed).permutation(len(u)) % k)); return np.array([f[g] for g in grupo])
def auc_grupo(s, yy, G, minimo=5):
    a, w = [], []
    for g in np.unique(G):
        i = G == g
        if minimo <= yy[i].sum() < i.sum(): a.append(auc(yy[i], s[i])); w.append(yy[i].sum())
    return float(np.average(a, weights=w))
def topo(s, yy):
    o = np.lexsort((DES, -s)); top = np.zeros(N, bool); top[o[(np.cumsum(LN[o]) / LN.sum()) <= 0.20]] = True; return top
def matriz_conf(s, yy):
    t = topo(s, yy); tp = int((t & (yy == 1)).sum()); fp = int((t & (yy == 0)).sum()); fn = int((~t & (yy == 1)).sum()); tn = int((~t & (yy == 0)).sum())
    assert tp + fn == yy.sum() and tp + fp + fn + tn == N
    rec = tp / (tp + fn); pre = tp / (tp + fp); return dict(VP=tp, FP=fp, FN=fn, VN=tn, recall=rec, precisao=pre, especificidade=tn / (tn + fp), F1=2 * pre * rec / (pre + rec))


# 1. Decomposição do ganho dos critérios do EAR (pedido da revisão independente de 22/11): a regra fixa usa faixas e pesos iguais;
#    a logística contínua muda três coisas ao mesmo tempo. Aqui cada mudança entra sozinha, nos mesmos 30 sorteios do notebook 24.
def faixas(d): return np.select([d <= 300, d <= 600, d <= 1200, d <= 1800], [4, 3, 2, 1], 0)
def classes_raio(r): return np.select([r < 500, r < 1200, r < 2300], [3, 2, 1], 0)
da = C["dmin_amv"].fillna(1e9).values
oh = lambda v, k, nome: pd.get_dummies(pd.Categorical(v, categories=range(k)), prefix=nome, dtype=float).iloc[:, 1:].values
X_R1 = np.column_stack([oh(faixas(dp), 5, "fp"), oh(classes_raio(rg), 4, "cr")])                          # mesmas faixas e classes da regra, pesos aprendidos
X_R2 = np.column_stack([X_R1, oh(faixas(da), 5, "fa")])                                                   # + faixas de distância ao AMV estimado
gate("faixas de pátio na regra: células na faixa mais próxima (até 300 m)", int((faixas(dp) == 4).sum()), int((dp <= 300).sum()), source="definição da regra")
NOTAS = {"R0 Regra do EAR (faixas fixas, pesos iguais)": None, "R1 Mesmas faixas, pesos aprendidos": X_R1, "R2 R1 + faixas de distância ao AMV": X_R2, "R3 Critérios do EAR contínuos (notebook 24)": XE}
L, GU = [], {}
for r in range(R):
    fo = folds_por(SEGC, SEED + r); S = {}
    for m, X in NOTAS.items():
        if X is None: S[m] = B2.copy(); continue
        s_ = np.zeros(N)
        for k in range(KF):
            te = fo == k; s_[te] = lr(X[~te], y[~te], X[te])
        S[m] = s_
    if r < 10: GU[r] = S
    for m, s_ in S.items(): L.append(dict(sorteio=r, metodo=m, auc=auc(y, s_), auc_malha=auc_grupo(s_, y, FERC), auc_linha=auc_grupo(s_, y, LINC), recall=matriz_conf(s_, y)["recall"]))
RES = pd.DataFrame(L); RES.to_csv(f"{TAB}/25_decomposicao_por_sorteio.csv", index=False)
T = RES.groupby("metodo")[["auc", "auc_malha", "auc_linha", "recall"]].mean().loc[list(NOTAS)]; display(T.round(3)); T.to_csv(f"{TAB}/25_decomposicao_resumo.csv")
gate("R3 reproduz os critérios contínuos do notebook 24 (AUC no país)", round(T.iloc[3]["auc"], 3), 0.632, tol=0.002, source="notebook 24")
gate("R3 reproduz os critérios contínuos do notebook 24 (AUC dentro das malhas)", round(T.iloc[3]["auc_malha"], 3), 0.655, tol=0.002, source="notebook 24")
log_ia("25.1 decomposição", "Claude", "FOCUS: separar pesos, AMV e medida contínua, mesmos sorteios do notebook 24", "25_decomposicao_resumo.csv", "2 gates contra o notebook 24")

# 2. Diferenças pareadas por sorteio e IC 95% por reamostragem de linhas inteiras (10 sorteios, 300 reamostragens), como no notebook 24
PARES = [(list(NOTAS)[1], list(NOTAS)[0]), (list(NOTAS)[2], list(NOTAS)[1]), (list(NOTAS)[3], list(NOTAS)[2]), (list(NOTAS)[3], list(NOTAS)[0])]
P = RES.pivot_table(index="sorteio", columns="metodo", values=["auc", "auc_malha"])
rng = np.random.default_rng(SEED); Lu = np.unique(LINC); ix = {l: np.where(LINC == l)[0] for l in Lu}; BOOT = []
for b in range(300):
    i = np.concatenate([ix[l] for l in rng.choice(Lu, len(Lu))])
    if y[i].sum() < 50: continue
    BOOT.append({(a, c): (np.mean([auc(y[i], GU[r][a][i]) - auc(y[i], GU[r][c][i]) for r in range(10)]), np.mean([auc_grupo(GU[r][a][i], y[i], FERC[i]) - auc_grupo(GU[r][c][i], y[i], FERC[i]) for r in range(10)])) for a, c in PARES})
D = []
for a, c in PARES:
    bn = np.array([x[(a, c)][0] for x in BOOT]); bm = np.array([x[(a, c)][1] for x in BOOT]); dn = P["auc"][a] - P["auc"][c]; dm = P["auc_malha"][a] - P["auc_malha"][c]
    D.append(dict(comparacao=f"{a[:2]} − {c[:2]}", dif_pais=dn.mean(), ic_pais=f"{np.percentile(bn, 2.5):.3f} a {np.percentile(bn, 97.5):.3f}", sorteios_com_ganho_pais=int((dn > 0).sum()),
                  dif_malha=dm.mean(), ic_malha=f"{np.percentile(bm, 2.5):.3f} a {np.percentile(bm, 97.5):.3f}", sorteios_com_ganho_malha=int((dm > 0).sum())))
D = pd.DataFrame(D).round(3); display(D); D.to_csv(f"{TAB}/25_decomposicao_diferencas.csv", index=False)
gate("soma das três parcelas igual ao ganho total dentro das malhas (R3 − R0)", round(float(D.iloc[:3]["dif_malha"].sum()), 3), round(float(D.iloc[3]["dif_malha"]), 3), tol=0.002, source="identidade aritmética")
log_ia("25.2 diferenças", "Claude", "FOCUS: IC por reamostragem de linhas inteiras", "25_decomposicao_diferencas.csv", "identidade da soma")

# 3. Vazamento: R1 com rótulos embaralhados (média de 5 embaralhamentos)
emb = []
for r in range(5):
    ye = np.random.default_rng(3000 + r).permutation(y); fo = folds_por(SEGC, SEED + r); s_ = np.zeros(N)
    for k in range(KF):
        te = fo == k; s_[te] = lr(X_R1[~te], ye[~te], X_R1[te])
    emb.append(auc(ye, s_))
gate_between("vazamento: faixas com pesos aprendidos e rótulos embaralhados", round(float(np.mean(emb)), 3), 0.45, 0.55, source="acaso")
exportar_registros("25")
