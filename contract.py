"""Structured tool and task contracts; declarations only."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    COMPUTE = "compute"


class Task(Enum):
    RUN = "retrieve-memory"


@dataclass
class Memory(Output):
    id: Annotated[str, "Unique memory ID"]
    profile: Annotated[str, "Investor profile ID"]
    symbol: Annotated[str, "Ticker"]
    regime: Annotated[str, "Market regime label"]
    observed_at: Annotated[str, "Original decision timestamp"]
    resolved_at: Annotated[str, "Outcome availability timestamp; empty means unresolved"]
    utility: Annotated[int, "Audited utility tie break, -100 to 100"]


@dataclass
class Hit(Output):
    id: Annotated[str, "Retrieved memory ID"]
    score: Annotated[int, "4 profile match + 2 symbol match + 1 regime match"]


@dataclass
class TaskInput(Output):
    memories: Annotated[list[Memory], "Frozen memory store"]
    profile: Annotated[str, "Requested profile"]
    symbol: Annotated[str, "Requested ticker"]
    regime: Annotated[str, "Requested regime"]
    cutoff: Annotated[str, "Inclusive decision timestamp"]
    ttl_days: Annotated[int, "Inclusive lifetime measured from resolution"]
    top_k: Annotated[int, "Maximum retrieval size; zero returns no hits"]


@dataclass
class TaskOutput(Output):
    hits: Annotated[list[Hit], "Rank score descending, utility descending, resolution descending, id ascending"]


TOOLS = {Tool.COMPUTE: (TaskInput, TaskOutput)}
TASKS = {Task.RUN: (TaskInput, TaskOutput)}
