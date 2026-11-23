# Figura 30: (a) ferrovia nova, cada malha inteira fora do ajuste: regra FICO, regra aferida e pátio + raio + tráfego; (b) Monte Carlo de posição (notebook 31).
import os, matplotlib, matplotlib.font_manager as fm
for f_ in ("lmsans10-regular.otf", "lmsans10-bold.otf", "lmsans10-oblique.otf"):
    for d_ in (f"{BASE}/data/fonts", "/usr/share/texmf/fonts/opentype/public/lm"):
        if os.path.exists(f"{d_}/{f_}"): fm.fontManager.addfont(f"{d_}/{f_}"); break
FONTE = "Latin Modern Sans" if any(f.name == "Latin Modern Sans" for f in fm.fontManager.ttflist) else "DejaVu Sans"
matplotlib.rcParams.update({"font.family": FONTE, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#7A8089", "axes.linewidth": 0.6})
import matplotlib.pyplot as plt
INK, MUTE, FAINT, TEAL, CLAY, GOLD = "#16191C", "#7A8089", "#C9CCD1", "#1E6E6E", "#BD4B2C", "#8C6D1F"
MF = pd.read_csv(f"{TAB}/30_malha_fora_ate_20km_por_malha.csv").sort_values("atingidas", ascending=True); MCs = pd.read_csv(f"{TAB}/31_replicas.csv"); RS = pd.read_csv(f"{TAB}/31_resumo_monte_carlo.csv")
fig, (a, b) = plt.subplots(1, 2, figsize=(8.4, 5.0), gridspec_kw=dict(width_ratios=[1.15, 1]))
yy_ = np.arange(len(MF))
for i, (_, r_) in enumerate(MF.iterrows()):
    a.plot([r_["regra FICO"], r_["B A + tráfego"]], [i, i], color=FAINT, lw=2.2, zorder=1)
    a.plot(r_["regra FICO"], i, "o", ms=5.5, mfc="white", mec=INK, mew=1.1, zorder=3); a.plot(r_["regra aferida (reescolhida)"], i, "s", ms=4.5, color=GOLD, zorder=3); a.plot(r_["B A + tráfego"], i, "o", ms=5.8, color=TEAL, mec="white", mew=0.8, zorder=4)
a.axvline(0.5, color=MUTE, lw=0.7, ls=(0, (4, 3))); a.set_yticks(yy_); a.set_yticklabels([f"{m} ({n})" for m, n in zip(MF["malha"], MF["atingidas"])], fontsize=8.2)
a.set_xlim(0.42, 0.82); a.set_xlabel("AUC na malha deixada de fora do ajuste (células a até 20 km de um pátio)", fontsize=8.8); a.tick_params(axis="y", length=0); a.spines["left"].set_visible(False)
w_ = MF["atingidas"]; med = {k_: np.average(MF[k_], weights=w_) for k_ in ("regra FICO", "regra aferida (reescolhida)", "B A + tráfego")}
a.set_title("(a) Ferrovia nova: cada malha fora do ajuste (até 20 km de pátio)", fontsize=9.4, loc="left", color=INK)
a.plot([], [], "o", mfc="white", mec=INK, label=f"faixas da FICO ({med['regra FICO']:.3f})".replace(".", ",")); a.plot([], [], "s", color=GOLD, label=f"faixas aferidas ({med['regra aferida (reescolhida)']:.3f})".replace(".", ","))
a.plot([], [], "o", color=TEAL, label=f"pátio, raio e tráfego, multiplicadores ({med['B A + tráfego']:.3f})".replace(".", ",")); a.legend(loc="upper left", bbox_to_anchor=(-0.32, -0.17), ncol=3, fontsize=7.4, frameon=False, title="média ponderada pelos km atingidos", title_fontsize=7.4, columnspacing=1.0, handletextpad=0.3)
ORD = list(RS["cenario"])
for j, c_ in enumerate(ORD):
    g = MCs[MCs["cenario"] == c_]["ganho_malhas"].values; jit = np.random.default_rng(j).uniform(-0.18, 0.18, len(g))
    b.plot(g, j + jit, "o", ms=2.2, color=TEAL, alpha=0.35, zorder=2); b.plot(np.median(g), j, "|", ms=14, mew=2.0, color=INK, zorder=3)
    r_ = RS[RS["cenario"] == c_].iloc[0]; b.text(0.033, j, f"pátio {int(r_['patio_igual_ao_27'] * 100 + 0.5)}% · raio {int(r_['raio_igual_ao_27'] * 100 + 0.5)}%", fontsize=7.2, va="center", color=MUTE)
b.axvline(0, color=MUTE, lw=0.7, ls=(0, (4, 3))); b.set_yticks(range(len(ORD))); b.set_yticklabels([c_.replace(" e pátio", "\ne pátio") for c_ in ORD], fontsize=7.8); b.set_xlim(-0.004, 0.062); b.set_ylim(len(ORD) - 0.5, -1.0)
b.set_xlabel("Ganho da regra aferida sobre a FICO\n(AUC dentro das malhas, 200 réplicas)", fontsize=8.6); b.tick_params(axis="y", length=0); b.spines["left"].set_visible(False)
b.set_title("(b) Monte Carlo do erro de posição", fontsize=9.4, loc="left", color=INK); b.text(0.033, -0.7, "limites iguais aos do artigo", fontsize=7.2, color=MUTE, va="center")
for ax_ in (a, b): ax_.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, p: f"{v:.2f}".replace(".", ",")))
fig.text(0.01, 0.01, "Fonte: o autor, a partir do RAAF e das Declarações de Rede 2025 (ANTT), 2011 a 2025; notebooks 30 e 31. Entre parênteses, km atingidos.", fontsize=7.2, color=MUTE)
fig.tight_layout(rect=(0, 0.035, 1, 1)); fig.subplots_adjust(bottom=0.27); fig.savefig(f"{FIG}/30_ferrovia_nova_monte_carlo_PT.png", dpi=220); plt.close(fig); print("figura 30 ok")
