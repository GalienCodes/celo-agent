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

"""This package contains round behaviours of CeloSwapperAbciApp."""

import json
import uuid
from abc import ABC
from dataclasses import asdict
from typing import Dict, Generator, Optional, Set, Type, cast

from packages.celo.skills.celo_swapper_abci.models import Params
from packages.celo.skills.celo_swapper_abci.rounds import (
    CeloSwapperAbciApp,
    DecisionMakingPayload,
    DecisionMakingRound,
    Event,
    MechMetadata,
    MechRequestPreparationPayload,
    MechRequestPreparationRound,
    PostTxDecisionMakingPayload,
    PostTxDecisionMakingRound,
    SwapPreparationPayload,
    SwapPreparationRound,
    SynchronizedData,
)
from packages.valory.skills.abstract_round_abci.base import AbstractRound
from packages.valory.skills.abstract_round_abci.behaviours import (
    AbstractRoundBehaviour,
    BaseBehaviour,
)
from packages.valory.skills.celo_swapper_abci.models import Params, SharedState


CELO_TOOL_NAME = ""
MECH_PROMPT = ""


class CeloSwapperBaseBehaviour(BaseBehaviour, ABC):
    """Base behaviour for the celo_swapper skill."""

    @property
    def synchronized_data(self) -> SynchronizedData:
        """Return the synchronized data."""
        return cast(SynchronizedData, super().synchronized_data)

    @property
    def params(self) -> Params:
        """Return the params."""
        return cast(Params, super().params)

    @property
    def local_state(self) -> SharedState:
        """Return the state."""
        return cast(SharedState, self.context.state)


class DecisionMakingBehaviour(CeloSwapperBaseBehaviour):
    """DecisionMakingBehaviour"""

    matching_round: Type[AbstractRound] = DecisionMakingRound

    def async_act(self) -> Generator:
        """Do the act, supporting asynchronous execution."""

        with self.context.benchmark_tool.measure(self.behaviour_id).local():

            # Default values
            event = Event.DONE.value
            swap_data = None

            # If there is no mech_response, we transition into mech request
            if not self.synchronized_data.mech_responses:
                event = Event.MECH.value

            # If the mech tool has decided not to swap, we skip swapping
            swap_data = self.process_mech_response()
            if not swap_data["swap"]:
                event = Event.DONE.value

            # If there is no most_voted_tx_hash, we transition into swap preparation
            if not self.synchronized_data.most_voted_tx_hash:
                event = Event.SWAP.value

            sender = self.context.agent_address
            payload = DecisionMakingPayload(
                sender=sender,
                event=event,
                swap_data=json.dumps(swap_data, sort_keys=True),
            )

        with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()

        self.set_done()

    def process_mech_response(self) -> Dict:
        """Get the swap data from the mech response"""

        mech_responses = self.synchronized_data.mech_responses

        return {}


class MechRequestPreparationBehaviour(CeloSwapperBaseBehaviour):
    """MechRequestPreparationBehaviour"""

    matching_round: Type[AbstractRound] = MechRequestPreparationRound

    def async_act(self) -> Generator:
        """Do the act, supporting asynchronous execution."""

        with self.context.benchmark_tool.measure(self.behaviour_id).local():
            mech_requests = self.get_mech_requests()
            sender = self.context.agent_address
            payload = MechRequestPreparationPayload(
                sender=sender, mech_requests=mech_requests
            )

        with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()

        self.set_done()

    def get_mech_requests(self):
        """Get mech requests"""

        mech_requests = [
            asdict(
                MechMetadata(
                    nonce=str(uuid.uuid4()),
                    tool=CELO_TOOL_NAME,
                    prompt=MECH_PROMPT,
                )
            )
        ]

        return json.dumps(mech_requests)


class SwapPreparationBehaviour(CeloSwapperBaseBehaviour):
    """SwapPreparationBehaviour"""

    matching_round: Type[AbstractRound] = SwapPreparationRound

    def async_act(self) -> Generator:
        """Do the act, supporting asynchronous execution."""

        with self.context.benchmark_tool.measure(self.behaviour_id).local():
            sender = self.context.agent_address
            tx_hash = yield from self.get_tx_hash()
            payload = SwapPreparationPayload(sender=sender, tx_hash=tx_hash)

        with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()

        self.set_done()

    def get_tx_hash(self) -> Generator[None, None, Optional[str]]:
        """Get the swap tx hash"""

        tx_hash = None

        swap_data = self.synchronized_data.swap_data

        # Check approval + Approval + Swap

        return tx_hash


class PostTxDecisionMakingBehaviour(CeloSwapperBaseBehaviour):
    """PostTxDecisionMakingBehaviour"""

    matching_round: Type[AbstractRound] = PostTxDecisionMakingRound

    def async_act(self) -> Generator:
        """Do the act, supporting asynchronous execution."""

        with self.context.benchmark_tool.measure(self.behaviour_id).local():
            event = cast(str, self.synchronized_data.post_tx_event)
            sender = self.context.agent_address
            payload = PostTxDecisionMakingPayload(sender=sender, event=event)

        with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()

        self.set_done()


class CeloSwapperRoundBehaviour(AbstractRoundBehaviour):
    """CeloSwapperRoundBehaviour"""

    initial_behaviour_cls = DecisionMakingBehaviour
    abci_app_cls = CeloSwapperAbciApp  # type: ignore
    behaviours: Set[Type[BaseBehaviour]] = [
        DecisionMakingBehaviour,
        MechRequestPreparationBehaviour,
        SwapPreparationBehaviour,
        PostTxDecisionMakingBehaviour,
    ]
