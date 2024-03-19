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

from packages.valory.skills.abstract_round_abci.base import (
    AbciApp,
    AbciAppTransitionFunction,
    AbstractRound,
    AppState,
    BaseSynchronizedData,
    DegenerateRound,
    EventToTimeout,
)

from packages.celo.skills.celo_swapper.payloads import (
    DecisionMakingPayload,
    FinishedDecisionMakingPayload,
    MarketDataCollectionPayload,
    MechRequestPreparationPayload,
    StrategyEvaluationPayload,
    SwapPreparationPayload,
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

    # TODO: replace AbstractRound with one of CollectDifferentUntilAllRound,
    # CollectSameUntilAllRound, CollectSameUntilThresholdRound,
    # CollectDifferentUntilThresholdRound, OnlyKeeperSendsRound, VotingRound,
    # from packages/valory/skills/abstract_round_abci/base.py
    # or implement the methods

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Enum]]:
        """Process the end of the block."""
        raise NotImplementedError

    def check_payload(self, payload: DecisionMakingPayload) -> None:
        """Check payload."""
        raise NotImplementedError

    def process_payload(self, payload: DecisionMakingPayload) -> None:
        """Process payload."""
        raise NotImplementedError


class FinishedDecisionMakingRound(AbstractRound):
    """FinishedDecisionMakingRound"""

    payload_class = FinishedDecisionMakingPayload
    payload_attribute = ""  # TODO: update
    synchronized_data_class = SynchronizedData

    # TODO: replace AbstractRound with one of CollectDifferentUntilAllRound,
    # CollectSameUntilAllRound, CollectSameUntilThresholdRound,
    # CollectDifferentUntilThresholdRound, OnlyKeeperSendsRound, VotingRound,
    # from packages/valory/skills/abstract_round_abci/base.py
    # or implement the methods

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Enum]]:
        """Process the end of the block."""
        raise NotImplementedError

    def check_payload(self, payload: FinishedDecisionMakingPayload) -> None:
        """Check payload."""
        raise NotImplementedError

    def process_payload(self, payload: FinishedDecisionMakingPayload) -> None:
        """Process payload."""
        raise NotImplementedError


class MarketDataCollectionRound(AbstractRound):
    """MarketDataCollectionRound"""

    payload_class = MarketDataCollectionPayload
    payload_attribute = ""  # TODO: update
    synchronized_data_class = SynchronizedData

    # TODO: replace AbstractRound with one of CollectDifferentUntilAllRound,
    # CollectSameUntilAllRound, CollectSameUntilThresholdRound,
    # CollectDifferentUntilThresholdRound, OnlyKeeperSendsRound, VotingRound,
    # from packages/valory/skills/abstract_round_abci/base.py
    # or implement the methods

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Enum]]:
        """Process the end of the block."""
        raise NotImplementedError

    def check_payload(self, payload: MarketDataCollectionPayload) -> None:
        """Check payload."""
        raise NotImplementedError

    def process_payload(self, payload: MarketDataCollectionPayload) -> None:
        """Process payload."""
        raise NotImplementedError


class MechRequestPreparationRound(AbstractRound):
    """MechRequestPreparationRound"""

    payload_class = MechRequestPreparationPayload
    payload_attribute = ""  # TODO: update
    synchronized_data_class = SynchronizedData

    # TODO: replace AbstractRound with one of CollectDifferentUntilAllRound,
    # CollectSameUntilAllRound, CollectSameUntilThresholdRound,
    # CollectDifferentUntilThresholdRound, OnlyKeeperSendsRound, VotingRound,
    # from packages/valory/skills/abstract_round_abci/base.py
    # or implement the methods

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Enum]]:
        """Process the end of the block."""
        raise NotImplementedError

    def check_payload(self, payload: MechRequestPreparationPayload) -> None:
        """Check payload."""
        raise NotImplementedError

    def process_payload(self, payload: MechRequestPreparationPayload) -> None:
        """Process payload."""
        raise NotImplementedError


