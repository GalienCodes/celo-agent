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

"""This package contains the rounds of CeloSwapperAbciApp."""

from enum import Enum
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

from packages.celo.skills.celo_swapper_abci.payloads import (
    DecisionMakingPayload,
    FinishedDecisionMakingPayload,
    MarketDataCollectionPayload,
    MechRequestPreparationPayload,
    StrategyEvaluationPayload,
    SwapPreparationPayload,
)
from packages.valory.skills.abstract_round_abci.base import (
    AbciApp,
    AbciAppTransitionFunction,
    AbstractRound,
    AppState,
    BaseSynchronizedData,
    DegenerateRound,
    EventToTimeout,
)


class Event(Enum):
    """CeloSwapperAbciApp Events"""

    MECH = "mech"
    ROUND_TIMEOUT = "round_timeout"
    SWAP = "swap"
    STRATEGY = "strategy"
    DONE = "done"
    NO_MAJORITY = "no_majority"


class SynchronizedData(BaseSynchronizedData):
    """
    Class to represent the synchronized data.

    This data is replicated by the tendermint application.
    """


class DecisionMakingRound(AbstractRound):
    """DecisionMakingRound"""

    payload_class = DecisionMakingPayload
    payload_attribute = ""  # TODO: update
    synchronized_data_class = SynchronizedData


class FinishedDecisionMakingRound(AbstractRound):
    """FinishedDecisionMakingRound"""

    payload_class = FinishedDecisionMakingPayload
    payload_attribute = ""  # TODO: update
    synchronized_data_class = SynchronizedData


class MarketDataCollectionRound(AbstractRound):
    """MarketDataCollectionRound"""

    payload_class = MarketDataCollectionPayload
    payload_attribute = ""  # TODO: update
    synchronized_data_class = SynchronizedData


class MechRequestPreparationRound(AbstractRound):
    """MechRequestPreparationRound"""

    payload_class = MechRequestPreparationPayload
    payload_attribute = ""  # TODO: update
    synchronized_data_class = SynchronizedData


class StrategyEvaluationRound(AbstractRound):
    """StrategyEvaluationRound"""

    payload_class = StrategyEvaluationPayload
    payload_attribute = ""  # TODO: update
    synchronized_data_class = SynchronizedData


class SwapPreparationRound(AbstractRound):
    """SwapPreparationRound"""

    payload_class = SwapPreparationPayload
    payload_attribute = ""  # TODO: update
    synchronized_data_class = SynchronizedData


class FinishedMechRequestPreparationRound(DegenerateRound):
    """FinishedMechRequestPreparationRound"""


class FinishedStrategyEvaluationRound(DegenerateRound):
    """FinishedStrategyEvaluationRound"""


class FinishedSwapPreparationRound(DegenerateRound):
    """FinishedSwapPreparationRound"""


class CeloSwapperAbciApp(AbciApp[Event]):
    """CeloSwapperAbciApp"""

    initial_round_cls: AppState = MarketDataCollectionRound
    initial_states: Set[AppState] = {
        DecisionMakingRound,
        MarketDataCollectionRound,
        StrategyEvaluationRound,
    }
    transition_function: AbciAppTransitionFunction = {
        MarketDataCollectionRound: {
            Event.DONE: StrategyEvaluationRound,
            Event.NO_MAJORITY: MarketDataCollectionRound,
            Event.ROUND_TIMEOUT: MarketDataCollectionRound,
        },
        StrategyEvaluationRound: {
            Event.DONE: FinishedStrategyEvaluationRound,
            Event.MECH: MechRequestPreparationRound,
            Event.SWAP: SwapPreparationRound,
            Event.NO_MAJORITY: StrategyEvaluationRound,
            Event.ROUND_TIMEOUT: StrategyEvaluationRound,
        },
        MechRequestPreparationRound: {
            Event.DONE: FinishedMechRequestPreparationRound,
            Event.NO_MAJORITY: MechRequestPreparationRound,
            Event.ROUND_TIMEOUT: MechRequestPreparationRound,
        },
        SwapPreparationRound: {
            Event.DONE: FinishedSwapPreparationRound,
            Event.NO_MAJORITY: SwapPreparationRound,
            Event.ROUND_TIMEOUT: SwapPreparationRound,
        },
        DecisionMakingRound: {
            Event.MECH: FinishedDecisionMakingRound,
            Event.STRATEGY: StrategyEvaluationRound,
            Event.NO_MAJORITY: DecisionMakingRound,
            Event.ROUND_TIMEOUT: DecisionMakingRound,
        },
        FinishedDecisionMakingRound: {},
        FinishedSwapPreparationRound: {},
        FinishedMechRequestPreparationRound: {},
        FinishedStrategyEvaluationRound: {},
    }
    final_states: Set[AppState] = {
        FinishedStrategyEvaluationRound,
        FinishedMechRequestPreparationRound,
        FinishedSwapPreparationRound,
    }
    event_to_timeout: EventToTimeout = {}
    cross_period_persisted_keys: FrozenSet[str] = frozenset()
    db_pre_conditions: Dict[AppState, Set[str]] = {
        DecisionMakingRound: set(),
        MarketDataCollectionRound: set(),
        StrategyEvaluationRound: set(),
    }
    db_post_conditions: Dict[AppState, Set[str]] = {
        FinishedStrategyEvaluationRound: set(),
        FinishedMechRequestPreparationRound: set(),
        FinishedSwapPreparationRound: set(),
    }
