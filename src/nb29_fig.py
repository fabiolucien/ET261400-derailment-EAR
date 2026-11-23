# Figura 29: risco relativo de cada classe de fator, nacional bruto e dentro das malhas ajustado pelas faixas aferidas. Estilo da dissertação.
import os, matplotlib, matplotlib.font_manager as fm
for f_ in ("lmsans10-regular.otf", "lmsans10-bold.otf", "lmsans10-oblique.otf"):
    for d_ in (f"{BASE}/data/fonts", "/usr/share/texmf/fonts/opentype/public/lm"):
        if os.path.exists(f"{d_}/{f_}"): fm.fontManager.addfont(f"{d_}/{f_}"); break
FONTE = "Latin Modern Sans" if any(f.name == "Latin Modern Sans" for f in fm.fontManager.ttflist) else "DejaVu Sans"
matplotlib.rcParams.update({"font.family": FONTE, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#7A8089", "axes.linewidth": 0.6})
import matplotlib.pyplot as plt
INK, MUTE, FAINT, TEAL, CLAY = "#16191C", "#7A8089", "#C9CCD1", "#1E6E6E", "#BD4B2C"
RRF_ = pd.read_csv(f"{TAB}/29_risco_relativo_fatores.csv"); DEC_ = pd.read_csv(f"{TAB}/29_decisao_fatores.csv").set_index("fator")
ORDEM = ["Tráfego (trens por dia vinculados)", "Carga por eixo (t)", "Velocidade máxima carregado (km/h)", "Rampa máxima (%)", "Dormente", "Trilho", "Fixação",
         "Taxa de dormentação (por km)", "Sinalização", "Produto perigoso", "Número de linhas", "Bitola"]
linhas = []
for f_ in ORDEM:
    g = RRF_[(RRF_["fator"] == f_) & (RRF_["classe"] != RRF_["referencia"]) & (RRF_["classe"] != "sem dado") & RRF_["rr_ajustado"].notna()]
    linhas.append(("titulo", f_, None))
    for _, r_ in g.iterrows(): linhas.append(("classe", f_, r_))
fig, ax = plt.subplots(figsize=(8.4, 9.6)); yv = 0; ticks, labs = [], []
for tipo, f_, r_ in linhas:
    if tipo == "titulo":
        ok_ = bool(DEC_.loc[f_, "entra_no_EAR_v3"]); ref_ = RRF_.loc[RRF_["fator"] == f_, "referencia"].iloc[0]
        ax.text(0.052, yv, f"{f_}  ·  ref.: {ref_}" + ("  ·  aprovado" if ok_ else ""), fontsize=8.6, fontweight="bold", color=TEAL if ok_ else INK, va="center", ha="left", transform=ax.get_yaxis_transform())
        yv -= 1; continue
    ax.plot([max(r_["ic_inf"], 0.06), min(r_["ic_sup"], 9.5)], [yv, yv], color=TEAL, lw=1.4, solid_capstyle="butt", zorder=3)
    ax.plot(r_["rr_ajustado"], yv, "o", ms=5.2, color=TEAL, mec="white", mew=0.8, zorder=4)
    ax.plot(max(r_["rr_bruto_nacional"], 0.06), yv, "D", ms=4.6, mfc="white", mec=CLAY, mew=1.1, zorder=5)
    ticks.append(yv); labs.append(r_["classe"]); yv -= 1
ax.axvline(1.0, color=MUTE, lw=0.8, ls=(0, (4, 3)), zorder=1); ax.set_xscale("log"); ax.set_xlim(0.06, 10); ax.set_ylim(yv + 0.5, 0.8)
ax.set_xticks([0.1, 0.25, 0.5, 1, 2, 4, 8]); ax.set_xticklabels(["0,1", "0,25", "0,5", "1", "2", "4", "8"])
ax.set_yticks(ticks); ax.set_yticklabels(labs, fontsize=8.2); ax.tick_params(axis="y", length=0); ax.spines["left"].set_visible(False)
ax.set_xlabel("Risco relativo de descarrilamento por via (escala logarítmica)", fontsize=9)
ax.plot([], [], "D", mfc="white", mec=CLAY, label="nacional, bruto (compara ferrovias)"); ax.plot([], [], "o", color=TEAL, label="dentro das malhas, ajustado por faixa de pátio e raio (IC 95%)")
ax.legend(loc="lower center", bbox_to_anchor=(0.45, 1.0), ncol=2, fontsize=8, frameon=False)
fig.text(0.01, 0.005, "Fonte: o autor, a partir do RAAF e das Declarações de Rede 2025 (ANTT), 2011 a 2025; notebook 29. Aprovado: atende aos três critérios declarados antes.", fontsize=7.2, color=MUTE)
fig.tight_layout(rect=(0, 0.015, 1, 0.985)); fig.savefig(f"{FIG}/29_fatores_dentro_das_malhas_PT.png", dpi=220); plt.close(fig)
print("figura 29 ok")
