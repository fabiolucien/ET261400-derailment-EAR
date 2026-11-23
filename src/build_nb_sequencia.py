# -*- coding: utf-8 -*-
"""Gera notebooks/ET261400_sequencia_completa.ipynb: a sequência completa do artigo em um só notebook do Colab.
Reúne, na ordem, as células dos notebooks 15 a 26 (sem alterar o código de nenhum), e acrescenta a consolidação final."""
import re, nbformat as nbf
from nb_common import DECLARACAO_IA

SEQ = [("15_previsao_malha_em_operacao", "primeira versão do modelo com histórico de acidentes e teste do gradient boosting", "Métodos, seção 2.2 (escolha da regressão logística)"),
       ("16_acerto_malha_existente", "blocos de 5 anos, ano a ano e teste de vazamento com rótulos embaralhados", "Métodos, seção 2.3 (teste de vazamento, 0,49)"),
       ("17_grade_de_janelas", "310 cenários de janelas de calibração e conferência", "registro; substituído no artigo pelo passo 21"),
       ("18_taxa_de_acerto_protocolo", "protocolo principal (origem móvel, 3 anos), alarmes falsos, grupos de critérios, resolução e base americana", "Tabela 2 e seção 3.3"),
       ("19_sensibilidade_operacao", "com e sem os trechos de tráfego interrompido", "seção 3.3 (0,81 com os trechos interrompidos)"),
       ("20_por_malha_baixa_operacao", "resultado por malha e sem as malhas de poucos eventos", "seção 3.3 (cinco malhas, 0,69)"),
       ("21_validacao_temporal_desenhos", "cinco desenhos de validação temporal da literatura, 185 avaliações", "Figura 1 e seção 3.2"),
       ("22_artigo_tabelas_figuras", "partição 2011-2020 contra 2021-2025, mapa, taxas por fator e kappa do modelo de linguagem", "Figura 2, Tabela 3 e seção 3.3"),
       ("23_teste_geral_periodo_inteiro", "teste geral: todos os acidentes de 2011 a 2025, sem recorte de tempo, com trechos inteiros fora do ajuste", "Tabela 2 (intervalos do teste espacial)"),
       ("24_testes_finais_modelos", "modelos da aula 6 no mesmo protocolo, matriz de confusão, hiperparâmetros, malha nunca vista e vazamento", "Tabela 2 e seção 3.1"),
       ("25_decomposicao_criterios_ear", "decomposição do ganho dos critérios do EAR: pesos aprendidos, AMV e medida contínua", "seção 3.1 (medida contínua)"),
       ("26_testes_da_revisao", "testes pedidos pela revisão: anos e trechos fora ao mesmo tempo, calibração (Brier) e modelo de linguagem na mesma cobertura do TF-IDF", "seções 3.3 e 3.4, Tabelas 1 e 2"),
       ("27_parametros_ear_aferidos", "novos parâmetros do EAR: faixas da FNS e da FICO aferidas com o risco relativo no Brasil e o bloco descarrilado nos EUA, recalibração aninhada", "seção 3.2, Figura 1 e Tabela 1"),
       ("28_auditoria_sorteios", "auditoria dos 30 sorteios: integridade da partição, estabilidade, permutação de rótulos e nulo que preserva o agrupamento espacial", "nota da Tabela 1 e seção 2.3"),
       ("29_fatores_dentro_das_malhas", "fatores da Declaração de Rede dentro das malhas: classes e regra declaradas antes, Mantel-Haenszel, placebo, Holm e conciliação com o artigo", "seção 3.1"),
       ("30_ear_v3_ferrovia_nova", "multiplicadores do EAR e teste como ferrovia nova (cada malha inteira fora), com limites reescolhidos sem a malha testada", "seção 3.2"),
       ("31_monte_carlo_posicao", "Monte Carlo do erro de posição (seis cenários), SIMEX e conferência do artefato de pátio", "seção 3.2 e Conclusões")]

cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s))
code = lambda s: cells.append(nbf.v4.new_code_cell(s))

