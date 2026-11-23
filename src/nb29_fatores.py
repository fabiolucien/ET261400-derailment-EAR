# 29 · Fatores da via dentro das malhas: quais servem de parâmetro do EAR e quais só separam ferrovias
# FOCUS (declarado antes do código, 22/11/2026, 23h20)
#  F: a Declaração de Rede traz, por trecho, bitola, velocidade, rampa, carga por eixo, capacidade vinculada (tráfego), dormente, trilho, fixação,
#     taxa de dormentação, sinalização, produto perigoso e número de linhas. Um EAR de ferrovia nova conhece esses valores no projeto.
#  O: separar, para cada fator, o que muda o risco de descarrilamento por via DENTRO de uma ferrovia (candidato a parâmetro do EAR)
#     do que só distingue uma ferrovia da outra (operador, manutenção, registro), que não se transfere a uma linha nova.
#  C: matriz de células e eventos do notebook 11; faixas aferidas no notebook 27 (pátio 250, 1.000, 1.500 e 3.000 m; raio 250, 300 e 600 m).
#  U: só dados públicos; classes de cada fator e regra de decisão escritas antes de rodar; mesmo protocolo dos notebooks 24 e 27
#     (trechos inteiros entre pátios fora do ajuste, 5 grupos, 30 sorteios, sementes 42 a 71); nada é ajustado para atingir alvo.
#  Regra de decisão (antes dos resultados): o fator entra no EAR v3 se
#    (a) for estimável dentro das malhas: em pelo menos 3 malhas há 2 classes com 5% ou mais das células (sem contar "sem dado");
#    (b) alguma classe tiver risco relativo ajustado com IC 95% que exclui 1 (Mantel-Haenszel estratificado por malha, faixa de pátio e classe de raio aferidas);
#    (c) somado à regra aferida, elevar a AUC dentro das malhas em trechos fora do ajuste, com IC 95% pareado acima de zero.
#  Restrição acrescentada pelo gate loop (depois da primeira execução, em que G6 falhou: 0,016): no item 3, a base e a base + fator incluem o efeito fixo
#    da malha (indicadoras). Sem ele, qualquer variável que marque a malha, mesmo embaralhada, melhora a ordenação dentro das malhas porque corrige os pesos
#    das faixas, confundidos com as diferenças entre malhas; o ganho medido seria desse ajuste, não do fator. A tolerância do G6 não mudou.
#  Gates: G1 20.936 células; G2 2.123 km atingidos; G3 regra FICO 0,588; G4 RR da classe de referência = 1; G5 células por classe somam 20.936;
#         G6 placebo: o fator embaralhado dentro de cada malha muda a AUC dentro das malhas em no máximo 0,01 (média dos sorteios).
import time
t0 = time.time()
def faixas_p(d, c): return np.select([d <= c[0], d <= c[1], d <= c[2], d <= c[3]], [4, 3, 2, 1], 0)
def classes_r(r, c): return np.select([r < c[0], r < c[1], r < c[2]], [3, 2, 1], 0)
FICO_P, FICO_R, AFER_P, AFER_R, W_AFER = (300, 600, 1200, 1800), (500, 1200, 2300), (250, 1000, 1500, 3000), (250, 300, 600), 0.6
gate("G1 células em operação", N, 20936, source="notebook 11")
gate("G2 km com descarrilamento por via, 2011 a 2025", int(y.sum()), 2123, source="notebook 11")
gate("G3 regra do EAR (FICO) reconstruída", round(auc(y, 0.5 * faixas_p(dp, FICO_P) / 4 + 0.5 * classes_r(rg, FICO_R) / 3), 3), 0.588, tol=0.002, source="notebooks 24 e 27")
KPA, KRA = faixas_p(dp, AFER_P), classes_r(rg, AFER_R)                 # faixa de pátio (0 a 4) e classe de raio (0 a 3) aferidas
S_AFER = W_AFER * KPA / 4 + (1 - W_AFER) * KRA / 3

