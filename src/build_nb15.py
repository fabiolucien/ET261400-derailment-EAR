# -*- coding: utf-8 -*-
"""Gera notebooks/15_previsao_malha_em_operacao.ipynb: treinar com o passado e prever os anos seguintes na malha em operação."""
import nbformat as nbf
from nb_common import HEADER_RULE, SETUP_CODE, DECLARACAO_IA
cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s))
code = lambda s: cells.append(nbf.v4.new_code_cell(s))
md(f"""# 15 · Malha em operação: treinar com o passado e prever os anos seguintes

{HEADER_RULE}

**Foco definido pelo autor (16/11).** O uso principal é a malha existente: com o que se sabe até um ano T (atributos da via e histórico de acidentes), apontar os quilômetros que terão descarrilamento por via nos anos seguintes, inclusive os que ainda não tiveram nenhum.

**Desenho (declarado antes dos resultados).** Janela móvel, sem olhar o futuro: para cada ano de corte T de 2016 a 2022, o modelo é ajustado com o histórico até T−3 para explicar os descarrilamentos de T−2 a T, e depois aplicado com o histórico até T para prever T+1 a T+3. São sete cortes; nenhum dado do período previsto entra no ajuste nem nos atributos. Métricas na malha inteira e também só nos quilômetros que nunca tinham tido descarrilamento por via até T.

**Métodos comparados em todos os cortes.** Regra do EAR (sem ajuste); histórico do próprio quilômetro; histórico do quilômetro, da vizinhança, da linha e da malha (logística); atributos da via sem histórico (modelo M2); atributos mais histórico (logística e gradient boosting, hiperparâmetros fixos).

**Gates.** 2.681 descarrilamentos por via entre 2011 e 2025; janelas de ajuste e de teste disjuntas em todos os cortes; nenhum atributo usa ano posterior a T.""")
code(SETUP_CODE)
code(r'''import warnings; warnings.filterwarnings("ignore")
from scipy import sparse
from scipy.stats import rankdata
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
SEED, H = 42, 3
C0 = pd.read_csv(f"{PROC}/11_celulas_1km.csv")
C = C0[~C0["sentido"].astype(str).str.contains("Interromp")].sort_values(["ferrovia", "linha", "km_a"]).reset_index(drop=True); gate("células em operação", len(C), 20936, source="notebook 11")
E = pd.read_csv(f"{PROC}/11_eventos_celulas.csv"); E = E[E["cel_id"].isin(C["cel_id"])].copy(); E["ano"] = E["ano"].astype(int); EV = E[E["via"]]
gate("descarrilamentos por via nas células", len(EV), 2681, source="notebook 11"); gate_between("anos dos eventos", float(EV["ano"].min()), 2011, 2011, source="recorte 2011 a 2025"); gate_between("último ano dos eventos", float(EV["ano"].max()), 2025, 2025, source="recorte 2011 a 2025")
display(EV.groupby("ano").size().to_frame("descarrilamentos por via").T)
idx = pd.Series(np.arange(len(C)), index=C["cel_id"])
def contagem(ev, a0, a1):
    v = np.zeros(len(C)); s = ev[(ev["ano"] >= a0) & (ev["ano"] <= a1)].groupby("cel_id").size(); v[idx[s.index].values] = s.values; return v
DIST = ["dmin_patio", "dmin_amv", "frac_zona_patio"] + [f"f16p{j}" for j in range(5)] + [f"f16a{j}" for j in range(5)]
CURV = ["rmin_geo"] + [f"fr_lt{l}" for l in (300, 400, 500, 600, 800)]
NUM = ["rampa_max_pct", "carga_eixo_t", "taxa_dorm", "gab_vert_m", "gab_horiz_m", "cap_vinc", "dias_op", "raio_min_m", "vma_carregado"]
CAT = ["dormente", "perfil_trilho", "fixacao", "sinalizacao", "controle_circ", "bitola", "sentido", "n_linhas"]
for c in NUM + DIST + CURV: C[c] = pd.to_numeric(C[c], errors="coerce")
for c in CAT: C[c] = C[c].astype(str).str.strip().replace({"nan": "NA", "": "NA"})
def design(df, num, cat):
    X = df[num].copy(); med = X.median().fillna(0.0)
    for c in num: X[c + "_na"] = X[c].isna().astype(float); X[c] = X[c].fillna(med[c])
    return pd.concat([X, pd.get_dummies(df[cat], dtype=float)], axis=1).values
X0 = design(C, DIST + CURV + NUM, CAT); LN = C["len_km"].values; fer = np.asarray(C["ferrovia"], dtype=object); LIN = np.asarray(C["ferrovia"] + "|" + C["linha"].astype(str), dtype=object); SEG = np.asarray(C["seg_id"].astype(str), dtype=object); KM = ((C["km_a"] + C["km_b"]) / 2).values
ri, ci = [], []
for l in np.unique(LIN):
    i = np.where(LIN == l)[0]; k = KM[i]; M = (np.abs(k[:, None] - k[None, :]) <= 20) & ~np.eye(len(i), dtype=bool); a, b = np.where(M); ri.append(i[a]); ci.append(i[b])
W = sparse.csr_matrix((np.ones(sum(len(a) for a in ri)), (np.concatenate(ri), np.concatenate(ci))), shape=(len(C), len(C))); nviz = np.asarray(W.sum(1)).ravel()
def historico(T):
    """Atributos de histórico com dados de 2011 até o ano T, por ano de observação (comparáveis entre cortes)."""
    assert T <= 2025; n = T - 2010; hv = contagem(EV, 2011, T); ha = contagem(E, 2011, T); b = (hv > 0).astype(float); d = pd.DataFrame({"b": b, "hv": hv})
    return np.column_stack([hv / n, ha / n, b, (W @ b) / np.maximum(nviz, 1), (W @ hv) / np.maximum(nviz, 1) / n, d.groupby(SEG)["b"].transform("mean").values, d.groupby(LIN)["b"].transform("mean").values, d.groupby(fer)["b"].transform("mean").values, d.groupby(fer)["hv"].transform("mean").values / n]), b
def cls16(d): return np.select([d <= 300, d <= 600, d <= 1200, d <= 1800], [4, 3, 2, 1], 0)
def rcls16(r_): return np.select([r_ < 500, r_ < 1200, r_ < 2300], [3, 2, 1], 0)
B2 = (0.5 * cls16(C["dmin_patio"].fillna(1e9)) / 4 + 0.5 * rcls16(C["rmin_geo"].fillna(1e6)) / 3).astype(float)
def auc(yy, s, m=None):
    if m is not None: yy, s = yy[m], s[m]
    n1 = yy.sum(); n0_ = len(yy) - n1; return float((rankdata(s)[yy == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0_)) if n1 >= 5 and n0_ >= 5 else np.nan
def auc_dentro(s, yy, m=None):
    a, w = [], []
    for f in np.unique(fer):
        i = (fer == f) if m is None else ((fer == f) & m)
        if yy[i].sum() >= 5 and yy[i].sum() < i.sum(): a.append(auc(yy[i], s[i])); w.append(yy[i].sum())
    return float(np.average(a, weights=w)) if a else np.nan
def captura(s, evv, p=0.20):
    o = np.lexsort((np.random.default_rng(SEED).random(len(s)), -s)); cum = np.cumsum(LN[o]) / LN.sum(); return float(evv[o][cum <= p].sum() / evv.sum())
def lr(Xtr, ytr, Xte):
    st = StandardScaler().fit(Xtr); return LogisticRegression(C=0.5, max_iter=3000).fit(st.transform(Xtr), ytr).predict_proba(st.transform(Xte))[:, 1]
def gbm(Xtr, ytr, Xte): return HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=15, l2_regularization=1.0, early_stopping=False, random_state=SEED).fit(Xtr, ytr).predict_proba(Xte)[:, 1]
log_ia("15.1 dados e histórico", "Claude", "FOCUS: histórico por ano de observação até T; vizinhança de 20 km na mesma linha; nada posterior a T", "historico(T), W", "4 gates de contagem e de período")''')
code(r'''L = []
for T in range(2016, 2023):
    tr_a0, tr_a1, te_a0, te_a1 = T - H + 1, T, T + 1, T + H; assert tr_a1 < te_a0 and te_a1 <= 2025
    Htr, _ = historico(T - H); Hte, ja = historico(T); ytr = (contagem(EV, tr_a0, tr_a1) > 0).astype(int); cte = contagem(EV, te_a0, te_a1); yte = (cte > 0).astype(int); novo = ja == 0
    S = {"Regra do EAR (sem ajuste)": B2, "Histórico do próprio km": Hte[:, 0], "Histórico (km, vizinhança, linha, malha)": lr(Htr, ytr, Hte), "Atributos da via, sem histórico (M2)": lr(X0, ytr, X0),
         "Atributos + histórico (logística)": lr(np.column_stack([X0, Htr]), ytr, np.column_stack([X0, Hte])), "Atributos + histórico (gradient boosting)": gbm(np.column_stack([X0, Htr]), ytr, np.column_stack([X0, Hte]))}
    for nome, s in S.items():
        L.append(dict(corte=T, ajuste=f"{tr_a0} a {tr_a1}", previsto=f"{te_a0} a {te_a1}", metodo=nome, atingidas=int(yte.sum()), atingidas_sem_acidente_antes=int(yte[novo].sum()), auc_malha_inteira=auc(yte, s), auc_dentro=auc_dentro(s, yte), captura20=captura(s, cte), auc_km_sem_acidente_antes=auc(yte, s, novo), auc_dentro_km_sem_acidente_antes=auc_dentro(s, yte, novo)))
    print(T, "ok", flush=True)
R_ = pd.DataFrame(L); R_.to_csv(f"{TAB}/15_previsao_por_corte.csv", index=False)
gate("cortes avaliados", int(R_["corte"].nunique()), 7, source="desenho: T de 2016 a 2022")
res = R_.groupby("metodo", sort=False)[["auc_malha_inteira", "auc_dentro", "captura20", "auc_km_sem_acidente_antes", "auc_dentro_km_sem_acidente_antes"]].agg(["mean", "min", "max"]).round(3); display(res); res.to_csv(f"{TAB}/15_previsao_resumo.csv")
c1 = R_.drop_duplicates("corte"); print("por corte: células atingidas no período previsto e, delas, quantas não tinham acidente antes:"); display(c1[["corte", "previsto", "atingidas", "atingidas_sem_acidente_antes"]].T)
display(R_.pivot(index="corte", columns="metodo", values="auc_malha_inteira").round(3))
log_ia("15.2 janela móvel", "Claude", "FOCUS: sete cortes; ajuste no passado, previsão dos 3 anos seguintes; métricas na malha inteira e nos km sem acidente anterior", "15_previsao_*.csv", "gate de número de cortes; asserções de janelas disjuntas")
exportar_registros("15")''')
md(f"""---
## Limites

Os atributos da via são os da Declaração de Rede de 2025 em todos os cortes. O registro do RAAF mudou de arquivo em dezembro de 2020, o que pode alterar a cobertura entre períodos; a AUC, por ser de ordenação, é pouco sensível ao nível geral. O histórico só existe em malha em operação; para ferrovia nova vale o cenário B do notebook 14.

{DECLARACAO_IA}""")
nb = nbf.v4.new_notebook(); nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"}, "colab": {"name": "15_previsao_malha_em_operacao.ipynb"}}
nbf.write(nb, "15_previsao_malha_em_operacao.ipynb"); print("ok 15")
