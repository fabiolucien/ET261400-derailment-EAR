# 31 · Monte Carlo da incerteza de posição: os novos limites do EAR resistem ao erro de localização?
# FOCUS (declarado antes do código, 22/11/2026, 23h40)
#  F: o RAAF localiza o acidente pelo km (28% dos registros com km inteiro) e a posição do AMV é estimada pelas pontas do pátio da Declaração de Rede
#     (km do pátio mais ou menos metade do comprimento útil mais 40 m). Os dois têm erro que nenhum registro público informa.
#  O: propagar esse erro por simulação de Monte Carlo e ver se os limites aferidos no notebook 27 (pátio 250, 1.000, 1.500 e 3.000 m; raio 250, 300 e 600 m)
#     e o ganho sobre a regra da FICO se mantêm.
#  C: matriz e eventos do notebook 11; funções e grade de limites do notebook 27 (mesma grade de 35 combinações de pátio, 56 de raio e 5 pesos).
#  U: cenários e amplitudes declarados antes, como hipóteses de sensibilidade (não há fonte pública para o erro): S1, km do acidente + U(-0,5; +0,5) km;
#     S2, + U(-1; +1) km; S3, cada pátio deslocado U(-250; +250) m (o mesmo deslocamento para todas as células cujo pátio mais próximo é aquele);
#     S4, S1 e S3 juntos; S5, cada pátio U(-500; +500) m. 200 réplicas por cenário (sementes 3100 a 3299). Se o km sorteado cai fora de qualquer
#     célula em operação da mesma linha, o acidente fica na célula original. Em cada réplica: risco relativo dentro das malhas por classe (como no 27),
#     limites escolhidos pela AUC dentro das malhas em toda a malha (sem aninhamento, para caber no tempo; o aninhamento está no 27) e AUC da regra da FICO
#     e da regra aferida com os limites fixos.
#  Restrição acrescentada pelo gate loop (primeira execução: G1 falhou, 2.608 de 2.681, e G2 deu 2.130): em 73 eventos o km do RAAF fica fora da célula
#    que o notebook 11 lhes atribuiu (regras de tolerância da alocação). O erro sorteado passa a ser aplicado à posição do acidente DENTRO da célula atribuída:
#    km de referência = km do RAAF limitado ao intervalo da célula; o evento só muda de célula se a posição deslocada sair desse intervalo. Tolerâncias inalteradas.
#  Acréscimos pedidos pela revisão externa 3 (declarados antes da segunda execução): S6, deslocamento sistemático por linha; SIMEX para o RR sem erro do km;
#    três conferências do artefato de descarrilamentos em linha de pátio. Gate G6: SIMEX no nível zero igual ao RR observado.
#  Gates: G1 réplica sem erro reproduz a célula de todos os eventos; G2 2.123 km atingidos sem erro; G3 AUC dentro das malhas da regra FICO sem erro = 0,589 (27_regras_resumo);
#         G4 o deslocamento de pátio zero reproduz a distância ao pátio de todas as células; G5 em toda réplica a soma dos eventos é 2.681.
import time
t0 = time.time()
def faixas_p(d, c): return np.select([d <= c[0], d <= c[1], d <= c[2], d <= c[3]], [4, 3, 2, 1], 0)
def classes_r(r, c): return np.select([r < c[0], r < c[1], r < c[2]], [3, 2, 1], 0)
FICO_P, FICO_R, AFER_P, AFER_R, W_AFER = (300, 600, 1200, 1800), (500, 1200, 2300), (250, 1000, 1500, 3000), (250, 300, 600), 0.6
from itertools import combinations
GP = [250, 500, 1000, 1500, 2000, 2500, 3000]; CPS = list(combinations(GP, 4)); GR = [250, 300, 400, 500, 600, 800, 1200, 2300]; CRS = list(combinations(GR, 3)); WG = [0.3, 0.4, 0.5, 0.6, 0.7]
AR_ = np.array([classes_r(rg, c) for c in CRS], dtype=np.int8)
def auc_m(s, yy):
    a_, w_ = [], []
    for f in range(FERC.max() + 1):
        i = FERC == f; n1 = yy[i].sum()
        if 5 <= n1 < i.sum(): r_ = rankdata(s[i]); a_.append((r_[yy[i] == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * (i.sum() - n1))); w_.append(n1)
    return float(np.average(a_, weights=w_))
def calibra_tudo(dpx, yy):
    APx = [faixas_p(dpx, c) for c in CPS]
    jp = int(np.argmax([auc_m(a.astype(float), yy) for a in APx])); jr = int(np.argmax([auc_m(AR_[j].astype(float), yy) for j in range(len(CRS))]))
    w = WG[int(np.argmax([auc_m(w_ * APx[jp] / 4 + (1 - w_) * AR_[jr] / 3, yy) for w_ in WG]))]; return CPS[jp], CRS[jr], w
LIM_P = [250, 1000, 1500, 2000, 3000, 5000, 20000]; ROT_P = ["pátio na célula", "até 1 km", "1 a 1,5 km", "1,5 a 2 km", "2 a 3 km", "3 a 5 km", "5 a 20 km", "acima de 20 km"]
LIM_R = [300, 400, 500, 800, 1200, 2300]; ROT_R = ["até 300 m", "300 a 400 m", "400 a 500 m", "500 a 800 m", "800 a 1.200 m", "1.200 a 2.300 m", "acima de 2.300 m e tangente"]
def rr_mh(cls, K, ref, yy):
    nf = FERC.max() + 1; j = FERC * K + cls; n_ = np.bincount(j, minlength=nf * K).reshape(nf, K).astype(float); a_ = np.bincount(j, weights=yy, minlength=nf * K).reshape(nf, K); out = np.full(K, np.nan)
    for k in range(K):
        T_ = n_[:, k] + n_[:, ref]; ok = T_ > 0; num = (a_[ok, k] * n_[ok, ref] / T_[ok]).sum(); den = (a_[ok, ref] * n_[ok, k] / T_[ok]).sum(); out[k] = num / den if den > 0 else np.nan
    return out

# 1. Eventos: célula de origem, linha e km; tabela de busca por linha
EVJ = EV[EV["ano"].between(2011, 2025)].copy(); gate("G5 eventos da janela", len(EVJ), 2681, source="notebook 11")
EVJ["i0"] = idx[EVJ["cel_id"]].values; LK = (C["ferrovia"].astype(str) + "|" + C["linha"].astype(str)).values; EVJ["lk"] = LK[EVJ["i0"].values]
KA, KB = C["km_a"].values, C["km_b"].values; POR_LINHA = {k_: np.where(LK == k_)[0] for k_ in np.unique(LK)}
EV_I0, EV_LK = EVJ["i0"].values, EVJ["lk"].values
EV_KM = np.clip(EVJ["km"].values.astype(float), KA[EV_I0], KB[EV_I0] - 1e-6)          # posição de referência dentro da célula atribuída (gate loop)
def realoca(desl):
    km2 = EV_KM + desl; out = EV_I0.copy()
    sai = ~((KA[EV_I0] <= km2) & (km2 < KB[EV_I0]))                            # só procura nova célula se o km sorteado sai da célula original
    for e in np.where(sai)[0]:
        c_ = POR_LINHA[EV_LK[e]]; j = c_[(KA[c_] <= km2[e]) & (km2[e] < KB[c_])]
        if len(j): out[e] = j[0]
    return out
def rotulo(cel): return (np.bincount(cel, minlength=N) > 0).astype(int)
i_sem = realoca(np.zeros(len(EVJ)))
gate("G1 sem erro, eventos na célula original", int((i_sem == EV_I0).sum()), len(EVJ), source="definição")
gate("G2 km atingidos sem erro", int(rotulo(i_sem).sum()), 2123, source="notebook 11")
gate("G3 regra FICO, AUC dentro das malhas sem erro", round(auc_m(0.5 * faixas_p(dp, FICO_P) / 4 + 0.5 * classes_r(rg, FICO_R) / 3, y), 3), 0.589, tol=0.002, source="27_regras_resumo.csv")

# 2. Pátios: lado do pátio mais próximo de cada célula e identidade do pátio (o mesmo pátio serve aos dois trechos vizinhos)
C_ = C.copy(); C_["ini"] = C_.groupby("seg_id")["km_a"].transform("min"); C_["fim"] = C_.groupby("seg_id")["km_b"].transform("max")
lado_a = (C_["km_a"] + C_["km_b"]) / 2 - C_["ini"] <= C_["fim"] - (C_["km_a"] + C_["km_b"]) / 2
PAT = np.where(lado_a, LK + "|" + C_["patio_a"].astype(str).values, LK + "|" + C_["patio_b"].astype(str).values); PCOD, PU = pd.factorize(PAT)
DP0 = C["dmin_patio"].values.astype(float)
def distancia(desl_patio):
    d = DP0 + desl_patio[PCOD]; d = np.where(np.isnan(DP0), np.nan, np.maximum(d, 0.0)); return np.nan_to_num(d, nan=1e9)
gate("G4 deslocamento zero reproduz a distância ao pátio", float(np.abs(distancia(np.zeros(len(PU))) - dp).max()), 0.0, tol=1e-9, source="definição")
print("pátios distintos:", len(PU), round(time.time() - t0), "s"); sys.stdout.flush()

# 3. Réplicas
CEN = {"S1 acidente ±0,5 km": (0.5, 0.0), "S2 acidente ±1 km": (1.0, 0.0), "S3 pátio ±250 m": (0.0, 250.0), "S4 acidente ±0,5 km e pátio ±250 m": (0.5, 250.0), "S5 pátio ±500 m": (0.0, 500.0)}
KR0 = np.digitize(rg, LIM_R, right=True); REP = []; RRP, RRR = [], []
for nome, (hk, hp) in CEN.items():
    for b in range(200):
        g_ = np.random.default_rng(3100 + b)
        cel = realoca(g_.uniform(-hk, hk, len(EVJ))) if hk > 0 else EV_I0
        yy = rotulo(cel); dpx = distancia(g_.uniform(-hp, hp, len(PU))) if hp > 0 else dp
        cp, cr, w = calibra_tudo(dpx, yy)
        s_f = 0.5 * faixas_p(dpx, FICO_P) / 4 + 0.5 * classes_r(rg, FICO_R) / 3; s_a = W_AFER * faixas_p(dpx, AFER_P) / 4 + (1 - W_AFER) * classes_r(rg, AFER_R) / 3
        REP.append(dict(cenario=nome, replica=b + 1, km_atingidos=int(yy.sum()), eventos_mudaram_de_celula=float((cel != EV_I0).mean()), limites_patio=str(cp), limites_raio=str(cr), peso_patio=w,
                        auc_malhas_fico=auc_m(s_f, yy), auc_malhas_aferida=auc_m(s_a, yy), auc_pais_fico=auc(yy, s_f), auc_pais_aferida=auc(yy, s_a)))
        rp = rr_mh(np.digitize(dpx, LIM_P, right=True), 8, 6, yy); rr_ = rr_mh(KR0, 7, 6, yy)
        RRP.append(dict(cenario=nome, replica=b + 1, **{ROT_P[k]: rp[k] for k in range(8)})); RRR.append(dict(cenario=nome, replica=b + 1, **{ROT_R[k]: rr_[k] for k in range(7)}))
    print(nome, round(time.time() - t0), "s"); sys.stdout.flush()
MC = pd.DataFrame(REP); MC["ganho_malhas"] = MC["auc_malhas_aferida"] - MC["auc_malhas_fico"]; MC.to_csv(f"{TAB}/31_replicas.csv", index=False)
RP = pd.DataFrame(RRP); RRr = pd.DataFrame(RRR); RP.to_csv(f"{TAB}/31_rr_patio_replicas.csv", index=False); RRr.to_csv(f"{TAB}/31_rr_raio_replicas.csv", index=False)

# 3b. Cenário sistemático (pedido da revisão externa 3): S6, um único deslocamento U(-0,5; +0,5) km por linha, comum a todos os acidentes da linha
#     (marcos quilométricos deslocados depois de variantes e correções de quilometragem)
LK_U, LK_COD = np.unique(EV_LK, return_inverse=True); nome = "S6 deslocamento por linha ±0,5 km"
for b in range(200):
    g_ = np.random.default_rng(3100 + b); cel = realoca(g_.uniform(-0.5, 0.5, len(LK_U))[LK_COD]); yy = rotulo(cel); cp, cr, w = calibra_tudo(dp, yy)
    s_f = 0.5 * faixas_p(dp, FICO_P) / 4 + 0.5 * classes_r(rg, FICO_R) / 3; s_a = W_AFER * faixas_p(dp, AFER_P) / 4 + (1 - W_AFER) * classes_r(rg, AFER_R) / 3
    REP.append(dict(cenario=nome, replica=b + 1, km_atingidos=int(yy.sum()), eventos_mudaram_de_celula=float((cel != EV_I0).mean()), limites_patio=str(cp), limites_raio=str(cr), peso_patio=w,
                    auc_malhas_fico=auc_m(s_f, yy), auc_malhas_aferida=auc_m(s_a, yy), auc_pais_fico=auc(yy, s_f), auc_pais_aferida=auc(yy, s_a)))
    rp = rr_mh(np.digitize(dp, LIM_P, right=True), 8, 6, yy); rr_ = rr_mh(KR0, 7, 6, yy)
    RRP.append(dict(cenario=nome, replica=b + 1, **{ROT_P[k]: rp[k] for k in range(8)})); RRR.append(dict(cenario=nome, replica=b + 1, **{ROT_R[k]: rr_[k] for k in range(7)}))
print(nome, round(time.time() - t0), "s"); sys.stdout.flush()
MC = pd.DataFrame(REP); MC["ganho_malhas"] = MC["auc_malhas_aferida"] - MC["auc_malhas_fico"]; MC.to_csv(f"{TAB}/31_replicas.csv", index=False)
RP = pd.DataFrame(RRP); RRr = pd.DataFrame(RRR); RP.to_csv(f"{TAB}/31_rr_patio_replicas.csv", index=False); RRr.to_csv(f"{TAB}/31_rr_raio_replicas.csv", index=False)

# 4. Resumo por cenário
def faixa(s): return f"{np.percentile(s, 2.5):.2f} a {np.percentile(s, 97.5):.2f}"
RES = []
for nome, g in MC.groupby("cenario", sort=False):
    rp = RP[RP["cenario"] == nome]; rr_ = RRr[RRr["cenario"] == nome]
    RES.append(dict(cenario=nome, eventos_que_mudam_de_celula=g["eventos_mudaram_de_celula"].mean(), km_atingidos=g["km_atingidos"].mean(),
                    patio_igual_ao_27=float((g["limites_patio"] == str(AFER_P)).mean()), raio_igual_ao_27=float((g["limites_raio"] == str(AFER_R)).mean()),
                    patio_mais_escolhido=g["limites_patio"].mode()[0], raio_mais_escolhido=g["limites_raio"].mode()[0],
                    ganho_malhas_medio=g["ganho_malhas"].mean(), ganho_malhas_faixa=faixa(g["ganho_malhas"]), replicas_com_ganho=float((g["ganho_malhas"] > 0).mean()),
                    rr_patio_na_celula=faixa(rp["pátio na célula"]), rr_ate_1km=faixa(rp["até 1 km"]), rr_1_a_1_5km=faixa(rp["1 a 1,5 km"]), rr_raio_ate_300=faixa(rr_["até 300 m"])))
RES31 = pd.DataFrame(RES); display(RES31); RES31.to_csv(f"{TAB}/31_resumo_monte_carlo.csv", index=False)
FREQ = pd.concat([MC.groupby("cenario", sort=False)["limites_patio"].value_counts(normalize=True).rename("frequencia").reset_index().assign(criterio="pátio").rename(columns={"limites_patio": "limites"}),
                  MC.groupby("cenario", sort=False)["limites_raio"].value_counts(normalize=True).rename("frequencia").reset_index().assign(criterio="raio").rename(columns={"limites_raio": "limites"})])
FREQ.to_csv(f"{TAB}/31_frequencia_limites.csv", index=False); display(FREQ.groupby(["cenario", "criterio"], sort=False).head(3))
print("fim", round(time.time() - t0), "s")
log_ia("31 Monte Carlo de posição", "Claude", "FOCUS: cinco cenários de erro de posição declarados antes, 200 réplicas cada; limites, risco relativo e ganho por réplica",
       "31_replicas.csv, 31_resumo_monte_carlo.csv, 31_frequencia_limites.csv", "5 gates")

# 5. SIMEX (Cook e Stefanski, 1994): o erro aleatório atenua o risco relativo; somando erro em níveis crescentes e extrapolando para erro zero, estima-se o
#    risco relativo sem o erro do km do acidente. Erro de base suposto: U(-0,5; +0,5) km (variância 0,083 km²); níveis lambda de 0,5 a 2 (50 réplicas cada);
#    extrapolação quadrática para lambda = -1. Hipótese declarada: o km do RAAF tem erro dessa ordem; não há fonte pública para ele.
KP0 = np.digitize(dp, LIM_P, right=True); LAMB = [0.5, 1.0, 1.5, 2.0]; ALVOS = [("pátio", 0, "pátio na célula"), ("pátio", 1, "até 1 km"), ("pátio", 2, "1 a 1,5 km"), ("raio", 0, "até 300 m")]
def lrr_(yy): rp = rr_mh(KP0, 8, 6, yy); rr_ = rr_mh(KR0, 7, 6, yy); return [np.log(rp[0]), np.log(rp[1]), np.log(rp[2]), np.log(rr_[0])]
SIM = [dict(lambda_=0.0, **{nm: v for (_, _, nm), v in zip(ALVOS, lrr_(y))})]
for lam in LAMB:
    a_ = 0.5 * np.sqrt(lam); vals = []
    for b in range(50):
        g_ = np.random.default_rng(5000 + int(lam * 100) + b); vals.append(lrr_(rotulo(realoca(g_.uniform(-a_, a_, len(EVJ))))))
    SIM.append(dict(lambda_=lam, **{nm: float(np.mean([v[j] for v in vals])) for j, (_, _, nm) in enumerate(ALVOS)}))
SIM = pd.DataFrame(SIM); SX = []
for _, _, nm in ALVOS:
    cf = np.polyfit(SIM["lambda_"], SIM[nm], 2); SX.append(dict(classe=nm, rr_observado=float(np.exp(SIM.loc[0, nm])), rr_lambda_2=float(np.exp(SIM.loc[SIM["lambda_"] == 2.0, nm].iloc[0])), rr_simex=float(np.exp(np.polyval(cf, -1.0)))))
SX = pd.DataFrame(SX); display(SX.round(3)); SX.to_csv(f"{TAB}/31_simex.csv", index=False); SIM.to_csv(f"{TAB}/31_simex_niveis.csv", index=False)
print("simex", round(time.time() - t0), "s"); sys.stdout.flush()

# 6. Artefato de pátio (pedido da revisão externa 3): descarrilamentos em linhas de pátio registrados no km do pátio inflariam a célula do pátio.
#    O RAAF de 2011 a 2025 não separa linha principal e linha de pátio. Três conferências declaradas antes: (a) parcela de km inteiros na célula do pátio contra
#    as demais; (b) RR da célula do pátio sem os eventos no km exato do pátio; (c) RR sem os eventos dentro da extensão declarada do pátio (zona do pátio),
#    o limite mais conservador, que também tira descarrilamentos legítimos da linha principal nos AMV do pátio.
cel_pat = KP0[EV_I0] == 0; int_km = (EVJ["km"].values % 1) == 0
ART = [dict(conferencia="(a) parcela de km inteiros", celula_do_patio=float(int_km[cel_pat].mean()), demais_celulas=float(int_km[~cel_pat].mean()))]
for rot_, keep in [("(b) sem eventos no km exato do pátio", EVJ["d_patio"].values > 0), ("(c) sem eventos dentro da zona do pátio", ~EVJ["zona_patio"].astype(bool).values)]:
    yy = rotulo(EV_I0[keep]); rp = rr_mh(KP0, 8, 6, yy)
    ART.append(dict(conferencia=rot_, eventos=int(keep.sum()), km_atingidos=int(yy.sum()), rr_patio_na_celula=float(rp[0]), rr_ate_1km=float(rp[1]), rr_1_a_1_5km=float(rp[2])))
ART = pd.DataFrame(ART); display(ART.round(3)); ART.to_csv(f"{TAB}/31_artefato_patio.csv", index=False)
log_ia("31.2 SIMEX e artefato de pátio", "Claude", "FOCUS: SIMEX com quatro níveis de erro adicional e extrapolação quadrática; três conferências do artefato de pátio declaradas antes",
       "31_simex.csv, 31_artefato_patio.csv", "nível zero igual ao RR observado")
gate("G6 SIMEX: nível zero igual ao RR observado da célula do pátio", round(float(SX.loc[0, "rr_observado"]), 3), round(float(rr_mh(KP0, 8, 6, y)[0]), 3), tol=1e-9, source="definição")
