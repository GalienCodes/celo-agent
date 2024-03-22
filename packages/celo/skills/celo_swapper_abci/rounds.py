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

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, FrozenSet, List, Optional, Set, Tuple, cast

from packages.celo.skills.celo_swapper_abci.payloads import (
    DecisionMakingPayload,
    MechRequestPreparationPayload,
    PostTxDecisionMakingPayload,
    SwapPreparationPayload,
)
from packages.valory.skills.abstract_round_abci.base import (
    AbciApp,
    AbciAppTransitionFunction,
    AppState,
    BaseSynchronizedData,
    CollectSameUntilThresholdRound,
    CollectionRound,
    DegenerateRound,
    DeserializedCollection,
    EventToTimeout,
    get_name,
)


class Event(Enum):
    """CeloSwapperAbciApp Events"""

    DECISION_MAKING = "decision_making"
    MECH = "mech"
    SWAP = "swap"
    DONE = "done"
    NO_MAJORITY = "no_majority"
    ROUND_TIMEOUT = "round_timeout"


@dataclass
class MechMetadata:
    """A Mech's metadata."""

    prompt: str
    tool: str
    nonce: str


@dataclass
class MechRequest:
    """A Mech's request."""

    data: str = ""
    requestId: int = 0


@dataclass
class MechInteractionResponse(MechRequest):
    """A structure for the response of a mech interaction task."""

    nonce: str = ""
    result: Optional[str] = None
    error: str = "Unknown"

    def retries_exceeded(self) -> None:
        """Set an incorrect format response."""
        self.error = "Retries were exceeded while trying to get the mech's response."

    def incorrect_format(self, res: Any) -> None:
        """Set an incorrect format response."""
        self.error = f"The response's format was unexpected: {res}"


class SynchronizedData(BaseSynchronizedData):
    """
    Class to represent the synchronized data.

    This data is replicated by the tendermint application.
    """

    @property
    def mech_requests(self) -> List[MechMetadata]:
        """Get the mech requests."""
        serialized = self.db.get("mech_requests", "[]")
        requests = json.loads(serialized)  # type: ignore
        return [MechMetadata(**metadata_item) for metadata_item in requests]

    @property
    def mech_responses(self) -> List[MechInteractionResponse]:
        """Get the mech responses."""
        serialized = self.db.get("mech_responses", "[]")
        responses = json.loads(serialized)  # type: ignore
        return [MechInteractionResponse(**response_item) for response_item in responses]

    @property
    def most_voted_tx_hash(self) -> str:
        """Get the most_voted_tx_hash."""
        return cast(str, self.db.get_strict("most_voted_tx_hash"))

    @property
    def post_tx_event(self) -> Optional[str]:
        """Get the post_tx_event."""
        return cast(str, self.db.get("post_tx_event", None))

    @property
    def swap_data(self) -> Optional[str]:
        """Get the post_tx_event."""
        serialized = self.db.get("swap_data", None)
        if serialized:
            return json.loads(serialized)
        return None


class DecisionMakingRound(CollectSameUntilThresholdRound):
    """DecisionMakingRound"""

    payload_class = DecisionMakingPayload
    synchronized_data_class = SynchronizedData

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Event]]:
        """Process the end of the block."""
        if self.threshold_reached:
            event = Event(self.most_voted_payload.event)
            swap_data = self.most_voted_payload.swap_data
            updates = {}

            # After using the mech interactions, clean them up
            if event == Event.SWAP:
                updates["mech_requests"] = []
                updates["mech_responses"] = []
                updates["swap_data"] = swap_data

            # Cleanup at the end of the period
            if event == Event.DONE:
                updates["post_tx_event"] = None
                updates["swap_data"] = None

            synchronized_data = self.synchronized_data.update(
                synchronized_data_class=self.synchronized_data_class,
                **{
                    get_name(getattr(SynchronizedData, k)): v
                    for k, v in updates.items()
                },
            )

            return synchronized_data, event

        if not self.is_majority_possible(
            self.collection, self.synchronized_data.nb_participants
        ):
            return self.synchronized_data, Event.NO_MAJORITY
        return None


