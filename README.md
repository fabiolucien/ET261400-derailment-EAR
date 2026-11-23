# Technical track factors in the susceptibility to railway derailments

Code and derived data of the short paper *Technical track factors in the susceptibility to railway derailments: machine learning and language models on open data*, ET 261400 Artificial Intelligence Applied to Transportation, Graduate Program in Transportation Engineering, Military Institute of Engineering (IME), Brazil, 2026.2. Author: Fábio Lucien David Maciel.

## What is here

| Folder | Content |
|---|---|
| `notebooks/` | Notebooks 13 and 15 to 32, one per step, and `ET261400_sequencia_completa.ipynb`, which runs steps 15 to 32 in order and checks every gate. Notebook 27 recalibrates the EAR bands; 28 audits the 30 random partitions (fold integrity, stability, label permutation and a circular-shift null); 29 tests each declared track attribute within networks (classes and decision rule fixed in advance, Mantel-Haenszel, placebo, Holm); 30 turns the recalibrated classes and linked traffic into within-network risk multipliers and tests them on networks left out whole (new railway), with prediction intervals; 31 propagates position errors of accidents and yards by Monte Carlo (six scenarios), with SIMEX and a yard-track check; 32 checks the excess around yards without level-crossing derailments, on both sides of a yard, with a 500 m or 1 km high band, without the double-track Vale lines, on single track only and on busier track (decision rules written before the results) |
| `notebooks/executados/` | `ET261400_sequencia_completa_EXECUTADO.ipynb`: the full sequence (steps 15 to 32) with its outputs, run from scratch on 23 November 2026 (164 of 164 gates); `28_auditoria_sorteios.ipynb`: the partition audit with its outputs (10 of 10 gates) |
| `data/processed/` | Derived data: 1-km cells of the 13 federal networks, track-caused derailments per cell, cell positions, US Form 54 track-caused derailments with narratives, the Form 54 subset of freight-train track-caused derailments with consist and derailed vehicles (2006 to 2025), the stored language-model labels, the level-crossing flag and recorded location of each derailment taken from the accident reports (`32_raaf_pn_local.csv`, built by `notebooks/prep32_raaf_pn_local.py` without reading the crew field), and the ANTT 2026 state boundaries and federal lines used only for the map |
| `data/fonts/` | Latin Modern Sans (GUST Font License), used only for the figures |
| `results/` | Tables (`tables/`) and figures (`figures/`) of the paper |
| `src/ear_v3_aplicar.py` | Applies the risk multipliers of notebook 30 (`results/tables/30_parametros_ear_v3.csv`) to a line split into 1-km cells (distance to the nearest yard or turnout, minimum radius, trains per day) and returns a susceptibility index, an index with exposure and map classes by length; example input and output for the North-South line in `results/tables/30_exemplo_*.csv`. The index ranks stretches; it is not a probability |
| `docs/PARAMETROS_EAR_V3.pdf` | Technical note in Portuguese: the updated EAR parameters, how to apply them, the new-railway test and the Monte Carlo |

## How to run

In Google Colab: open `notebooks/ET261400_sequencia_completa.ipynb`, upload `et261400_colab.zip` (at the root of this repository: the data and notebooks needed by the sequence) through the Files panel, then *Runtime > Run all*. It takes 120 to 150 minutes in Colab and checks 164 of 164 gates. Locally: `pip install -r requirements.txt`, decompress `data/processed/11_celulas_1km.csv.gz` (kept compressed here because of the file size limit of the web upload), set `ET261400_BASE` to this folder and run the notebook with Jupyter.

## Sources and licences

- Accident reports (RAAF), ANTT open data portal, Creative Commons Attribution: https://dados.antt.gov.br/dataset/relatorio-de-acompanhamento-de-acidentes-ferroviarios-raaf
- Network Statements 2025 and federal network shapefile, ANTT: https://www.gov.br/antt/pt-br/assuntos/ferrovias/declaracao-de-rede/declaracao-de-rede-2025
- Rail Equipment Accident/Incident Data (Form 54), Federal Railroad Administration, U.S. public data: https://catalog.data.gov/dataset/rail-equipment-accident-incident-data-form-54
- Band limits of the two public risk analysis studies (EAR) of the North-South (2015) and Centre-West Integration (2016) railways, ENEFER and VALEC, as transcribed in `results/tables/27_parametros_ear_fns_fico.csv`

The crew field of the accident reports, their only personal data, was removed at ingestion. No restricted data are used. Code: MIT licence. Derived data: same terms as the sources, with attribution to ANTT and FRA.

## Use of AI

Claude (Anthropic) wrote the code from specifications written by the author and classified accident narratives; ChatGPT (OpenAI) and Gemini (Google) independently re-implemented the rolling-origin check, without access to the results, and, with Claude, reviewed the analyses of notebooks 29 to 31 and the full paper as mock referees. Every step has gates declared before the code, and the full sequence runs from scratch with all gates passed. The author checked every result and is responsible for the content.
