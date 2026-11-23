# -*- coding: utf-8 -*-
"""Gera notebooks/00_executar_tudo.ipynb: executa todos os notebooks do zero, em ordem, e consolida gates e tabelas do artigo."""
import nbformat as nbf
cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s))
code = lambda s: cells.append(nbf.v4.new_code_cell(s))
md("""# 00 · Executar tudo do zero e consolidar (ET 261400)

Este notebook cumpre a regra da disciplina de **reiniciar e executar tudo do zero antes de reportar qualquer número**. Ele executa os notebooks 01 a 24 em ordem, cada um em um kernel novo, grava as versões executadas em `notebooks/executados/`, reúne todos os gates em uma tabela única e mostra as tabelas que alimentam o artigo.

**Como usar no Colab.** (1) Envie `et261400_completo.zip` pelo painel de arquivos (ou as partes `et261400_completo.zip.part00`, `part01`, ...), ou mantenha a pasta `ET261400` no Google Drive. (2) Ambiente de execução → Executar tudo. Tempo esperado: cerca de 30 a 40 minutos.

**O que não é reexecutado aqui.** A extração do OpenStreetMap (notebook 05a) depende da rede; o pacote traz os dados já extraídos, com data. As chamadas a modelos de linguagem (notebook 04b) usam o cache de rótulos gravado; sem o cache, o 04b precisa ser aberto e executado diretamente no Colab.

**Declaração de uso de IA.** Ferramenta: Claude (Anthropic) escreveu este notebook a partir de especificação do autor. Parte do trabalho: orquestração da execução e consolidação dos registros. Responsável pelo conteúdo: o autor, que confere a tabela de gates antes de usar qualquer número.""")
code(r'''import os, sys, glob, json, time, subprocess, zipfile, datetime as dt
import pandas as pd
IN_COLAB = os.path.exists("/content")
if os.environ.get("ET261400_BASE"):
    BASE = os.environ["ET261400_BASE"]
elif IN_COLAB:
    partes = sorted(glob.glob("/content/et261400_completo.zip.part*"))
    if partes and not os.path.exists("/content/et261400_completo.zip"):
        with open("/content/et261400_completo.zip", "wb") as f:
            for p in partes: f.write(open(p, "rb").read())
    if os.path.exists("/content/et261400_completo.zip") and not os.path.exists("/content/ET261400/data"):
        zipfile.ZipFile("/content/et261400_completo.zip").extractall("/content/ET261400")
    if os.path.exists("/content/ET261400/data"):
        BASE = "/content/ET261400"
    else:
        from google.colab import drive
        drive.mount("/content/drive"); BASE = "/content/drive/MyDrive/ET261400"
else:
    BASE = os.path.abspath("..")
os.environ["ET261400_BASE"] = BASE; os.environ["MPLBACKEND"] = "Agg"
NB, EXE, TAB = f"{BASE}/notebooks", f"{BASE}/notebooks/executados", f"{BASE}/results/tables"
os.makedirs(EXE, exist_ok=True); print("BASE =", BASE, "|", dt.datetime.now().isoformat(timespec="seconds"))
ORDEM = ["01_ingestao_raaf_gates", "02_matriz_dr_dicionario", "03_eixo_curvatura_gate_fca", "04_llm_classificacao_causas", "04b_llm_api_confirmacao", "05_elementos_osm_gates_fca",
         "06_baselines_modelos_dr", "07_resposta_exposicao_grupo_complementar", "08_comparacao_modelos_exposicao", "09_contagem_offset_exposicao", "10_osm_no_modelo_fca",
         "11_celulas_1km_baseline_mvp", "12_sensibilidade_posicao", "13_mvp_mapa_nacional", "14_experimentos_melhoria", "15_previsao_malha_em_operacao", "16_acerto_malha_existente", "17_grade_de_janelas", "18_taxa_de_acerto_protocolo", "19_sensibilidade_operacao", "20_por_malha_baixa_operacao", "21_validacao_temporal_desenhos", "22_artigo_tabelas_figuras", "23_teste_geral_periodo_inteiro", "24_testes_finais_modelos", "25_decomposicao_criterios_ear", "26_testes_da_revisao", "27_parametros_ear_aferidos"]
faltam = [n for n in ORDEM if not os.path.exists(f"{NB}/{n}.ipynb")]; print("notebooks ausentes:", faltam or "nenhum")''')
code(r'''# apaga os registros de gates anteriores para que a tabela final venha só desta execução
for f in glob.glob(f"{TAB}/*_gates.csv"): os.remove(f)
log = []
for n in ORDEM:
    if not os.path.exists(f"{NB}/{n}.ipynb"): continue
    t0 = time.time()
    r = subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", f"{NB}/{n}.ipynb", "--output-dir", EXE,
                        "--ExecutePreprocessor.timeout=7200", "--ExecutePreprocessor.kernel_name=python3"], capture_output=True, text=True, cwd=NB)
    ok = r.returncode == 0; log.append(dict(notebook=n, ok=ok, minutos=round((time.time() - t0) / 60, 1), erro="" if ok else r.stderr[-600:]))
    print(f"{'OK  ' if ok else 'ERRO'} {n}  {log[-1]['minutos']} min", flush=True)
    if not ok: print(r.stderr[-1500:])
execucao = pd.DataFrame(log); execucao.to_csv(f"{TAB}/00_execucao.csv", index=False); execucao[["notebook", "ok", "minutos"]]''')
code(r'''G = []
for f in sorted(glob.glob(f"{TAB}/*_gates.csv")):
    if os.path.basename(f).startswith("00_"): continue
    d = pd.read_csv(f); d.insert(0, "notebook", os.path.basename(f).replace("_gates.csv", "")); G.append(d)
G = pd.concat(G, ignore_index=True); G.to_csv(f"{TAB}/00_gates_consolidado.csv", index=False)
res = G.groupby("notebook")["ok"].agg(gates="size", passaram="sum"); res["falharam"] = res["gates"] - res["passaram"]; display(res)
print(f"TOTAL: {int(G['ok'].sum())} de {len(G)} gates PASS em {dt.datetime.now().isoformat(timespec='seconds')}")
print("\nGates que falharam (cada um está documentado como limitação no notebook de origem; nenhum foi alargado para passar):")
display(G.loc[~G["ok"], ["notebook", "gate", "got", "expected", "source"]])''')
code(r'''pd.set_option("display.width", 220); pd.set_option("display.max_colwidth", 70)
def mostra(titulo, arq, **kw):
    p = f"{TAB}/{arq}"
    if os.path.exists(p): print("\n" + titulo); display(pd.read_csv(p, **kw))
    else: print("\n" + titulo, "-> arquivo ausente:", arq)
mostra("Tabela 1 do artigo · baselines e modelos em células de 1 km (notebook 11)", "11_metricas_resumo.csv", header=[0, 1], index_col=0)
mostra("Sensibilidade à posição do evento (notebook 12)", "12_sensibilidade_resumo.csv", header=[0, 1], index_col=0)
mostra("Tabela 2 do artigo · modelos de linguagem contra o código oficial (notebook 04b)", "04b_kappa_metodos.csv")
mostra("Famílias de causa, Brasil e EUA (notebook 04b)", "04b_familias_brasil_eua.csv")
vers = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True).stdout.splitlines()
keep = [v for v in vers if v.split("==")[0].lower() in ("numpy", "pandas", "scikit-learn", "scipy", "matplotlib", "geopandas", "shapely", "pyproj", "nbconvert", "openpyxl", "statsmodels")]
open(f"{BASE}/requirements_executado.txt", "w").write("\n".join([f"# python {sys.version.split()[0]} · {dt.date.today().isoformat()}"] + keep) + "\n"); print("\n".join(keep))''')
nb = nbf.v4.new_notebook(); nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"}, "colab": {"name": "00_executar_tudo.ipynb"}}
nbf.write(nb, "00_executar_tudo.ipynb"); print("ok 00")
