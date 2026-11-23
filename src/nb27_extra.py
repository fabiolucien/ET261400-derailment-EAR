
from itertools import combinations
import matplotlib.patheffects as pe

# 1. Parâmetros dos dois EAR, transcritos dos estudos públicos (texto conferido em 22/11/2026; ENEFER, 2015 e 2016)
L_TREM = 1690.0      # trem-tipo do EAR da FNS: "comprimento do trem tipo ... com 1690m", premissa declarada para as distâncias das faixas
PAR = pd.DataFrame([
    dict(estudo="EAR FNS (ENEFER, 2015)", criterio="Distância a AMV, OAE e passagem em nível", muito_alto="até 200 m", alto="200 a 400 m", moderado="400 a 800 m", baixo="800 a 1.600 m", fora="acima de 1.600 m",
         premissa="trem-tipo de 1.690 m; a faixa externa (1.600 m) corresponde a um comprimento de trem"),
    dict(estudo="EAR FNS (ENEFER, 2015)", criterio="Raio de curva", muito_alto="abaixo de 500 m", alto="500 a 800 m", moderado="800 a 1.200 m", baixo="acima de 1.200 m", fora="", premissa="curvas de menor raio e maior superelevação"),
    dict(estudo="EAR FICO (ENEFER, 2016)", criterio="Distância a AMV, OAE e passagem em nível", muito_alto="até 300 m", alto="300 a 600 m", moderado="600 a 1.200 m", baixo="1.200 a 1.800 m", fora="acima de 1.800 m",
         premissa="até 19 vagões de carga perigosa (cerca de 300 m) na frente do trem"),
    dict(estudo="EAR FICO (ENEFER, 2016)", criterio="Raio de curva", muito_alto="abaixo de 500 m", alto="500 a 1.200 m", moderado="1.200 a 2.300 m", baixo="acima de 2.300 m", fora="",
         premissa="superelevação só até o raio de 2.291,838 m (especificação de projeto geométrico da VALEC)"),
])
display(PAR); PAR.to_csv(f"{TAB}/27_parametros_ear_fns_fico.csv", index=False)
def faixas_p(d, c): return np.select([d <= c[0], d <= c[1], d <= c[2], d <= c[3]], [4, 3, 2, 1], 0)
def classes_r(r, c): return np.select([r < c[0], r < c[1], r < c[2]], [3, 2, 1], 0)
FICO_P, FICO_R, FNS_P, FNS_R = (300, 600, 1200, 1800), (500, 1200, 2300), (200, 400, 800, 1600), (500, 800, 1200)
def regra(cp, cr, w=0.5): return w * faixas_p(dp, cp) / 4 + (1 - w) * classes_r(rg, cr) / 3
S_FICO, S_FNS = regra(FICO_P, FICO_R), regra(FNS_P, FNS_R)
gate("regra FICO reconstruída igual à regra do EAR (B2)", float(np.abs(S_FICO - B2).max()), 0.0, tol=1e-12, source="notebook 11")
log_ia("27.1 parâmetros", "Claude", "FOCUS: transcrever as faixas dos dois EAR públicos e reconstruir as duas regras", "27_parametros_ear_fns_fico.csv", "regra FICO idêntica à B2")