class StrategyEvaluationRound(AbstractRound):
    """StrategyEvaluationRound"""

    payload_class = StrategyEvaluationPayload
    payload_attribute = ""  # TODO: update
    synchronized_data_class = SynchronizedData

    # TODO: replace AbstractRound with one of CollectDifferentUntilAllRound,
    # CollectSameUntilAllRound, CollectSameUntilThresholdRound,
    # CollectDifferentUntilThresholdRound, OnlyKeeperSendsRound, VotingRound,
    # from packages/valory/skills/abstract_round_abci/base.py
    # or implement the methods

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Enum]]:
        """Process the end of the block."""
        raise NotImplementedError

    def check_payload(self, payload: StrategyEvaluationPayload) -> None:
        """Check payload."""
        raise NotImplementedError

    def process_payload(self, payload: StrategyEvaluationPayload) -> None:
        """Process payload."""
        raise NotImplementedError


class SwapPreparationRound(AbstractRound):
    """SwapPreparationRound"""

    payload_class = SwapPreparationPayload
    payload_attribute = ""  # TODO: update
    synchronized_data_class = SynchronizedData

    # TODO: replace AbstractRound with one of CollectDifferentUntilAllRound,
    # CollectSameUntilAllRound, CollectSameUntilThresholdRound,
    # CollectDifferentUntilThresholdRound, OnlyKeeperSendsRound, VotingRound,
    # from packages/valory/skills/abstract_round_abci/base.py
    # or implement the methods

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Enum]]:
        """Process the end of the block."""
        raise NotImplementedError

    def check_payload(self, payload: SwapPreparationPayload) -> None:
        """Check payload."""
        raise NotImplementedError

    def process_payload(self, payload: SwapPreparationPayload) -> None:
        """Process payload."""
        raise NotImplementedError


class FinishedMechRequestPreparationRound(DegenerateRound):
    """FinishedMechRequestPreparationRound"""


class FinishedStrategyEvaluationRound(DegenerateRound):
    """FinishedStrategyEvaluationRound"""


class FinishedSwapPreparationRound(DegenerateRound):
    """FinishedSwapPreparationRound"""


class CeloSwapperAbciApp(AbciApp[Event]):
    """CeloSwapperAbciApp"""

    initial_round_cls: AppState = MarketDataCollectionRound
    initial_states: Set[AppState] = {DecisionMakingRound, MarketDataCollectionRound, StrategyEvaluationRound}
    transition_function: AbciAppTransitionFunction = {
        MarketDataCollectionRound: {
            Event.DONE: StrategyEvaluationRound,
            Event.NO_MAJORITY: MarketDataCollectionRound,
            Event.ROUND_TIMEOUT: MarketDataCollectionRound
        },
        StrategyEvaluationRound: {
            Event.DONE: FinishedStrategyEvaluationRound,
            Event.MECH: MechRequestPreparationRound,
            Event.SWAP: SwapPreparationRound,
            Event.NO_MAJORITY: StrategyEvaluationRound,
            Event.ROUND_TIMEOUT: StrategyEvaluationRound
        },
        MechRequestPreparationRound: {
            Event.DONE: FinishedMechRequestPreparationRound,
            Event.NO_MAJORITY: MechRequestPreparationRound,
            Event.ROUND_TIMEOUT: MechRequestPreparationRound
        },
        SwapPreparationRound: {
            Event.DONE: FinishedSwapPreparationRound,
            Event.NO_MAJORITY: SwapPreparationRound,
            Event.ROUND_TIMEOUT: SwapPreparationRound
        },
        DecisionMakingRound: {
            Event.MECH: FinishedDecisionMakingRound,
            Event.STRATEGY: StrategyEvaluationRound,
            Event.NO_MAJORITY: DecisionMakingRound,
            Event.ROUND_TIMEOUT: DecisionMakingRound
        },
        FinishedDecisionMakingRound: {},
        FinishedSwapPreparationRound: {},
        FinishedMechRequestPreparationRound: {},
        FinishedStrategyEvaluationRound: {}
    }
    final_states: Set[AppState] = {FinishedStrategyEvaluationRound, FinishedMechRequestPreparationRound, FinishedSwapPreparationRound}
    event_to_timeout: EventToTimeout = {}
    cross_period_persisted_keys: FrozenSet[str] = frozenset()
    db_pre_conditions: Dict[AppState, Set[str]] = {
        DecisionMakingRound: [],
    	MarketDataCollectionRound: [],
    	StrategyEvaluationRound: [],
    }
    db_post_conditions: Dict[AppState, Set[str]] = {
        FinishedStrategyEvaluationRound: [],
    	FinishedMechRequestPreparationRound: [],
    	FinishedSwapPreparationRound: [],
    }
