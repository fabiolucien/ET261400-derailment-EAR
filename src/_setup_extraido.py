# === Setup: caminhos, bibliotecas e as três ferramentas (gate, gate_between, log_ia) ===
import os, sys, json, re, unicodedata, datetime as dt
import numpy as np
import pandas as pd

IN_COLAB = "google.colab" in sys.modules or os.path.exists("/content")
if os.environ.get("ET261400_BASE"):
    BASE = os.environ["ET261400_BASE"]                # definido pelo notebook 00 (execução em lote) ou pela execução local
elif IN_COLAB and os.path.exists("/content/ET261400/data"):
    BASE = "/content/ET261400"                        # pacote já descompactado na sessão do Colab
elif IN_COLAB and os.path.exists("/content/et261400_colab.zip"):
    import zipfile
    zipfile.ZipFile("/content/et261400_colab.zip").extractall("/content/ET261400")   # pacote enviado pelo painel de arquivos
    BASE = "/content/ET261400"
elif IN_COLAB:
    from google.colab import drive
    drive.mount("/content/drive", force_remount=False)
    BASE = "/content/drive/MyDrive/ET261400"          # pasta do projeto no Drive (ajustar se for outra)
else:
    BASE = os.environ.get("ET261400_BASE", os.path.abspath(".."))   # execução local: raiz do repositório
RAW, PROC = f"{BASE}/data/raw", f"{BASE}/data/processed"
FIG, TAB = f"{BASE}/results/figures", f"{BASE}/results/tables"
for d in (PROC, FIG, TAB):
    os.makedirs(d, exist_ok=True)
print("BASE =", BASE)

_GATES = []          # todo gate executado fica registrado aqui
_LOG_IA = []         # registro de uso de IA: passo, ferramenta, especificação, resultado

def gate(name, got, expected, tol=0.0, source=""):
    """Compara um número calculado com um número que já se tinha antes do código.
    tol vem da fonte (meio passo de arredondamento, faixa publicada), nunca é alargada até passar."""
    if got is None:
        print(f"[ -- ] {name}: nada calculado ainda"); return False
    ok = abs(got - expected) <= tol
    _GATES.append(dict(gate=name, got=got, expected=expected, tol=tol, ok=ok, source=source))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: obtido {got}, esperado {expected} (tol +/-{tol}) {('| ' + source) if source else ''}")
    return ok

def gate_between(name, got, low, high, source=""):
    """O mesmo, quando a fonte publica uma faixa e não um número."""
    if got is None:
        print(f"[ -- ] {name}: nada calculado ainda"); return False
    ok = low <= got <= high
    _GATES.append(dict(gate=name, got=got, expected=f"[{low}, {high}]", tol=None, ok=ok, source=source))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: obtido {got}, faixa [{low}, {high}] {('| ' + source) if source else ''}")
    return ok

def log_ia(passo, ferramenta, especificacao, resultado, verificacao):
    """Registro de uso de IA exigido pela disciplina: o que foi pedido, a que ferramenta, o que voltou e como foi verificado."""
    _LOG_IA.append(dict(data=dt.date.today().isoformat(), passo=passo, ferramenta=ferramenta,
                        especificacao=especificacao.strip(), resultado=resultado, verificacao=verificacao))

def exportar_registros(prefixo):
    pd.DataFrame(_GATES).to_csv(f"{TAB}/{prefixo}_gates.csv", index=False)
    pd.DataFrame(_LOG_IA).to_csv(f"{TAB}/{prefixo}_registro_uso_ia.csv", index=False)
    n_ok = sum(g["ok"] for g in _GATES)
    print(f"gates: {n_ok}/{len(_GATES)} PASS | registros de IA: {len(_LOG_IA)} | exportados em {TAB}")

def norm_txt(s):
    """Maiúsculas sem acento, espaços simples: chave de junção para nomes de pátios e estações."""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).upper().strip()
