"""FragGate FG-0.1 constants.

Magic FGT1. Version 0.1.0. Paper FG-WP-0.1.
Author: Aziel Eliab.
"""

from __future__ import annotations

MAGIC = "FGT1"
VERSION = "0.1.0"
PAPER = "FG-WP-0.1"
AUTHOR = "Aziel Eliab"
HOMEPAGE = "https://aziel-runtime.vibelock.workers.dev/"
REPOSITORY = "https://github.com/AzielEliab/fraggate"

# TemporalLock-shaped genesis previous-hash (SHA-256 width). Not a product fork.
GENESIS_PREV_HASH = "0" * 64

BUILTIN_TOOLS = (
    "runtime.ping",
    "registry.list",
    "registry.verify",
    "claim.check",
    "runtime.receipt",
)

GROUNDING_KINDS = (
    "registry",
    "project_map",
    "receipt",
    "file",
    "operator",
    "search",
    "memory",
    "schema",
)

FG_HALLUC_TOOL = "FG-HALLUC-TOOL"
FG_HALLUC_FACT = "FG-HALLUC-FACT"
FG_HALLUC_ARTIFACT = "FG-HALLUC-ARTIFACT"
FG_FRAG_SCHEMA = "FG-FRAG-SCHEMA"
FG_FRAG_ORPHAN = "FG-FRAG-ORPHAN"
FG_GATE = "FG-GATE"
FG_EXPORT = "FG-EXPORT"
FG_ERR = "FG-ERR"

ERROR_CODES = (
    FG_HALLUC_TOOL,
    FG_HALLUC_FACT,
    FG_HALLUC_ARTIFACT,
    FG_FRAG_SCHEMA,
    FG_FRAG_ORPHAN,
    FG_GATE,
    FG_EXPORT,
    FG_ERR,
)

GATE_NAMES = (
    "Definition",
    "Evidence",
    "Impact",
    "Integrity",
    "Responsibility",
)

PASS = "PASS"
REVISE = "REVISE"
BLOCK = "BLOCK"

STATUS_OK = "ok"
STATUS_REFUSE = "refuse"