linhas = "\n".join(f"| {i} | `{n}` | {o} | {a} |" for i, (n, o, a) in enumerate(SEQ, 1))
md(f"""# ET 261400 · Sequência completa do artigo, do dado ao resultado

**Trabalho:** Fatores técnicos da via na suscetibilidade a descarrilamentos ferroviários: aprendizado de máquina e modelos de linguagem sobre dados abertos.
**Autor:** Fábio Lucien David Maciel (IME, Mestrado em Engenharia de Transportes). **Disciplina:** ET 261400, 2026.2.

Este notebook executa, em ordem e do zero, todos os cálculos que sustentam o short paper. Cada passo traz a especificação, os gates declarados antes do código, o código e o resultado. Ao final, uma tabela reúne todos os gates e as tabelas e figuras do artigo.

## Como executar no Colab

1. Envie o arquivo `et261400_colab.zip` pelo painel de arquivos do Colab (ícone de pasta, à esquerda), ou deixe-o no Google Drive em `MyDrive/ET261400/colab/et261400_colab.zip`.
2. Menu Ambiente de execução → Executar tudo. Tempo esperado: de 120 a 150 minutos no Colab (o passo 10, com os cinco modelos em 30 sorteios, leva cerca de 30).

O pacote traz só dados públicos já processados: células de 1 km das 13 malhas (Declarações de Rede de 2025 e eixo da malha, ANTT), descarrilamentos do RAAF de 2011 a 2025 (ANTT), posição das células no mapa, narrativas da base americana (FRA, Form 54) e os rótulos gravados dos modelos de linguagem. Não há chave de API neste notebook.

## A sequência

| Passo | Notebook de origem | O que faz | Onde entra no artigo |
|---|---|---|---|
{linhas}

A preparação dos dados (ingestão do RAAF, matriz das Declarações de Rede, curvatura do eixo, células de 1 km e classificação das narrativas pelos modelos de linguagem) está nos notebooks 01 a 14 do repositório; este notebook parte dos arquivos que eles gravam em `data/processed`.

{DECLARACAO_IA}""")

code(r'''# === Passo 0: localizar o pacote de dados (Colab) ===
import os, sys, zipfile, time, datetime as dt
T0_GERAL = time.time()
if os.path.exists("/content") and not os.environ.get("ET261400_BASE"):
    if not os.path.exists("/content/et261400_colab.zip") and not os.path.exists("/content/ET261400/data"):
        from google.colab import drive
        drive.mount("/content/drive", force_remount=False)
        origem = "/content/drive/MyDrive/ET261400/colab/et261400_colab.zip"
        assert os.path.exists(origem), "Envie et261400_colab.zip pelo painel de arquivos ou coloque-o em MyDrive/ET261400/colab/"
        import shutil; shutil.copy(origem, "/content/et261400_colab.zip")
    if os.path.exists("/content/et261400_colab.zip"): zipfile.ZipFile("/content/et261400_colab.zip").extractall("/content/ET261400")   # sempre a versão do pacote enviado
print("início:", dt.datetime.now().isoformat(timespec="seconds"))''')

for i, (n, oque, artigo) in enumerate(SEQ, 1):
    nb = nbf.read(f"{n}.ipynb", as_version=4)
    for j, c in enumerate(nb.cells):
        s = c.source
        if c.cell_type == "markdown":
            if j == 0:
                s = re.sub(r"^# (\d+) · ", lambda m: f"---\n# Passo {i} · (notebook {m.group(1)}) ", s, count=1)
                s += f"\n\n**Onde entra no artigo:** {artigo}."
            else:
                s = re.sub(r"^## ", "### ", s, flags=re.M)
                s = s.split("**Declaração de uso de IA")[0].rstrip()   # a declaração fica uma vez, no início e no fim
            if s.strip(): md(s)
        else:
            code((f"# ---- Passo {i} · notebook {n} ----\n_t0 = time.time()\n" if j == 1 else "") + s)
    code(f'print("Passo {i} concluído em", round((time.time() - _t0) / 60, 1), "min")')

