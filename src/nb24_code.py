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

# Hiperparâmetros fixados antes de rodar (valores usuais da documentação do scikit-learn e da aula 6); a grade da seção 3 mede a sensibilidade
MODELOS = {
    "Regressão logística (atributos)": lambda s: LogisticRegression(C=0.5, max_iter=3000),
    "Árvore de decisão": lambda s: DecisionTreeClassifier(max_depth=6, min_samples_leaf=50, random_state=s),
    "Random Forest": lambda s: RandomForestClassifier(n_estimators=200, min_samples_leaf=20, max_features="sqrt", n_jobs=-1, random_state=s),
    "Gradient boosting (HGB)": lambda s: HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, early_stopping=True, validation_fraction=0.1, random_state=s),
    "MLP (32, 16)": lambda s: MLPClassifier(hidden_layer_sizes=(32, 16), alpha=1e-3, early_stopping=True, max_iter=300, random_state=s),
}
def notas(fo, yy, modelos=MODELOS, seed=SEED):
    S = {"Regra do EAR por faixas": B2.copy(), "Dummy: taxa da malha": np.zeros(N), "Critérios do EAR contínuos (logística)": np.zeros(N)}
    S.update({m: np.zeros(N) for m in modelos})
    for k in range(KF):
        te = fo == k; tr = ~te
        t = pd.Series(yy[tr]).groupby(FERC[tr]).mean(); S["Dummy: taxa da malha"][te] = pd.Series(FERC[te]).map(t).fillna(yy[tr].mean()).values
        S["Critérios do EAR contínuos (logística)"][te] = lr(XE[tr], yy[tr], XE[te])
        for m, f in modelos.items(): S[m][te] = f(seed).fit(X0[tr], yy[tr]).predict_proba(X0[te])[:, 1]
    return S
import time; t0 = time.time(); L, GUARDA = [], {}
for r in range(R):
    fo = folds_por(SEGC, SEED + r); S = notas(fo, y, seed=SEED + r)
    if r < 10: GUARDA[r] = S
    for m, s in S.items():
        L.append(dict(sorteio=r, metodo=m, auc=auc(y, s), auc_malha=0.5 if m.startswith("Dummy") else auc_grupo(s, y, FERC), auc_linha=auc_grupo(s, y, LINC), pr_auc=average_precision_score(y, s), **matriz_conf(s, y)))
    if r % 5 == 4: print(f"sorteio {r + 1} de {R}: {round((time.time() - t0) / 60, 1)} min", flush=True)
RES = pd.DataFrame(L); RES.to_csv(f"{TAB}/24_modelos_por_sorteio.csv", index=False)
ORDEM = ["Regra do EAR por faixas", "Dummy: taxa da malha", "Critérios do EAR contínuos (logística)"] + list(MODELOS)
COLS = ["auc", "auc_malha", "auc_linha", "pr_auc", "recall", "precisao", "F1"]
T = RES.groupby("metodo")[COLS].mean().loc[ORDEM].round(3)
T = T.join(RES.groupby("metodo")["auc"].agg(auc_min="min", auc_max="max").round(3)).join(RES.groupby("metodo")[["VP", "FP", "FN", "VN"]].mean().round(0))
display(T); T.to_csv(f"{TAB}/24_modelos_resumo.csv")
gate("logística com atributos: AUC no país igual ao notebook 23 (mesmos sorteios)", round(T.loc["Regressão logística (atributos)", "auc"], 3), 0.759, tol=0.002, source="notebook 23")
gate("critérios contínuos: AUC no país igual ao notebook 23", round(T.loc["Critérios do EAR contínuos (logística)", "auc"], 3), 0.632, tol=0.002, source="notebook 23")
gate("Dummy da malha: AUC no país igual ao notebook 23", round(T.loc["Dummy: taxa da malha", "auc"], 3), 0.693, tol=0.002, source="notebook 23")
gate("logística com atributos: recall na classe muito alta igual à captura do notebook 23", round(T.loc["Regressão logística (atributos)", "recall"], 3), 0.510, tol=0.005, source="notebook 23")
gate("gradient boosting: AUC dentro das malhas perto da dissertação (0,671; outros hiperparâmetros)", round(T.loc["Gradient boosting (HGB)", "auc_malha"], 3), 0.671, tol=0.02, source="dissertação v4, Tabela 22")
log_ia("24.2 modelos da aula 6", "Claude", "FOCUS: mesmo protocolo, mesmos sorteios, hiperparâmetros fixados antes", "24_modelos_resumo.csv", "4 gates contra o notebook 23 e 1 contra a dissertação")

