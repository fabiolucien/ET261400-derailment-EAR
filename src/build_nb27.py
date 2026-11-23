# -*- coding: utf-8 -*-
import nbformat as nbf
from nb_common import HEADER_RULE, SETUP_CODE, DECLARACAO_IA
cells = []; md = lambda s: cells.append(nbf.v4.new_markdown_cell(s)); code = lambda s: cells.append(nbf.v4.new_code_cell(s))
md(f"""# 27 · Novos parâmetros do EAR: as faixas da FNS e da FICO aferidas com dados públicos do Brasil e dos EUA

{HEADER_RULE}

**Por que este passo.** Os dois Estudos de Análise de Risco públicos que deram origem à regra (FNS, ENEFER 2015; FICO, ENEFER 2016) fixaram as faixas de distância a AMV, OAE e passagens em nível e as classes de raio por premissa: na FNS, o comprimento do trem-tipo (1.690 m); na FICO, o bloco de até 19 vagões de carga perigosa (cerca de 300 m) e o limite de superelevação (raio de 2.291,838 m). Nenhum dos dois conferiu as faixas com acidentes. Este notebook faz essa aferição e propõe novos parâmetros, sem mudar a forma do EAR (quatro classes por critério, soma ponderada).

**Desenho, declarado antes de rodar.**
1. Transcrever as faixas dos dois estudos e reconstruir as duas regras (a da FICO é a regra B2 dos notebooks anteriores).
2. Perfil brasileiro: risco relativo de descarrilamento por causa de via em cada classe de distância ao pátio e de raio, dentro de cada malha (Mantel-Haenszel), com IC 95% por reamostragem de linhas inteiras. A posição do acidente vem do km do RAAF: a resolução é a célula de 1 km.
3. Extensão física nos EUA (FRA, Form 54): veículos descarrilados como fração do trem, em descarrilamentos de trens de carga por causa de via na linha principal, 2006 a 2025, convertida em metros para o trem-tipo de 1.690 m.
4. Recalibração aninhada: faixas de pátio, classes de raio e peso escolhidos só nos grupos de ajuste, nos mesmos 30 sorteios de trechos inteiros fora; critério de escolha, a AUC dentro das malhas no ajuste. EAR v2: os mesmos critérios mais seis atributos de projeto (rampa, carga por eixo, tráfego, velocidade, dormente, trilho), com pontos inteiros de −4 a +4 e classes que, no ajuste, cobrem 50%, 80% e 90% dos quilômetros com descarrilamento.
5. Diferenças pareadas com IC por linhas; conferência temporal (aferir em 2011 a 2018, conferir em 2019 a 2025 em trechos não vistos); rótulos embaralhados.

**Gates.** Contagens dos notebooks 11 e 24; regra FICO idêntica à B2 e igual a 0,588; logística com atributos igual ao notebook 24 (0,759); somas dos perfis; recorte da FRA (6.606 e 2.772 registros); 150 ajustes; rótulos embaralhados entre 0,45 e 0,55.""")
code(SETUP_CODE)
base = open("nb27_base.py").read(); extra = open("nb27_extra.py").read()
code(base)
partes = extra.split("\n# ")
code(partes[0]); [code("# " + p) for p in partes[1:]]
md("""### Figura do artigo

Painéis (a) e (b): risco relativo dentro das malhas por classe, com IC 95% por linhas; as faixas abaixo mostram a classe que cada regra atribui (moda das células da classe). Painel (c): distribuição do comprimento do bloco descarrilado nos EUA, em metros para o trem-tipo de 1.690 m, com os limites das faixas da FICO e da FNS.""")
code(open("nb27_fig.py").read() + '\nexportar_registros("27")')
md(f"""---
## Referências

ENEFER Consultoria e Projetos, & VALEC. (2015). *Estudo de Análise de Risco (EAR) da Ferrovia Norte-Sul (EF-151): trecho Porto Nacional (TO) a Anápolis (GO)*. VALEC.

ENEFER Consultoria e Projetos, & VALEC. (2016). *Estudo de Análise de Risco (EAR) da Ferrovia de Integração Centro-Oeste (FICO): trecho Campinorte (GO) a Lucas do Rio Verde (MT)*. VALEC.

Federal Railroad Administration. (2026). *Rail equipment accident/incident data (Form 54)* [Data set]. https://catalog.data.gov/dataset/rail-equipment-accident-incident-data-form-54

Liu, X., Saat, M. R., Qin, X., & Barkan, C. P. L. (2013). Analysis of U.S. freight-train derailment severity using zero-truncated negative binomial regression and quantile regression. *Accident Analysis & Prevention, 59*, 87–93. https://doi.org/10.1016/j.aap.2013.04.039

Madsen, P. M., Dillon, R. L., Triantis, K. P., & Bradley, J. A. (2024). The relationship between freight train length and the risk of derailment. *Risk Analysis, 44*(11), 2616–2628. https://doi.org/10.1111/risa.14312

Mantel, N., & Haenszel, W. (1959). Statistical aspects of the analysis of data from retrospective studies of disease. *Journal of the National Cancer Institute, 22*(4), 719–748. https://doi.org/10.1093/jnci/22.4.719

## Limites

A posição do acidente no RAAF é o quilômetro: faixas abaixo de cerca de 500 m não se distinguem (200, 250 e 300 m caem na mesma célula). A distância ao pátio é a referência pública para os AMV; OAE e passagens em nível não entram por falta de cadastro público completo. O raio vem da geometria do traçado no OpenStreetMap, não do projeto; em uma ferrovia nova, com raios de projeto, os limites de raio podem se deslocar. A extensão física vem de trens dos EUA (mediana de 81 vagões) e foi convertida pela fração do trem, sem conferir essa escala com trens brasileiros; a distância percorrida depois do descarrilamento não é registrada. A restrição da faixa externa a dois trens-tipo foi acrescentada depois da primeira execução e a variante sem ela está registrada (item 4b).

{DECLARACAO_IA}""")
nb = nbf.v4.new_notebook(); nb["cells"] = cells; nb["metadata"] = {"kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"}, "colab": {"name": "27_parametros_ear_aferidos.ipynb"}}
nbf.write(nb, "27_parametros_ear_aferidos.ipynb"); print("ok 27")
