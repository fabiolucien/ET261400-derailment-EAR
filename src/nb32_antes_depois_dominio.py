# 32 · Antes e depois do pátio, limite de 500 m ou 1 km, linhas duplicadas e de pouco tráfego, critério novo
# FOCUS (23/11/2026, 1h; pedido do autor às 0h46 e 0h50, declarado antes de qualquer resultado deste notebook)
#  F: o autor pergunta (1) se o excesso de risco no km antes e depois do pátio não é, na verdade, acidente de PN ou OAE vizinhos; (2) se a faixa do EAR
#     deve valer dos dois lados do pátio; (3) se a faixa alta termina em 500 m ou em 1 km, conferindo para frente e para trás no tempo e numa ferrovia
#     que não entrou no ajuste; (4) se tirar as linhas duplicadas da Vale (EFVM e EFC), as ferrovias pequenas e os trechos de pouco tráfego muda o
#     resultado; (5) se algum critério novo deve entrar no EAR.
#  O: tabelas 32_*.csv; uma recomendação por pergunta, pela regra abaixo.
#  C: matriz e protocolo dos notebooks 27, 30 e 31; campos PN e local registrado do RAAF (data/processed/32_raaf_pn_local.csv, sem o campo Equipagem).
#  U (regras de decisão, escritas antes):
#   R1 PN e OAE: se, sem os descarrilamentos que o RAAF marca em PN, a célula do pátio e o km seguinte continuam acima de 1 com IC 95% acima de 1,
#      o excesso perto do pátio não é efeito de PN. Só com eventos registrados como trecho corrido (2021-2025): conclusão só se o IC excluir 1.
#      OAE: não há inventário nacional; só a FCA tem pontes do OpenStreetMap (notebook 11).
#   R2 simetria: razão entre o risco do lado de km crescente e o de km decrescente do pátio, com IC por linhas; se o IC contém 1 nas três faixas,
#      a faixa vale dos dois lados, como no EAR. O RAAF não registra o sentido do trem; "antes e depois" aqui é a ordem dos km.
#   R3 500 m ou 1 km: o limite de 500 m só substitui o de 1 km se ganhar com IC acima de zero no período inteiro, nos dois períodos (2011-2018 e
#      2019-2025, para frente e para trás) e na malha deixada de fora (mais malhas com ganho, teste do sinal p < 0,05). O mesmo vale ao contrário.
#      Se nenhum ganhar de forma consistente, a faixa alta fica "de 500 m a 1 km" e o EAR usa 1 km (cobre o trecho de maior risco por inteiro).
#   R4 domínio: variantes declaradas agora: D1 sem EFVM e EFC; D2 só linha singela (campo da Declaração de Rede); D3 sem as malhas com menos de 50 km
#      atingidos; D4 só células com 3 ou mais trens por dia vinculados; D5 singela e 3 ou mais trens por dia. Todas são relatadas. Uma variante
#      só pode virar domínio do artigo se tiver justificativa física anterior aos dados e se o resultado da malha inteira ficar ao lado; não se
#      escolhe a variante pela maior AUC.
#   R5 critério novo: entra no EAR se mudar o risco dentro das malhas (notebook 29) e melhorar a ordenação numa malha deixada de fora
#      (notebook 30); linha singela ou dupla é testada aqui como interação com o pátio.
#  Gates: G1 perfil do notebook 27 reproduzido (célula do pátio 1,969; até 1 km 1,870); G2 regra FICO dentro das malhas 0,589; G3 junção dos campos
#         do RAAF (2.681 eventos por via, 144 em PN); G4 placebo de lado (média de 50 embaralhamentos) entre 0,95 e 1,05; G5 B com limites fixos,
#         malha fora até 20 km, entre 0,62 e 0,67 (notebook 30, com limites reescolhidos: 0,645).
import time
from itertools import combinations
t0 = time.time()
def faixas_p(d, c): return np.select([d <= c[0], d <= c[1], d <= c[2], d <= c[3]], [4, 3, 2, 1], 0)
def classes_r(r, c): return np.select([r < c[0], r < c[1], r < c[2]], [3, 2, 1], 0)
FICO_P, FICO_R, AFER_P, AFER_R, A500_P = (300, 600, 1200, 1800), (500, 1200, 2300), (250, 1000, 1500, 3000), (250, 300, 600), (250, 500, 1500, 3000)
S_FICO = 0.5 * faixas_p(dp, FICO_P) / 4 + 0.5 * classes_r(rg, FICO_R) / 3
NL = LINC.max() + 1; LINHAS = [np.where(LINC == l)[0] for l in range(NL)]
def rr_mh(cls, K, ref, yy, w=None, S=None):
    w = np.ones(N) if w is None else w; S = FERC if S is None else S; ns = S.max() + 1; j = S * K + cls
    n_ = np.bincount(j, weights=w, minlength=ns * K).reshape(ns, K); a_ = np.bincount(j, weights=w * yy, minlength=ns * K).reshape(ns, K); out = np.full(K, np.nan)
    for k in range(K):
        T_ = n_[:, k] + n_[:, ref]; ok = T_ > 0; num = (a_[ok, k] * n_[ok, ref] / T_[ok]).sum(); den = (a_[ok, ref] * n_[ok, k] / T_[ok]).sum(); out[k] = num / den if den > 0 else np.nan
    return out
