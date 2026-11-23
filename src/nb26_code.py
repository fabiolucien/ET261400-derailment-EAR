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


from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import cohen_kappa_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline

# 1. Desenho conjunto (revisão de 22/11, item I1): anos futuros E trechos fora do ajuste ao mesmo tempo.
#    Origem móvel com janela expansiva (Tashman, 2000), como no notebook 21; em cada origem, cinco grupos de trechos entre pátios, cinco sorteios.
def conta_anos(a0, a1): return conta(CV_, a0, a1)
NT = {"Regra do EAR por faixas": None, "Critérios do EAR contínuos": XE, "EAR calibrado (atributos da via)": X0}
J = []
for H, origens in ((3, range(2015, 2023)), (1, range(2014, 2025))):
    for T in origens:
        ycal = (conta_anos(2011, T) > 0).astype(int); yc = (conta_anos(T + 1, T + H) > 0).astype(int)
        for m, X in NT.items():
            if X is None:
                J.append(dict(H=H, T=T, metodo=m, desenho="mesmas células", sorteio=-1, auc=auc(yc, B2), auc_malha=auc_grupo(B2, yc, FERC))); continue
            s0 = lr(X, ycal, X); J.append(dict(H=H, T=T, metodo=m, desenho="mesmas células", sorteio=-1, auc=auc(yc, s0), auc_malha=auc_grupo(s0, yc, FERC)))
            for r in range(5):
                fo = folds_por(SEGC, SEED + r); s_ = np.zeros(N)
                for k in range(KF):
                    te = fo == k; s_[te] = lr(X[~te], ycal[~te], X[te])
                J.append(dict(H=H, T=T, metodo=m, desenho="trechos fora", sorteio=r, auc=auc(yc, s_), auc_malha=auc_grupo(s_, yc, FERC)))
J = pd.DataFrame(J); J.to_csv(f"{TAB}/26_conjunto_por_origem.csv", index=False)
CJ = J.groupby(["H", "metodo", "desenho"])[["auc", "auc_malha"]].mean().round(3); display(CJ); CJ.to_csv(f"{TAB}/26_conjunto_resumo.csv")
ref = J[(J.H == 3) & (J.desenho == "mesmas células")].groupby("metodo")[["auc", "auc_malha"]].mean()
gate("mesmas células, H = 3: EAR calibrado igual ao notebook 18 (AUC no país)", round(ref.loc["EAR calibrado (atributos da via)", "auc"], 3), 0.752, tol=0.003, source="notebook 18")
gate("mesmas células, H = 3: EAR calibrado igual ao notebook 18 (AUC dentro das malhas)", round(ref.loc["EAR calibrado (atributos da via)", "auc_malha"], 3), 0.665, tol=0.003, source="notebook 18")
gate("regra do EAR, H = 3, igual ao notebook 18", round(ref.loc["Regra do EAR por faixas", "auc"], 3), 0.580, tol=0.003, source="notebook 18")
po = J[J.desenho == "trechos fora"].groupby(["H", "T", "metodo"])["auc"].mean().unstack("metodo")
ganho = (po["EAR calibrado (atributos da via)"] - J[J.metodo == "Regra do EAR por faixas"].set_index(["H", "T"])["auc"]); print("origens com o EAR calibrado (trechos fora) acima da regra:", int((ganho > 0).sum()), "de", len(ganho), "| menor diferença:", round(float(ganho.min()), 3))
log_ia("26.1 desenho conjunto", "Claude", "FOCUS: origem móvel com trechos fora do ajuste; mesmas funções dos notebooks 21 e 24", "26_conjunto_resumo.csv", "3 gates contra o notebook 18")

# 2. Calibração das probabilidades fora do ajuste (revisão, item 5c): Brier, Brier skill e inclinação de calibração, 10 sorteios do protocolo espacial
CAL = []
for r in range(10):
    fo = folds_por(SEGC, SEED + r); P_ = {"Regressão logística (atributos)": np.zeros(N), "Gradient boosting (HGB)": np.zeros(N)}
    for k in range(KF):
        te = fo == k
        P_["Regressão logística (atributos)"][te] = LogisticRegression(C=0.5, max_iter=3000).fit(X0[~te], y[~te]).predict_proba(X0[te])[:, 1]
        P_["Gradient boosting (HGB)"][te] = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, early_stopping=True, validation_fraction=0.1, random_state=SEED + r).fit(X0[~te], y[~te]).predict_proba(X0[te])[:, 1]
    for m, p in P_.items():
        p = np.clip(p, 1e-6, 1 - 1e-6); lg = np.log(p / (1 - p)).reshape(-1, 1)
        inc = LogisticRegression(C=1e6, max_iter=2000).fit(lg, y).coef_[0, 0]
        CAL.append(dict(sorteio=r, modelo=m, brier=float(np.mean((p - y) ** 2)), brier_taxa_base=float(y.mean() * (1 - y.mean())), media_prevista=float(p.mean()), inclinacao=float(inc)))