# 1. Diferenças: média dos 30 sorteios, parcela de sorteios com ganho e IC 95% por reamostragem de linhas inteiras (10 sorteios, 300 reamostragens)
PARES = [("Critérios do EAR contínuos (logística)", "Regra do EAR por faixas"), ("Regressão logística (atributos)", "Regra do EAR por faixas"), ("Regressão logística (atributos)", "Critérios do EAR contínuos (logística)"),
         ("Árvore de decisão", "Regressão logística (atributos)"), ("Random Forest", "Regressão logística (atributos)"), ("Gradient boosting (HGB)", "Regressão logística (atributos)"), ("MLP (32, 16)", "Regressão logística (atributos)")]
P = RES.pivot_table(index="sorteio", columns="metodo", values=["auc", "auc_malha"])
rng = np.random.default_rng(SEED); Lu = np.unique(LINC); ix = {l: np.where(LINC == l)[0] for l in Lu}; B = 300; BOOT = []
for b in range(B):
    i = np.concatenate([ix[l] for l in rng.choice(Lu, len(Lu))])
    if y[i].sum() < 50: continue
    reg = {}
    for a, c in PARES:
        da = [auc(y[i], GUARDA[r][a][i]) - auc(y[i], GUARDA[r][c][i]) for r in range(10)]
        dm = [auc_grupo_i - auc_grupo_j for auc_grupo_i, auc_grupo_j in [(auc_grupo(GUARDA[r][a][i], y[i], FERC[i]), auc_grupo(GUARDA[r][c][i], y[i], FERC[i])) for r in range(10)]]
        reg[(a, c)] = (np.mean(da), np.mean(dm))
    BOOT.append(reg)
D = []
for a, c in PARES:
    bn = np.array([x[(a, c)][0] for x in BOOT]); bm = np.array([x[(a, c)][1] for x in BOOT])
    dn = P["auc"][a] - P["auc"][c]; dmal = P["auc_malha"][a] - P["auc_malha"][c]
    D.append(dict(comparacao=f"{a} − {c}", dif_pais=dn.mean(), ic_pais=f"{np.percentile(bn, 2.5):.3f} a {np.percentile(bn, 97.5):.3f}", sorteios_com_ganho_pais=int((dn > 0).sum()),
                  dif_malha=dmal.mean(), ic_malha=f"{np.percentile(bm, 2.5):.3f} a {np.percentile(bm, 97.5):.3f}", sorteios_com_ganho_malha=int((dmal > 0).sum())))
D = pd.DataFrame(D).round(3); display(D); D.to_csv(f"{TAB}/24_diferencas.csv", index=False)
log_ia("24.3 diferenças", "Claude", "FOCUS: IC por reamostragem de linhas inteiras, como na dissertação", "24_diferencas.csv", "IC e sorteios")

# 2. Matriz de confusão na classe muito alta (20% da extensão de maior nota), média dos 30 sorteios
MC = RES.groupby("metodo")[["VP", "FP", "FN", "VN", "recall", "precisao", "especificidade"]].agg(["mean", lambda v: np.percentile(v, 2.5), lambda v: np.percentile(v, 97.5)]).loc[ORDEM]
MC.columns = [f"{a}_{ {'mean': 'media', '<lambda_0>': 'p2_5', '<lambda_1>': 'p97_5'}[b] }" for a, b in MC.columns]; MC = MC.round(3); display(MC); MC.to_csv(f"{TAB}/24_matriz_confusao.csv")
print("taxa-base (quilômetros atingidos):", round(y.mean(), 3))

