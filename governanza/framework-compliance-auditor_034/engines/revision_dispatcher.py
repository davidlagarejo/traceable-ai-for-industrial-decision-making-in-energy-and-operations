from __future__ import annotations

from collections import Counter

from models.datatypes import RevisionPacket


def summarize_revision_actions(packet: RevisionPacket) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for instructions in packet.grouped_fixes_by_section.values():
        for instruction in instructions:
            counter[instruction.action.value] += 1
    return dict(counter)