CAL = pd.DataFrame(CAL); CAL["brier_skill"] = 1 - CAL.brier / CAL.brier_taxa_base
CR = CAL.groupby("modelo")[["brier", "brier_taxa_base", "brier_skill", "inclinacao", "media_prevista"]].mean().round(4); display(CR); CR.to_csv(f"{TAB}/26_calibracao.csv")
gate("Brier da taxa-base constante = p(1 − p)", round(float(CAL.brier_taxa_base.iloc[0]), 4), round(float(y.mean() * (1 - y.mean())), 4), tol=0.0, source="definição")
log_ia("26.2 calibração", "Claude", "FOCUS: Brier e inclinação de calibração das notas fora do ajuste", "26_calibracao.csv", "gate de definição")

# 3. Modelo de linguagem contra o TF-IDF na mesma cobertura (revisão, item C2). Mesmo classificador e mesma amostra B do notebook 04b
MAPA = {"F5 plataforma, lastro e drenagem": "ROADBED", "F1 geometria e bitola": "TRACK_GEOMETRY", "F3 trilho, juntas e fixações": "RAIL_JOINT", "F4 AMV e aparelhos": "SWITCH_FROG", "F6 obras de arte e outros": "OTHER_WAY_STRUCTURE"}
fra = pd.read_csv(f"{PROC}/fra_desc_via_2006_2026.csv"); fra["oficial"] = fra["familia"].map(MAPA); fra = fra.drop_duplicates("Narrative").reset_index(drop=True); fra["uid"] = fra.index
gate("narrativas distintas (FRA)", len(fra), 11356, source="notebook 04b")
Lb = pd.read_csv(f"{PROC}/04b_llm_rotulos_fra.csv"); Bm = Lb[Lb.amostra == "B"].merge(fra[["uid", "Narrative"]], on="uid", how="left")
gate("amostra B com narrativa", int(Bm["Narrative"].notna().sum()), 600, source="notebook 04b")
Tr = fra[~fra["uid"].isin(Bm["uid"])]
clf = make_pipeline(TfidfVectorizer(ngram_range=(1, 2), min_df=3, sublinear_tf=True), LogisticRegression(C=5, max_iter=2000, class_weight="balanced")).fit(Tr["Narrative"], Tr["oficial"])
pr = clf.predict_proba(Bm["Narrative"]); pred = clf.classes_[pr.argmax(1)]; conf = pr.max(1)
cobS = Bm["sonnet"] != "UNDETERMINED"; q = cobS.mean(); corte = np.quantile(conf, 1 - q); cobT = conf >= corte
k = lambda a, b: cohen_kappa_score(a, b)
TF = pd.DataFrame([dict(classificador="TF-IDF, todas as 600", cobertura=1.0, kappa=k(Bm["oficial"], pred)),
                   dict(classificador="TF-IDF, nas 391 do Sonnet", cobertura=float(cobS.mean()), kappa=k(Bm.loc[cobS, "oficial"], pred[cobS.values])),
                   dict(classificador="TF-IDF abstendo-se na mesma cobertura (menor confiança)", cobertura=float(cobT.mean()), kappa=k(Bm.loc[cobT, "oficial"], pred[cobT])),
                   dict(classificador="Claude Sonnet, nas próprias 391", cobertura=float(cobS.mean()), kappa=k(Bm.loc[cobS, "oficial"], Bm.loc[cobS, "sonnet"]))]).round(3)
display(TF); TF.to_csv(f"{TAB}/26_tfidf_mesma_cobertura.csv", index=False)
gate("TF-IDF em todas as 600 perto do notebook 04b (0,613)", round(float(TF.kappa.iloc[0]), 3), 0.613, tol=0.03, source="notebook 04b; versão do scikit-learn pode mudar a terceira casa")
gate("TF-IDF nas 391 do Sonnet perto do notebook 04b (0,802)", round(float(TF.kappa.iloc[1]), 3), 0.802, tol=0.03, source="notebook 04b")
gate("Sonnet nas próprias narrativas igual ao notebook 04b", round(float(TF.kappa.iloc[3]), 3), 0.866, tol=0.001, source="notebook 04b")
log_ia("26.3 mesma cobertura", "Claude", "FOCUS: abstenção do TF-IDF pela menor confiança, na cobertura do Sonnet", "26_tfidf_mesma_cobertura.csv", "3 gates contra o notebook 04b")
exportar_registros("26")