# 2. Perfil brasileiro: risco relativo por classe de distância ao pátio e de raio, dentro de cada malha (Mantel-Haenszel),
#    com IC 95% por reamostragem de linhas inteiras. A posição do acidente vem do km do RAAF: a resolução é a célula de 1 km.
LIM_P = [250, 1000, 1500, 2000, 3000, 5000, 20000]
ROT_P = ["pátio na célula", "até 1 km", "1 a 1,5 km", "1,5 a 2 km", "2 a 3 km", "3 a 5 km", "5 a 20 km", "acima de 20 km"]; REF_P = 6
LIM_R = [300, 400, 500, 800, 1200, 2300]
ROT_R = ["até 300 m", "300 a 400 m", "400 a 500 m", "500 a 800 m", "800 a 1.200 m", "1.200 a 2.300 m", "acima de 2.300 m e tangente"]; REF_R = 6
KP_ = np.digitize(dp, LIM_P, right=True); KR_ = np.digitize(rg, LIM_R, right=True)
NL = LINC.max() + 1
def rr_mh(cls, K, ref, yy, w):
    nf = FERC.max() + 1; j = FERC * K + cls
    n_ = np.bincount(j, weights=w, minlength=nf * K).reshape(nf, K); a_ = np.bincount(j, weights=w * yy, minlength=nf * K).reshape(nf, K); out = np.full(K, np.nan)
    for k in range(K):
        T_ = n_[:, k] + n_[:, ref]; ok = T_ > 0; num = (a_[ok, k] * n_[ok, ref] / T_[ok]).sum(); den = (a_[ok, ref] * n_[ok, k] / T_[ok]).sum(); out[k] = num / den if den > 0 else np.nan
    return out
def perfil(cls, K, ref, rot):
    rr = rr_mh(cls, K, ref, y, np.ones(N)); rng_ = np.random.default_rng(SEED); B_ = []
    for b in range(300):
        B_.append(rr_mh(cls, K, ref, y, np.bincount(rng_.choice(NL, NL), minlength=NL)[LINC].astype(float)))
    B_ = np.array(B_)
    return pd.DataFrame(dict(classe=rot, celulas=np.bincount(cls, minlength=K), km_com_descarrilamento=np.bincount(cls, weights=y, minlength=K).astype(int),
                             taxa_nacional=np.bincount(cls, weights=y, minlength=K) / np.bincount(cls, minlength=K), rr_dentro_malhas=rr,
                             ic_inf=np.nanpercentile(B_, 2.5, axis=0), ic_sup=np.nanpercentile(B_, 97.5, axis=0)))
PP, PR = perfil(KP_, 8, REF_P, ROT_P), perfil(KR_, 7, REF_R, ROT_R)
display(PP.round(3)); display(PR.round(3)); PP.to_csv(f"{TAB}/27_perfil_distancia_patio.csv", index=False); PR.to_csv(f"{TAB}/27_perfil_raio.csv", index=False)
gate("perfil por distância: células somam a malha em operação", int(PP["celulas"].sum()), N, source="notebook 11")
gate("perfil por distância: quilômetros com descarrilamento somam 2.123", int(PP["km_com_descarrilamento"].sum()), 2123, source="notebook 11")
gate("perfil por raio: células somam a malha em operação", int(PR["celulas"].sum()), N, source="notebook 11")
gate("classe de referência com risco relativo 1", float(PP.loc[REF_P, "rr_dentro_malhas"]), 1.0, tol=1e-12, source="definição")
log_ia("27.2 perfil brasileiro", "Claude", "FOCUS: risco relativo dentro das malhas (Mantel-Haenszel), IC por linhas", "27_perfil_distancia_patio.csv, 27_perfil_raio.csv", "somas e referência")