def boot_w(b): return np.bincount(np.random.default_rng(SEED + b).choice(NL, NL), minlength=NL)[LINC].astype(float)
WB = [boot_w(b) for b in range(300)]
def perfil(cls, K, ref, rot, yy):
    rr = rr_mh(cls, K, ref, yy); B_ = np.array([rr_mh(cls, K, ref, yy, w) for w in WB])
    return pd.DataFrame(dict(classe=rot, celulas=np.bincount(cls, minlength=K), km_atingidos=np.bincount(cls, weights=yy, minlength=K).astype(int), rr=rr,
                             ic_inf=np.nanpercentile(B_, 2.5, axis=0), ic_sup=np.nanpercentile(B_, 97.5, axis=0)))
y1, y2 = (conta(CV_, 2011, 2018) > 0).astype(int), (conta(CV_, 2019, 2025) > 0).astype(int)

# G1: perfil do notebook 27
LIM27 = [250, 1000, 1500, 2000, 3000, 5000, 20000]; K27 = np.digitize(dp, LIM27, right=True)
r27 = rr_mh(K27, 8, 6, y); gate("G1 célula do pátio (notebook 27)", round(float(r27[0]), 3), 1.969, tol=0.001, source="27_perfil_distancia_patio.csv")
gate("G1 até 1 km (notebook 27)", round(float(r27[1]), 3), 1.870, tol=0.001, source="27_perfil_distancia_patio.csv")
gate("G2 regra FICO dentro das malhas", round(auc_grupo(S_FICO, y, FERC), 3), 0.589, tol=0.002, source="notebook 24")
log_ia("32.0 base", "Claude", "FOCUS do notebook 32; funções dos notebooks 27 e 30", "rr_mh, perfil", "G1 e G2")

# 1. Perfil fino dentro do primeiro km e meio, no período inteiro e nos dois períodos (para frente e para trás)
LIMF = [250, 500, 750, 1000, 1500, 2000, 3000, 5000, 20000]
ROTF = ["célula do pátio (até 250 m)", "250 a 500 m", "500 a 750 m", "750 a 1.000 m", "1 a 1,5 km", "1,5 a 2 km", "2 a 3 km", "3 a 5 km", "5 a 20 km (referência)", "acima de 20 km"]
KF_ = np.digitize(dp, LIMF, right=True)
PF = []
for nome, yy in [("2011 a 2025", y), ("2011 a 2018", y1), ("2019 a 2025", y2)]:
    p_ = perfil(KF_, 10, 8, ROTF, yy); p_.insert(0, "periodo", nome); PF.append(p_)
PF = pd.concat(PF, ignore_index=True); display(PF.round(3)); PF.to_csv(f"{TAB}/32_perfil_fino_patio.csv", index=False)
print("perfil fino", round(time.time() - t0), "s"); sys.stdout.flush()