# 1. Classes de cada fator, declaradas antes (cortes de projeto; zero na Declaração de Rede = sem dado, exceto rampa)
def cls_num(col, cortes, rot, zero_na=True):
    v = pd.to_numeric(C[col], errors="coerce").values.astype(float)
    if zero_na: v[v <= 0] = np.nan
    k = np.digitize(np.nan_to_num(v, nan=-1), cortes, right=True); out = np.array(rot, dtype=object)[np.minimum(k, len(rot) - 1)]; out[np.isnan(v)] = "sem dado"; return out.astype(str)
def txt(col, mapa=None):                                                         # texto com ausente explícito (o pandas recente mantém NaN em colunas de texto)
    s = C[col].astype(object).where(C[col].notna(), "sem dado").astype(str).str.strip().replace({"NA": "sem dado", "nan": "sem dado", "": "sem dado"})
    return (s.replace(mapa) if mapa else s).values
PERF = C["perfil_trilho"].astype(str).str.extract(r"(\d+)")[0].astype(float).values
SIN = pd.Series(txt("sinalizacao"))
FAT = {
    "Bitola": txt("bitola"),
    "Velocidade máxima carregado (km/h)": cls_num("vma_carregado", [30, 40, 60], ["até 30", "31 a 40", "41 a 60", "acima de 60"]),
    "Rampa máxima (%)": cls_num("rampa_max_pct", [1.0, 1.5, 2.0], ["até 1,0", "1,0 a 1,5", "1,5 a 2,0", "acima de 2,0"], zero_na=False),
    "Carga por eixo (t)": cls_num("carga_eixo_t", [20, 25, 30], ["até 20", "20 a 25", "25 a 30", "acima de 30"]),
    "Tráfego (trens por dia vinculados)": np.where(pd.to_numeric(C["cap_vinc"], errors="coerce").fillna(0).values <= 0, "zero vinculado",
                                                   cls_num("cap_vinc", [1, 3, 10], ["até 1", "1 a 3", "3 a 10", "acima de 10"])),
    "Dormente": txt("dormente", {"Mad/Conc": "misto", "Mad/Aço": "misto"}),
    "Trilho": np.where(np.isnan(PERF), "sem dado", np.select([PERF <= 45, PERF <= 57], ["leve (até TR 45)", "médio (TR 50 a 57)"], "pesado (TR 60 ou mais)")),
    "Fixação": txt("fixacao"),
    "Taxa de dormentação (por km)": cls_num("taxa_dorm", [1667, 1750, 1790], ["até 1.667", "1.668 a 1.750", "1.751 a 1.790", "acima de 1.790"]),
    "Sinalização": np.select([SIN.str.contains("não sinal", case=False), SIN.eq("ABS"), SIN.isin(["CTC", "CBTC", "ATC"])], ["não sinalizado", "ABS", "CTC, CBTC ou ATC"], "TWE ou outro"),
    "Produto perigoso": txt("produto_perigoso"),
    "Número de linhas": txt("n_linhas"),
}
for k_, v_ in FAT.items(): gate(f"G5 {k_}: células por classe somam a malha", int(len(v_)), N, source="definição")
log_ia("29.1 classes", "Claude", "FOCUS: classes de cada fator por cortes de projeto declarados antes", "dicionário FAT", "somas")

# 2. Estimabilidade, risco relativo ajustado e taxa nacional por classe
NL = LINC.max() + 1; ESTR = pd.factorize(pd.Series(FERC).astype(str) + "|" + pd.Series(KPA).astype(str) + "|" + pd.Series(KRA).astype(str))[0]
def rr_mh_s(cls, K, ref, yy, w, S):
    ns = S.max() + 1; j = S * K + cls
    n_ = np.bincount(j, weights=w, minlength=ns * K).reshape(ns, K); a_ = np.bincount(j, weights=w * yy, minlength=ns * K).reshape(ns, K); out = np.full(K, np.nan)
    for k in range(K):
        T_ = n_[:, k] + n_[:, ref]; ok = T_ > 0; num = (a_[ok, k] * n_[ok, ref] / T_[ok]).sum(); den = (a_[ok, ref] * n_[ok, k] / T_[ok]).sum(); out[k] = num / den if den > 0 else np.nan
    return out
