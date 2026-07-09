"""
This file defines the Pydantic schema used to process the results of the LLM.
"""
from typing import Literal, List
from pydantic import BaseModel
from src.prompts import STEREOTYPES_LIST

TRAIT_NAMES = tuple(item["name"] for item in STEREOTYPES_LIST)
TraitName = Literal[TRAIT_NAMES]


class TraitEvaluation(BaseModel):
    name: TraitName # type: ignore
    response: Literal["yes", "no"]
    reasoning: str

class ValidationSchema(BaseModel):
    model_config = {"extra": "forbid"}
    evaluations: List[TraitEvaluation]