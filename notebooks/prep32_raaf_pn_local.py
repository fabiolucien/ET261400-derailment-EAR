# Prepara data/processed/32_raaf_pn_local.csv: para cada descarrilamento da matriz (fonte, linha do RAAF), o campo PN e o local registrado.
# Lê só as colunas necessárias; o campo Equipagem (nomes de tripulantes) não é lido.
import pandas as pd, numpy as np, os
BASE = os.environ.get("ET261400_BASE", "/home/claude"); RAW = f"{BASE}/data/raw/ANTT"; PROC = f"{BASE}/data/processed"
A = pd.read_csv(f"{RAW}/acidentes_ferroviarios_2004-2020.csv", sep=";", encoding="latin1", usecols=["Concessionaria", "Quilômetro_Inicial", "Perímetro_Urbano", "PN"])
B = pd.read_csv(f"{RAW}/acidentes_ferroviarios_12.2020-01.2026.csv", sep=";", encoding="latin1", usecols=["Concessionaria", "Quilômetro_Inicial", "Perímetro_Urbano", "PN"])
E = pd.read_csv(f"{PROC}/11_eventos_celulas.csv")
out = []
for fonte, R in [("2004-2020", A), ("12.2020-01.2026", B)]:
    e = E[E["fonte"] == fonte]; r = R.iloc[e["linha_raaf"].values]
    km = pd.to_numeric(r["Quilômetro_Inicial"].astype(str).str.replace(",", "."), errors="coerce").values
    assert (r["Concessionaria"].values == e["ferrovia"].values).all() and np.allclose(km, e["km"].values, atol=0.01), "junção pela linha do RAAF"
    t = r["Perímetro_Urbano"].astype(str).str.strip().str.lower()
    if fonte == "2004-2020": loc = np.where(t.isin(["não", "nan", ""]), "fora do perímetro urbano ou não informado", "perímetro urbano")
    else: loc = np.select([t.str.contains("trecho corrido|via corrida", regex=True), t.str.contains("p[aá]tio|terminal", regex=True)], ["trecho corrido", "pátio ou terminal"], "outro ou não informado")
    out.append(pd.DataFrame({"fonte": fonte, "linha_raaf": e["linha_raaf"].values, "pn": (r["PN"].astype(str).str.strip() == "Sim").values, "local_registrado": loc}))
O = pd.concat(out, ignore_index=True); O.to_csv(f"{PROC}/32_raaf_pn_local.csv", index=False); print(len(O), O["pn"].sum(), O["local_registrado"].value_counts().to_dict())