LIN_RR, LIN_EST = [], []
rng_ = np.random.default_rng(SEED); WB = [np.bincount(rng_.choice(NL, NL), minlength=NL)[LINC].astype(float) for _ in range(300)]
for nome, v in FAT.items():
    rot = [c for c in pd.Series(v).value_counts().index if c != "sem dado"] + (["sem dado"] if (v == "sem dado").any() else [])
    cod = np.array([rot.index(x) for x in v]); K = len(rot); ref = 0                      # referência: a classe com mais células
    t = pd.crosstab(FERC, v); t = t.drop(columns=[c for c in t.columns if c == "sem dado"]); frac = t.div(t.sum(1), axis=0)
    n_malhas = int(((frac >= 0.05).sum(1) >= 2).sum()); entre = 1 - float((frac.max(1) * t.sum(1)).sum() / t.values.sum())
    rr = rr_mh_s(cod, K, ref, y, np.ones(N), ESTR); rr_m = rr_mh_s(cod, K, ref, y, np.ones(N), FERC)
    B_ = np.array([rr_mh_s(cod, K, ref, y, w_, ESTR) for w_ in WB])
    for k in range(K):
        i = cod == k
        LIN_RR.append(dict(fator=nome, classe=rot[k], referencia=rot[ref], celulas=int(i.sum()), km_atingidos=int(y[i].sum()), taxa_nacional=float(y[i].mean()),
                           malhas_com_a_classe=int((t[rot[k]] > 0).sum()) if rot[k] in t.columns else 0,
                           rr_bruto_nacional=float(y[i].mean() / y[cod == ref].mean()), rr_dentro_malhas=float(rr_m[k]), rr_ajustado=float(rr[k]),
                           ic_inf=float(np.nanpercentile(B_[:, k], 2.5)), ic_sup=float(np.nanpercentile(B_[:, k], 97.5))))
    LIN_EST.append(dict(fator=nome, classes=K, malhas_com_2_classes=n_malhas, celulas_fora_da_classe_dominante_da_malha=entre, estimavel=n_malhas >= 3))
RRF = pd.DataFrame(LIN_RR); EST = pd.DataFrame(LIN_EST)
RRF["ic_exclui_1"] = (RRF["classe"] != RRF["referencia"]) & (RRF["classe"] != "sem dado") & ((RRF["ic_inf"] > 1) | (RRF["ic_sup"] < 1))
gate("G4 RR da classe de referência", float(RRF.loc[RRF["classe"] == RRF["referencia"], "rr_ajustado"].abs().max()), 1.0, tol=1e-9, source="definição")
display(EST.round(3)); display(RRF.round(3)); RRF.to_csv(f"{TAB}/29_risco_relativo_fatores.csv", index=False)
print("rr ok", round(time.time() - t0), "s"); sys.stdout.flush()
log_ia("29.2 risco relativo", "Claude", "FOCUS: Mantel-Haenszel por malha, faixa de pátio e classe de raio; IC por 300 reamostragens de linhas", "29_risco_relativo_fatores.csv", "referência = 1")