# 3. Extensão física do descarrilamento nos EUA (FRA, Form 54): quantos veículos descarrilam, como fração do trem.
#    Filtro declarado: tipo 01 (descarrilamento), causa principal de via (código T), trem de carga, 2006 a 2025.
RAW_FRA = f"{RAW}/Rail_Equipment_Accident_Incident_Data_(Form_54)_Subset_–_Unique_Train_Accidents_(Not_at_Grade_Crossings)_20260918.csv"
ARQ_FRA = f"{PROC}/fra54_desc_via_carga_2006_2025.csv.gz"
LOC_ = ["Head End Locomotives", "Mid Train Manual Locomotives", "Mid Train Remote Locomotives", "Rear End Manual Locomotives", "Rear End Remote Locomotives"]
if os.path.exists(RAW_FRA):                                   # refaz o recorte a partir do arquivo bruto da FRA, quando ele estiver na pasta data/raw
    cols_ = ["Year", "Accident Type Code", "Hazmat Cars", "Hazmat Released Cars", "Track Type", "Track Class", "Track Density", "Equipment Type", "Train Speed", "First Car Position"] + LOC_ + ["Derailed " + c for c in LOC_] + \
            ["Loaded Freight Cars", "Empty Freight Cars", "Derailed Loaded Freight Cars", "Derailed Empty Freight Cars", "Primary Accident Cause Code", "Primary Accident Cause"]
    F0 = pd.read_csv(RAW_FRA, usecols=cols_, low_memory=False)
    F0 = F0[(F0["Accident Type Code"] == 1) & F0["Primary Accident Cause Code"].astype(str).str.startswith("T") & (F0["Equipment Type"] == "Freight Train") & F0["Year"].between(2006, 2025)].copy()
    for c in cols_:
        if c not in ("Track Type", "Track Class", "Equipment Type", "Primary Accident Cause Code", "Primary Accident Cause"): F0[c] = pd.to_numeric(F0[c], errors="coerce")
    F0["carros"] = F0["Loaded Freight Cars"].fillna(0) + F0["Empty Freight Cars"].fillna(0); F0["locos"] = F0[LOC_].fillna(0).sum(axis=1)
    F0["der_carros"] = F0["Derailed Loaded Freight Cars"].fillna(0) + F0["Derailed Empty Freight Cars"].fillna(0); F0["der_locos"] = F0[["Derailed " + c for c in LOC_]].fillna(0).sum(axis=1)
    F0["veic"] = F0["carros"] + F0["locos"]; F0["der"] = F0["der_carros"] + F0["der_locos"]; F0.to_csv(ARQ_FRA, index=False)
FR = pd.read_csv(ARQ_FRA, low_memory=False)
gate("descarrilamentos de trens de carga com causa de via, EUA, 2006 a 2025", len(FR), 6606, source="FRA Form 54, recorte declarado")
FM = FR[(FR["Track Type"] == "Main") & (FR["carros"] >= 10) & (FR["der"] >= 1)].copy()
gate("os mesmos na via principal, trens com 10 vagões ou mais", len(FM), 2772, source="FRA Form 54, recorte declarado")
FM["fracao"] = FM["der"] / FM["veic"]; FM["aparelho"] = FM["Primary Accident Cause Code"].astype(str).str.startswith("T3"); FM["pos_rel"] = FM["First Car Position"] / FM["veic"]
QS = [0.5, 0.75, 0.9, 0.95, 0.99]; LF = []
for nome, g in [("todas as causas de via", FM), ("aparelhos de mudança de via e chaves (T3xx)", FM[FM["aparelho"]])]:
    for q in QS:
        LF.append(dict(grupo=nome, n=len(g), quantil=q, veiculos_descarrilados=float(g["der"].quantile(q)), fracao_do_trem=float(g["fracao"].quantile(q)), metros_no_trem_tipo_FNS=float(g["fracao"].quantile(q) * L_TREM)))
FQ = pd.DataFrame(LF); display(FQ.round(3)); FQ.to_csv(f"{TAB}/27_fra_extensao_descarrilamento.csv", index=False)
POS = dict(mediana_posicao_relativa=float(FM["pos_rel"].median()), primeiro_quinto=float((FM["pos_rel"] <= 0.2).mean()), mediana_vagoes_no_trem=float(FM["carros"].median()), velocidade_mediana_mph=float(FM["Train Speed"].median()))
print(POS)
gate_between("fração descarrilada mediana entre 0 e 1", float(FM["fracao"].median()), 0.0, 1.0, source="definição")
log_ia("27.3 extensão física (EUA)", "Claude", "FOCUS: veículos descarrilados como fração do trem, convertidos para o trem-tipo de 1.690 m", "27_fra_extensao_descarrilamento.csv", "contagens do recorte")