md("""---
# Consolidação: gates de todos os passos e os números do artigo""")
code(r'''import glob
G = []
for f in sorted(glob.glob(f"{TAB}/*_gates.csv")):
    nome = os.path.basename(f).replace("_gates.csv", "")
    if nome in ("15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27"):
        d = pd.read_csv(f); d.insert(0, "notebook", nome); G.append(d)
G = pd.concat(G, ignore_index=True); G.to_csv(f"{TAB}/00_gates_sequencia_artigo.csv", index=False)
res = G.groupby("notebook")["ok"].agg(gates="size", passaram="sum"); res["falharam"] = res["gates"] - res["passaram"]; display(res)
print(f"TOTAL: {int(G['ok'].sum())} de {len(G)} gates PASS")
if (~G["ok"]).any(): display(G.loc[~G["ok"], ["notebook", "gate", "got", "expected", "source"]])''')
code(r'''# Tabela 2 do artigo (protocolo principal, notebook 18) e intervalos de confiança
pd.set_option("display.width", 220)
t = pd.read_csv(f"{TAB}/18_origem_movel_por_origem.csv"); t = t[t.horizonte == 3]
T2 = t.groupby("metodo")[["auc", "auc_dentro", "acerto_20", "auc_km_sem_acidente_ate_T", "alarme_falso_20"]].mean().round(3)
T2 = T2.join(pd.read_csv(f"{TAB}/18_ic95_auc.csv", index_col=0)[["ic95_inf", "ic95_sup"]]); display(T2)
print("Tabela 3 do artigo (modelo de linguagem, amostra confirmatória)"); display(pd.read_csv(f"{TAB}/22_llm_amostra_B.csv"))
print("Partição 2011-2020 contra 2021-2025 (Figura 2)"); display(pd.read_csv(f"{TAB}/22_particao_2011_2020_2021_2025.csv").round(3))
print("Validação temporal por desenho (Figura 1)"); display(pd.read_csv(f"{TAB}/21_validacao_temporal_por_desenho.csv"))
print("Teste geral e testes no tempo, lado a lado (AUC)"); display(pd.read_csv(f"{TAB}/23_geral_e_no_tempo_lado_a_lado.csv", index_col=0))
print("Modelos da aula 6 no protocolo espacial (Tabela 2)"); display(pd.read_csv(f"{TAB}/24_modelos_resumo.csv", index_col=0))
print("Matriz de confusão na classe muito alta"); display(pd.read_csv(f"{TAB}/24_matriz_confusao.csv", index_col=0))
print("Decomposição do ganho dos critérios do EAR"); display(pd.read_csv(f"{TAB}/25_decomposicao_resumo.csv", index_col=0)); display(pd.read_csv(f"{TAB}/25_decomposicao_diferencas.csv"))
print("Testes da revisão"); display(pd.read_csv(f"{TAB}/26_conjunto_resumo.csv")); display(pd.read_csv(f"{TAB}/26_calibracao.csv")); display(pd.read_csv(f"{TAB}/26_tfidf_mesma_cobertura.csv"))
print("Novos parâmetros do EAR"); display(pd.read_csv(f"{TAB}/27_regras_resumo.csv", index_col=0).round(3)); display(pd.read_csv(f"{TAB}/27_diferencas.csv")); display(pd.read_csv(f"{TAB}/27_parametros_recalibrados.csv"))''')
code(r'''from IPython.display import Image, display as _d
for f in ("21_validacao_temporal.png", "22_mapa_particao_temporal.png"):
    print(f); _d(Image(f"{FIG}/{f}", width=900))
import subprocess
vers = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True).stdout.splitlines()
print("python", sys.version.split()[0], "|", "; ".join(v for v in vers if v.split("==")[0].lower() in ("numpy", "pandas", "scikit-learn", "scipy", "matplotlib")))
print("fim:", dt.datetime.now().isoformat(timespec="seconds"), "| tempo total:", round((time.time() - T0_GERAL) / 60, 1), "min")''')
md(f"""---
## Limites desta sequência

Os atributos da via são os da Declaração de Rede de 2025 em todos os anos. O passo 9 (teste geral) mede se a nota vale para trechos não vistos, não se antecipa o futuro. As avaliações do passo 7 se sobrepõem no tempo e não são independentes. Os rótulos dos modelos de linguagem foram gravados em 15/11/2026 e aqui são só relidos; a versão exata e a temperatura dos modelos não foram controladas. O mapa mostra 88,9% das células, as que têm posição no eixo da ANTT.

{DECLARACAO_IA}""")

nb = nbf.v4.new_notebook(); nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"}, "colab": {"name": "ET261400_sequencia_completa.ipynb", "provenance": []}}
nbf.write(nb, "ET261400_sequencia_completa.ipynb"); print("ok sequencia:", len(cells), "células")