# 3. Ganho dentro das malhas ao somar cada fator à regra aferida (trechos inteiros fora; 30 sorteios) e placebo
def oh(v): return pd.get_dummies(pd.Series(v).astype(str), dtype=float).iloc[:, 1:].values
XB0 = np.column_stack([oh(KPA), oh(KRA)])                                       # sem malha: usado só na malha inteira fora (item 4), em que a malha é desconhecida
XB = np.column_stack([XB0, oh(FERC)])                                            # com efeito fixo da malha: base do ganho dentro das malhas (item 3)
XF = {k_: oh(v_) for k_, v_ in FAT.items()}
def placebo(v, seed):                                                           # embaralha o fator dentro de cada malha (mantém a distribuição por malha)
    r_ = np.random.default_rng(seed); v2 = np.array(v, dtype=object).copy()
    for f in range(FERC.max() + 1):
        i = np.where(FERC == f)[0]; v2[i] = v2[r_.permutation(i)]
    return oh(v2.astype(str))
LIN_G, GU29 = [], {}
for r in range(R):
    fo = folds_por(SEGC, SEED + r); S = {"base": np.zeros(N)}; S.update({k_: np.zeros(N) for k_ in FAT}); S["placebo"] = {k_: np.zeros(N) for k_ in FAT} if r < 10 else None
    XP = {k_: placebo(v_, 1000 + r) for k_, v_ in FAT.items()} if r < 10 else None
    for k in range(KF):
        te = fo == k; tr = ~te
        S["base"][te] = lr(XB[tr], y[tr], XB[te])
        for k_ in FAT:
            Xk = np.column_stack([XB, XF[k_]]); S[k_][te] = lr(Xk[tr], y[tr], Xk[te])
            if r < 10: Xp = np.column_stack([XB, XP[k_]]); S["placebo"][k_][te] = lr(Xp[tr], y[tr], Xp[te])
    ab, am = auc(y, S["base"]), auc_grupo(S["base"], y, FERC)
    for k_ in FAT:
        LIN_G.append(dict(sorteio=r + 1, fator=k_, auc_pais_base=ab, auc_malhas_base=am, auc_pais=auc(y, S[k_]), auc_malhas=auc_grupo(S[k_], y, FERC),
                          placebo_malhas=auc_grupo(S["placebo"][k_], y, FERC) if r < 10 else np.nan))
    if r < 10: GU29[r] = {k_: S[k_] for k_ in ["base"] + list(FAT)}
    if r in (0, 9, 29): print("sorteio", r + 1, round(time.time() - t0), "s"); sys.stdout.flush()
G29 = pd.DataFrame(LIN_G); G29["ganho_malhas"] = G29["auc_malhas"] - G29["auc_malhas_base"]; G29["ganho_pais"] = G29["auc_pais"] - G29["auc_pais_base"]; G29["placebo_ganho"] = G29["placebo_malhas"] - G29["auc_malhas_base"]
G29.to_csv(f"{TAB}/29_ganho_por_sorteio.csv", index=False)
gate_between("G6 placebo: maior ganho médio com o fator embaralhado dentro da malha", round(float(G29.groupby("fator")["placebo_ganho"].mean().abs().max()), 4), 0.0, 0.01, source="acaso")
# IC 95% pareado por reamostragem de linhas inteiras (10 primeiros sorteios, 300 reamostragens), como nos notebooks 24 e 27
rng = np.random.default_rng(SEED); Lu = np.unique(LINC); ix = {l: np.where(LINC == l)[0] for l in Lu}; BT = {k_: [] for k_ in FAT}
for b in range(300):
    i = np.concatenate([ix[l] for l in rng.choice(Lu, len(Lu))])
    if y[i].sum() < 50: continue
    base_m = [auc_grupo(GU29[r]["base"][i], y[i], FERC[i]) for r in range(10)]
    for k_ in FAT: BT[k_].append(np.mean([auc_grupo(GU29[r][k_][i], y[i], FERC[i]) - base_m[r] for r in range(10)]))
RES29 = G29.groupby("fator").agg(auc_malhas_base=("auc_malhas_base", "mean"), auc_malhas=("auc_malhas", "mean"), ganho_malhas=("ganho_malhas", "mean"),
                                 sorteios_com_ganho=("ganho_malhas", lambda s: int((s > 0).sum())), ganho_pais=("ganho_pais", "mean"), placebo=("placebo_ganho", "mean")).reset_index()