# 2. Regra com faixa alta até 1 km contra até 500 m (pesos 0,5 e 0,6), dentro das malhas
def regra(cp, w): return w * faixas_p(dp, cp) / 4 + (1 - w) * classes_r(rg, AFER_R) / 3
CMP = []
for w in (0.5, 0.6):
    s1, s5 = regra(AFER_P, w), regra(A500_P, w)
    for nome, yy in [("2011 a 2025", y), ("2011 a 2018", y1), ("2019 a 2025", y2)]:
        a1, a5 = auc_grupo(s1, yy, FERC), auc_grupo(s5, yy, FERC); D_ = []
        for b in range(300):
            ii = np.concatenate([LINHAS[l] for l in np.random.default_rng(SEED + b).choice(NL, NL)])
            D_.append(auc_grupo(s5[ii], yy[ii], FERC[ii]) - auc_grupo(s1[ii], yy[ii], FERC[ii]))
        CMP.append(dict(peso_patio=w, periodo=nome, auc_1km=a1, auc_500m=a5, dif_500_menos_1km=a5 - a1, ic_inf=np.percentile(D_, 2.5), ic_sup=np.percentile(D_, 97.5)))
CMP = pd.DataFrame(CMP); display(CMP.round(4)); CMP.to_csv(f"{TAB}/32_limite_500m_1km.csv", index=False)
# extensão marcada como alta ou muito alta em cada versão
EXT = pd.DataFrame([dict(versao=v, km_alta_ou_muito_alta=float(LN[faixas_p(dp, c) >= 3].sum()), parcela=float(LN[faixas_p(dp, c) >= 3].sum() / LN.sum())) for v, c in [("até 1 km", AFER_P), ("até 500 m", A500_P)]])
display(EXT.round(3)); EXT.to_csv(f"{TAB}/32_extensao_faixa_alta.csv", index=False)
print("comparação 500 m e 1 km", round(time.time() - t0), "s"); sys.stdout.flush()

# 3. Malha deixada de fora (ferrovia nova): multiplicadores de pátio, raio e tráfego ajustados sem a malha, faixa alta até 1 km ou até 500 m
CAPV = pd.to_numeric(C["cap_vinc"], errors="coerce").fillna(0).values; TRAF = np.where(CAPV <= 0, 0, np.digitize(CAPV, [1, 3, 10], right=True) + 1)
def cls_patio(c): k = faixas_p(dp, c).astype(int); k[(k == 0) & (dp > 20000)] = 5; return k
def mult(cls, K, ref, yy, S, m):
    ns = S.max() + 1; j = S[m] * K + cls[m]; n_ = np.bincount(j, minlength=ns * K).reshape(ns, K).astype(float); a_ = np.bincount(j, weights=yy[m], minlength=ns * K).reshape(ns, K); out = np.ones(K)
    for k in range(K):
        T_ = n_[:, k] + n_[:, ref]; ok = T_ > 0; num = (a_[ok, k] * n_[ok, ref] / T_[ok]).sum(); den = (a_[ok, ref] * n_[ok, k] / T_[ok]).sum()
        out[k] = max(num / den, 0.05) if den > 0 and num > 0 else (0.05 if den > 0 else 1.0)
    return out
def nota_B(cp, m, yy):
    kp, kr = cls_patio(cp), classes_r(rg, AFER_R).astype(int); Stl = pd.factorize(pd.Series(FERC).astype(str) + "|" + pd.Series(kp).astype(str) + "|" + pd.Series(kr).astype(str))[0]
    Tp, Tr, Tt = mult(kp, 6, 0, yy, FERC, m), mult(kr, 4, 0, yy, FERC, m), mult(TRAF, 5, 2, yy, Stl, m)
    return np.log(Tp[kp]) + np.log(Tr[kr]) + np.log(Tt[TRAF])
MF = []
for f in range(FERC.max() + 1):
    te = FERC == f
    if y[te].sum() < 5: continue
    perto = te & (dp <= 20000)
    for v, cp in [("até 1 km", AFER_P), ("até 500 m", A500_P)]:
        s = nota_B(cp, ~te, y); MF.append(dict(malha=C["ferrovia"].values[te][0], versao=v, km_atingidos=int(y[te].sum()), auc=auc(y[te], s[te]), auc_ate_20km=auc(y[perto], s[perto]) if 0 < y[perto].sum() < perto.sum() else np.nan))
