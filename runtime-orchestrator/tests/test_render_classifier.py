from __future__ import annotations

from runtime_orchestrator.source_acquisition.render_classifier import (
    classify_static_render_candidate,
)


def test_render_classifier_marks_experience_builder_shell_as_sparse() -> None:
    html = """
    <!doctype html>
    <html lang="en-us">
      <head><title>Experience</title></head>
      <body>
        <div id="loading">
          <div class="loading-content">
            <div class="jimu-primary-loading-app"></div>
          </div>
        </div>
        <div id="app"></div>
        <script type="systemjs-importmap">{}</script>
      </body>
    </html>
    """

    classified = classify_static_render_candidate(
        html=html,
        selector_plan=["#app", "#loading", ".jimu-primary-loading-app", "main", "body"],
        status_code=200,
    )

    assert classified["render_mode"] == "shell_or_sparse"
    assert "jimu-primary-loading-app" in classified["shell_markers"]
    assert classified["visible_text_length"] < 120
