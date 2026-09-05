"""Claim validation. No fact without grounding. Invented artifacts are errors."""

from __future__ import annotations

from typing import Iterable, Sequence

from fraggate.constants import FG_HALLUC_ARTIFACT, FG_HALLUC_FACT
from fraggate.envelopes import Artifact, Claim, Fact, GroundingRef
from fraggate.errors import FragRefuse


def validate_grounding(
    refs: Sequence[GroundingRef],
    *,
    allow_search: bool,
    where: str,
) -> None:
    if not refs:
        raise FragRefuse(FG_HALLUC_FACT, f"ungrounded fact: {where} has no GroundingRef")
    for ref in refs:
        if ref.kind == "search" and not allow_search:
            raise FragRefuse(
                FG_HALLUC_FACT,
                f"search grounding refused without allow_search ({where})",
                {"ref": ref.to_dict()},
            )


def validate_fact(fact: Fact, *, allow_search: bool, where: str) -> None:
    if not fact.text.strip():
        raise FragRefuse(FG_HALLUC_FACT, f"empty fact text ({where})")
    validate_grounding(fact.grounding, allow_search=allow_search, where=where)


def validate_artifact(artifact: Artifact, *, where: str) -> None:
    if artifact.invented:
        raise FragRefuse(
            FG_HALLUC_ARTIFACT,
            f"invented artifact is an error, not a draft ({where}: {artifact.id})",
            {"artifact": artifact.to_dict()},
        )
    if not artifact.digest and not artifact.ref:
        raise FragRefuse(
            FG_HALLUC_ARTIFACT,
            f"invented artifact is an error, not a draft ({where}: {artifact.id} has no digest or ref)",
            {"artifact": artifact.to_dict()},
        )


def validate_claim(claim: Claim, *, allow_search: bool, where: str = "claim") -> None:
    if not claim.statement.strip():
        raise FragRefuse(FG_HALLUC_FACT, f"empty claim statement ({where})")
    if claim.facts:
        for i, fact in enumerate(claim.facts):
            validate_fact(fact, allow_search=allow_search, where=f"{where}.facts[{i}]")
    elif claim.grounding:
        validate_grounding(claim.grounding, allow_search=allow_search, where=where)
    else:
        raise FragRefuse(
            FG_HALLUC_FACT,
            f"ungrounded fact: {where} has neither facts with GroundingRef nor claim-level grounding",
        )
    for i, artifact in enumerate(claim.artifacts):
        validate_artifact(artifact, where=f"{where}.artifacts[{i}]")


def validate_claims(
    claims: Iterable[Claim],
    *,
    allow_search: bool,
) -> list[Claim]:
    out = list(claims)
    for i, claim in enumerate(out):
        validate_claim(claim, allow_search=allow_search, where=f"claims[{i}]")
    return out
