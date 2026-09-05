"""FragGate FG-0.1 — kernel against tool fragmentation and model hallucination.

Author: Aziel Eliab.
License: Apache-2.0.
"""

from fraggate.constants import (
    AUTHOR,
    ERROR_CODES,
    HOMEPAGE,
    MAGIC,
    PAPER,
    VERSION,
)
from fraggate.envelopes import (
    Artifact,
    CallEnvelope,
    Claim,
    Fact,
    GroundingRef,
    ResultEnvelope,
    ToolSpec,
)
from fraggate.errors import FragGateError, FragRefuse
from fraggate.kernel import FragGate
from fraggate.ledger import Ledger
from fraggate.registry import Registry

__all__ = [
    "AUTHOR",
    "ERROR_CODES",
    "HOMEPAGE",
    "MAGIC",
    "PAPER",
    "VERSION",
    "Artifact",
    "CallEnvelope",
    "Claim",
    "Fact",
    "FragGate",
    "FragGateError",
    "FragRefuse",
    "GroundingRef",
    "Ledger",
    "Registry",
    "ResultEnvelope",
    "ToolSpec",
]