# 3. Sensibilidade aos hiperparâmetros (10 sorteios; grade declarada antes)
GRADE = [("Regressão logística (atributos)", "C", [0.01, 0.1, 0.5, 1.0, 10.0], lambda v, s: LogisticRegression(C=v, max_iter=3000)),
         ("Árvore de decisão", "max_depth", [4, 6, 10], lambda v, s: DecisionTreeClassifier(max_depth=v, min_samples_leaf=50, random_state=s)),
         ("Random Forest", "min_samples_leaf", [5, 20, 50], lambda v, s: RandomForestClassifier(n_estimators=200, min_samples_leaf=v, max_features="sqrt", n_jobs=-1, random_state=s)),
         ("Gradient boosting (HGB)", "learning_rate", [0.03, 0.05, 0.1], lambda v, s: HistGradientBoostingClassifier(max_iter=300, learning_rate=v, early_stopping=True, validation_fraction=0.1, random_state=s)),
         ("MLP (32, 16)", "alpha", [1e-4, 1e-3, 1e-2], lambda v, s: MLPClassifier(hidden_layer_sizes=(32, 16), alpha=v, early_stopping=True, max_iter=300, random_state=s))]
H = []
for m, par, vals, f in GRADE:
    for v in vals:
        for r in range(10):
            fo = folds_por(SEGC, SEED + r); s_ = np.zeros(N)
            for k in range(KF):
                te = fo == k; s_[te] = f(v, SEED + r).fit(X0[~te], y[~te]).predict_proba(X0[te])[:, 1]
            H.append(dict(modelo=m, parametro=par, valor=v, sorteio=r, auc=auc(y, s_), auc_malha=auc_grupo(s_, y, FERC)))
H = pd.DataFrame(H).groupby(["modelo", "parametro", "valor"])[["auc", "auc_malha"]].mean().round(3); display(H); H.to_csv(f"{TAB}/24_hiperparametros.csv")
log_ia("24.4 hiperparâmetros", "Claude", "FOCUS: grade pequena declarada antes; relatar toda a grade", "24_hiperparametros.csv", "faixa de variação")

# 4. Uma malha inteira fora do ajuste (transferência), AUC na própria malha deixada de fora
LM = []
for f in range(FERC.max() + 1):
    te = FERC == f
    if y[te].sum() < 5: continue
    tr = ~te; nome = C["ferrovia"].iloc[np.where(te)[0][0]]
    reg = dict(malha=nome, celulas=int(te.sum()), atingidas=int(y[te].sum()), regra=auc(y[te], B2[te]), criterios_continuos=auc(y[te], lr(XE[tr], y[tr], XE[te])), logistica_atributos=auc(y[te], lr(X0[tr], y[tr], X0[te])))
    for m in ("Random Forest", "Gradient boosting (HGB)"): reg[m] = auc(y[te], MODELOS[m](SEED).fit(X0[tr], y[tr]).predict_proba(X0[te])[:, 1])
    LM.append(reg)
LM = pd.DataFrame(LM).round(3); display(LM); LM.to_csv(f"{TAB}/24_malha_fora.csv", index=False)
pond = {c: float(np.average(LM[c], weights=LM["atingidas"])) for c in ["regra", "criterios_continuos", "logistica_atributos", "Random Forest", "Gradient boosting (HGB)"]}; print({k: round(v, 3) for k, v in pond.items()})
gate("malha nunca vista: critérios contínuos perto da dissertação (0,643)", round(pond["criterios_continuos"], 3), 0.643, tol=0.02, source="dissertação v4, seção 7")
log_ia("24.5 malha fora", "Claude", "FOCUS: cada malha com pelo menos 5 km atingidos fica fora uma vez", "24_malha_fora.csv", "1 gate contra a dissertação")

# 5. Teste de vazamento: rótulos embaralhados no melhor modelo de árvores, média de 5 embaralhamentos
emb = []
for r in range(5):
    ye = np.random.default_rng(2000 + r).permutation(y); fo = folds_por(SEGC, SEED + r); s_ = np.zeros(N)
    for k in range(KF):
        te = fo == k; s_[te] = MODELOS["Gradient boosting (HGB)"](SEED).fit(X0[~te], ye[~te]).predict_proba(X0[te])[:, 1]
    emb.append(auc(ye, s_))
gate_between("vazamento: gradient boosting com rótulos embaralhados", round(float(np.mean(emb)), 3), 0.45, 0.55, source="acaso")
exportar_registros("24")
