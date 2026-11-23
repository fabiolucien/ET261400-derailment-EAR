# 28 · Auditoria dos sorteios: os resultados dependem do acaso da partição?
# FOCUS (declarado antes do código)
#  F: auditoria metodológica do protocolo de validação do artigo (trechos inteiros entre pátios fora do ajuste, 5 grupos, 30 sorteios, sementes 42 a 71).
#  O: mostrar, com dados, que (i) a partição é correta, (ii) 30 sorteios bastam, (iii) o resultado não é obra do acaso, (iv) o bloco espacial é maior que o alcance da dependência espacial.
#  C: matriz de células e eventos do notebook 11; funções do notebook 27 (folds_por, auc, auc_grupo, lr, X0, B2).
#  U: só dados públicos; mesmas sementes; nada é ajustado para atingir alvo.
#  Gates (respostas conhecidas e tolerâncias, com fonte):
#   G1 cada trecho entre pátios cai em um único grupo em cada sorteio: 30 de 30 (definição do protocolo)
#   G2 cada célula recebe exatamente uma nota fora do ajuste por sorteio: 20.936 (notebook 11)
#   G3 todo grupo tem quilômetros com descarrilamento: mínimo de pelo menos 100 (2.123 / 5 = 425 em média)
#   G4 regra do EAR (FICO) = 0,588 (notebook 24 e dissertação), tol 0,002
#   G5 logística com atributos, média de 30 sorteios, recalculada aqui = 0,759 (tabela 24_modelos_resumo), tol 0,002
#   G6 teste de permutação: média da AUC com rótulos embaralhados entre 0,45 e 0,55 (acaso = 0,50)
import time
t0 = time.time()

# 1. Integridade da partição em cada sorteio
LINHAS = []
for r in range(R):
    fo = folds_por(SEGC, SEED + r)
    seg_fold = pd.DataFrame({"seg": SEGC, "f": fo}).groupby("seg")["f"].nunique()
    por_grupo = pd.DataFrame({"f": fo, "y": y, "km": LN}).groupby("f").agg(celulas=("y", "size"), atingidas=("y", "sum"), km=("km", "sum"))
    LINHAS.append({"sorteio": r + 1, "semente": SEED + r, "trechos_divididos": int((seg_fold > 1).sum()), "celulas_avaliadas": int(len(fo)),
                   "min_celulas_grupo": int(por_grupo["celulas"].min()), "max_celulas_grupo": int(por_grupo["celulas"].max()),
                   "min_atingidas_grupo": int(por_grupo["atingidas"].min()), "max_atingidas_grupo": int(por_grupo["atingidas"].max()),
                   "taxa_min_grupo": float((por_grupo["atingidas"] / por_grupo["celulas"]).min()), "taxa_max_grupo": float((por_grupo["atingidas"] / por_grupo["celulas"]).max())})
P = pd.DataFrame(LINHAS)
gate("G1 trechos divididos entre grupos (todos os sorteios)", int(P["trechos_divididos"].sum()), 0, source="definição do protocolo")
gate("G2 células avaliadas por sorteio", int(P["celulas_avaliadas"].min()), N, source="notebook 11")
gate_between("G3 mínimo de km atingidos em um grupo", int(P["min_atingidas_grupo"].min()), 100, 2123, source="2.123 / 5 = 425 em média")
P.to_csv(f"{TAB}/28_particoes_por_sorteio.csv", index=False)

# 2. Logística com atributos recalculada nos 30 sorteios (rota independente da tabela do notebook 24)
gate("G4 regra do EAR (FICO)", round(auc(y, B2), 3), 0.588, tol=0.002, source="notebook 24 e dissertação v4")
AUCS = []
for r in range(R):
    fo = folds_por(SEGC, SEED + r); s = np.zeros(N)
    for k in range(KF):
        te = fo == k; s[te] = lr(X0[~te], y[~te], X0[te])
    AUCS.append({"sorteio": r + 1, "auc_pais": auc(y, s), "auc_malhas": auc_grupo(s, y, FERC)})
A = pd.DataFrame(AUCS)
gate("G5 logística com atributos, média de 30 sorteios", round(A["auc_pais"].mean(), 3), 0.759, tol=0.002, source="24_modelos_resumo.csv")
# estabilidade de Monte Carlo: média acumulada e erro-padrão da média
A["media_acumulada"] = A["auc_pais"].expanding().mean(); A["ep_media"] = A["auc_pais"].expanding().std() / np.sqrt(A["sorteio"])
A.to_csv(f"{TAB}/28_logistica_por_sorteio.csv", index=False)
EST = {"media_30": A["auc_pais"].mean(), "dp_entre_sorteios": A["auc_pais"].std(), "min": A["auc_pais"].min(), "max": A["auc_pais"].max(),
       "ep_media_30": A["auc_pais"].std() / np.sqrt(R), "media_10": A["auc_pais"].iloc[:10].mean(), "media_20": A["auc_pais"].iloc[:20].mean(),
       "malhas_media": A["auc_malhas"].mean(), "malhas_dp": A["auc_malhas"].std()}
print("estabilidade:", {k: round(v, 4) for k, v in EST.items()}, round(time.time() - t0), "s"); sys.stdout.flush()

# 3. Teste de permutação (rótulos embaralhados entre células), mesma partição do sorteio 1
B = 100; fo = folds_por(SEGC, SEED); rng = np.random.default_rng(2026); NUL = []
obs = A.loc[0, "auc_pais"]; obs_m = A.loc[0, "auc_malhas"]
for b in range(B):
    yp = rng.permutation(y); s = np.zeros(N)
    for k in range(KF):
        te = fo == k; s[te] = lr(X0[~te], yp[~te], X0[te])
    NUL.append({"perm": b + 1, "auc_pais": auc(yp, s), "auc_malhas": auc_grupo(s, yp, FERC)})
