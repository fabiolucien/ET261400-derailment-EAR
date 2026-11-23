# Estilo das figuras: o mesmo da dissertação e do artigo AAP (Latin Modern Sans; tinta, cinzas, verde-petróleo e argila)
import os, matplotlib, matplotlib.font_manager as fm, json as _json
for f_ in ("lmsans10-regular.otf", "lmsans10-bold.otf", "lmsans10-oblique.otf"):
    for d_ in (f"{BASE}/data/fonts", "/usr/share/texmf/fonts/opentype/public/lm"):
        if os.path.exists(f"{d_}/{f_}"): fm.fontManager.addfont(f"{d_}/{f_}"); break
FONTE = "Latin Modern Sans" if any(f.name == "Latin Modern Sans" for f in fm.fontManager.ttflist) else "DejaVu Sans"
matplotlib.rcParams.update({"font.family": FONTE, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#7A8089", "axes.linewidth": 0.6, "xtick.color": "#16191C", "ytick.color": "#16191C"})
INK, MUTE, FAINT, GRID, TEAL, CLAY, GOLD = "#16191C", "#7A8089", "#C9CCD1", "#E6E8EB", "#1E6E6E", "#BD4B2C", "#8C6D1F"
# Figura 2 do artigo: classe muito alta calibrada em 2011-2020 e quilômetros com descarrilamento em 2021-2025 (rótulos em inglês)
from matplotlib.collections import PolyCollection, LineCollection
from matplotlib.lines import Line2D
from pyproj import Transformer
P = pd.read_csv(f"{PROC}/13_celulas_posicao.csv").set_index("cel_id").loc[C["cel_id"].values]; lon, lat = P["lon"].values, P["lat"].values; ok = np.isfinite(lon)
gate("células com posição no mapa", int(ok.sum()), 18618, source="notebook 13")
s = S["Calibrated (track attributes)"]; _, _, o = curva(s); top = np.zeros(N, bool); top[o[(np.cumsum(LN[o]) / LN.sum()) <= 0.20]] = True
TRF = Transformer.from_crs("EPSG:4674", "+proj=poly +lat_0=0 +lon_0=-54 +ellps=GRS80 +units=m +no_defs", always_xy=True)   # policônica, como na dissertação
X, Y = np.full(N, np.nan), np.full(N, np.nan); X[ok], Y[ok] = TRF.transform(lon[ok], lat[ok])
def proj(coords): xx, yy = TRF.transform(*np.asarray(coords, float).T); return np.column_stack([xx, yy])
UFG = _json.load(open(f"{PROC}/antt_uf2026.geojson"))["features"]; LIG = _json.load(open(f"{PROC}/antt_linhas2026.geojson"))["features"]
gate("estados no contorno da ANTT (UF2026)", len(UFG), 27, source="IBGE: 26 estados e o Distrito Federal")
def trechos(mask):
    # liga células consecutivas da mesma linha (ordem do km) que estão a menos de 3 km uma da outra
    segs = []; D = pd.DataFrame({"f": C["ferrovia"].values, "l": C["linha"].values, "km": C["km_a"].values, "x": X, "y": Y, "m": mask})[ok]
    for _, g in D.sort_values(["f", "l", "km"]).groupby(["f", "l"], sort=False):
        x, y_, m = g["x"].values, g["y"].values, g["m"].values
        for i in range(len(g) - 1):
            if m[i] and m[i + 1] and np.hypot(x[i + 1] - x[i], y_[i + 1] - y_[i]) < 3000: segs.append([(x[i], y_[i]), (x[i + 1], y_[i + 1])])
    return segs
fig = plt.figure(figsize=(8.4, 6.0)); a = fig.add_axes([0.0, 0.03, 0.60, 0.90]); b = fig.add_axes([0.675, 0.40, 0.315, 0.46])
a.add_collection(PolyCollection([proj(r) for f in UFG for r in f["geometry"]["coordinates"] if len(r) > 3], facecolors="#F3F4F6", edgecolors="#D5D8DC", linewidths=0.4, zorder=0))
a.add_collection(LineCollection([proj(l) for f in LIG for l in f["geometry"]["coordinates"]], colors=FAINT, linewidths=0.6, linestyles=(0, (2, 1.5)), zorder=1))
a.add_collection(LineCollection(trechos(np.ones(N, bool)), colors=MUTE, linewidths=0.75, zorder=2, capstyle="round"))
a.add_collection(LineCollection(trechos(top), colors=TEAL, linewidths=2.1, zorder=3, capstyle="round")); a.scatter(X[ok & top], Y[ok & top], s=1.6, color=TEAL, linewidths=0, zorder=3)
m1 = ok & (y == 1) & ~top; m2 = ok & (y == 1) & top
a.scatter(X[m1], Y[m1], s=11, facecolors="white", edgecolors=CLAY, linewidths=0.8, zorder=4)
a.scatter(X[m2], Y[m2], s=15, color=CLAY, edgecolors="white", linewidths=0.4, zorder=5)
POS = {"FTL": (0, 6e4), "FNSTN": (-1.9e5, -4e4), "RMN": (-1.4e5, 0), "RMC": (0, 8e4), "FCA": (1.3e5, 4e4), "EFVM": (1.4e5, 0), "MRS": (1.2e5, -5e4), "RMP": (-1.2e5, 3e4), "RMO": (-1.3e5, 7e4), "RMS": (-1.3e5, -4e4), "EFPO": (-1.5e5, 0), "FTC": (1.2e5, -3e4)}
for f in pd.unique(C["ferrovia"]):
    i = ok & (C["ferrovia"].values == f)
    if i.sum() >= 0.3 * (C["ferrovia"].values == f).sum():   # rótulo só para malhas com ao menos 30% das células posicionadas
        dx, dy = POS.get(f, (0, 6e4)); a.text(np.median(X[i]) + dx, np.median(Y[i]) + dy, f, fontsize=7.4, color=INK, ha="center", va="center", fontweight="bold", zorder=8, path_effects=[pe.withStroke(linewidth=2.4, foreground="white")])
x0, x1 = np.nanmin(X), np.nanmax(X); y0, y1 = np.nanmin(Y), np.nanmax(Y); a.set_xlim(x0 - 6.5e5, x1 + 2.0e5); a.set_ylim(y0 - 1.6e5, y1 + 1.2e5); a.set_aspect("equal"); a.axis("off")
H_ = [Line2D([], [], color=MUTE, lw=1.0, label="Network in operation (18,618 km positioned)"), Line2D([], [], color=FAINT, lw=1.0, ls=(0, (2, 1.5)), label="Other federal lines (ANTT axis)"),
      Line2D([], [], color=TEAL, lw=2.4, label="Top class (20% of track length)"), Line2D([], [], marker="o", ls="", mfc=CLAY, mec="white", mew=0.4, ms=5.4, label=f"Derailed km inside the class ({int(m2.sum())})"),
      Line2D([], [], marker="o", ls="", mfc="white", mec=CLAY, mew=0.9, ms=4.8, label=f"Derailed km outside the class ({int(m1.sum())})")]
lg = a.legend(handles=H_, loc="upper left", bbox_to_anchor=(0.0, 0.97), frameon=True, facecolor="white", edgecolor="none", framealpha=0.92, fontsize=7.4, handlelength=1.8, labelspacing=0.55, borderpad=0.6)
a.set_title("(a) Calibrated on 2011–2020, checked on 2021–2025", loc="left", fontsize=10, color=INK, fontweight="bold")
sx, sy = x1 - 5.4e5, y0 - 1.0e5; a.plot([sx, sx + 5e5], [sy, sy], color=INK, lw=1.3, solid_capstyle="butt"); a.text(sx + 2.5e5, sy + 3.5e4, "500 km", ha="center", va="bottom", fontsize=7.4, color=INK)
xn, yn = x0 - 5.6e5, y0 + 0.6e5; a.annotate("", xy=(xn, yn + 1.6e5), xytext=(xn, yn), arrowprops=dict(arrowstyle="-|>,head_width=0.3,head_length=0.6", color=INK, lw=1.1)); a.text(xn, yn + 1.75e5, "N", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=INK)
a.text(x0 - 6.4e5, y0 - 1.55e5, "Polyconic projection, SIRGAS 2000.\nBoundaries and lines: ANTT (2026)", ha="left", va="bottom", fontsize=6.2, color=MUTE, linespacing=1.3)
ROTULO = {"Expert rule (bands)": "Expert rule (FICO bands)", "Calibrated (track attributes)": "Logistic score (track attributes)", "Calibrated + accident history": "Logistic score + accident history"}
COR = {"Expert rule (bands)": INK, "Network-rate dummy": GOLD, "Calibrated (track attributes)": TEAL, "Calibrated + accident history": CLAY}; LS = {"Expert rule (bands)": (0, (4, 2)), "Network-rate dummy": (0, (1, 1.5)), "Calibrated (track attributes)": "-", "Calibrated + accident history": "-"}
for m in COR:
    x_, y_, _ = curva(S[m]); b.plot(100 * x_, 100 * y_, linestyle=LS[m], color=COR[m], lw=1.8, label=f"{ROTULO.get(m, m)}, {T1.set_index('metodo').loc[m, 'auc']:.2f}")
xc, yc, _ = curva(S["Calibrated (track attributes)"]); b.fill_between(100 * xc, 100 * xc, 100 * yc, color=TEAL, alpha=0.10, linewidth=0)
for m, dx, dy in (("Calibrated + accident history", -30, 6), ("Calibrated (track attributes)", 9, -22), ("Expert rule (bands)", 8, -12)):
    v = 100 * T1.set_index("metodo").loc[m, "classe_muito_alta"]; b.plot(20, v, "o", ms=6, color=COR[m], mec="white", mew=1.0, zorder=5); b.annotate(f"{v:.0f}%", (20, v), xytext=(dx, dy), textcoords="offset points", fontsize=8, color=INK, fontweight="bold", path_effects=[pe.withStroke(linewidth=2.6, foreground="white")], zorder=6)
b.plot([0, 100], [0, 100], color=MUTE, lw=0.8); b.axvline(20, color="#B8BEC6", lw=1.0); b.text(21.5, 97, "top class", fontsize=8.2, color=MUTE, ha="left", va="top")
b.set_xlim(0, 100); b.set_ylim(0, 100); b.grid(color=GRID, lw=0.6); b.set_axisbelow(True); b.set_xlabel("Track length, highest score first (%)", fontsize=8.6, color=INK); b.set_ylabel("Derailed km of 2021–2025 covered (%)", fontsize=8.6, color=INK)
b.legend(frameon=False, fontsize=7.4, loc="upper left", bbox_to_anchor=(-0.24, -0.2), handlelength=2.2, title="Score and AUC on 2021–2025", title_fontsize=7.6, alignment="left", borderaxespad=0.0); b.set_title("(b) Prediction-rate curve", loc="left", fontsize=10, color=INK, pad=8, fontweight="bold")
fig.savefig(f"{FIG}/22_mapa_particao_temporal.png", dpi=300, facecolor="white"); plt.show()
print("posicionadas:", int(ok.sum()), "de", N, "| km de 2021-2025 com posição:", int((ok & (y == 1)).sum()), "de", int(y.sum()))
log_ia("22.2 figura 2", "Claude", "FOCUS: mapa da classe muito alta (quintil superior) calibrada no passado contra descarrilamentos do período seguinte; curva de taxa de predição", "22_mapa_particao_temporal.png", "gate do número de células posicionadas")

# 2. Taxas por fator (descritivo; um fator por vez; associação, não causa)
C["n_ev"] = conta(CV_, 2011, 2025); C["y15"] = (C["n_ev"] > 0).astype(int)
def taxa(g, nome):
    t = C.groupby(g, observed=True).agg(km=("y15", "size"), km_atingidos=("y15", "sum"), eventos=("n_ev", "sum")).reset_index().rename(columns={g.name if hasattr(g, "name") else g: "faixa"}); t.insert(0, "fator", nome); t["pct_km_atingidos"] = (100 * t.km_atingidos / t.km).round(1); t["eventos_por_100km_ano"] = (100 * t.eventos / t.km / 15).round(2); return t
F = pd.concat([taxa(pd.cut(C["dmin_patio"], [0, 300, 600, 1200, 1800, 1e9], labels=["até 300 m", "300 a 600 m", "600 a 1.200 m", "1.200 a 1.800 m", "mais de 1.800 m"], include_lowest=True).rename("faixa"), "distância a pátio"),
               taxa(pd.cut(C["rmin_geo"], [0, 500, 1200, 2300, 1e9], labels=["menos de 500 m", "500 a 1.200 m", "1.200 a 2.300 m", "2.300 m ou mais"], include_lowest=True).rename("faixa"), "raio de curva (eixo)"),
               taxa(pd.cut(C["cap_vinc"].fillna(0), [-1, 0, 1, 5, 15, 1e9], labels=["0", "até 1", "1 a 5", "5 a 15", "mais de 15"]).rename("faixa"), "trens por dia (capacidade vinculada)"),
               taxa(C["bitola"].rename("faixa"), "bitola"), taxa(C["dormente"].rename("faixa"), "dormente"), taxa(C["perfil_trilho"].rename("faixa"), "perfil do trilho"), taxa(C["fixacao"].rename("faixa"), "fixação")], ignore_index=True)
F = F[F.km >= 300]; display(F); F.to_csv(f"{TAB}/22_taxas_por_fator.csv", index=False)
gate("soma dos eventos nas faixas de bitola", int(F[F.fator == "bitola"]["eventos"].sum()), 2681, source="total de descarrilamentos por via")
log_ia("22.3 taxas por fator", "Claude", "FOCUS: taxa por 100 km por ano, um fator por vez, só faixas com pelo menos 300 km", "22_taxas_por_fator.csv", "gate de soma por bitola")

# 3. Modelo de linguagem: kappa e cobertura na amostra confirmatória B (rótulos do notebook 04b)
L = pd.read_csv(f"{PROC}/04b_llm_rotulos_fra.csv"); B_ = L[L.amostra == "B"]; gate("narrativas da amostra B", len(B_), 600, source="notebook 04b")
cob = B_["sonnet"] != "UNDETERMINED"; k = lambda col, m: cohen_kappa_score(B_.loc[m, "oficial"], B_.loc[m, col])
LL = pd.DataFrame([dict(modelo="Claude Sonnet", cobertura=cob.mean(), kappa_onde_atribui=k("sonnet", cob), kappa_todas=k("sonnet", B_.index == B_.index)),
                   dict(modelo="Claude Haiku (nas narrativas do Sonnet)", cobertura=(B_["haiku"] != "UNDETERMINED").mean(), kappa_onde_atribui=k("haiku", cob), kappa_todas=k("haiku", B_.index == B_.index)),
                   dict(modelo="Gemini Flash (nas narrativas do Sonnet)", cobertura=(B_["gemini_flash"] != "UNDETERMINED").mean(), kappa_onde_atribui=k("gemini_flash", cob), kappa_todas=k("gemini_flash", B_.index == B_.index))]).round(3); display(LL); LL.to_csv(f"{TAB}/22_llm_amostra_B.csv", index=False)
gate("kappa do Sonnet onde atribui família", round(float(LL.loc[0, "kappa_onde_atribui"]), 3), 0.866, tol=0.001, source="notebook 04b"); gate("cobertura do Sonnet", round(float(LL.loc[0, "cobertura"]), 3), 0.652, tol=0.001, source="notebook 04b")
print("kappa Sonnet x Gemini, seis rótulos:", round(cohen_kappa_score(B_["sonnet"], B_["gemini_flash"]), 3))
log_ia("22.4 modelo de linguagem", "Claude", "FOCUS: recomputar kappa e cobertura a partir dos rótulos gravados", "22_llm_amostra_B.csv", "3 gates contra o notebook 04b")
exportar_registros("22")