MF = pd.DataFrame(MF); P_ = MF.pivot(index="malha", columns="versao", values="auc_ate_20km"); W_ = MF.groupby("malha")["km_atingidos"].first()
dif = (P_["até 500 m"] - P_["até 1 km"]).dropna(); from math import comb
k5 = int((dif > 0).sum()); n_ = int((dif != 0).sum()); p5 = sum(comb(n_, k) for k in range(k5, n_ + 1)) / 2 ** n_; p1 = sum(comb(n_, k) for k in range(n_ - k5, n_ + 1)) / 2 ** n_
RMF = pd.DataFrame([dict(versao=v, auc_ate_20km_ponderada=float(np.average(P_[v].dropna(), weights=W_[P_[v].dropna().index]))) for v in ["até 1 km", "até 500 m"]])
RMF["malhas_em_que_500m_ganha"] = k5; RMF["malhas"] = n_; RMF["p_sinal_500m"] = p5; RMF["p_sinal_1km"] = p1
display(MF.round(3)); display(RMF.round(4)); MF.to_csv(f"{TAB}/32_malha_fora_500m_1km.csv", index=False); RMF.to_csv(f"{TAB}/32_malha_fora_500m_1km_resumo.csv", index=False)
gate_between("G5 B com limites fixos, malha fora até 20 km", round(float(RMF.loc[0, "auc_ate_20km_ponderada"]), 3), 0.62, 0.67, source="notebook 30 (0,645 com limites reescolhidos)")
log_ia("32.1 limite", "Claude", "FOCUS: perfil fino, regra com 1 km e 500 m, malha fora", "32_perfil_fino_patio.csv, 32_limite_500m_1km.csv, 32_malha_fora_500m_1km.csv", "G5")
print("malha fora", round(time.time() - t0), "s"); sys.stdout.flush()

# 4. PN e local registrado: o excesso perto do pátio some sem os descarrilamentos em PN? E só com os registrados como trecho corrido?
PNL = pd.read_csv(f"{PROC}/32_raaf_pn_local.csv"); EVX = EV.merge(PNL, on=["fonte", "linha_raaf"], how="left", validate="many_to_one")
gate("G3 eventos por via com campos do RAAF", int(EVX["pn"].notna().sum()), 2681, source="notebook 11"); gate("G3 eventos por via em PN", int(EVX["pn"].sum()), 144, source="contagem direta do campo PN do RAAF, conferida fora do notebook")
def rotulo_de(ev): return (np.bincount(idx[ev["cel_id"]].values, minlength=N) > 0).astype(int)
ROT27 = ["pátio na célula", "até 1 km", "1 a 1,5 km", "1,5 a 2 km", "2 a 3 km", "3 a 5 km", "5 a 20 km", "acima de 20 km"]
CF = []
for nome, ev in [("todos, 2011 a 2025", EVX), ("sem os em PN, 2011 a 2025", EVX[~EVX["pn"]]), ("todos, 2021 a 2025", EVX[EVX["ano"] >= 2021]),
                 ("só registrados como trecho corrido, 2021 a 2025", EVX[(EVX["ano"] >= 2021) & (EVX["local_registrado"] == "trecho corrido")]),
                 ("sem os registrados dentro da zona do pátio (notebook 31)", EVX[~EVX["zona_patio"]])]:
    p_ = perfil(K27, 8, 6, ROT27, rotulo_de(ev)).iloc[:3]; p_.insert(0, "eventos", nome); p_.insert(1, "n_eventos", len(ev)); CF.append(p_)
CF = pd.concat(CF, ignore_index=True); display(CF.round(3)); CF.to_csv(f"{TAB}/32_pn_e_local.csv", index=False)
log_ia("32.2 PN", "Claude", "FOCUS: perfil sem eventos em PN e só com trecho corrido", "32_pn_e_local.csv", "G3")
print("PN", round(time.time() - t0), "s"); sys.stdout.flush()