NU = pd.DataFrame(NUL)
gate_between("G6 média da AUC com rótulos embaralhados", round(NU["auc_pais"].mean(), 3), 0.45, 0.55, source="acaso = 0,50")
p_pais = (1 + (NU["auc_pais"] >= obs).sum()) / (1 + B); p_malhas = (1 + (NU["auc_malhas"] >= obs_m).sum()) / (1 + B)
NU.to_csv(f"{TAB}/28_permutacao_rotulos.csv", index=False)
print("permutação:", round(NU["auc_pais"].mean(), 3), round(NU["auc_pais"].max(), 3), "obs", round(obs, 3), "p", round(p_pais, 3), "| malhas", round(NU["auc_malhas"].max(), 3), "obs", round(obs_m, 3), "p", round(p_malhas, 3), round(time.time() - t0), "s"); sys.stdout.flush()

# 4. Nulo que mantém o agrupamento espacial: deslocamento circular do vetor de descarrilamentos ao longo da malha ordenada
#    (as células estão ordenadas por ferrovia, linha e km; o deslocamento preserva a distância entre quilômetros atingidos)
DESL = []; rng2 = np.random.default_rng(2027)
for b in range(B):
    sh = int(rng2.integers(500, N - 500)); yp = np.roll(y, sh); s = np.zeros(N)
    for k in range(KF):
        te = fo == k; s[te] = lr(X0[~te], yp[~te], X0[te])
    DESL.append({"perm": b + 1, "deslocamento": sh, "auc_pais": auc(yp, s), "auc_malhas": auc_grupo(s, yp, FERC)})
DS = pd.DataFrame(DESL); DS.to_csv(f"{TAB}/28_deslocamento_circular.csv", index=False)
p_desl = (1 + (DS["auc_pais"] >= obs).sum()) / (1 + B); p_desl_m = (1 + (DS["auc_malhas"] >= obs_m).sum()) / (1 + B)
print("deslocamento:", round(DS["auc_pais"].mean(), 3), round(DS["auc_pais"].max(), 3), "p", round(p_desl, 3), "| malhas", round(DS["auc_malhas"].mean(), 3), round(DS["auc_malhas"].max(), 3), "p", round(p_desl_m, 3), round(time.time() - t0), "s"); sys.stdout.flush()

# 5. Alcance da dependência espacial ao longo da linha e tamanho dos blocos
#    razão = P(km i+d atingido | km i atingido) / taxa-base da linha, para d de 1 a 40 km, na mesma linha
RAZ = []
lin_km = pd.DataFrame({"lin": LINC, "km": np.round(KM).astype(int), "y": y})
for d in range(1, 41):
    num = den = esp = 0.0
    for l, g in lin_km.groupby("lin"):
        if g["y"].sum() == 0: continue
        m = dict(zip(g["km"], g["y"])); base = g["y"].mean()
        pares = [(m[k], m[k + d]) for k in m if (k + d) in m]
        if not pares: continue
        a = np.array(pares); hit = a[:, 0] == 1
        num += a[hit, 1].sum(); den += hit.sum(); esp += hit.sum() * base
    RAZ.append({"distancia_km": d, "prob_condicional": num / den, "esperado_sem_dependencia": esp / den, "razao": (num / den) / (esp / den)})
RZ = pd.DataFrame(RAZ); RZ.to_csv(f"{TAB}/28_dependencia_espacial.csv", index=False)
alc = int(RZ.loc[RZ["razao"] < 1.10, "distancia_km"].min()) if (RZ["razao"] < 1.10).any() else 40
seg_len = pd.DataFrame({"seg": SEGC, "km": LN, "y": y}).groupby("seg").agg(km=("km", "sum"), y=("y", "sum"))
EST.update({"alcance_km_razao_menor_1_1": alc, "mediana_km_trecho": float(seg_len["km"].median()),
            "km_atingidos_em_trechos_maiores_que_alcance": float(seg_len.loc[seg_len["km"] > alc, "y"].sum() / seg_len["y"].sum()),
            "p_permutacao_pais": p_pais, "p_permutacao_malhas": p_malhas, "p_deslocamento_pais": p_desl, "p_deslocamento_malhas": p_desl_m,
            "nulo_perm_media": NU["auc_pais"].mean(), "nulo_perm_max": NU["auc_pais"].max(), "nulo_desl_media": DS["auc_pais"].mean(), "nulo_desl_max": DS["auc_pais"].max(),
            "nulo_desl_malhas_media": DS["auc_malhas"].mean(), "nulo_desl_malhas_max": DS["auc_malhas"].max(), "obs_sorteio1": obs, "obs_malhas_sorteio1": obs_m})
pd.Series(EST).to_csv(f"{TAB}/28_resumo_auditoria.csv", header=["valor"])
print(RZ.head(12).round(3).to_string()); print("alcance", alc, "mediana trecho", EST["mediana_km_trecho"], "parcela", round(EST["km_atingidos_em_trechos_maiores_que_alcance"], 3))
log_ia("28 auditoria dos sorteios", "Claude", "FOCUS: integridade da partição, estabilidade de Monte Carlo, permutação, deslocamento circular, alcance espacial", "28_*.csv", "6 gates")
print("fim", round(time.time() - t0), "s")
