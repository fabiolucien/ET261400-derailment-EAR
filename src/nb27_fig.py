# Figura do artigo: aferição das faixas do EAR (perfil brasileiro dentro das malhas e extensão física nos EUA). Estilo da dissertação.
import os, matplotlib, matplotlib.font_manager as fm
for f_ in ("lmsans10-regular.otf", "lmsans10-bold.otf", "lmsans10-oblique.otf"):
    for d_ in (f"{BASE}/data/fonts", "/usr/share/texmf/fonts/opentype/public/lm"):
        if os.path.exists(f"{d_}/{f_}"): fm.fontManager.addfont(f"{d_}/{f_}"); break
FONTE = "Latin Modern Sans" if any(f.name == "Latin Modern Sans" for f in fm.fontManager.ttflist) else "DejaVu Sans"
matplotlib.rcParams.update({"font.family": FONTE, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#7A8089", "axes.linewidth": 0.6, "xtick.color": "#16191C", "ytick.color": "#16191C"})
import matplotlib.pyplot as plt
INK, MUTE, FAINT, GRID, TEAL, CLAY, GOLD = "#16191C", "#7A8089", "#C9CCD1", "#E6E8EB", "#1E6E6E", "#BD4B2C", "#8C6D1F"
TXT = {"en": dict(pa="(a) Distance to the nearest yard", pb="(b) Minimum curve radius", pc="(c) Derailed block (US)",
                  xa="Distance class (km)", xb="Radius class (m)", xc="Metres, for the 1,690 m design train", ya="Relative risk within networks", yc="Derailments (%)",
                  rows=("FICO", "FNS", "Recal."), cls=("VH", "H", "M", "L", "–"), all_="All track causes (n = {n})", sw="Turnouts and switches (n = {n})",
                  lp=["Yard\ncell", "0.25–\n1", "1–\n1.5", "1.5–\n2", "2–\n3", "3–\n5", "5–20\nref.", ">20"], lr=["<300", "300–\n400", "400–\n500", "500–\n800", "800–\n1200", "1200–\n2300", ">2300\nref."],
                  fico="FICO bands", fns="FNS bands", ref="reference class", chave="Rows: class that each rule gives to most cells of the\ncolumn. VH very high, H high, M moderate, L low,\n– outside the bands. Recal.: recalibrated in this study.\nBars: 95% CI from 300 resamples of whole lines."),
       "pt": dict(pa="(a) Distância ao pátio mais próximo", pb="(b) Raio mínimo de curva", pc="(c) Bloco descarrilado, EUA",
                  xa="Classe de distância (km)", xb="Classe de raio (m)", xc="Metros, no trem-tipo de 1.690 m", ya="Risco relativo dentro das malhas", yc="Descarrilamentos (%)",
                  rows=("FICO", "FNS", "Aferida"), cls=("MA", "A", "M", "B", "–"), all_="Todas as causas de via (n = {n})", sw="AMV e chaves (n = {n})",
                  lp=["Pátio", "0,25–\n1", "1–\n1,5", "1,5–\n2", "2–\n3", "3–\n5", "5–20\nref.", ">20"], lr=["<300", "300–\n400", "400–\n500", "500–\n800", "800–\n1200", "1200–\n2300", ">2300\nref."],
                  fico="faixas da FICO", fns="faixas da FNS", ref="classe de referência", chave="Linhas: classe que cada regra dá à maioria das células\nda coluna. MA muito alta, A alta, M moderada, B baixa,\n– fora das faixas. Aferida: recalibrada neste estudo.\nBarras: IC 95% por 300 reamostragens de linhas.")}
SHADE = {4: (CLAY, 1.0), 3: (CLAY, 0.62), 2: (CLAY, 0.34), 1: (CLAY, 0.14), 0: ("#FFFFFF", 0.0)}
def moda_classe(cls_bin, cls_regra, K):
    return [int(np.bincount(cls_regra[cls_bin == k]).argmax()) if (cls_bin == k).any() else 0 for k in range(K)]
def faixa_texto(v, n_niveis):                       # 4 níveis para o pátio (4..0); 3 para o raio (3..0) mapeados para MA, A, M, B
    return v if n_niveis == 4 else v + 1          # no raio, a classe baixa (tangente e raios grandes) existe no EAR: 0 pontos = B
def painel_rr(a, P_, lab, ref, faixas, n_niveis, T_, titulo, xl):
    x = np.arange(len(P_)); rr = P_["rr_dentro_malhas"].values; lo = P_["ic_inf"].values; hi = P_["ic_sup"].values
    a.axhline(1.0, color=MUTE, lw=0.8, ls=(0, (4, 3)), zorder=1)
    for i in x:
        if i == ref: a.plot(i, 1.0, "o", ms=5.5, mfc="white", mec=MUTE, mew=1.1, zorder=4); continue
        a.plot([i, i], [lo[i], hi[i]], color=TEAL, lw=1.4, solid_capstyle="butt", zorder=3); a.plot(i, rr[i], "o", ms=5.5, color=TEAL, mec="white", mew=0.9, zorder=4)
    a.set_xticks(x); a.set_xticklabels(lab, fontsize=7.2, color=INK, linespacing=0.95); a.set_xlim(-0.6, len(P_) - 0.4); a.set_ylim(0, 2.6)
    a.grid(axis="y", color=GRID, lw=0.6); a.set_axisbelow(True); a.tick_params(axis="y", labelsize=7.8); a.tick_params(axis="x", length=0, pad=3)
    a.set_title(titulo, loc="left", fontsize=9.2, color=INK, fontweight="bold", pad=6); a.set_xlabel(xl, fontsize=8.0, color=INK, labelpad=2)
    for j, (nome, cl) in enumerate(zip(T_["rows"], faixas)):          # faixa das classes que cada regra atribui
        yy = -0.76 - 0.27 * j
        a.text(-0.75, yy, nome, ha="right", va="center", fontsize=7.2, color=INK, transform=a.get_yaxis_transform() if False else a.transData, clip_on=False)
        for i in x:
            v = faixa_texto(cl[i], n_niveis); cor, al = SHADE[v]
            a.add_patch(plt.Rectangle((i - 0.46, yy - 0.12), 0.92, 0.24, transform=a.transData, facecolor=cor, alpha=al if v else 1.0, edgecolor=FAINT if not v else "none", lw=0.5, clip_on=False, zorder=2))
            a.text(i, yy, T_["cls"][4 - v], ha="center", va="center", fontsize=6.8, color="white" if v >= 3 else INK, clip_on=False, zorder=3)
def figura_27(lang="en", arq=None):
    T_ = TXT[lang]; fig = plt.figure(figsize=(7.4, 3.5), dpi=300); gs = fig.add_gridspec(1, 3, width_ratios=[1.12, 1.0, 0.95], wspace=0.36, left=0.075, right=0.985, top=0.87, bottom=0.33)
    a, b, c = fig.add_subplot(gs[0]), fig.add_subplot(gs[1]), fig.add_subplot(gs[2])
    fp = [moda_classe(KP_, faixas_p(dp, FICO_P), 8), moda_classe(KP_, faixas_p(dp, FNS_P), 8), moda_classe(KP_, faixas_p(dp, MODA_P), 8)]
    fr = [moda_classe(KR_, classes_r(rg, FICO_R), 7), moda_classe(KR_, classes_r(rg, FNS_R), 7), moda_classe(KR_, classes_r(rg, MODA_R), 7)]
    painel_rr(a, PP, T_["lp"], REF_P, fp, 4, T_, T_["pa"], T_["xa"]); a.set_ylabel(T_["ya"], fontsize=7.8, color=INK)
    painel_rr(b, PR, T_["lr"], REF_R, fr, 3, T_, T_["pb"], T_["xb"])
    for g_, cor, ls, nome in [(FM, INK, "-", T_["all_"]), (FM[FM["aparelho"]], TEAL, "-", T_["sw"])]:
        v = np.sort(g_["fracao"].values * L_TREM); c.step(np.concatenate([[0], v]), np.linspace(0, 100, len(v) + 1), where="post", color=cor, lw=1.4, ls=ls, label=nome.format(n=(f"{len(g_):,}" if lang == "en" else f"{len(g_):,}".replace(",", "."))))
    for lim, cor, yy, nome in [(FICO_P, CLAY, 105, "FICO"), (FNS_P, GOLD, 112, "FNS")]:
        c.plot([0, 1800], [yy, yy], color=FAINT, lw=0.6, clip_on=False)
        for v in lim:
            if v <= 1800: c.plot([v, v], [yy - 2.4, yy + 2.4], color=cor, lw=1.4, clip_on=False, solid_capstyle="butt")
        c.text(-60, yy, nome, fontsize=7.0, color=cor, va="center", ha="right", clip_on=False, fontweight="bold")
    c.set_xlim(0, 1800); c.set_ylim(0, 100); c.set_xticks([0, 400, 800, 1200, 1600]); c.set_xticklabels(["0", "400", "800", "1,200" if lang == "en" else "1.200", "1,600" if lang == "en" else "1.600"]); c.tick_params(labelsize=7.8)
    c.grid(color=GRID, lw=0.6); c.set_axisbelow(True); c.set_xlabel(T_["xc"], fontsize=7.8, color=INK, labelpad=2); c.set_ylabel(T_["yc"], fontsize=7.8, color=INK)
    c.set_title(T_["pc"], loc="left", fontsize=9.2, color=INK, fontweight="bold", pad=22); c.legend(frameon=False, fontsize=7.0, loc="lower right", handlelength=1.6)
    fig.text(0.705, 0.16, T_["chave"], fontsize=6.9, color=MUTE, ha="left", va="center", linespacing=1.35)
    if arq: fig.savefig(arq, dpi=300, facecolor="white"); print("figura:", arq)
    return fig
fig = figura_27("en", f"{FIG}/27_aferição_faixas_ear.png".replace("ç", "c").replace("ã", "a")); plt.show()
fig = figura_27("pt", f"{FIG}/27_afericao_faixas_ear_PT.png"); plt.show()