# 5. Simetria: lado de km crescente e de km decrescente do pátio mais próximo
km_lo = C.groupby("seg_id")["km_a"].transform("min").values; km_hi = C.groupby("seg_id")["km_b"].transform("max").values
LADO = np.where((C["km_a"].values - km_lo) <= (km_hi - C["km_b"].values), 0, 1)     # 0: célula depois do pátio no sentido dos km; 1: antes
def cls_lado(lado):
    b = np.digitize(dp, [250, 1000, 1500, 3000, 20000], right=True)              # 0 pátio, 1 até 1 km, 2 1 a 1,5 km, 3 1,5 a 3 km, 4 ref, 5 acima de 20 km
    k = np.select([b == 0, b == 4, b == 5], [0, 7, 8], 0); m = (b >= 1) & (b <= 3); k[m] = 1 + 2 * (b[m] - 1) + lado[m]; return k
ROTL = ["célula do pátio", "até 1 km, km crescente", "até 1 km, km decrescente", "1 a 1,5 km, km crescente", "1 a 1,5 km, km decrescente", "1,5 a 3 km, km crescente", "1,5 a 3 km, km decrescente", "3 a 20 km (referência)", "acima de 20 km"]
KL = cls_lado(LADO); rl = rr_mh(KL, 9, 7, y); BL = np.array([rr_mh(KL, 9, 7, y, w) for w in WB])
SIM = pd.DataFrame([dict(faixa=f, rr_km_crescente=rl[a], rr_km_decrescente=rl[a + 1], razao=rl[a] / rl[a + 1], ic_inf=np.nanpercentile(BL[:, a] / BL[:, a + 1], 2.5), ic_sup=np.nanpercentile(BL[:, a] / BL[:, a + 1], 97.5),
                         celulas_crescente=int((KL == a).sum()), celulas_decrescente=int((KL == a + 1).sum())) for f, a in [("até 1 km", 1), ("1 a 1,5 km", 3), ("1,5 a 3 km", 5)]])
display(SIM.round(3)); SIM.to_csv(f"{TAB}/32_simetria_lados.csv", index=False)
pl = []
for b in range(50):
    kk = cls_lado(np.random.default_rng(SEED + 1000 + b).integers(0, 2, N)); r_ = rr_mh(kk, 9, 7, y); pl.append(r_[1] / r_[2])
gate_between("G4 placebo de lado, razão média até 1 km", round(float(np.mean(pl)), 3), 0.95, 1.05, source="lados sorteados: razão esperada 1")
log_ia("32.3 simetria", "Claude", "FOCUS: risco relativo por lado do pátio, IC por linhas, placebo", "32_simetria_lados.csv", "G4")
print("simetria", round(time.time() - t0), "s"); sys.stdout.flush()

