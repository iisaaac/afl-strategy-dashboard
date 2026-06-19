"""Tests for sample strategy brief generation."""

from __future__ import annotations

from scripts.generate_sample_brief import generate_sample_strategy_brief


def test_generate_sample_strategy_brief_writes_html_and_markdown(tmp_path) -> None:
    saved = generate_sample_strategy_brief(tmp_path)

    html = saved["html"].read_text(encoding="utf-8")
    markdown = saved["markdown"].read_text(encoding="utf-8")

    assert saved["html"].name == "sample_strategy_brief.html"
    assert saved["markdown"].name == "sample_strategy_brief.md"
    assert len(html) > 1000
    assert len(markdown) > 1000
    assert "Synthetic/demo sample data" in html
    assert "Synthetic/demo sample data" in markdown
    assert "Executive Snapshot" in html
    assert "Executive Snapshot" in markdown
    assert "Methodology Caveat" in html
    assert "Methodology Caveat" in markdown
    assert "does not contain official AFL attendance" in markdown
