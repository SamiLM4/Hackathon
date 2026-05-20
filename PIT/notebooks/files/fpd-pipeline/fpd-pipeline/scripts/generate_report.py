"""
generate_report.py
Agrega outputs dos notebooks em JSONs que o dashboard web consome.
Roda após todos os notebooks no GitHub Actions.
"""

import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

BASE     = Path("outputs")
FIGS     = BASE / "figures"
LOGS_DIR = BASE / "logs"
REPORT   = BASE / "report"
REPORT.mkdir(parents=True, exist_ok=True)
(BASE / "logs").mkdir(parents=True, exist_ok=True)

# ─── 1. Métricas ─────────────────────────────────────────────────────────────
def load_metricas():
    p = BASE / "metricas.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}

# ─── 2. Tabela de decil ──────────────────────────────────────────────────────
def load_decil():
    import csv
    p = BASE / "tabela_decil.csv"
    if not p.exists():
        return []
    rows = []
    with open(p, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append({k: float(v) if _is_float(v) else v for k, v in row.items()})
    return rows

def _is_float(s):
    try: float(s); return True
    except: return False

# ─── 3. Status dos notebooks ─────────────────────────────────────────────────
def notebook_status():
    notebooks = [
        "dev3_metrics",
        "dev3_pitch_modulos5a9",
        "dev3_pitch_completo",
    ]
    results = []
    executed_dir = BASE / "executed"
    for nb in notebooks:
        log_file = LOGS_DIR / f"{nb}.log"
        out_file  = executed_dir / f"{nb}_out.ipynb" if executed_dir.exists() else None

        status = "pending"
        error_msg = None
        duration = None

        if log_file.exists():
            content = log_file.read_text(encoding="utf-8", errors="replace")
            if "Execution succeeded" in content or "✅" in content:
                status = "success"
            elif "Error" in content or "Traceback" in content or "failed" in content.lower():
                status = "error"
                # pega última linha de erro
                lines = [l for l in content.splitlines() if l.strip()]
                error_msg = lines[-1] if lines else "Erro desconhecido"
            else:
                status = "success"  # papermill sem erro = ok

        if out_file and out_file.exists():
            # tenta ler o notebook executado para checar erros
            try:
                nb_data = json.loads(out_file.read_text(encoding="utf-8"))
                for cell in nb_data.get("cells", []):
                    for output in cell.get("outputs", []):
                        if output.get("output_type") == "error":
                            status = "error"
                            error_msg = output.get("ename", "") + ": " + output.get("evalue", "")
                            break
                if status != "error":
                    status = "success"
            except Exception:
                pass

        results.append({
            "name": nb,
            "status": status,
            "error": error_msg,
        })
    return results

# ─── 4. Lista de figuras geradas ─────────────────────────────────────────────
def list_figures():
    if not FIGS.exists():
        return []
    return sorted([
        {"file": f.name, "path": f"figures/{f.name}"}
        for f in FIGS.glob("*.png")
    ], key=lambda x: x["file"])

# ─── 5. Resumo executivo ─────────────────────────────────────────────────────
def load_resumo():
    p = BASE / "resumo_executivo.md"
    if p.exists():
        return p.read_text(encoding="utf-8")
    return ""

# ─── 6. Política 12A ─────────────────────────────────────────────────────────
def load_politica():
    p = BASE / "politica_12A.md"
    if p.exists():
        return p.read_text(encoding="utf-8")
    return ""

# ─── 7. Distribuição de faixas a partir do submission ────────────────────────
def load_faixas():
    p = BASE / "submission.csv"
    if not p.exists():
        return {}
    try:
        import csv
        rows = []
        with open(p, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        if not rows or "prob_fpd" not in rows[0]:
            return {}
        scores = [float(r["prob_fpd"]) for r in rows if r.get("prob_fpd")]
        total = len(scores)
        faixas = {
            "Baixo":   sum(1 for s in scores if s < 0.20),
            "Médio":   sum(1 for s in scores if 0.20 <= s < 0.45),
            "Alto":    sum(1 for s in scores if 0.45 <= s < 0.70),
            "Crítico": sum(1 for s in scores if s >= 0.70),
        }
        return {k: {"n": v, "pct": round(v / total * 100, 1)} for k, v in faixas.items()}
    except Exception as e:
        print(f"⚠️ Erro ao carregar submission: {e}")
        return {}

# ─── 8. Top features ─────────────────────────────────────────────────────────
def load_features():
    p = BASE / "feature_importance.csv"
    if not p.exists():
        return []
    try:
        import csv
        rows = []
        with open(p, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rows.append({"feature": row["feature"], "importance": float(row["importance"])})
        return sorted(rows, key=lambda x: -x["importance"])[:15]
    except Exception as e:
        print(f"⚠️ Erro ao carregar features: {e}")
        return []

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("📊 Gerando relatório de execução...")

    commit_sha = os.environ.get("GITHUB_SHA", "local")[:8]
    branch     = os.environ.get("GITHUB_REF_NAME", "local")
    actor      = os.environ.get("GITHUB_ACTOR", "local")
    run_number = os.environ.get("GITHUB_RUN_NUMBER", "0")

    metricas  = load_metricas()
    decil     = load_decil()
    notebooks = notebook_status()
    figures   = list_figures()
    faixas    = load_faixas()
    features  = load_features()
    resumo    = load_resumo()
    politica  = load_politica()

    n_success = sum(1 for n in notebooks if n["status"] == "success")
    n_error   = sum(1 for n in notebooks if n["status"] == "error")
    overall   = "success" if n_error == 0 else ("partial" if n_success > 0 else "error")

    meta = {
        "timestamp":   datetime.now(timezone.utc).isoformat(),
        "commit":      commit_sha,
        "branch":      branch,
        "actor":       actor,
        "run_number":  run_number,
        "overall":     overall,
        "notebooks":   notebooks,
        "figures":     figures,
        "metricas":    metricas,
        "faixas":      faixas,
        "features":    features,
        "resumo_md":   resumo,
        "politica_md": politica,
    }

    out = BASE / "run_meta.json"
    out.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ run_meta.json salvo em {out}")

    decil_out = BASE / "decil_data.json"
    decil_out.write_text(json.dumps(decil, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ decil_data.json salvo em {decil_out}")

    print(f"\n{'='*50}")
    print(f"Status geral: {overall.upper()}")
    print(f"Notebooks: {n_success} ok, {n_error} com erro")
    print(f"Figuras geradas: {len(figures)}")
    if metricas:
        print(f"ROC AUC: {metricas.get('ROC_AUC', '?')}")
        print(f"KS:      {metricas.get('KS', '?')}")

if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
