# -*- coding: utf-8 -*-
"""Gera notebooks/17_grade_de_janelas.ipynb: grade de janelas de calibração e de conferência na malha existente, para frente e para trás."""
import nbformat as nbf
from nb_common import HEADER_RULE, SETUP_CODE, DECLARACAO_IA
cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s))
code = lambda s: cells.append(nbf.v4.new_code_cell(s))
md(f"""# 17 · Malha existente: grade de janelas de calibração e de conferência

{HEADER_RULE}

**Pedido do autor (16/11).** Varrer janelas de 1, 2, 5 e 10 anos, do início, do meio e do fim do período, para frente e para trás, e ver em que cenário o EAR calibrado identifica melhor os quilômetros que tiveram descarrilamento por via. Sempre na malha existente, onde o acidente real permite conferir.

**Desenho (declarado antes dos resultados).**

1. Janelas adjacentes: calibração de 1, 2, 5 ou 10 anos; conferência de 1, 2 ou 5 anos imediatamente depois (para frente) ou imediatamente antes (para trás); todas as posições possíveis entre 2011 e 2025.
2. Todos os anos disponíveis: calibração com todos os anos anteriores (mínimo de 3) e conferência nos 1, 2 ou 5 anos seguintes; e o espelho para trás.
3. Com defasagem: calibração com todos os anos anteriores e conferência em um único ano, 3 ou 5 anos depois do fim da calibração; e o espelho para trás.

Em todos: nota só com atributos da via (regressão logística do notebook 16, hiperparâmetros fixos); duas conferências (mesmos km; km fora da calibração, por grupos de trecho); regra do EAR por faixas como baseline na mesma conferência. Todos os cenários são reportados; o melhor cenário é descrito, não escolhido como resultado principal.

**Gates.** 2.681 descarrilamentos por via; janelas disjuntas em todos os cenários; teste de vazamento pela média de 20 embaralhamentos entre 0,45 e 0,55.""")
code(SETUP_CODE)
code(r'''import warnings; warnings.filterwarnings("ignore")
from scipy.stats import rankdata
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from joblib import Parallel, delayed
SEED = 42
C0 = pd.read_csv(f"{PROC}/11_celulas_1km.csv")
C = C0[~C0["sentido"].astype(str).str.contains("Interromp")].sort_values(["ferrovia", "linha", "km_a"]).reset_index(drop=True); gate("células em operação", len(C), 20936, source="notebook 11")
E = pd.read_csv(f"{PROC}/11_eventos_celulas.csv"); E = E[E["cel_id"].isin(C["cel_id"])].copy(); E["ano"] = E["ano"].astype(int); EV = E[E["via"]]
gate("descarrilamentos por via nas células", len(EV), 2681, source="notebook 11")
idx = pd.Series(np.arange(len(C)), index=C["cel_id"]); ANOS = list(range(2011, 2026))
CA = np.zeros((len(ANOS), len(C)))
for k, a in enumerate(ANOS):
    s = EV[EV["ano"] == a].groupby("cel_id").size(); CA[k, idx[s.index].values] = s.values
gate("soma da matriz ano x célula", int(CA.sum()), 2681, source="partição por ano")
def contagem(a0, a1): return CA[a0 - 2011:a1 - 2011 + 1].sum(0)
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
X = StandardScaler().fit_transform(design(C, DIST + CURV + NUM, CAT))  # padronização só usa atributos, nunca a resposta
LN = C["len_km"].values; fer = np.asarray(C["ferrovia"], dtype=object); FERC = pd.factorize(C["ferrovia"])[0]; SEGC = pd.factorize(C["seg_id"].astype(str))[0]; NSEG = SEGC.max() + 1
FOLD = np.random.default_rng(SEED).permutation(NSEG)[SEGC] % 5; DES = np.random.default_rng(SEED).random(len(C))
def cls16(d): return np.select([d <= 300, d <= 600, d <= 1200, d <= 1800], [4, 3, 2, 1], 0)
def rcls16(r_): return np.select([r_ < 500, r_ < 1200, r_ < 2300], [3, 2, 1], 0)
B2 = (0.5 * cls16(C["dmin_patio"].fillna(1e9)) / 4 + 0.5 * rcls16(C["rmin_geo"].fillna(1e6)) / 3).astype(float)
def auc(yy, s):
    n1 = yy.sum(); n0_ = len(yy) - n1; return float((rankdata(s)[yy == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0_)) if n1 >= 5 and n0_ >= 5 else np.nan
def auc_dentro(s, yy):
    a, w = [], []
    for f in range(FERC.max() + 1):
        i = FERC == f
        if yy[i].sum() >= 5 and yy[i].sum() < i.sum(): a.append(auc(yy[i], s[i])); w.append(yy[i].sum())
    return float(np.average(a, weights=w)) if a else np.nan
def captura(s, evv, p=0.20):
    o = np.lexsort((DES, -s)); cum = np.cumsum(LN[o]) / LN.sum(); return float(evv[o][cum <= p].sum() / evv.sum())
def lr(Xtr, ytr, Xte): return LogisticRegression(C=0.5, max_iter=3000).fit(Xtr, ytr).predict_proba(Xte)[:, 1]
def cenario(tipo, cal, conf, embaralhar=None):
    assert cal[1] < conf[0] or conf[1] < cal[0], "janelas sobrepostas"
    ycal = (contagem(*cal) > 0).astype(int); cconf = contagem(*conf); yconf = (cconf > 0).astype(int)
    if ycal.sum() < 20 or yconf.sum() < 20: return []
    if embaralhar is not None: ycal = np.random.default_rng(1000 + embaralhar).permutation(ycal)
    base = dict(tipo=tipo, cal_ini=cal[0], cal_fim=cal[1], conf_ini=conf[0], conf_fim=conf[1], anos_calibracao=cal[1] - cal[0] + 1, anos_conferencia=conf[1] - conf[0] + 1, sentido="para frente" if cal[1] < conf[0] else "para trás",
                defasagem=(conf[0] - cal[1] - 1) if cal[1] < conf[0] else (cal[0] - conf[1] - 1), km_com_acidente_calibracao=int(ycal.sum()), km_com_acidente_conferido=int(yconf.sum()))
    def linha(nome, conferencia, s): return dict(base, metodo=nome, conferencia=conferencia, auc=auc(yconf, s), auc_dentro=auc_dentro(s, yconf), captura20=captura(s, cconf))
    s1 = lr(X, ycal, X); s2 = np.zeros(len(C))
    for k in range(5): te = FOLD == k; s2[te] = lr(X[~te], ycal[~te], X[te])
    return [linha("Regra do EAR por faixas", "mesmos km", B2), linha("Regra do EAR por faixas", "km fora da calibração", B2), linha("EAR calibrado (atributos da via)", "mesmos km", s1), linha("EAR calibrado (atributos da via)", "km fora da calibração", s2)]
J = []
for L_ in (1, 2, 5, 10):
    for M_ in (1, 2, 5):
        for a in range(2011, 2026 - L_ - M_ + 1): J.append(("janelas adjacentes", (a, a + L_ - 1), (a + L_, a + L_ + M_ - 1)))
        for a in range(2011 + M_, 2026 - L_ + 1): J.append(("janelas adjacentes", (a, a + L_ - 1), (a - M_, a - 1)))
for M_ in (1, 2, 5):
    for T in range(2014, 2026 - M_ + 1): J.append(("todos os anos disponíveis", (2011, T - 1), (T, T + M_ - 1)))
    for T in range(2010 + M_, 2023): J.append(("todos os anos disponíveis", (T + 1, 2025), (T - M_ + 1, T)))
for g in (3, 5):
    for T in range(2014, 2026 - g + 1): J.append(("com defasagem", (2011, T - 1), (T + g - 1, T + g - 1)))
    for T in range(2010 + g, 2023): J.append(("com defasagem", (T + 1, 2025), (T - g + 1, T - g + 1)))
print("cenários declarados:", len(J)); gate_between("número de cenários", float(len(J)), 250, 400, source="desenho")
log_ia("17.1 grade declarada", "Claude", "FOCUS: grade de janelas adjacentes, todos os anos e defasagem; para frente e para trás; só atributos da via", "lista J", "3 gates de contagem; gate do número de cenários")''')
code(r'''import time; t0 = time.time()
OUT = Parallel(n_jobs=2, batch_size=4)(delayed(cenario)(*j) for j in J); R = pd.DataFrame([l for o in OUT for l in o]); print("minutos:", round((time.time() - t0) / 60, 1), "| linhas:", len(R), "| cenários avaliados:", len(R) // 4)
R.to_csv(f"{TAB}/17_grade_por_cenario.csv", index=False)
vz = [cenario("vazamento", (2011, 2015), (2021, 2025), embaralhar=k) for k in range(20)]; vzm = pd.Series([l["auc"] for o in vz for l in o if l["metodo"].startswith("EAR calibrado") and l["conferencia"] == "km fora da calibração"])
print("vazamento: média", round(vzm.mean(), 3), "| mínimo", round(vzm.min(), 3), "| máximo", round(vzm.max(), 3)); gate_between("teste de vazamento (média de 20 embaralhamentos)", float(vzm.mean()), 0.45, 0.55, source="acaso")
M = ["auc", "auc_dentro", "captura20"]
print("== Geral: todos os cenários =="); g0 = R.groupby(["metodo", "conferencia"], sort=False)[M].agg(["mean", "min", "max"]).round(3); display(g0)
print("== Por tipo e sentido =="); g1 = R.groupby(["tipo", "sentido", "metodo", "conferencia"], sort=False)[M].mean().round(3); g1["n"] = R.groupby(["tipo", "sentido", "metodo", "conferencia"], sort=False).size(); display(g1)
A = R[(R.tipo == "janelas adjacentes") & (R.metodo.str.startswith("EAR calibrado"))]
print("== Janelas adjacentes: AUC por anos de calibração (linhas) e de conferência (colunas) ==")
for conf in ("mesmos km", "km fora da calibração"):
    for sen in ("para frente", "para trás"): print(conf, "|", sen); display(A[(A.conferencia == conf) & (A.sentido == sen)].pivot_table(index="anos_calibracao", columns="anos_conferencia", values="auc").round(3))
print("== AUC por ano final da janela conferida (para frente, km fora da calibração) =="); display(R[(R.sentido == "para frente") & (R.conferencia == "km fora da calibração")].pivot_table(index="conf_fim", columns="metodo", values="auc").round(3))
res = R.groupby(["tipo", "sentido", "anos_calibracao", "anos_conferencia", "defasagem", "metodo", "conferencia"], sort=False)[M].agg(["mean", "min", "max", "count"]).round(3); res.to_csv(f"{TAB}/17_grade_resumo.csv")
gan = R.pivot_table(index=["tipo", "cal_ini", "cal_fim", "conf_ini", "conf_fim", "conferencia"], columns="metodo", values="auc"); d = gan["EAR calibrado (atributos da via)"] - gan["Regra do EAR por faixas"]
print("EAR calibrado acima da regra por faixas em", int((d > 0).sum()), "de", len(d), "comparações; diferença média", round(d.mean(), 3), "| mínima", round(d.min(), 3), "| máxima", round(d.max(), 3))
top = R[R.metodo.str.startswith("EAR calibrado") & (R.conferencia == "km fora da calibração")].sort_values("auc", ascending=False); print("== Dez melhores e dez piores cenários (km fora da calibração) =="); display(top.head(10)[["tipo", "cal_ini", "cal_fim", "conf_ini", "conf_fim", "km_com_acidente_conferido", "auc", "auc_dentro", "captura20"]]); display(top.tail(10)[["tipo", "cal_ini", "cal_fim", "conf_ini", "conf_fim", "km_com_acidente_conferido", "auc", "auc_dentro", "captura20"]])
log_ia("17.2 grade executada", "Claude", "FOCUS: todos os cenários reportados; melhor cenário descrito, não escolhido como resultado principal", "17_grade_*.csv", "gate de vazamento por média de 20 embaralhamentos")
exportar_registros("17")''')
md(f"""---
## Limites

Os atributos da via são os da Declaração de Rede de 2025 em todas as janelas. Cenários com janelas curtas têm poucos quilômetros com descarrilamento e oscilam mais; foram descartados os cenários com menos de 20 quilômetros atingidos na calibração ou na conferência. Os cenários se sobrepõem no tempo e não são independentes entre si: a média resume a grade, não é um intervalo de confiança.

{DECLARACAO_IA}""")
nb = nbf.v4.new_notebook(); nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"}, "colab": {"name": "17_grade_de_janelas.ipynb"}}
nbf.write(nb, "17_grade_de_janelas.ipynb"); print("ok 17")
