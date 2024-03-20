# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2024 Valory AG
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""This module contains the transaction payloads of the CeloSwapperAbciApp."""

from dataclasses import dataclass

from packages.valory.skills.abstract_round_abci.base import BaseTxPayload


@dataclass(frozen=True)
class DecisionMakingPayload(BaseTxPayload):
    """Represent a transaction payload for the DecisionMakingRound."""

    # TODO: define your attributes


@dataclass(frozen=True)
class FinishedDecisionMakingPayload(BaseTxPayload):
    """Represent a transaction payload for the FinishedDecisionMakingRound."""

    # TODO: define your attributes


@dataclass(frozen=True)
class MarketDataCollectionPayload(BaseTxPayload):
    """Represent a transaction payload for the MarketDataCollectionRound."""

    # TODO: define your attributes


@dataclass(frozen=True)
class MechRequestPreparationPayload(BaseTxPayload):
    """Represent a transaction payload for the MechRequestPreparationRound."""

    # TODO: define your attributes


@dataclass(frozen=True)
class StrategyEvaluationPayload(BaseTxPayload):
    """Represent a transaction payload for the StrategyEvaluationRound."""

    # TODO: define your attributes


@dataclass(frozen=True)
class SwapPreparationPayload(BaseTxPayload):
    """Represent a transaction payload for the SwapPreparationRound."""

    # TODO: define your attributes
