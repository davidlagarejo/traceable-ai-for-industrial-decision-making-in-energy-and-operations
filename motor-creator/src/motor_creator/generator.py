"""
Artifact generator — AI-assisted content generation layer (Phase 5).

This module is OPTIONAL. The core orchestrator works without it.
Requires: pip install motor-creator[ai]  (anthropic package)

Architecture:
- generator.py is a thin call layer. It never decides workflow.
- The orchestrator decides WHEN to generate. Generator decides HOW.
- Generated artifacts are written by artifact_manager (not here).
- Generation status is tracked in motor_state.json artifacts[stage][generated_by].
- Generated content is NEVER written silently over existing human-authored content.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from .models import MotorEntry, Stage


# ─── Generation metadata ───────────────────────────────────────────────────

GENERATED_BY_HUMAN = "human"
GENERATED_BY_AI = "ai"
GENERATED_PENDING = "pending"


class GenerationResult:
    def __init__(
        self,
        artifact_name: str,
        content: str,
        motor_id: str,
        stage: Stage,
        generated_by: str = GENERATED_BY_AI,
        model: str = "",
    ):
        self.artifact_name = artifact_name
        self.content = content
        self.motor_id = motor_id
        self.stage = stage
        self.generated_by = generated_by
        self.model = model

    def to_metadata(self) -> dict:
        return {
            "artifact": self.artifact_name,
            "generated_by": self.generated_by,
            "model": self.model,
            "stage": self.stage.value,
        }


# ─── Prompt builders ───────────────────────────────────────────────────────

def _build_system_prompt() -> str:
    return """You are a Principal Software Architect building the ZLab Operational Truth Framework.
Your task is to generate documentation artifacts for framework motors.

Rules:
- Be precise and technical. No filler.
- Follow the exact sections requested.
- Do not invent functionality beyond what is described.
- Do not mix responsibilities with other motors.
- Mark nothing as TODO or TBD — generate real content.
- Preserve deterministic-first design: no AI as core decision maker.
"""


def _build_artifact_prompt(
    artifact_name: str,
    stage: Stage,
    motor_entry: MotorEntry,
    context: dict,
) -> str:
    motor_info = (
        f"Motor: {motor_entry.name} ({motor_entry.motor_id})\n"
        f"Group: {motor_entry.group}\n"
        f"Dependencies: {motor_entry.requires}\n"
    )
    if context.get("purpose"):
        motor_info += f"Purpose: {context['purpose']}\n"
    if context.get("existing_artifacts"):
        motor_info += f"Existing artifacts available: {context['existing_artifacts']}\n"

    artifact_instructions = {
        "functional_contract": (
            "Generate a functional_contract.md with sections: ## inputs, ## outputs, ## limits, ## validations.\n"
            "Be specific. Define exact types and constraints. No ambiguity."
        ),
        "master_concept_doc": (
            "Generate a master_concept_doc.md with sections: ## purpose, ## what_it_does, "
            "## what_it_does_not_do, ## why_it_exists.\n"
            "Be concise and precise."
        ),
        "technical_schema": (
            "Generate a technical_schema.md with sections: ## entities, ## fields, "
            "## relationships, ## identifiers, ## versioning, ## lineage.\n"
            "Use concrete field names and types."
        ),
        "test_spec": (
            "Generate a test_spec.md with sections: ## happy_path, ## sparse_case, "
            "## malformed_input, ## edge_cases, ## pass_criteria, ## fail_criteria.\n"
            "Each section should have at least 2 concrete test scenarios."
        ),
        "failure_modes_spec": (
            "Generate a failure_modes_spec.md with sections: ## failure_modes_list, "
            "## anti_patterns, ## degradation_signals, ## expensive_errors.\n"
            "Be concrete about technical failure modes."
        ),
    }

    instruction = artifact_instructions.get(
        artifact_name,
        f"Generate {artifact_name}.md for stage {stage.value}. Be specific and complete.",
    )

    return f"{motor_info}\n{instruction}"


# ─── Generator class ───────────────────────────────────────────────────────

class ArtifactGenerator:
    """
    AI-powered artifact content generator.
    Requires anthropic package: pip install motor-creator[ai]
    """

    def __init__(self, model: str = "claude-sonnet-4-6", max_tokens: int = 4096):
        self.model = model
        self.max_tokens = max_tokens
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic()
            except ImportError:
                raise RuntimeError(
                    "anthropic package not installed. "
                    "Run: pip install motor-creator[ai]"
                )
        return self._client

    def generate(
        self,
        artifact_name: str,
        stage: Stage,
        motor_entry: MotorEntry,
        context: Optional[dict] = None,
    ) -> GenerationResult:
        """
        Generate content for a single artifact.
        Does NOT write the file — caller is responsible for writing via artifact_manager.
        """
        client = self._get_client()
        ctx = context or {}

        messages = [
            {
                "role": "user",
                "content": _build_artifact_prompt(artifact_name, stage, motor_entry, ctx),
            }
        ]

        response = client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=_build_system_prompt(),
            messages=messages,
        )

        content = response.content[0].text
        return GenerationResult(
            artifact_name=artifact_name,
            content=content,
            motor_id=motor_entry.motor_id,
            stage=stage,
            generated_by=GENERATED_BY_AI,
            model=self.model,
        )

    def generate_and_write(
        self,
        artifact_name: str,
        stage: Stage,
        motor_entry: MotorEntry,
        motor_dir: Path,
        context: Optional[dict] = None,
        overwrite: bool = False,
    ) -> Optional[Path]:
        """
        Generate content and write to file.
        Returns path if written, None if file already exists and overwrite=False.
        """
        from .artifact_manager import get_artifact_path

        p = get_artifact_path(motor_dir, stage, artifact_name)

        if p.exists() and not overwrite:
            return None  # Never overwrite silently

        result = self.generate(artifact_name, stage, motor_entry, context)

        # Prepend generation metadata as a comment
        header = (
            f"<!-- generated_by: {result.generated_by} | model: {result.model} | "
            f"motor: {result.motor_id} | stage: {stage.value} -->\n\n"
        )
        full_content = header + result.content

        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(full_content, encoding="utf-8")
        return p
