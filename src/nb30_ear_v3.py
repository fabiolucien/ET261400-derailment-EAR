# 30 · EAR v3: multiplicadores de risco para replicar num EAR, e teste como ferrovia nova
# FOCUS (versão 2, 23/11/2026, 0h; refeita depois da revisão externa 3; a versão 1 está em nb30_ear_v3_versao1.py e em revisoes/revisao3_respostas.md)
#  F: o autor quer um modelo que aponte os trechos mais suscetíveis num EAR que ele vai replicar ou numa linha nova, com parâmetros atualizados.
#  O: (i) tabela de multiplicadores de risco relativo dentro das malhas (Mantel-Haenszel) por classe de cada critério: distância ao pátio e raio (notebook 27)
#     e os fatores aprovados no notebook 29 (tráfego vinculado e carga por eixo); (ii) desempenho em trechos inteiros fora do ajuste (30 sorteios) e com cada
#     malha inteira fora (a ferrovia nova); (iii) heterogeneidade entre malhas e intervalo de predição de cada multiplicador, a incerteza certa para uma
#     ferrovia que não está nos dados; (iv) caso Norte-Sul (FNSTN) com intervalo; (v) comparação com um modelo conjunto (logística com as mesmas classes).
#  C: notebooks 11, 27 e 29. Variantes declaradas antes: A pátio + raio; B A + tráfego; C A + carga; D A + tráfego + carga; J logística conjunta com as classes de B.
#  U (mudanças pedidas pela revisão externa 3, declaradas antes desta execução):
#     1. sem vazamento: em cada dobra (e em cada malha deixada de fora) os limites de pátio e de raio são reescolhidos só no ajuste, com a grade e o critério
#        do notebook 27; a regra aferida também é reescolhida;
#     2. referência do pátio igual à do artigo: do limite externo a 20 km; a classe acima de 20 km (linhas longas de pouco tráfego) fica separada;
#     3. tráfego é exposição: a nota de B é suscetibilidade (pátio e raio) mais exposição (capacidade vinculada da Declaração de Rede de 2025, em trens por dia);
#     4. a escolha entre B e D se faz pela malha inteira fora, por parcimônia (empate dentro de 0,005 fica com o modelo mais simples);
#     5. IC pareado por reamostragem de linhas e teste de sinal na malha fora; AUC dentro das linhas; erro-padrão de Hanley e McNeil (1982) no caso FNSTN;
#     6. efeitos aleatórios (DerSimonian e Laird, 1986) dos log-RR por malha, com I² e intervalo de predição (Higgins, Thompson e Spiegelhalter, 2009).
#  Gates: G1 logística com atributos, malha fora, 0,633 (24_malha_fora); G2 regra FICO, malha fora, 0,589; G3 B com rótulos embaralhados entre 0,45 e 0,55;
#         G4 multiplicador de referência 1; G5 classes do mapa somam 100%; G6 nenhuma classe de B sem km atingido (o piso não atua em B);
#         G7 meta-análise de estimativas idênticas dá tau² = 0 (definição).
import time
from itertools import combinations
t0 = time.time()
def faixas_p(d, c): return np.select([d <= c[0], d <= c[1], d <= c[2], d <= c[3]], [4, 3, 2, 1], 0)
def classes_r(r, c): return np.select([r < c[0], r < c[1], r < c[2]], [3, 2, 1], 0)
FICO_P, FICO_R, AFER_P, AFER_R = (300, 600, 1200, 1800), (500, 1200, 2300), (250, 1000, 1500, 3000), (250, 300, 600)
S_FICO = 0.5 * faixas_p(dp, FICO_P) / 4 + 0.5 * classes_r(rg, FICO_R) / 3
GP = [250, 500, 1000, 1500, 2000, 2500, 3000]; CPS = list(combinations(GP, 4)); GR = [250, 300, 400, 500, 600, 800, 1200, 2300]; CRS = list(combinations(GR, 3)); WG = [0.3, 0.4, 0.5, 0.6, 0.7]
AP_ = np.array([faixas_p(dp, c) for c in CPS], dtype=np.int8); AR_ = np.array([classes_r(rg, c) for c in CRS], dtype=np.int8)
def auc_m_mask(s, m):
    a_, w_ = [], []
    for f in np.unique(FERC[m]):
        i = m & (FERC == f); n1 = y[i].sum(); n = i.sum()
        if 5 <= n1 < n: r_ = rankdata(s[i]); a_.append((r_[y[i] == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * (n - n1))); w_.append(n1)
    return float(np.average(a_, weights=w_))
def escolhe(m):                                                           # mesma grade e mesmo critério do notebook 27, só nas células de ajuste
    jp = int(np.argmax([auc_m_mask(AP_[j].astype(float), m) for j in range(len(CPS))])); jr = int(np.argmax([auc_m_mask(AR_[j].astype(float), m) for j in range(len(CRS))]))
    w = WG[int(np.argmax([auc_m_mask(w_ * AP_[jp] / 4 + (1 - w_) * AR_[jr] / 3, m) for w_ in WG]))]; return jp, jr, w
def cls_patio(jp): k = AP_[jp].astype(int).copy(); k[(k == 0) & (dp > 20000)] = 5; return k      # 0 = do limite externo a 20 km (referência); 5 = acima de 20 km
CAPV = pd.to_numeric(C["cap_vinc"], errors="coerce").fillna(0).values; CARGA = np.array(pd.to_numeric(C["carga_eixo_t"], errors="coerce"), dtype=float); CARGA[CARGA <= 0] = np.nan
TRAF = np.where(CAPV <= 0, 0, np.digitize(CAPV, [1, 3, 10], right=True) + 1)
LOAD = np.where(np.isnan(CARGA), 4, np.digitize(np.nan_to_num(CARGA), [20, 25, 30], right=True))
ROT = {"pátio": ["do limite externo a 20 km (referência)", "baixa", "moderada", "alta", "muito alta (célula do pátio)", "acima de 20 km"],
       "raio": ["acima do limite externo e tangente (referência)", "classe baixa", "classe média", "classe alta (menor raio)"],
       "tráfego": ["zero vinculado", "até 1 trem/dia", "1 a 3 trens/dia (referência)", "3 a 10 trens/dia", "acima de 10 trens/dia"],
       "carga por eixo": ["até 20 t (referência)", "20 a 25 t", "25 a 30 t", "acima de 30 t", "sem dado"]}
REF = {"pátio": 0, "raio": 0, "tráfego": 2, "carga por eixo": 0}
def rr_mh_s(cls, K, ref, yy, S, m):
    ns = S.max() + 1; j = S[m] * K + cls[m]
    n_ = np.bincount(j, minlength=ns * K).reshape(ns, K).astype(float); a_ = np.bincount(j, weights=yy[m], minlength=ns * K).reshape(ns, K); out = np.ones(K)
    for k in range(K):
        T_ = n_[:, k] + n_[:, ref]; ok = T_ > 0; num = (a_[ok, k] * n_[ok, ref] / T_[ok]).sum(); den = (a_[ok, ref] * n_[ok, k] / T_[ok]).sum()
        out[k] = max(num / den, 0.05) if den > 0 and num > 0 else (0.05 if den > 0 else 1.0)
    return out
VAR = {"A pátio e raio": ["pátio", "raio"], "B A + tráfego": ["pátio", "raio", "tráfego"], "C A + carga por eixo": ["pátio", "raio", "carga por eixo"], "D A + tráfego + carga": ["pátio", "raio", "tráfego", "carga por eixo"]}
def classes_de(jp, jr): return {"pátio": cls_patio(jp), "raio": AR_[jr].astype(int), "tráfego": TRAF, "carga por eixo": LOAD}
def ajusta(m, yy, CL):
    S_tl = pd.factorize(pd.Series(FERC).astype(str) + "|" + pd.Series(CL["pátio"]).astype(str) + "|" + pd.Series(CL["raio"]).astype(str))[0]
    return {c_: rr_mh_s(CL[c_], len(ROT[c_]), REF[c_], yy, FERC if c_ in ("pátio", "raio") else S_tl, m) for c_ in CL}
def pontua(T, CL, crits): return np.sum([np.log(T[c_][CL[c_]]) for c_ in crits], axis=0)
def oh(v): return pd.get_dummies(pd.Series(v).astype(str), dtype=float).iloc[:, 1:].values
def conjunta(CL, m_tr, m_te): X_ = np.column_stack([oh(CL["pátio"]), oh(CL["raio"]), oh(CL["tráfego"])]); return lr(X_[m_tr], y[m_tr], X_[m_te])
METS = list(VAR) + ["J logística conjunta (classes de B)", "regra aferida (reescolhida)", "regra FICO"]

# 1. Trechos inteiros fora do ajuste, 30 sorteios, limites reescolhidos em cada dobra
LIN, GU30, ESC30 = [], {}, []
for r in range(R):
    fo = folds_por(SEGC, SEED + r); S = {v: np.zeros(N) for v in METS}; S["regra FICO"] = S_FICO.copy()
    for k in range(KF):
        te = fo == k; tr = ~te; jp, jr, w = escolhe(tr); CL = classes_de(jp, jr); T = ajusta(tr, y, CL); ESC30.append(dict(sorteio=r + 1, grupo=k, patio=str(CPS[jp]), raio=str(CRS[jr]), peso=w))
        for v, cr in VAR.items(): S[v][te] = pontua(T, CL, cr)[te]
        S["J logística conjunta (classes de B)"][te] = conjunta(CL, tr, te); S["regra aferida (reescolhida)"][te] = (w * AP_[jp] / 4 + (1 - w) * AR_[jr] / 3)[te]
    for v in METS: LIN.append(dict(sorteio=r + 1, metodo=v, auc=auc(y, S[v]), auc_malha=auc_grupo(S[v], y, FERC), auc_linha=auc_grupo(S[v], y, LINC), ap=average_precision_score(y, S[v]),
                                   **{k_: v_ for k_, v_ in matriz_conf(S[v], y).items() if k_ in ("recall", "precisao")}))
    if r < 10: GU30[r] = S
    if r in (0, 9, 29): print("sorteio", r + 1, round(time.time() - t0), "s"); sys.stdout.flush()
L30 = pd.DataFrame(LIN); RES30 = L30.groupby("metodo", sort=False)[["auc", "auc_malha", "auc_linha", "ap", "recall", "precisao"]].mean()
display(RES30.round(3)); RES30.to_csv(f"{TAB}/30_resumo.csv"); L30.to_csv(f"{TAB}/30_por_sorteio.csv", index=False); pd.DataFrame(ESC30).to_csv(f"{TAB}/30_limites_por_dobra.csv", index=False)
print(pd.DataFrame(ESC30)["patio"].value_counts().head(3).to_dict(), pd.DataFrame(ESC30)["raio"].value_counts().head(3).to_dict())
# rótulos embaralhados (5 vezes), sorteio 1, variante B
emb = []; CL0 = classes_de(CPS.index(AFER_P), CRS.index(AFER_R))
for b in range(5):
    ye = np.random.default_rng(500 + b).permutation(y); fo = folds_por(SEGC, SEED); s_ = np.zeros(N)
    for k in range(KF):
        te = fo == k; s_[te] = pontua(ajusta(~te, ye, CL0), CL0, VAR["B A + tráfego"])[te]
    emb.append(auc(ye, s_))
gate_between("G3 variante B com rótulos embaralhados (média de 5)", round(float(np.mean(emb)), 3), 0.45, 0.55, source="acaso")
PAR30 = [("B A + tráfego", "A pátio e raio"), ("B A + tráfego", "regra FICO"), ("B A + tráfego", "regra aferida (reescolhida)"), ("D A + tráfego + carga", "B A + tráfego"), ("J logística conjunta (classes de B)", "B A + tráfego")]
rng = np.random.default_rng(SEED); Lu = np.unique(LINC); ix = {l: np.where(LINC == l)[0] for l in Lu}; BT = []
for b in range(300):
    i = np.concatenate([ix[l] for l in rng.choice(Lu, len(Lu))])
    if y[i].sum() < 50: continue
    BT.append({(a, c): (np.mean([auc(y[i], GU30[r][a][i]) - auc(y[i], GU30[r][c][i]) for r in range(10)]), np.mean([auc_grupo(GU30[r][a][i], y[i], FERC[i]) - auc_grupo(GU30[r][c][i], y[i], FERC[i]) for r in range(10)])) for a, c in PAR30})
P30 = L30.pivot_table(index="sorteio", columns="metodo", values=["auc", "auc_malha"]); D30 = []
for a, c in PAR30:
    bn = np.array([x_[(a, c)][0] for x_ in BT]); bm = np.array([x_[(a, c)][1] for x_ in BT]); dn = P30["auc"][a] - P30["auc"][c]; dm = P30["auc_malha"][a] - P30["auc_malha"][c]
    D30.append(dict(comparacao=f"{a} − {c}", dif_pais=dn.mean(), ic_pais=f"{np.percentile(bn, 2.5):.3f} a {np.percentile(bn, 97.5):.3f}", sorteios_com_ganho_pais=int((dn > 0).sum()),
                    dif_malha=dm.mean(), ic_malha=f"{np.percentile(bm, 2.5):.3f} a {np.percentile(bm, 97.5):.3f}", sorteios_com_ganho_malha=int((dm > 0).sum())))
D30 = pd.DataFrame(D30).round(3); display(D30); D30.to_csv(f"{TAB}/30_diferencas.csv", index=False)
print("trechos fora ok", round(time.time() - t0), "s"); sys.stdout.flush()
log_ia("30.1 trechos fora", "Claude", "FOCUS: limites reescolhidos em cada dobra; multiplicadores só no ajuste; 30 sorteios; IC por linhas", "30_resumo.csv, 30_diferencas.csv", "placebo")

# 2. Ferrovia nova: cada malha inteira fora (limites e multiplicadores sem ela); média ponderada pelos km atingidos; AUC também dentro das linhas da malha fora
S_MF = {v: np.full(N, np.nan) for v in METS + ["logística com atributos"]}; ESC_MF = []
for f in range(FERC.max() + 1):
    te = FERC == f; tr = ~te; jp, jr, w = escolhe(tr); CL = classes_de(jp, jr); T = ajusta(tr, y, CL); ESC_MF.append(dict(malha=C["ferrovia"].values[te][0], patio=str(CPS[jp]), raio=str(CRS[jr])))
    for v, cr in VAR.items(): S_MF[v][te] = pontua(T, CL, cr)[te]
    S_MF["J logística conjunta (classes de B)"][te] = conjunta(CL, tr, te); S_MF["regra aferida (reescolhida)"][te] = (w * AP_[jp] / 4 + (1 - w) * AR_[jr] / 3)[te]
    S_MF["regra FICO"][te] = S_FICO[te]; S_MF["logística com atributos"][te] = lr(X0[tr], y[tr], X0[te])
LM = []
for f in range(FERC.max() + 1):
    te = FERC == f
    if y[te].sum() < 5: continue
    reg = dict(malha=C["ferrovia"].values[te][0], celulas=int(te.sum()), atingidas=int(y[te].sum()))
    for v in S_MF: reg[v] = auc(y[te], S_MF[v][te]); reg[v + " | linhas"] = auc_grupo(S_MF[v][te], y[te], LINC[te], minimo=3)
    LM.append(reg)
MF30 = pd.DataFrame(LM); MF30.to_csv(f"{TAB}/30_malha_fora.csv", index=False); pd.DataFrame(ESC_MF).to_csv(f"{TAB}/30_limites_malha_fora.csv", index=False); w_ = MF30["atingidas"]
MEDIA = pd.DataFrame([dict(escore=v, auc_malha_fora=float(np.average(MF30[v], weights=w_)), auc_linhas_da_malha_fora=float(np.average(MF30[v + " | linhas"], weights=w_)),
                           malhas_acima_da_FICO=int((MF30[v] > MF30["regra FICO"]).sum())) for v in S_MF])
display(MF30[["malha", "atingidas"] + list(S_MF)].round(3)); display(MEDIA.round(3)); MEDIA.to_csv(f"{TAB}/30_malha_fora_resumo.csv", index=False)
MED_ = MEDIA.set_index("escore")["auc_malha_fora"]
gate("G1 logística com atributos, malha inteira fora (média ponderada)", round(float(MED_["logística com atributos"]), 3), 0.633, tol=0.002, source="24_malha_fora.csv")
gate("G2 regra FICO, malha inteira fora (média ponderada)", round(float(MED_["regra FICO"]), 3), 0.589, tol=0.002, source="24_malha_fora.csv")
# 2a. O mesmo, só nas células a até 20 km de um pátio (86% da malha): a classe acima de 20 km marca trechos longos de linhas de pouco uso, o que mede uso da
#     linha e não proximidade do AMV, e numa ferrovia nova com pátios a cada 20 a 30 km quase não ocorre (recorte declarado antes desta execução)
p20 = dp <= 20000; L20 = []
for f in range(FERC.max() + 1):
    te = (FERC == f) & p20
    if y[te].sum() < 5: continue
    L20.append(dict(malha=C["ferrovia"].values[te][0], atingidas=int(y[te].sum()), **{v: auc(y[te], S_MF[v][te]) for v in S_MF}))
MF20 = pd.DataFrame(L20); w20 = MF20["atingidas"]; MED20 = pd.DataFrame([dict(escore=v, auc_malha_fora_ate_20km=float(np.average(MF20[v], weights=w20)), malhas_acima_da_FICO=int((MF20[v] > MF20["regra FICO"]).sum()), malhas=len(MF20)) for v in S_MF])
display(MED20.round(3)); MED20.to_csv(f"{TAB}/30_malha_fora_ate_20km.csv", index=False); MF20.to_csv(f"{TAB}/30_malha_fora_ate_20km_por_malha.csv", index=False)
from scipy.stats import binom
PARMF = [("B A + tráfego", "regra FICO"), ("B A + tráfego", "regra aferida (reescolhida)"), ("B A + tráfego", "A pátio e raio"), ("B A + tráfego", "logística com atributos"),
         ("D A + tráfego + carga", "B A + tráfego"), ("J logística conjunta (classes de B)", "B A + tráfego")]
OKM = [f for f in range(FERC.max() + 1) if y[FERC == f].sum() >= 5]; rngm = np.random.default_rng(SEED); BM = {pq: [] for pq in PARMF}; VS = sorted(set(sum(PARMF, ())))
for b in range(300):
    i = np.concatenate([ix[l] for l in rngm.choice(Lu, len(Lu))]); yi, fi = y[i], FERC[i]; aucs = {v: [] for v in VS}; ws = []
    for f in OKM:
        j = fi == f
        if not (1 <= yi[j].sum() < j.sum()): continue
        ws.append(yi[j].sum())
        for v in VS: aucs[v].append(auc(yi[j], S_MF[v][i][j]))
    for a, c in PARMF: BM[(a, c)].append(np.average(np.array(aucs[a]) - np.array(aucs[c]), weights=ws))
DMF = []
for a, c in PARMF:
    d_ = MF30[a] - MF30[c]; k_ = int((d_ > 0).sum()); n_ = int((d_ != 0).sum())
    DMF.append(dict(comparacao=f"{a} − {c}", dif=float(np.average(d_, weights=w_)), ic_inf=float(np.percentile(BM[(a, c)], 2.5)), ic_sup=float(np.percentile(BM[(a, c)], 97.5)),
                    malhas_com_ganho=k_, malhas=n_, p_sinal_unilateral=float(binom.sf(k_ - 1, n_, 0.5))))
DMF = pd.DataFrame(DMF); display(DMF.round(3)); DMF.to_csv(f"{TAB}/30_malha_fora_diferencas.csv", index=False)
CL_B = classes_de(CPS.index(AFER_P), CRS.index(AFER_R))
gate("G6 menor número de km atingidos numa classe de B (toda a malha)", int(min(min(np.bincount(CL_B[c_][y == 1], minlength=len(ROT[c_]))) for c_ in ("pátio", "raio", "tráfego")) > 0), 1, source="o piso de 0,05 não atua em B")
print("malha fora ok", round(time.time() - t0), "s"); sys.stdout.flush()
log_ia("30.2 ferrovia nova", "Claude", "FOCUS: cada malha fora, limites e multiplicadores sem ela; AUC dentro das linhas; IC pareado por linhas; teste de sinal", "30_malha_fora*.csv", "G1 e G2")

# 3. Parâmetros finais (toda a malha, limites do notebook 27), IC por linhas, e efeitos aleatórios entre malhas com intervalo de predição
from scipy.stats import t as tdist
TF = ajusta(np.ones(N, bool), y, CL_B); S_TL = pd.factorize(pd.Series(FERC).astype(str) + "|" + pd.Series(CL_B["pátio"]).astype(str) + "|" + pd.Series(CL_B["raio"]).astype(str))[0]
NLn = LINC.max() + 1; rngb = np.random.default_rng(SEED); BB = {c_: [] for c_ in CL_B}
for b in range(300):
    m_ = np.repeat(np.arange(N), np.bincount(rngb.choice(NLn, NLn), minlength=NLn)[LINC]); yb = y[m_]
    for c_ in CL_B:
        S_ = (FERC if c_ in ("pátio", "raio") else S_TL)[m_]; K = len(ROT[c_]); ref = REF[c_]; j = S_ * K + CL_B[c_][m_]; ns = S_.max() + 1
        n_ = np.bincount(j, minlength=ns * K).reshape(ns, K).astype(float); a_ = np.bincount(j, weights=yb, minlength=ns * K).reshape(ns, K); out = np.full(K, np.nan)
        for k in range(K):
            T_ = n_[:, k] + n_[:, ref]; ok = T_ > 0; num = (a_[ok, k] * n_[ok, ref] / T_[ok]).sum(); den = (a_[ok, ref] * n_[ok, k] / T_[ok]).sum(); out[k] = num / den if den > 0 else np.nan
        BB[c_].append(out)
def gr_malha(cls, k, ref, strata_in):                               # RR de Mantel-Haenszel e variância de Greenland e Robins (1985) em cada malha
    out = []
    for f in range(FERC.max() + 1):
        m_ = (FERC == f) & np.isin(cls, [k, ref]); num = den = vnum = 0.0
        for s_ in np.unique(strata_in[m_]):
            j = m_ & (strata_in == s_); n1 = (cls[j] == k).sum(); n0 = (cls[j] == ref).sum(); T_ = n1 + n0
            if n1 == 0 or n0 == 0: continue
            a = y[j][cls[j] == k].sum(); c = y[j][cls[j] == ref].sum(); num += a * n0 / T_; den += c * n1 / T_; vnum += (n1 * n0 * (a + c) - a * c * T_) / T_ ** 2
        if num > 0 and den > 0: out.append((C["ferrovia"].values[FERC == f][0], np.log(num / den), vnum / (num * den)))
    return out
def dl(est):                                                         # DerSimonian e Laird (1986); intervalo de predição de Higgins et al. (2009)
    yv = np.array([e[1] for e in est]); v = np.array([e[2] for e in est]); k = len(yv); w = 1 / v; mu_f = (w * yv).sum() / w.sum(); Q = (w * (yv - mu_f) ** 2).sum()
    tau2 = max(0.0, (Q - (k - 1)) / (w.sum() - (w ** 2).sum() / w.sum())) if k > 1 else 0.0; ws_ = 1 / (v + tau2); mu = (ws_ * yv).sum() / ws_.sum(); se = np.sqrt(1 / ws_.sum())
    I2 = max(0.0, (Q - (k - 1)) / Q) if Q > 0 else 0.0; tq = tdist.ppf(0.975, k - 2) if k > 2 else np.nan; pi = (mu - tq * np.sqrt(tau2 + se ** 2), mu + tq * np.sqrt(tau2 + se ** 2)) if k > 2 else (np.nan, np.nan)
    return dict(malhas=k, rr_aleatorio=float(np.exp(mu)), ic_inf_aleat=float(np.exp(mu - 1.96 * se)), ic_sup_aleat=float(np.exp(mu + 1.96 * se)), tau2=float(tau2), I2=float(I2),
                predicao_inf=float(np.exp(pi[0])), predicao_sup=float(np.exp(pi[1])))
t_ = dl([("a", 0.3, 0.01), ("b", 0.3, 0.02), ("c", 0.3, 0.05)]); gate("G7 meta-análise de estimativas idênticas: tau²", round(t_["tau2"], 9), 0.0, tol=1e-9, source="definição")
STR_PR = np.zeros(N, dtype=int); PT = []
for c_ in CL_B:
    B_ = np.array(BB[c_])
    for k, nome in enumerate(ROT[c_]):
        reg = dict(criterio=c_, classe=nome, referencia=k == REF[c_], celulas=int((CL_B[c_] == k).sum()), km_atingidos=int(y[CL_B[c_] == k].sum()), multiplicador=float(TF[c_][k]),
                   ic_inf=float(np.nanpercentile(B_[:, k], 2.5)), ic_sup=float(np.nanpercentile(B_[:, k], 97.5)))
        if k != REF[c_] and nome != "sem dado":
            est = gr_malha(CL_B[c_], k, REF[c_], STR_PR if c_ in ("pátio", "raio") else S_TL)
            if len(est) >= 3: reg.update(dl(est))
        PT.append(reg)
PT30 = pd.DataFrame(PT); gate("G4 multiplicador da classe de referência", float(PT30.loc[PT30["referencia"], "multiplicador"].max()), 1.0, tol=1e-9, source="definição")
display(PT30.round(3)); PT30.to_csv(f"{TAB}/30_parametros_ear_v3.csv", index=False)
print("parâmetros ok", round(time.time() - t0), "s"); sys.stdout.flush()
# classes do mapa dentro de cada malha (cortes declarados antes: 10% muito alta, 20% alta, 30% moderada, 40% baixa), com as notas da malha inteira fora
CORTES = [(0.10, "muito alta"), (0.30, "alta"), (0.60, "moderada"), (1.01, "baixa")]; LCM = []
for k_, s in S_MF.items():
    cl = np.empty(N, dtype=object)
    for f in range(FERC.max() + 1):
        i = np.where(FERC == f)[0]; o_ = i[np.lexsort((DES[i], -s[i]))]; cum_ = np.cumsum(LN[o_]) / LN[i].sum(); feito = np.zeros(len(o_), bool)
        for corte, nome in CORTES: sel = (cum_ <= corte) & ~feito; cl[o_[sel]] = nome; feito |= sel
    for corte, nome in CORTES:
        m_ = cl == nome; LCM.append(dict(escore=k_, classe=nome, parcela_extensao=float(LN[m_].sum() / LN.sum()), parcela_km_atingidos=float(y[m_].sum() / y.sum()), km_atingidos=int(y[m_].sum())))
CLM30 = pd.DataFrame(LCM); display(CLM30.pivot_table(index="escore", columns="classe", values="parcela_km_atingidos", sort=False).round(3)); CLM30.to_csv(f"{TAB}/30_classes_dentro_da_malha.csv", index=False)
gate("G5 classes do mapa somam a extensão (variante B)", round(float(CLM30.loc[CLM30["escore"] == "B A + tráfego", "parcela_extensao"].sum()), 6), 1.0, tol=1e-6, source="definição")
log_ia("30.3 parâmetros", "Claude", "FOCUS: multiplicadores com IC por linhas; efeitos aleatórios por malha com intervalo de predição; classes por extensão dentro da malha", "30_parametros_ear_v3.csv, 30_classes_dentro_da_malha.csv", "G4, G5 e G7")

# 4. Caso Norte-Sul (FNSTN): ajustado sem ela; erro-padrão de Hanley e McNeil (1982)
fns = (C["ferrovia"] == "FNSTN").values; S_FNS = 0.5 * faixas_p(dp, (200, 400, 800, 1600)) / 4 + 0.5 * classes_r(rg, (500, 800, 1200)) / 3
def hanley(A, n1, n0): q1 = A / (2 - A); q2 = 2 * A * A / (1 + A); return float(np.sqrt((A * (1 - A) + (n1 - 1) * (q1 - A * A) + (n0 - 1) * (q2 - A * A)) / (n1 * n0)))
def recall_top(s, m, frac=0.2):
    i = np.where(m)[0]; o_ = i[np.lexsort((DES[i], -s[i]))]; top = o_[np.cumsum(LN[o_]) / LN[i].sum() <= frac]; return int(y[top].sum())
APL = []; n1_ = int(y[fns].sum()); n0_ = int(fns.sum() - n1_)
for nome, s in [("EAR da FNS (ENEFER, 2015)", S_FNS), ("regra FICO", S_FICO), ("regra aferida, ajustada sem a FNSTN", S_MF["regra aferida (reescolhida)"]), ("A pátio e raio, sem a FNSTN", S_MF["A pátio e raio"]),
                ("B pátio, raio e tráfego, sem a FNSTN", S_MF["B A + tráfego"]), ("logística com atributos, sem a FNSTN", S_MF["logística com atributos"])]:
    A_ = auc(y[fns], s[fns]); se_ = hanley(A_, n1_, n0_)
    APL.append(dict(escore=nome, km_atingidos=n1_, auc=A_, ic_inf=A_ - 1.96 * se_, ic_sup=A_ + 1.96 * se_, km_atingidos_nos_20pct=recall_top(s, fns)))
APL30 = pd.DataFrame(APL); display(APL30.round(3)); APL30.to_csv(f"{TAB}/30_aplicacao_fns.csv", index=False)
print("fim", round(time.time() - t0), "s")
log_ia("30.4 Norte-Sul", "Claude", "FOCUS: modelo ajustado sem a FNSTN aplicado a ela; IC de Hanley e McNeil", "30_aplicacao_fns.csv", "mesma resposta e mesma extensão")
