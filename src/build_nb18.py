# -*- coding: utf-8 -*-
"""Gera notebooks/18_taxa_de_acerto_protocolo.ipynb: protocolo principal da taxa de acerto na malha existente (origem móvel), alarmes falsos, critérios e resolução."""
import nbformat as nbf
from nb_common import HEADER_RULE, SETUP_CODE, DECLARACAO_IA
cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s))
code = lambda s: cells.append(nbf.v4.new_code_cell(s))
md(f"""# 18 · Taxa de acerto na malha existente: protocolo principal, alarmes falsos, critérios e resolução

{HEADER_RULE}

**Pergunta do autor (16/11).** Como apurar, de forma estatisticamente defensável, a taxa de acerto do EAR calibrado na malha existente, se ela varia conforme o ano e a janela? E o que falta para aumentá-la, sem alarme falso?

**Protocolo principal (declarado antes dos resultados): origem móvel, para frente.** É o desenho de avaliação fora da amostra usado em previsão (Tashman, 2000) e a lógica dos testes de consistência entre períodos usados para comparar métodos de identificação de pontos críticos (Cheng e Washington, 2008). Para cada ano de origem T, o modelo é calibrado com os descarrilamentos de 2011 a T e conferido contra os descarrilamentos de T+1 a T+H. Horizonte principal H = 3 anos (origens de 2015 a 2022, oito conferências); sensibilidade com H = 1 e H = 5. O resultado é a média das origens, com a faixa e um intervalo de 95% por reamostragem de linhas inteiras.

**Duas medidas, porque respondem a perguntas diferentes.**

1. AUC: de cada 100 pares (um quilômetro com descarrilamento no período conferido, um sem), em quantos o quilômetro com descarrilamento recebeu a nota maior. Não depende de corte.
2. Taxa de acerto com corte de área (Chainey, Tompson e Uhlig, 2008): marcando os X% de quilômetros de maior nota, que percentual dos descarrilamentos do período conferido cai neles; e o índice de acurácia de previsão, que é essa taxa dividida por X. Reportada para X de 10, 20, 30, 40 e 50.

**Alarme falso.** Quilômetro marcado que não teve descarrilamento no horizonte. Como o evento é raro, a maior parte dos quilômetros marcados não terá evento em três anos, qualquer que seja o modelo; por isso o notebook reporta a concentração de risco (taxa nos marcados dividida pela taxa nos não marcados) e a repete só nos quilômetros que ainda não tinham descarrilamento até T.

**Métodos sob o mesmo protocolo.** Regra do EAR por faixas; Dummy da taxa da malha; critérios do EAR em medida contínua; EAR calibrado só com atributos da via; EAR calibrado mais histórico de acidentes da vizinhança, da linha e da malha (só possível em malha existente).

**Análises complementares, todas declaradas e todas reportadas.** (a) Grupos de critérios: o que cada grupo de atributos acrescenta aos critérios do EAR e o que se perde ao retirá-lo. (b) Resolução: a mesma conferência em blocos de 1, 2, 5 e 10 km, motivada pela incerteza de posição do RAAF (28% dos eventos em quilômetro inteiro). (c) Base americana (FRA): causas por tipo de via, para verificar se há critério não considerado.

**Gates.** 20.936 células; 2.681 descarrilamentos por via; janelas de calibração e de conferência disjuntas; oito origens no horizonte principal.""")
code(SETUP_CODE)
code(r'''import warnings; warnings.filterwarnings("ignore")
from scipy import sparse
from scipy.stats import rankdata
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
SEED = 42
C0 = pd.read_csv(f"{PROC}/11_celulas_1km.csv")
C = C0[~C0["sentido"].astype(str).str.contains("Interromp")].sort_values(["ferrovia", "linha", "km_a"]).reset_index(drop=True); gate("células em operação", len(C), 20936, source="notebook 11")
E = pd.read_csv(f"{PROC}/11_eventos_celulas.csv"); E = E[E["cel_id"].isin(C["cel_id"])].copy(); E["ano"] = E["ano"].astype(int); EV = E[E["via"]]
gate("descarrilamentos por via nas células", len(EV), 2681, source="notebook 11")
idx = pd.Series(np.arange(len(C)), index=C["cel_id"]); N = len(C)
def matriz(ev):
    M_ = np.zeros((15, N))
    for k in range(15):
        s = ev[ev["ano"] == 2011 + k].groupby("cel_id").size(); M_[k, idx[s.index].values] = s.values
    return M_
CV_, CA_ = matriz(EV), matriz(E)
def cont(M_, a0, a1): return M_[a0 - 2011:a1 - 2011 + 1].sum(0)
GR = {"distância a pátio e AMV (EAR)": (["dmin_patio", "dmin_amv", "frac_zona_patio"] + [f"f16p{j}" for j in range(5)] + [f"f16a{j}" for j in range(5)], []),
      "raio de curva (EAR)": (["rmin_geo"] + [f"fr_lt{l}" for l in (300, 400, 500, 600, 800)], []),
      "superestrutura: trilho, dormente, fixação": (["taxa_dorm"], ["dormente", "perfil_trilho", "fixacao"]),
      "tráfego: capacidade vinculada, dias, linhas": (["cap_vinc", "dias_op"], ["sentido", "n_linhas"]),
      "carga por eixo e velocidade": (["carga_eixo_t", "vma_carregado"], []),
      "rampa e raio declarados": (["rampa_max_pct", "raio_min_m"], []),
      "sinalização e controle": ([], ["sinalizacao", "controle_circ"]),
      "bitola e gabarito": (["gab_vert_m", "gab_horiz_m"], ["bitola"])}
for num, cat in GR.values():
    for c in num: C[c] = pd.to_numeric(C[c], errors="coerce")
    for c in cat: C[c] = C[c].astype(str).str.strip().replace({"nan": "NA", "": "NA"})
def design(grupos):
    num = [c for g in grupos for c in GR[g][0]]; cat = [c for g in grupos for c in GR[g][1]]; X = C[num].copy(); med = X.median().fillna(0.0)
    for c in num: X[c + "_na"] = X[c].isna().astype(float); X[c] = X[c].fillna(med[c])
    X = pd.concat([X, pd.get_dummies(C[cat], dtype=float)], axis=1) if cat else X; return StandardScaler().fit_transform(X.values)
TODOS = list(GR); EARG = TODOS[:2]; X0 = design(TODOS); XE = design(EARG)
LN = C["len_km"].values; FERC = pd.factorize(C["ferrovia"])[0]; LIN = np.asarray(C["ferrovia"] + "|" + C["linha"].astype(str), dtype=object); LINC = pd.factorize(LIN)[0]; SEG = np.asarray(C["seg_id"].astype(str), dtype=object); KM = ((C["km_a"] + C["km_b"]) / 2).values
ri, ci = [], []
for l in range(LINC.max() + 1):
    i = np.where(LINC == l)[0]; k = KM[i]; M_ = (np.abs(k[:, None] - k[None, :]) <= 20) & ~np.eye(len(i), dtype=bool); a, b = np.where(M_); ri.append(i[a]); ci.append(i[b])
W = sparse.csr_matrix((np.ones(sum(len(a) for a in ri)), (np.concatenate(ri), np.concatenate(ci))), shape=(N, N)); nviz = np.asarray(W.sum(1)).ravel()
def historico(T):
    """Histórico com dados de 2011 até T, por ano de observação. Nada posterior a T."""
    n = T - 2010; hv = cont(CV_, 2011, T); ha = cont(CA_, 2011, T); b = (hv > 0).astype(float); d = pd.DataFrame({"b": b, "hv": hv})
    H_ = np.column_stack([hv / n, ha / n, b, (W @ b) / np.maximum(nviz, 1), (W @ hv) / np.maximum(nviz, 1) / n, d.groupby(SEG)["b"].transform("mean").values, d.groupby(LINC)["b"].transform("mean").values, d.groupby(FERC)["b"].transform("mean").values, d.groupby(FERC)["hv"].transform("mean").values / n])
    return H_, b
def cls16(d): return np.select([d <= 300, d <= 600, d <= 1200, d <= 1800], [4, 3, 2, 1], 0)
def rcls16(r_): return np.select([r_ < 500, r_ < 1200, r_ < 2300], [3, 2, 1], 0)
B2 = (0.5 * cls16(C["dmin_patio"].fillna(1e9)) / 4 + 0.5 * rcls16(C["rmin_geo"].fillna(1e6)) / 3).astype(float)
def auc(yy, s):
    n1 = yy.sum(); n0_ = len(yy) - n1; return float((rankdata(s)[yy == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0_)) if n1 >= 5 and n0_ >= 5 else np.nan
def auc_dentro(s, yy, grp=FERC):
    a, w = [], []
    for f in np.unique(grp):
        i = grp == f
        if yy[i].sum() >= 5 and yy[i].sum() < i.sum(): a.append(auc(yy[i], s[i])); w.append(yy[i].sum())
    return float(np.average(a, weights=w)) if a else np.nan
DES = np.random.default_rng(SEED).random(N)
def ordem(s): return np.lexsort((DES, -s))
def lr(Xtr, ytr, Xte): return LogisticRegression(C=0.5, max_iter=3000).fit(Xtr, ytr).predict_proba(Xte)[:, 1]
def notas(T, H):
    """Notas de cada método com dados até T; resposta conferida de T+1 a T+H."""
    assert T + H <= 2025; ycal = (cont(CV_, 2011, T) > 0).astype(int); cconf = cont(CV_, T + 1, T + H); yconf = (cconf > 0).astype(int)
    Htr, _ = historico(T - H); Hte, ja = historico(T); ytr = (cont(CV_, T - H + 1, T) > 0).astype(int); st = StandardScaler().fit(Htr)
    taxa = pd.Series(ycal).groupby(FERC).transform("mean").values
    S = {"Regra do EAR por faixas": B2, "Dummy: taxa da malha até T": taxa, "Critérios do EAR em medida contínua": lr(XE, ycal, XE), "EAR calibrado (atributos da via)": lr(X0, ycal, X0),
         "EAR calibrado + histórico de acidentes": lr(np.column_stack([X0, st.transform(Htr)]), ytr, np.column_stack([X0, st.transform(Hte)]))}
    return S, yconf, cconf, ja == 0
CORTES = (0.10, 0.20, 0.30, 0.40, 0.50)
def medidas(s, yconf, cconf, novo):
    o = ordem(s); cum = np.cumsum(LN[o]) / LN.sum(); d = dict(auc=auc(yconf, s), auc_dentro=auc_dentro(s, yconf), auc_km_sem_acidente_ate_T=auc(yconf[novo], s[novo]))
    for p in CORTES:
        m = np.zeros(N, bool); m[o[cum <= p]] = True; d[f"acerto_{int(p*100)}"] = float(cconf[m].sum() / cconf.sum()); d[f"km_atingidos_{int(p*100)}"] = float(yconf[m].sum() / yconf.sum())
        if p == 0.20:
            d["alarme_falso_20"] = float(1 - yconf[m].mean()); d["concentracao_20"] = float(yconf[m].mean() / yconf[~m].mean())
            a, b = yconf[m & novo].mean(), yconf[~m & novo].mean(); d["taxa_marcados_sem_acidente_ate_T"] = float(a); d["taxa_nao_marcados_sem_acidente_ate_T"] = float(b); d["concentracao_20_sem_acidente_ate_T"] = float(a / b)
    return d
log_ia("18.1 dados e funções", "Claude", "FOCUS: origem móvel para frente; AUC e taxa de acerto com corte de área; alarme falso e concentração de risco", "notas(T, H), medidas()", "2 gates de contagem")''')
code(r'''# 1. Protocolo principal e sensibilidade ao horizonte
L, GUARDA = [], {}
for H in (3, 1, 5):
    for T in range(2015, 2026 - H):
        if T - H < 2012: continue
        S, yconf, cconf, novo = notas(T, H); GUARDA[(H, T)] = (S, yconf, cconf, novo)
        for nome, s in S.items(): L.append(dict(horizonte=H, origem=T, calibra=f"2011 a {T}", confere=f"{T+1} a {T+H}", metodo=nome, km_com_descarrilamento=int(yconf.sum()), deles_sem_acidente_ate_T=int(yconf[novo].sum()), **medidas(s, yconf, cconf, novo)))
    print("horizonte", H, "ok", flush=True)
R = pd.DataFrame(L); R.to_csv(f"{TAB}/18_origem_movel_por_origem.csv", index=False)
gate("origens no horizonte principal (3 anos)", int(R[R.horizonte == 3]["origem"].nunique()), 8, source="desenho: T de 2015 a 2022")
P = R[R.horizonte == 3]; COL = ["auc", "auc_dentro", "auc_km_sem_acidente_ate_T", "acerto_10", "acerto_20", "acerto_30", "acerto_40", "acerto_50", "alarme_falso_20", "concentracao_20", "concentracao_20_sem_acidente_ate_T"]
print("== PROTOCOLO PRINCIPAL: horizonte de 3 anos, 8 origens =="); p1 = P.groupby("metodo", sort=False)[COL].agg(["mean", "min", "max"]).round(3); display(p1.T)
print("== Por origem (AUC na malha inteira) =="); display(P.pivot(index="confere", columns="metodo", values="auc").round(3))
print("== Sensibilidade ao horizonte (média das origens) =="); display(R.groupby(["horizonte", "metodo"], sort=False)[["auc", "auc_dentro", "acerto_20", "acerto_40", "concentracao_20"]].mean().round(3))
# intervalo de 95% por reamostragem de linhas inteiras (notas fixas; 300 reamostragens)
rng = np.random.default_rng(SEED); cel_lin = [np.where(LINC == l)[0] for l in range(LINC.max() + 1)]; B = {m: [] for m in P.metodo.unique()}; Dif = []
for b in range(300):
    ii = np.concatenate([cel_lin[l] for l in rng.integers(0, len(cel_lin), len(cel_lin))]); v = {m: [] for m in B}
    for T in range(2015, 2023):
        S, yconf, _, _ = GUARDA[(3, T)]
        for m in B: v[m].append(auc(yconf[ii], S[m][ii]))
    for m in B: B[m].append(np.nanmean(v[m]))
    Dif.append(B["EAR calibrado (atributos da via)"][-1] - B["Regra do EAR por faixas"][-1])
ic = pd.DataFrame({m: dict(media=P[P.metodo == m]["auc"].mean(), ic95_inf=np.percentile(B[m], 2.5), ic95_sup=np.percentile(B[m], 97.5)) for m in B}).T.round(3); display(ic); ic.to_csv(f"{TAB}/18_ic95_auc.csv")
print("EAR calibrado menos regra: IC 95% de", round(np.percentile(Dif, 2.5), 3), "a", round(np.percentile(Dif, 97.5), 3))
p1.to_csv(f"{TAB}/18_protocolo_principal.csv")
log_ia("18.2 protocolo principal", "Claude", "FOCUS: 8 origens, horizonte de 3 anos; sensibilidade 1 e 5 anos; IC por reamostragem de linhas", "18_origem_movel_por_origem.csv, 18_protocolo_principal.csv, 18_ic95_auc.csv", "gate de número de origens")''')
code(r'''# 2. Grupos de critérios: o que cada um acrescenta aos critérios do EAR e o que se perde ao retirá-lo (horizonte de 3 anos, 8 origens)
def roda(grupos):
    Xg = design(grupos); a, d = [], []
    for T in range(2015, 2023):
        ycal = (cont(CV_, 2011, T) > 0).astype(int); yconf = (cont(CV_, T + 1, T + 3) > 0).astype(int); s = lr(Xg, ycal, Xg); a.append(auc(yconf, s)); d.append(auc_dentro(s, yconf))
    return float(np.mean(a)), float(np.mean(d))
L = [dict(configuracao="só critérios do EAR (pátio e AMV, raio)", **dict(zip(("auc", "auc_dentro"), roda(EARG)))), dict(configuracao="todos os grupos", **dict(zip(("auc", "auc_dentro"), roda(TODOS))))]
for g in TODOS[2:]: L.append(dict(configuracao="critérios do EAR + " + g, **dict(zip(("auc", "auc_dentro"), roda(EARG + [g])))))
for g in TODOS: L.append(dict(configuracao="todos menos " + g, **dict(zip(("auc", "auc_dentro"), roda([x for x in TODOS if x != g])))))
G = pd.DataFrame(L).round(3); G.to_csv(f"{TAB}/18_grupos_de_criterios.csv", index=False); display(G)
log_ia("18.3 grupos de critérios", "Claude", "FOCUS: acréscimo e retirada de um grupo por vez, mesmo protocolo", "18_grupos_de_criterios.csv", "comparação com a linha 'todos os grupos' da seção 1")''')
code(r'''# 3. Resolução: a mesma conferência em blocos de 1, 2, 5 e 10 km (horizonte de 3 anos, 8 origens)
pos = pd.Series(KM).groupby(LINC).rank(method="first").values.astype(int) - 1; L = []
for r in (1, 2, 5, 10):
    blk = pd.factorize(pd.Series(LINC).astype(str) + "_" + pd.Series(pos // r).astype(str))[0]; fb = pd.Series(FERC).groupby(blk).first().values
    for T in range(2015, 2023):
        S, yconf, _, _ = GUARDA[(3, T)]; yb = pd.Series(yconf).groupby(blk).max().values
        for m, s in S.items():
            sb = pd.Series(s).groupby(blk).max().values if m.startswith(("Regra", "Dummy")) else 1 - np.exp(pd.Series(np.log1p(-np.clip(s, 0, 1 - 1e-9))).groupby(blk).sum().values)
            L.append(dict(bloco_km=r, origem=T, metodo=m, blocos=len(yb), blocos_com_descarrilamento=int(yb.sum()), auc=auc(yb, sb), auc_dentro=auc_dentro(sb, yb, fb)))
RS = pd.DataFrame(L); RS.to_csv(f"{TAB}/18_resolucao.csv", index=False); display(RS.groupby(["bloco_km", "metodo"], sort=False)[["blocos", "blocos_com_descarrilamento", "auc", "auc_dentro"]].mean().round(3))
log_ia("18.4 resolução", "Claude", "FOCUS: agregação das notas por bloco (probabilidade de ao menos um evento); regra e Dummy pelo máximo", "18_resolucao.csv", "bloco de 1 km reproduz a seção 1")''')
code(r'''# 4. Base americana (FRA, descarrilamentos por via de 2006 a 2026): causas por tipo de via, para checar critérios
F_ = pd.read_csv(f"{PROC}/fra_desc_via_2006_2026.csv"); print("narrativas:", len(F_))
t = pd.crosstab(F_["Track Type"].fillna("NA"), F_["familia"]); t["total"] = t.sum(1); t = t.sort_values("total", ascending=False); display(t); display((t.div(t["total"], axis=0) * 100).round(1))
display((F_["Primary Accident Cause"].value_counts().head(15) / len(F_) * 100).round(1).to_frame("% dos descarrilamentos por via"))
t.to_csv(f"{TAB}/18_fra_tipo_de_via_por_familia.csv"); F_["Primary Accident Cause"].value_counts().head(25).to_csv(f"{TAB}/18_fra_causas_mais_frequentes.csv")
log_ia("18.5 base americana", "Claude", "FOCUS: tabela descritiva; sem modelo", "18_fra_*.csv", "total de narrativas confere com o notebook 04")
exportar_registros("18")''')
md(f"""---
## Referências do protocolo (situação da verificação em 16/11/2026)

Chainey, S., Tompson, L., & Uhlig, S. (2008). The utility of hotspot mapping for predicting spatial patterns of crime. *Security Journal, 21*(1). Texto lido (definição da taxa de acerto e do índice de acurácia de previsão; desenho com várias janelas de passado e de futuro). Páginas: a confirmar.

Cheng, W., & Washington, S. (2008). New criteria for evaluating methods of identifying hot spots. *Transportation Research Record, 2083*, 76–85. https://doi.org/10.3141/2083-09. Resumo lido.

Tashman, L. J. (2000). Out-of-sample tests of forecasting accuracy: an analysis and review. *International Journal of Forecasting, 16*(4), 437–450. Registro bibliográfico confirmado; resumo a ler antes de citar no artigo.

## Limites

Os atributos da via são os da Declaração de Rede de 2025 em todas as origens. As origens se sobrepõem no tempo e não são independentes; o intervalo por reamostragem de linhas trata a dependência espacial, não a temporal. O alarme falso em horizonte de três anos superestima o erro real, porque um quilômetro marcado pode vir a ter descarrilamento depois do horizonte.

{DECLARACAO_IA}""")
nb = nbf.v4.new_notebook(); nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"}, "colab": {"name": "18_taxa_de_acerto_protocolo.ipynb"}}
nbf.write(nb, "18_taxa_de_acerto_protocolo.ipynb"); print("ok 18")