RES29["ic_inf"] = [np.percentile(BT[k_], 2.5) for k_ in RES29["fator"]]; RES29["ic_sup"] = [np.percentile(BT[k_], 97.5) for k_ in RES29["fator"]]
print("bootstrap ok", round(time.time() - t0), "s"); sys.stdout.flush()

# 4. Malha inteira fora do ajuste (simula a ferrovia nova): base e base + fator, AUC na malha deixada de fora, média ponderada pelos km atingidos
LIN_M = []
for f in range(FERC.max() + 1):
    te = FERC == f; tr = ~te
    if y[te].sum() < 5: continue
    sb = lr(XB0[tr], y[tr], XB0[te]); reg = dict(malha=C["ferrovia"].values[te][0], atingidas=int(y[te].sum()), base=auc(y[te], sb))
    for k_ in FAT:
        Xk = np.column_stack([XB0, XF[k_]]); reg[k_] = auc(y[te], lr(Xk[tr], y[tr], Xk[te]))
    LIN_M.append(reg)
MF29 = pd.DataFrame(LIN_M); MF29.to_csv(f"{TAB}/29_malha_fora.csv", index=False)
wm = MF29["atingidas"]
RES29["malha_fora_base"] = float(np.average(MF29["base"], weights=wm)); RES29["malha_fora_com_fator"] = [float(np.average(MF29[k_], weights=wm)) for k_ in RES29["fator"]]
RES29["malhas_em_que_ajuda"] = [int((MF29[k_] > MF29["base"]).sum()) for k_ in RES29["fator"]]
# 4b. Multiplicidade (pedido da revisão externa 3): valor-p unilateral do ganho pela reamostragem de linhas e correção de Holm (1979) nos 12 fatores
RES29["p_unilateral"] = [(1 + int((np.array(BT[k_]) <= 0).sum())) / (1 + len(BT[k_])) for k_ in RES29["fator"]]
ordem_ = np.argsort(RES29["p_unilateral"].values); m_ = len(ordem_); adj_ = np.empty(m_); acc_ = 0.0
for rank_, j_ in enumerate(ordem_): acc_ = max(acc_, min(1.0, (m_ - rank_) * RES29["p_unilateral"].values[j_])); adj_[j_] = acc_
RES29["p_holm"] = adj_
# 5. Regra de decisão, aplicada como foi escrita
EST_ = EST.set_index("fator"); RR_ = RRF.groupby("fator")["ic_exclui_1"].any()
RES29["a_estimavel"] = [bool(EST_.loc[k_, "estimavel"]) for k_ in RES29["fator"]]; RES29["b_rr_ic_exclui_1"] = [bool(RR_[k_]) for k_ in RES29["fator"]]
RES29["c_ganho_ic_acima_de_zero"] = RES29["ic_inf"] > 0; RES29["entra_no_EAR_v3"] = RES29["a_estimavel"] & RES29["b_rr_ic_exclui_1"] & RES29["c_ganho_ic_acima_de_zero"]
RES29["entra_com_Holm"] = RES29["a_estimavel"] & RES29["b_rr_ic_exclui_1"] & (RES29["p_holm"] < 0.05)
RES29 = RES29.merge(EST[["fator", "malhas_com_2_classes", "celulas_fora_da_classe_dominante_da_malha"]], on="fator").sort_values("ganho_malhas", ascending=False)
display(RES29.round(4)); RES29.to_csv(f"{TAB}/29_decisao_fatores.csv", index=False)
print("fatores aprovados:", RES29.loc[RES29["entra_no_EAR_v3"], "fator"].tolist(), round(time.time() - t0), "s")
log_ia("29.3 ganho e decisão", "Claude", "FOCUS: base = faixas aferidas com pesos aprendidos; base + fator; 30 sorteios; IC por linhas; malha inteira fora; regra de decisão declarada antes",
       "29_ganho_por_sorteio.csv, 29_malha_fora.csv, 29_decisao_fatores.csv", "placebo e referência")

