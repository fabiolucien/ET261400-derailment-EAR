# Figura 1 do artigo (rótulos em inglês, porque o artigo é em inglês)
import os, matplotlib, matplotlib.font_manager as fm                     # estilo da dissertação: Latin Modern Sans, tinta, cinzas, verde-petróleo e argila
for f_ in ("lmsans10-regular.otf", "lmsans10-bold.otf", "lmsans10-oblique.otf"):
    for d_ in (f"{BASE}/data/fonts", "/usr/share/texmf/fonts/opentype/public/lm"):
        if os.path.exists(f"{d_}/{f_}"): fm.fontManager.addfont(f"{d_}/{f_}"); break
FONTE = "Latin Modern Sans" if any(f.name == "Latin Modern Sans" for f in fm.fontManager.ttflist) else "DejaVu Sans"
matplotlib.rcParams.update({"font.family": FONTE, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#7A8089", "axes.linewidth": 0.6, "xtick.color": "#16191C", "ytick.color": "#16191C"})
import matplotlib.pyplot as plt
INK, MUTE, GRID, TEAL, CLAY, GOLD = "#16191C", "#7A8089", "#E6E8EB", "#1E6E6E", "#BD4B2C", "#8C6D1F"
COR = {"Regra do EAR por faixas": INK, "Dummy: taxa da malha": GOLD, "EAR calibrado (atributos da via)": TEAL, "EAR calibrado + histórico de acidentes": CLAY}
EN = {"Regra do EAR por faixas": "Expert rule (FICO bands)", "Dummy: taxa da malha": "Network-rate dummy", "EAR calibrado (atributos da via)": "Logistic score (track attributes)", "EAR calibrado + histórico de acidentes": "Logistic score + accident history"}
LS = {"Regra do EAR por faixas": (0, (4, 2)), "Dummy: taxa da malha": (0, (1, 1.5)), "EAR calibrado (atributos da via)": "-", "EAR calibrado + histórico de acidentes": "-"}
fig, ax = plt.subplots(1, 2, figsize=(8.4, 5.0), gridspec_kw={"width_ratios": [1.0, 1.12]})
a = ax[0]; d = R[(R.desenho.str.startswith("D1")) & (R.rotulo == "H=1")]
for m in MET:
    g = d[d.metodo == m].sort_values("conf_ini"); a.plot(g.conf_ini, g.auc, linestyle=LS[m], color=COR[m], lw=2, marker="o", ms=4.5, mec="white", mew=0.8, label=EN[m]); a.annotate(f"{g.auc.iloc[-1]:.2f}", (g.conf_ini.iloc[-1], g.auc.iloc[-1]), xytext=(6, 0), textcoords="offset points", va="center", fontsize=9, color=INK)
a.axhline(0.5, color=MUTE, lw=0.8); a.text(2025.9, 0.508, "chance", fontsize=8.5, color=MUTE, ha="right")
a.set_ylim(0.33, 0.90); a.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9]); a.set_xlim(2014.6, 2026.2); a.set_xticks(range(2015, 2026, 2)); a.grid(axis="y", color=GRID, lw=0.8); a.set_axisbelow(True)
a.set_xlabel("Checked year (calibrated on all earlier years)", fontsize=10, color=INK); a.set_ylabel("AUC, all 20,936 cells", fontsize=10, color=INK); a.set_title("(a) Rolling origin, one year ahead", loc="left", fontsize=10, color=INK, fontweight="bold"); a.legend(frameon=False, fontsize=8.4, loc="lower left", ncol=1, handlelength=2.4, borderaxespad=0.2, labelspacing=0.3)
b = ax[1]; ordem = [("D1 origem móvel, janela expansiva", f"H={h}", f"Expanding, {h} yr ahead") for h in (1, 2, 3, 4, 5)] + [("D2 origem móvel, janela fixa", f"W={w}, H={h}", f"Fixed {w}-yr, {h} yr ahead") for w in (3, 5, 7) for h in (1, 3, 5)] + [("D3 espelho para trás", f"H={h}", f"Backward, {h} yr") for h in (1, 3, 5)] + [("D4 validação cruzada em blocos", "K=3 blocos de 5 ano(s)", "Blocked CV, 3 × 5 yr"), ("D4 validação cruzada em blocos", "K=5 blocos de 3 ano(s)", "Blocked CV, 5 × 3 yr"), ("D4 validação cruzada em blocos", "K=15 blocos de 1 ano(s)", "Blocked CV, 15 × 1 yr"), ("D5 um ano de fora, com lacuna", "lacuna de 1 ano", "Leave-one-year-out")]
yy = np.arange(len(ordem))[::-1]
for y_, (de, ro, lab) in zip(yy, ordem):
    for m in MET:
        v = R[(R.desenho == de) & (R.rotulo == ro) & (R.metodo == m)]["auc"]
        if len(v) == 0 or m.startswith("Dummy"): continue
        dy = 0.22 if m.endswith("histórico de acidentes") else (-0.22 if (m.startswith("EAR calibrado (") and de.startswith("D1")) else 0.0)
        b.plot([v.min(), v.max()], [y_ + dy, y_ + dy], color=COR[m], lw=1.6, alpha=0.55, solid_capstyle="round"); b.plot(v.mean(), y_ + dy, "o" if not m.startswith("Regra") else "D", color=COR[m], ms=6 if not m.startswith("Regra") else 4.5, mec="white", mew=0.8)
b.set_yticks(yy); b.set_yticklabels([o[2] for o in ordem], fontsize=8.6, color=INK); b.set_xlim(0.5, 0.9); b.grid(axis="x", color=GRID, lw=0.8); b.set_axisbelow(True); b.tick_params(axis="y", length=0)
for sep in (15.5, 6.5, 3.5): b.axhline(sep, color=GRID, lw=0.8)
b.set_xlabel("AUC: mean (marker) and range (line)", fontsize=10, color=INK); b.set_title(f"(b) All {len(OUT)} evaluations, by design", loc="left", fontsize=10, color=INK, fontweight="bold")
fig.tight_layout(w_pad=1.2); fig.savefig(f"{FIG}/21_validacao_temporal.png", dpi=300, facecolor="white"); plt.show()
exportar_registros("21")
