"""Static regression checks for the browser extension wiring."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXTENSION = ROOT / "extension"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_manifest_is_v1_and_allows_local_backend_hosts() -> None:
    manifest = json.loads(read_text(EXTENSION / "manifest.json"))

    assert manifest["version"] == "1.0.0"
    assert manifest["version_name"] == "1.0"
    assert "http://127.0.0.1/*" in manifest["host_permissions"]
    assert "http://localhost/*" in manifest["host_permissions"]


def test_content_script_uses_api_before_lexicon_fallback() -> None:
    content = read_text(EXTENSION / "content.js")

    assert "function debeUsarApi" in content
    assert "fragmentos = recolectarFragmentosML();" in content
    assert "escanearLexicon();" in content
    assert "API_UNAVAILABLE" in content
    assert "if (!config.activo || !regexActiva) return" not in content


def test_beto_results_apply_censorship_mark_not_only_outline() -> None:
    content = read_text(EXTENSION / "content.js")
    styles = read_text(EXTENSION / "styles.css")

    assert "crearMarcaML" in content
    assert "replaceChild(marca, node)" in content
    assert "hate-ml-mark" in styles
    assert ".hate-ml-mark.hate-detect-mode-blur" in styles
    assert ".hate-ml-mark.hate-detect-mode-hide" in styles


def test_background_requires_model_loaded_before_predicting() -> None:
    background = read_text(EXTENSION / "background.js")

    assert "model_loaded !== false" in background
    assert "model_not_loaded" in background
    assert "notifyApiUnavailable" in background


def test_ui_copy_declares_api_as_primary_engine() -> None:
    popup = read_text(EXTENSION / "popup/popup.html")
    options = read_text(EXTENSION / "options/options.html")
    readme = read_text(EXTENSION / "README.md")

    assert "Motor principal" in popup
    assert "API BETO local" in popup
    assert "API BETO Local" in options
    assert "Motor Principal" in options
    assert "El motor principal es la API local de BETO" in readme
    assert "Backend BETO (opcional)" not in options
