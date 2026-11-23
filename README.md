# Technical track factors in the susceptibility to railway derailments

Code and derived data of the short paper *Technical track factors in the susceptibility to railway derailments: machine learning and language models on open data*, ET 261400 Artificial Intelligence Applied to Transportation, Graduate Program in Transportation Engineering, Military Institute of Engineering (IME), Brazil, 2026.2. Author: Fábio Lucien David Maciel.

## What is here

| Folder | Content |
|---|---|
| `notebooks/` | Notebooks 13 and 15 to 28, one per step, and `ET261400_sequencia_completa.ipynb`, which runs steps 15 to 27 in order and checks every gate; notebook 27 recalibrates the EAR bands; notebook 28 audits the 30 random partitions (integrity of the folds, stability across draws, label permutation test and a circular-shift null that keeps the spatial clustering of derailments) |
| `notebooks/executados/` | `ET261400_sequencia_completa_EXECUTADO.ipynb`: the full sequence with its outputs, run from scratch on 22 November 2026 (100 of 100 gates); `28_auditoria_sorteios.ipynb`: the partition audit with its outputs (10 of 10 gates) |
| `data/processed/` | Derived data: 1-km cells of the 13 federal networks, track-caused derailments per cell, cell positions, US Form 54 track-caused derailments with narratives, the Form 54 subset of freight-train track-caused derailments with consist and derailed vehicles (2006 to 2025), the stored language-model labels, and the ANTT 2026 state boundaries and federal lines used only for the map |
| `data/fonts/` | Latin Modern Sans (GUST Font License), used only for the figures |
| `results/` | Tables (`tables/`) and figures (`figures/`) of the paper |

## How to run

In Google Colab: open `notebooks/ET261400_sequencia_completa.ipynb`, upload `et261400_colab.zip` (at the root of this repository: the data and notebooks needed by the sequence) through the Files panel, then *Runtime > Run all*. It takes 95 to 120 minutes in Colab and checks 100 gates. Locally: `pip install -r requirements.txt`, decompress `data/processed/11_celulas_1km.csv.gz` (kept compressed here because of the file size limit of the web upload), set `ET261400_BASE` to this folder and run the notebook with Jupyter.

## Sources and licences

- Accident reports (RAAF), ANTT open data portal, Creative Commons Attribution: https://dados.antt.gov.br/dataset/relatorio-de-acompanhamento-de-acidentes-ferroviarios-raaf
- Network Statements 2025 and federal network shapefile, ANTT: https://www.gov.br/antt/pt-br/assuntos/ferrovias/declaracao-de-rede/declaracao-de-rede-2025
- Rail Equipment Accident/Incident Data (Form 54), Federal Railroad Administration, U.S. public data: https://catalog.data.gov/dataset/rail-equipment-accident-incident-data-form-54
- Band limits of the two public risk analysis studies (EAR) of the North-South (2015) and Centre-West Integration (2016) railways, ENEFER and VALEC, as transcribed in `results/tables/27_parametros_ear_fns_fico.csv`

The crew field of the accident reports, their only personal data, was removed at ingestion. No restricted data are used. Code: MIT licence. Derived data: same terms as the sources, with attribution to ANTT and FRA.

## Use of AI

Claude (Anthropic) wrote the code from specifications written by the author and classified accident narratives; ChatGPT (OpenAI) and Gemini (Google) reproduced the rolling-origin check independently, without access to the results. Every step has gates declared before the code, and the full sequence runs from scratch with all gates passed. The author checked every result and is responsible for the content.
