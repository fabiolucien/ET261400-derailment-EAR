import time; t0 = time.time()
OUT = Parallel(n_jobs=2, batch_size=2)(delayed(avalia)(*j) for j in J); OUT = [o for o in OUT if o]
R = pd.DataFrame([l for o in OUT for l in o[0]]); GUARDA = [o[1] for o in OUT]; print("minutos:", round((time.time() - t0) / 60, 1), "| avaliações válidas:", len(OUT), "| linhas:", len(R))
R.to_csv(f"{TAB}/21_validacao_temporal_por_avaliacao.csv", index=False)
MET = ["Regra do EAR por faixas", "Dummy: taxa da malha", "EAR calibrado (atributos da via)", "EAR calibrado + histórico de acidentes"]
g = R.groupby(["desenho", "rotulo", "metodo"], sort=False)[["auc", "auc_dentro", "classe_muito_alta"]].agg(["mean", "min", "max"]); g[("n", "")] = R.groupby(["desenho", "rotulo", "metodo"], sort=False).size(); g = g.round(3); g.to_csv(f"{TAB}/21_validacao_temporal_resumo.csv")
res = R.pivot_table(index=["desenho", "rotulo"], columns="metodo", values="auc", aggfunc="mean", sort=False)[[m for m in MET if m in R.metodo.unique()]].round(3); res["n"] = R[R.metodo == MET[0]].groupby(["desenho", "rotulo"], sort=False).size(); display(res)
print("== AUC dentro da malha =="); display(R.pivot_table(index=["desenho", "rotulo"], columns="metodo", values="auc_dentro", aggfunc="mean", sort=False)[[m for m in MET if m in R.metodo.unique()]].round(3))
print("== Por desenho (todas as configurações) =="); d = R.groupby(["desenho", "metodo"], sort=False)["auc"].agg(["mean", "min", "max", "count"]).round(3); display(d); d.to_csv(f"{TAB}/21_validacao_temporal_por_desenho.csv")
# reprodução do notebook 18: D1, H=3, origens de 2015 a 2022
p = R[(R.desenho.str.startswith("D1")) & (R.rotulo == "H=3") & (R.conf_ini >= 2016) & (R.metodo == "EAR calibrado (atributos da via)")]["auc"].mean(); gate("D1 com H=3 e origens de 2015 a 2022 reproduz o notebook 18", round(float(p), 3), 0.752, tol=0.002, source="notebook 18")
p = R[(R.desenho.str.startswith("D1")) & (R.rotulo == "H=3") & (R.conf_ini >= 2016) & (R.metodo == "EAR calibrado + histórico de acidentes")]["auc"].mean(); gate("idem, com histórico", round(float(p), 3), 0.791, tol=0.002, source="notebook 18")
pv = R.pivot_table(index=["desenho", "rotulo", "calibra", "confere"], columns="metodo", values="auc"); dif = pv["EAR calibrado (atributos da via)"] - pv["Regra do EAR por faixas"]
print("EAR calibrado acima da regra em", int((dif > 0).sum()), "de", int(dif.notna().sum()), "avaliações; diferença média", round(dif.mean(), 3), "| mínima", round(dif.min(), 3), "| máxima", round(dif.max(), 3))
# intervalo de 95% da média por desenho, por reamostragem de linhas inteiras (notas fixas; 300 reamostragens)
rng = np.random.default_rng(SEED); cel_lin = [np.where(LINC == l)[0] for l in range(LINC.max() + 1)]; amostras = [np.concatenate([cel_lin[l] for l in rng.integers(0, len(cel_lin), len(cel_lin))]) for _ in range(300)]; L = []
for chave in dict.fromkeys((gq[0], gq[1]) for gq in GUARDA):
    itens = [gq for gq in GUARDA if (gq[0], gq[1]) == chave]
    for m in MET:
        im = [gq for gq in itens if m in gq[5]]
        if not im: continue
        bs = [np.nanmean([auc(gq[4][ii], gq[5][m][ii]) for gq in im]) for ii in amostras]; L.append(dict(desenho=chave[0], rotulo=chave[1], metodo=m, n=len(im), media=np.nanmean([auc(gq[4], gq[5][m]) for gq in im]), ic95_inf=np.nanpercentile(bs, 2.5), ic95_sup=np.nanpercentile(bs, 97.5)))
IC = pd.DataFrame(L).round(3); IC.to_csv(f"{TAB}/21_validacao_temporal_ic95.csv", index=False); display(IC[IC.metodo.str.startswith("EAR calibrado")])
log_ia("21.2 bateria executada", "Claude", "FOCUS: cinco desenhos declarados; todos reportados; IC por reamostragem de linhas", "21_validacao_temporal_*.csv", "2 gates de reprodução do notebook 18")
