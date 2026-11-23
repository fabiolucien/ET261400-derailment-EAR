# -*- coding: utf-8 -*-
"""EAR v3 · aplica os multiplicadores aferidos (notebook 30) a um traçado dividido em células de cerca de 1 km.

Uso (linha de comando):
    python ear_v3_aplicar.py celulas.csv saida.csv [parametros.csv]

celulas.csv precisa das colunas:
    id             identificador da célula (por exemplo, o km inicial)
    extensao_km    extensão da célula em km (1,0 na célula cheia)
    dist_patio_m   distância da célula à ponta do pátio ou ao AMV mais próximo, em metros (0 se o pátio está na célula)
    raio_m         raio mínimo da curva na célula, em metros (vazio ou 0 = tangente)
    trens_dia      tráfego previsto, em trens por dia (plano operacional ou capacidade vinculada)

Saída: as mesmas colunas, as classes de cada critério, os multiplicadores, dois índices e a classe do mapa.
    indice_tecnico   = multiplicador do pátio x multiplicador do raio (suscetibilidade da via)
    indice_exposicao = indice_tecnico x multiplicador do tráfego (frequência relativa esperada; o tráfego é exposição)
    classe_mapa      = cortes pela extensão da própria linha: 10% muito alta, 20% alta, 30% moderada, 40% baixa

Os índices ordenam os trechos de uma linha; não são probabilidade de descarrilamento. Os multiplicadores são riscos relativos
dentro das malhas federais (RAAF, 2011 a 2025); para uma ferrovia nova, use também o intervalo de predição da tabela.
Autor: Fábio Lucien David Maciel (ET 261400, IME). Código escrito com apoio do Claude (Anthropic), conferido pelo autor.
"""
import sys
import numpy as np
import pandas as pd

LIMITES_PATIO = (250, 1000, 1500, 3000)      # notebook 27: escolhidos em 138 de 150 ajustes; o limite de 1.000 m não é firme (notebook 31)
LIMITES_RAIO = (250, 300, 600)               # notebook 27: escolhidos em 125 de 150 ajustes
CLASSE_PATIO = ["do limite externo a 20 km (referência)", "baixa", "moderada", "alta", "muito alta (célula do pátio)", "acima de 20 km"]
CLASSE_RAIO = ["acima do limite externo e tangente (referência)", "classe baixa", "classe média", "classe alta (menor raio)"]
CLASSE_TRAF = ["zero vinculado", "até 1 trem/dia", "1 a 3 trens/dia (referência)", "3 a 10 trens/dia", "acima de 10 trens/dia"]


def classes(df):
    d = np.array(df["dist_patio_m"], dtype=float)
    kp = np.select([d <= LIMITES_PATIO[0], d <= LIMITES_PATIO[1], d <= LIMITES_PATIO[2], d <= LIMITES_PATIO[3]], [4, 3, 2, 1], 0)
    kp[(kp == 0) & (d > 20000)] = 5
    r = np.array(pd.to_numeric(df["raio_m"], errors="coerce").fillna(1e6), dtype=float); r[r <= 0] = 1e6
    kr = np.select([r < LIMITES_RAIO[0], r < LIMITES_RAIO[1], r < LIMITES_RAIO[2]], [3, 2, 1], 0)
    t = np.array(pd.to_numeric(df["trens_dia"], errors="coerce").fillna(0), dtype=float)
    kt = np.where(t <= 0, 0, np.digitize(t, [1, 3, 10], right=True) + 1)
    return kp, kr, kt


def aplica(df, par):
    mult = {c: par[par["criterio"] == c].reset_index(drop=True)["multiplicador"].values for c in ("pátio", "raio", "tráfego")}
    kp, kr, kt = classes(df)
    out = df.copy()
    out["classe_patio"] = [CLASSE_PATIO[k] for k in kp]; out["classe_raio"] = [CLASSE_RAIO[k] for k in kr]; out["classe_trafego"] = [CLASSE_TRAF[k] for k in kt]
    out["mult_patio"] = mult["pátio"][kp]; out["mult_raio"] = mult["raio"][kr]; out["mult_trafego"] = mult["tráfego"][kt]
    out["indice_tecnico"] = out["mult_patio"] * out["mult_raio"]; out["indice_exposicao"] = out["indice_tecnico"] * out["mult_trafego"]
    o = np.argsort(-out["indice_exposicao"].values, kind="stable"); cum = np.cumsum(out["extensao_km"].values[o]) / out["extensao_km"].sum()
    cl = np.empty(len(out), dtype=object); feito = np.zeros(len(o), bool)
    for corte, nome in [(0.10, "muito alta"), (0.30, "alta"), (0.60, "moderada"), (1.01, "baixa")]:
        sel = (cum <= corte) & ~feito; cl[o[sel]] = nome; feito |= sel
    cl[o[~feito]] = "baixa"; out["classe_mapa"] = cl
    return out


if __name__ == "__main__":
    entrada, saida = sys.argv[1], sys.argv[2]
    par = pd.read_csv(sys.argv[3] if len(sys.argv) > 3 else "results/tables/30_parametros_ear_v3.csv")
    res = aplica(pd.read_csv(entrada), par)
    res.to_csv(saida, index=False)
    print(res["classe_mapa"].value_counts().to_string())