# 6. Conciliação com o artigo (pedido da revisão externa 3): o artigo diz que os atributos declarados não acrescentam nada mensurável dentro das malhas
#    (logística com critérios contínuos e atributos contra só os critérios contínuos, sem efeito fixo de malha: +0,009). Teste que decide, declarado antes:
#    se, com efeito fixo de malha e critérios contínuos (distância sem teto), o tráfego ainda acrescentar com IC acima de zero, a frase do artigo precisa mudar;
#    se o ganho cair para perto de zero, a distância contínua já carrega a informação do tráfego e a frase fica, com ressalva.
FE_ = oh(FERC); XTRAF = XF["Tráfego (trens por dia vinculados)"]
MOD6 = {"contínuos": XE, "contínuos + malha": np.column_stack([XE, FE_]), "contínuos + malha + tráfego": np.column_stack([XE, FE_, XTRAF]),
        "contínuos + atributos (artigo)": X0, "contínuos + atributos + malha": np.column_stack([X0, FE_])}
L6, GU6 = [], {}
for r in range(R):
    fo = folds_por(SEGC, SEED + r); S6 = {k_: np.zeros(N) for k_ in MOD6}
    for k in range(KF):
        te = fo == k
        for k_, X_ in MOD6.items(): S6[k_][te] = lr(X_[~te], y[~te], X_[te])
    for k_ in MOD6: L6.append(dict(sorteio=r + 1, modelo=k_, auc_malhas=auc_grupo(S6[k_], y, FERC), auc_linhas=auc_grupo(S6[k_], y, LINC)))
    if r < 10: GU6[r] = S6
T6 = pd.DataFrame(L6); P6 = T6.pivot_table(index="sorteio", columns="modelo", values="auc_malhas")
PAR6 = [("contínuos + malha + tráfego", "contínuos + malha"), ("contínuos + atributos (artigo)", "contínuos"), ("contínuos + atributos + malha", "contínuos + malha")]
rng6 = np.random.default_rng(SEED); B6 = {pq: [] for pq in PAR6}
for b in range(300):
    i = np.concatenate([ix[l] for l in rng6.choice(Lu, len(Lu))])
    if y[i].sum() < 50: continue
    for a_, c_ in PAR6: B6[(a_, c_)].append(np.mean([auc_grupo(GU6[r][a_][i], y[i], FERC[i]) - auc_grupo(GU6[r][c_][i], y[i], FERC[i]) for r in range(10)]))
CONC = pd.DataFrame([dict(comparacao=f"{a_} − {c_}", ganho_malhas=float((P6[a_] - P6[c_]).mean()), ic_inf=float(np.percentile(B6[(a_, c_)], 2.5)), ic_sup=float(np.percentile(B6[(a_, c_)], 97.5)),
                          sorteios_com_ganho=int(((P6[a_] - P6[c_]) > 0).sum())) for a_, c_ in PAR6])
display(T6.groupby("modelo")[["auc_malhas", "auc_linhas"]].mean().round(3)); display(CONC.round(3)); CONC.to_csv(f"{TAB}/29_conciliacao_artigo.csv", index=False)
gate("reprodução do artigo: contínuos + atributos − contínuos, dentro das malhas", round(float(CONC.loc[1, "ganho_malhas"]), 3), 0.009, tol=0.003, source="24_diferencas.csv (+0,009)")
log_ia("29.4 conciliação", "Claude", "FOCUS: critérios contínuos com e sem efeito fixo de malha e tráfego; mesmo protocolo; IC por linhas", "29_conciliacao_artigo.csv", "reproduz o +0,009 do artigo")
