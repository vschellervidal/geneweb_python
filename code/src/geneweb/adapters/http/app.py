from __future__ import annotations

from fastapi import FastAPI, Query

from geneweb.adapters.ocaml_bridge.bridge import OcamlCommandError, run_gwb2ged

app = FastAPI(title="GeneWeb Python API", version="0.1.0")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/export/gwb2ged")
def export_gwb2ged(
    input_dir: str = Query(..., description="Chemin répertoire GWB"),
) -> dict[str, str]:
    try:
        out = run_gwb2ged(["-i", input_dir, "-o", "-"])
        return {"stdout": out}
    except OcamlCommandError as e:
        return {"error": e.stderr}