# 4. Recalibração aninhada: as faixas e o peso do EAR escolhidos só nos grupos de ajuste, nos mesmos 30 sorteios (trechos inteiros fora).
#    Critério declarado antes de rodar: maior AUC dentro das malhas nos grupos de ajuste (o EAR é aplicado dentro de uma ferrovia).
#    Restrição acrescentada em U depois da primeira execução (regra do gate loop): a faixa externa não passa de cerca de dois trens-tipo (3.000 m < 2 × 1.690 m).
#    Sem ela, a busca escolheu o limite superior da grade (5 km) em todos os ajustes: as células a mais de 20 km de um pátio estão em trechos
#    longos de linhas com pouco ou nenhum tráfego (FTL, RMO, RMS, RMC), e a distância passa a medir o uso da linha, não a proximidade do AMV. O item 4b registra essa variante.
GP = [250, 500, 1000, 1500, 2000, 2500, 3000]; CPS = list(combinations(GP, 4))
GR = [250, 300, 400, 500, 600, 800, 1200, 2300]; CRS = list(combinations(GR, 3)); WG = [0.3, 0.4, 0.5, 0.6, 0.7]
AP = np.array([faixas_p(dp, c) for c in CPS], dtype=np.int8); AR = np.array([classes_r(rg, c) for c in CRS], dtype=np.int8)
gate("grade de faixas de pátio: combinações de 4 limites em 7 valores", len(CPS), 35, source="combinatória")
def auc_malha_idx(s, gi):
    a_, w_ = [], []
    for i_, yy in gi:
        n1 = yy.sum(); n0 = len(yy) - n1; r_ = rankdata(s[i_]); a_.append((r_[yy == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)); w_.append(n1)
    return float(np.average(a_, weights=w_))
def grupos(mask, yy):
    out = []
    for f in range(FERC.max() + 1):
        i_ = np.where(mask & (FERC == f))[0]
        if 5 <= yy[i_].sum() < len(i_): out.append((i_, yy[i_]))
    return out
def calibra(tr, yy):
    gi = grupos(tr, yy)
    jp = int(np.argmax([auc_malha_idx(AP[j].astype(float), gi) for j in range(len(CPS))]))
    jr = int(np.argmax([auc_malha_idx(AR[j].astype(float), gi) for j in range(len(CRS))]))
    w = WG[int(np.argmax([auc_malha_idx(w_ * AP[jp] / 4 + (1 - w_) * AR[jr] / 3, gi) for w_ in WG]))]
    return jp, jr, w
# Critérios adicionais da EAR v2, todos conhecidos no projeto de uma ferrovia nova (Declaração de Rede de 2025 na malha existente)
def quartis(c):
    v = pd.to_numeric(C[c], errors="coerce"); q = pd.qcut(v, 4, labels=False, duplicates="drop"); return np.array(["sem dado" if np.isnan(x) else f"Q{int(x) + 1}" for x in q.values])
PERF = C["perfil_trilho"].astype(str).str.extract(r"(\d+)")[0].astype(float).values
CLS_V2 = {"rampa": quartis("rampa_max_pct"), "carga_eixo": quartis("carga_eixo_t"), "trafego": quartis("tremkm_ano"), "velocidade": quartis("vma_carregado"),
          "dormente": np.array([str(x) if isinstance(x, str) else "NA" for x in C["dormente"]]), "trilho": np.select([PERF <= 45, PERF <= 57], ["leve (até TR 45)", "médio (TR 50 a 57)"], "pesado (TR 60 ou mais)")}
def oh_(v, nome): return pd.get_dummies(pd.Series(v).astype(str), prefix=nome, dtype=float).iloc[:, 1:].values if len(np.unique(v)) > 1 else np.zeros((len(v), 0))
X_EXTRA = np.column_stack([oh_(v, k) for k, v in CLS_V2.items()])
def X_v2(jp, jr): return np.column_stack([oh_(AP[jp], "p"), oh_(AR[jr], "r"), X_EXTRA])
def pontos(Xtr, ytr, Xte):
    m_ = LogisticRegression(C=0.5, max_iter=3000).fit(Xtr, ytr); b_ = m_.coef_.ravel(); pts = np.round(4 * b_ / np.abs(b_).max())
    return Xte @ pts, m_.predict_proba(Xte)[:, 1], pts
def limiares(s_tr, y_tr, alvos=(0.5, 0.8, 0.9)):
    v = np.sort(np.unique(s_tr))[::-1]; cob = np.array([y_tr[s_tr >= t].sum() for t in v]) / y_tr.sum(); return [float(v[np.argmax(cob >= a)]) for a in alvos]
def km_para_recall(s, yy, alvo):
    o = np.lexsort((DES, -s)); rc = np.cumsum(yy[o]) / yy.sum(); k_ = int(np.argmax(rc >= alvo)); km = np.cumsum(LN[o])[k_] / LN.sum(); fp = (1 - yy[o][:k_ + 1]).sum() / (len(yy) - yy.sum())
    return float(km), float(fp)
MET = ["Regra do EAR, faixas da FICO (atual)", "Regra do EAR, faixas da FNS", "Regra do EAR recalibrada (faixas e peso aferidos)", "EAR v2 por pontos (8 critérios de projeto)", "Logística com atributos (notebook 24, referência)"]
L27, ESC, CLA, GU27 = [], [], [], {}
for r in range(R):
    fo = folds_por(SEGC, SEED + r); S = {MET[0]: S_FICO.copy(), MET[1]: S_FNS.copy(), MET[2]: np.zeros(N), MET[3]: np.zeros(N), MET[4]: np.zeros(N)}; CL_ = np.zeros(N, int)
    for k in range(KF):
        te = fo == k; tr = ~te; jp, jr, w = calibra(tr, y); ESC.append(dict(sorteio=r, grupo=k, faixas_patio=CPS[jp], classes_raio=CRS[jr], peso_patio=w))
        S[MET[2]][te] = w * AP[jp][te] / 4 + (1 - w) * AR[jr][te] / 3
        Xv = X_v2(jp, jr); sp, _, pts = pontos(Xv[tr], y[tr], Xv); S[MET[3]][te] = sp[te]
        t50, t80, t90 = limiares(sp[tr], y[tr]); CL_[te] = np.select([sp[te] >= t50, sp[te] >= t80, sp[te] >= t90], [3, 2, 1], 0)
        S[MET[4]][te] = lr(X0[tr], y[tr], X0[te])
    if r < 10: GU27[r] = S
    for m, s_ in S.items():
        k80, f80 = km_para_recall(s_, y, 0.8); k90, f90 = km_para_recall(s_, y, 0.9)
        L27.append(dict(sorteio=r, metodo=m, auc=auc(y, s_), auc_malha=auc_grupo(s_, y, FERC), auc_linha=auc_grupo(s_, y, LINC), ap=average_precision_score(y, s_), recall_top20=matriz_conf(s_, y)["recall"], precisao_top20=matriz_conf(s_, y)["precisao"],
                        km_recall80=k80, fp_recall80=f80, km_recall90=k90, fp_recall90=f90))
    for c_, nome in [(3, "Muito alto"), (2, "Muito alto + Alto"), (1, "Muito alto + Alto + Moderado")]:
        sel = CL_ >= c_; tp = int((sel & (y == 1)).sum()); fp = int((sel & (y == 0)).sum())
        CLA.append(dict(sorteio=r, classes=nome, alvo_no_ajuste={3: 0.5, 2: 0.8, 1: 0.9}[c_], sensibilidade=tp / y.sum(), km=float(LN[sel].sum() / LN.sum()), falsos_positivos=fp / (N - y.sum()), precisao=tp / max(tp + fp, 1)))
R27 = pd.DataFrame(L27); R27.to_csv(f"{TAB}/27_regras_por_sorteio.csv", index=False)
T27 = R27.groupby("metodo")[["auc", "auc_malha", "auc_linha", "ap", "recall_top20", "precisao_top20", "km_recall80", "fp_recall80", "km_recall90", "fp_recall90"]].mean().loc[MET]
display(T27.round(3)); T27.to_csv(f"{TAB}/27_regras_resumo.csv")
ES = pd.DataFrame(ESC); ES.to_csv(f"{TAB}/27_parametros_escolhidos.csv", index=False)
FREQ = pd.concat([ES["faixas_patio"].astype(str).value_counts().rename("ajustes").to_frame().assign(criterio="faixas de distância ao pátio (m)"),
                  ES["classes_raio"].astype(str).value_counts().rename("ajustes").to_frame().assign(criterio="classes de raio (m)"),
                  ES["peso_patio"].astype(str).value_counts().rename("ajustes").to_frame().assign(criterio="peso do pátio")]).reset_index(names="valor")
display(FREQ); FREQ.to_csv(f"{TAB}/27_frequencia_parametros.csv", index=False)
CL27 = pd.DataFrame(CLA).groupby("classes")[["alvo_no_ajuste", "sensibilidade", "km", "falsos_positivos", "precisao"]].mean(); display(CL27.round(3)); CL27.to_csv(f"{TAB}/27_classes_ear_v2.csv")
gate("regra FICO no protocolo igual ao notebook 11 (AUC no país)", round(float(T27.loc[MET[0], "auc"]), 3), 0.588, tol=0.002, source="notebook 11")
gate("logística com atributos igual ao notebook 24 (AUC no país)", round(float(T27.loc[MET[4], "auc"]), 3), 0.759, tol=0.003, source="notebook 24")
gate("ajustes registrados: 30 sorteios × 5 grupos", len(ES), 150, source="desenho")
log_ia("27.4 recalibração aninhada", "Claude", "FOCUS: faixas, classes de raio e peso escolhidos só nos grupos de ajuste; pontos inteiros da EAR v2", "27_regras_resumo.csv, 27_parametros_escolhidos.csv", "regra e logística iguais aos notebooks 11 e 24")

# 4b. Sensibilidade: a mesma recalibração sem a restrição da faixa externa (grade até 5 km), 10 sorteios
CPS_L = list(combinations([250, 500, 1000, 1500, 2000, 2500, 3000, 4000, 5000], 4)); AP_L = np.array([faixas_p(dp, c) for c in CPS_L], dtype=np.int8); LS, ESL = [], []
for r in range(10):
    fo = folds_por(SEGC, SEED + r); s_ = np.zeros(N)
    for k in range(KF):
        te = fo == k; tr = ~te; gi = grupos(tr, y); jp = int(np.argmax([auc_malha_idx(AP_L[j].astype(float), gi) for j in range(len(CPS_L))])); jr = int(np.argmax([auc_malha_idx(AR[j].astype(float), gi) for j in range(len(CRS))]))
        w = WG[int(np.argmax([auc_malha_idx(w_ * AP_L[jp] / 4 + (1 - w_) * AR[jr] / 3, gi) for w_ in WG]))]
        s_[te] = w * AP_L[jp][te] / 4 + (1 - w) * AR[jr][te] / 3; ESL.append(str(CPS_L[jp]))
    LS.append(dict(sorteio=r, auc=auc(y, s_), auc_malha=auc_grupo(s_, y, FERC), km_recall80=km_para_recall(s_, y, 0.8)[0]))
SL = pd.DataFrame(LS).mean().drop("sorteio").to_frame("sem restrição (grade até 5 km)").T.assign(faixas_mais_escolhidas=pd.Series(ESL).value_counts().index[0], vezes=int(pd.Series(ESL).value_counts().iloc[0]), faixa_externa_5km=int(sum(e.endswith("5000)") for e in ESL)))
display(SL.round(3)); SL.to_csv(f"{TAB}/27_sensibilidade_faixa_externa.csv")
log_ia("27.4b sensibilidade da faixa externa", "Claude", "FOCUS: repetir a recalibração sem o limite de dois trens-tipo", "27_sensibilidade_faixa_externa.csv", "registro das escolhas")

# 4c. Quanto da vantagem da medida contínua vem das células longe de pátios? Mesmos 10 primeiros sorteios, AUC dentro das malhas
#     na malha inteira e só nas células a até 20 km de um pátio (fora delas estão os trechos longos de linhas com pouco tráfego).
LC = []; perto = dp <= 20000
for r in range(10):
    fo = folds_por(SEGC, SEED + r); s_ = np.zeros(N)
    for k in range(KF):
        te = fo == k; s_[te] = lr(XE[~te], y[~te], XE[te])
    for m, sc in [(MET[0], GU27[r][MET[0]]), (MET[2], GU27[r][MET[2]]), ("Critérios do EAR contínuos (notebook 24)", s_), (MET[4], GU27[r][MET[4]])]:
        LC.append(dict(sorteio=r, metodo=m, auc_malha=auc_grupo(sc, y, FERC), auc_malha_ate_20km=auc_grupo(sc[perto], y[perto], FERC[perto]), auc_ate_20km=auc(y[perto], sc[perto])))
LC = pd.DataFrame(LC).groupby("metodo", sort=False)[["auc_malha", "auc_malha_ate_20km", "auc_ate_20km"]].mean(); display(LC.round(3)); LC.to_csv(f"{TAB}/27_celulas_ate_20km.csv")
gate("células a até 20 km de um pátio", int(perto.sum()), int((C["dmin_patio"].fillna(1e9) <= 20000).sum()), source="definição")
log_ia("27.4c células longe de pátios", "Claude", "FOCUS: repetir a AUC dentro das malhas sem os trechos longos sem pátio", "27_celulas_ate_20km.csv", "contagem")

# 5. Diferenças pareadas por sorteio e IC 95% por reamostragem de linhas inteiras (10 sorteios, 300 reamostragens)
PAR27 = [(MET[1], MET[0]), (MET[2], MET[0]), (MET[3], MET[0]), (MET[3], MET[2]), (MET[4], MET[3])]
P27 = R27.pivot_table(index="sorteio", columns="metodo", values=["auc", "auc_malha", "km_recall80"])
rng = np.random.default_rng(SEED); Lu = np.unique(LINC); ix = {l: np.where(LINC == l)[0] for l in Lu}; BOOT27 = []
for b in range(300):
    i = np.concatenate([ix[l] for l in rng.choice(Lu, len(Lu))])
    if y[i].sum() < 50: continue
    BOOT27.append({(a, c): (np.mean([auc(y[i], GU27[r][a][i]) - auc(y[i], GU27[r][c][i]) for r in range(10)]), np.mean([auc_grupo(GU27[r][a][i], y[i], FERC[i]) - auc_grupo(GU27[r][c][i], y[i], FERC[i]) for r in range(10)])) for a, c in PAR27})
D27 = []
for a, c in PAR27:
    bn = np.array([x_[(a, c)][0] for x_ in BOOT27]); bm = np.array([x_[(a, c)][1] for x_ in BOOT27])
    dn = P27["auc"][a] - P27["auc"][c]; dm = P27["auc_malha"][a] - P27["auc_malha"][c]; dk = P27["km_recall80"][a] - P27["km_recall80"][c]
    D27.append(dict(comparacao=f"{a} − {c}", dif_pais=dn.mean(), ic_pais=f"{np.percentile(bn, 2.5):.3f} a {np.percentile(bn, 97.5):.3f}", sorteios_com_ganho_pais=int((dn > 0).sum()),
                    dif_malha=dm.mean(), ic_malha=f"{np.percentile(bm, 2.5):.3f} a {np.percentile(bm, 97.5):.3f}", sorteios_com_ganho_malha=int((dm > 0).sum()), dif_km_recall80=dk.mean()))
D27 = pd.DataFrame(D27).round(3); display(D27); D27.to_csv(f"{TAB}/27_diferencas.csv", index=False)
log_ia("27.5 diferenças", "Claude", "FOCUS: IC por reamostragem de linhas inteiras, como nos notebooks 24 e 25", "27_diferencas.csv", "mesmos sorteios")

# 6. Conferência temporal: parâmetros e pontos aferidos com 2011 a 2018 nos trechos de ajuste; conferidos com 2019 a 2025 nos trechos deixados de fora
y_a = (conta(CV_, 2011, 2018) > 0).astype(int); y_b = (conta(CV_, 2019, 2025) > 0).astype(int); LT = []
for r in range(10):
    fo = folds_por(SEGC, SEED + r); S = {MET[0]: S_FICO.copy(), MET[1]: S_FNS.copy(), MET[2]: np.zeros(N), MET[3]: np.zeros(N), MET[4]: np.zeros(N)}
    for k in range(KF):
        te = fo == k; tr = ~te; jp, jr, w = calibra(tr, y_a); S[MET[2]][te] = w * AP[jp][te] / 4 + (1 - w) * AR[jr][te] / 3
        Xv = X_v2(jp, jr); sp, _, _ = pontos(Xv[tr], y_a[tr], Xv); S[MET[3]][te] = sp[te]; S[MET[4]][te] = lr(X0[tr], y_a[tr], X0[te])
    for m, s_ in S.items(): LT.append(dict(sorteio=r, metodo=m, auc=auc(y_b, s_), auc_malha=auc_grupo(s_, y_b, FERC), km_recall80=km_para_recall(s_, y_b, 0.8)[0]))
TT27 = pd.DataFrame(LT).groupby("metodo")[["auc", "auc_malha", "km_recall80"]].mean().loc[MET]; display(TT27.round(3)); TT27.to_csv(f"{TAB}/27_conferencia_temporal.csv")
gate("quilômetros com descarrilamento em 2019 a 2025", int(y_b.sum()), int((conta(CV_, 2019, 2025) > 0).sum()), source="notebook 11")
log_ia("27.6 conferência temporal", "Claude", "FOCUS: aferir com 2011 a 2018 e conferir com 2019 a 2025 em trechos não vistos", "27_conferencia_temporal.csv", "contagem")

# 7. Vazamento: EAR v2 com rótulos embaralhados (5 embaralhamentos)
emb = []
for r in range(5):
    ye = np.random.default_rng(3000 + r).permutation(y); fo = folds_por(SEGC, SEED + r); s_ = np.zeros(N)
    for k in range(KF):
        te = fo == k; tr = ~te; jp, jr, w = calibra(tr, ye); Xv = X_v2(jp, jr); sp, _, _ = pontos(Xv[tr], ye[tr], Xv); s_[te] = sp[te]
    emb.append(auc(ye, s_))
gate_between("vazamento: EAR v2 com rótulos embaralhados", round(float(np.mean(emb)), 3), 0.45, 0.55, source="acaso")

# 8. Pontos da EAR v2 ajustados na malha inteira (para a tabela de parâmetros; a validação é a dos itens 4 a 6)
MODA_P = ES["faixas_patio"].value_counts().index[0]; MODA_R = ES["classes_raio"].value_counts().index[0]; MODA_W = float(ES["peso_patio"].value_counts().index[0])
jp0, jr0 = CPS.index(MODA_P), CRS.index(MODA_R); Xv0 = X_v2(jp0, jr0); _, _, PTS = pontos(Xv0, y, Xv0)
NOMES = list(pd.get_dummies(pd.Series(AP[jp0]).astype(str), prefix="patio").columns[1:]) + list(pd.get_dummies(pd.Series(AR[jr0]).astype(str), prefix="raio").columns[1:]) + \
        [c_ for k_, v_ in CLS_V2.items() for c_ in pd.get_dummies(pd.Series(v_).astype(str), prefix=k_).columns[1:]]
PT = pd.DataFrame(dict(classe=NOMES, pontos=PTS.astype(int))); display(PT); PT.to_csv(f"{TAB}/27_pontos_ear_v2.csv", index=False)
NOVO = pd.DataFrame([dict(criterio="Distância ao pátio (AMV)", limites_m=str(MODA_P), em_comprimentos_de_trem=str(tuple(round(v / L_TREM, 2) for v in MODA_P))),
                     dict(criterio="Raio de curva", limites_m=str(MODA_R), em_comprimentos_de_trem=""), dict(criterio="Peso do pátio na regra", limites_m=str(MODA_W), em_comprimentos_de_trem="")])
display(NOVO); NOVO.to_csv(f"{TAB}/27_parametros_recalibrados.csv", index=False)
log_ia("27.8 parâmetros finais", "Claude", "FOCUS: parâmetros mais escolhidos nos 150 ajustes e pontos na malha inteira", "27_parametros_recalibrados.csv, 27_pontos_ear_v2.csv", "itens 4 a 7")