# 6. Domínios: sem a Vale (EFVM e EFC), só singela, sem malhas pequenas, só com 3 ou mais trens por dia, singela e 3 ou mais
GP = [250, 500, 1000, 1500, 2000, 2500, 3000]; CPS = list(combinations(GP, 4)); GR = [250, 300, 400, 500, 600, 800, 1200, 2300]; CRS = list(combinations(GR, 3)); WG = [0.3, 0.4, 0.5, 0.6, 0.7]
AP_ = np.array([faixas_p(dp, c) for c in CPS], dtype=np.int8); AR_ = np.array([classes_r(rg, c) for c in CRS], dtype=np.int8)
def auc_m_mask(s, m, yy):
    a_, w_ = [], []
    for f in np.unique(FERC[m]):
        i = m & (FERC == f); n1 = yy[i].sum(); n = i.sum()
        if 5 <= n1 < n: r_ = rankdata(s[i]); a_.append((r_[yy[i] == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * (n - n1))); w_.append(n1)
    return float(np.average(a_, weights=w_)) if w_ else np.nan
def escolhe(m, yy):
    jp = int(np.nanargmax([auc_m_mask(AP_[j].astype(float), m, yy) for j in range(len(CPS))])); jr = int(np.nanargmax([auc_m_mask(AR_[j].astype(float), m, yy) for j in range(len(CRS))]))
    w = WG[int(np.nanargmax([auc_m_mask(w_ * AP_[jp] / 4 + (1 - w_) * AR_[jr] / 3, m, yy) for w_ in WG]))]; return jp, jr, w
FER = C["ferrovia"].values; SING = C["n_linhas"].astype(str).values == "Singela"; HIT_M = pd.Series(y).groupby(FER).sum()
PEQ = set(HIT_M[HIT_M < 50].index)
DOM = {"D0 todas as células em operação": np.ones(N, bool), "D1 sem EFVM e EFC (Vale, linha dupla)": ~np.isin(FER, ["EFVM", "EFC"]), "D2 só linha singela": SING,
       "D3 sem as malhas com menos de 50 km atingidos": ~np.isin(FER, list(PEQ)), "D4 só 3 ou mais trens por dia vinculados": CAPV >= 3, "D5 singela e 3 ou mais trens por dia": SING & (CAPV >= 3)}
print("malhas com menos de 50 km atingidos:", sorted(PEQ))
DR_ = []
for nome, m in DOM.items():
    lin = []
    for r in range(10):
        fo = folds_por(SEGC, SEED + r); sA, sL = np.full(N, np.nan), np.full(N, np.nan); ch = []
        for k in range(KF):
            te = (fo == k) & m; tr = (fo != k) & m; jp, jr, w = escolhe(tr, y); ch.append(f"{CPS[jp]} {CRS[jr]} {w}")
            sA[te] = (w * AP_[jp] / 4 + (1 - w) * AR_[jr] / 3)[te]; sL[te] = lr(X0[tr], y[tr], X0[te])
        lin.append(dict(sorteio=r + 1, auc_regra_fico=auc(y[m], S_FICO[m]), auc_malha_fico=auc_m_mask(S_FICO, m, y), auc_aferida=auc(y[m], sA[m]), auc_malha_aferida=auc_m_mask(sA, m, y),
                        auc_logistica=auc(y[m], sL[m]), auc_malha_logistica=auc_m_mask(sL, m, y), escolha_mais_comum=pd.Series(ch).value_counts().index[0]))
    L_ = pd.DataFrame(lin); jp, jr, w = escolhe(m, y)
    rp = rr_mh(K27, 8, 6, y.astype(float) * m, np.where(m, 1.0, 0.0))
    DR_.append(dict(dominio=nome, celulas=int(m.sum()), km_atingidos=int(y[m].sum()), malhas=int(len(np.unique(FER[m]))), **L_.drop(columns=["sorteio", "escolha_mais_comum"]).mean().to_dict(),
                    limites_patio_no_dominio=str(CPS[jp]), limites_raio_no_dominio=str(CRS[jr]), peso_patio=w, rr_celula_patio=rp[0], rr_ate_1km=rp[1], rr_1_a_1_5km=rp[2]))
    print(nome, round(time.time() - t0), "s"); sys.stdout.flush()
DOMR = pd.DataFrame(DR_); display(DOMR.round(3)); DOMR.to_csv(f"{TAB}/32_dominios.csv", index=False)

# 7. Critério novo: linha singela ou dupla como interação com o pátio (o risco perto do pátio muda na linha dupla?)
INT = []
for nome, m in [("singela", SING), ("dupla", ~SING)]:
    mm = m.astype(float); r_ = rr_mh(K27, 8, 6, y * mm, mm); B_ = np.array([rr_mh(K27, 8, 6, y * mm, w * mm) for w in WB])
    for k in range(3): INT.append(dict(linha=nome, classe=ROT27[k], rr=r_[k], ic_inf=np.nanpercentile(B_[:, k], 2.5), ic_sup=np.nanpercentile(B_[:, k], 97.5),
                                       celulas=int(((K27 == k) & m).sum()), km_atingidos=int(y[(K27 == k) & m].sum()), celulas_ref=int(((K27 == 6) & m).sum()), km_atingidos_ref=int(y[(K27 == 6) & m].sum())))
INT = pd.DataFrame(INT); display(INT.round(3)); INT.to_csv(f"{TAB}/32_singela_dupla.csv", index=False)
log_ia("32.4 domínios e critério novo", "Claude", "FOCUS: variantes D1 a D5 declaradas antes; interação singela e dupla", "32_dominios.csv, 32_singela_dupla.csv", "D0 reproduz os notebooks 24 e 27")
print("fim", round(time.time() - t0), "s")