class MechRequestPreparationRound(CollectSameUntilThresholdRound):
    """MechRequestPreparationRound"""

    payload_class = MechRequestPreparationPayload
    synchronized_data_class = SynchronizedData

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Event]]:
        """Process the end of the block."""
        if self.threshold_reached:
            synchronized_data = self.synchronized_data.update(
                synchronized_data_class=self.synchronized_data_class,
                **{
                    # Go to mech responses after exiting tx settlemet
                    get_name(SynchronizedData.post_tx_event): Event.MECH.value,
                    get_name(SynchronizedData.mech_requests): self.most_voted_payload,
                },
            )
            return synchronized_data, Event(self.most_voted_payload)

        if not self.is_majority_possible(
            self.collection, self.synchronized_data.nb_participants
        ):
            return self.synchronized_data, Event.NO_MAJORITY
        return None


class SwapPreparationRound(CollectSameUntilThresholdRound):
    """SwapPreparationRound"""

    payload_class = SwapPreparationPayload
    synchronized_data_class = SynchronizedData

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Event]]:
        """Process the end of the block."""
        if self.threshold_reached:
            synchronized_data = self.synchronized_data.update(
                synchronized_data_class=self.synchronized_data_class,
                **{
                    # Go to decision making after exiting tx settlemet
                    get_name(
                        SynchronizedData.post_tx_event
                    ): Event.DECISION_MAKING.value,
                    get_name(
                        SynchronizedData.most_voted_tx_hash
                    ): self.most_voted_payload,
                },
            )
            return synchronized_data, Event(self.most_voted_payload)

        if not self.is_majority_possible(
            self.collection, self.synchronized_data.nb_participants
        ):
            return self.synchronized_data, Event.NO_MAJORITY
        return None


class PostTxDecisionMakingRound(CollectSameUntilThresholdRound):
    """PostTxDecisionMakingRound"""

    payload_class = PostTxDecisionMakingPayload
    synchronized_data_class = SynchronizedData

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Event]]:
        """Process the end of the block."""
        if self.threshold_reached:
            return self.synchronized_data, Event(self.most_voted_payload)

        if not self.is_majority_possible(
            self.collection, self.synchronized_data.nb_participants
        ):
            return self.synchronized_data, Event.NO_MAJORITY
        return None


class FinishedPostTxDecisionMakingRound(DegenerateRound):
    """FinishedPostTxDecisionMakingRound"""


class FinishedMechRequestPreparationRound(DegenerateRound):
    """FinishedMechRequestPreparationRound"""


class FinishedDecisionMakingRound(DegenerateRound):
    """FinishedDecisionMakingRound"""


class FinishedSwapPreparationRound(DegenerateRound):
    """FinishedSwapPreparationRound"""


class CeloSwapperAbciApp(AbciApp[Event]):
    """CeloSwapperAbciApp"""

    initial_round_cls: AppState = DecisionMakingRound
    initial_states: Set[AppState] = {
        PostTxDecisionMakingRound,
        DecisionMakingRound,
    }
    transition_function: AbciAppTransitionFunction = {
        DecisionMakingRound: {
            Event.DONE: FinishedDecisionMakingRound,
            Event.MECH: MechRequestPreparationRound,
            Event.SWAP: SwapPreparationRound,
            Event.NO_MAJORITY: DecisionMakingRound,
            Event.ROUND_TIMEOUT: DecisionMakingRound,
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
        PostTxDecisionMakingRound: {
            Event.MECH: FinishedPostTxDecisionMakingRound,
            Event.DECISION_MAKING: DecisionMakingRound,
            Event.NO_MAJORITY: PostTxDecisionMakingRound,
            Event.ROUND_TIMEOUT: PostTxDecisionMakingRound,
        },
        FinishedMechRequestPreparationRound: {},
        FinishedSwapPreparationRound: {},
        FinishedDecisionMakingRound: {},
        FinishedPostTxDecisionMakingRound: {},
    }
    final_states: Set[AppState] = {
        FinishedDecisionMakingRound,
        FinishedMechRequestPreparationRound,
        FinishedSwapPreparationRound,
    }
    event_to_timeout: EventToTimeout = {}
    cross_period_persisted_keys: FrozenSet[str] = frozenset()
    db_pre_conditions: Dict[AppState, Set[str]] = {
        PostTxDecisionMakingRound: set(),
        DecisionMakingRound: set(),
    }
    db_post_conditions: Dict[AppState, Set[str]] = {
        FinishedDecisionMakingRound: set(),
        FinishedMechRequestPreparationRound: set(),
        FinishedSwapPreparationRound: set(),
    }
