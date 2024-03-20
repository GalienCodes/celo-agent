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

from abc import ABC
from typing import Generator, Set, Type, cast

from packages.celo.skills.celo_swapper_abci.models import Params
from packages.celo.skills.celo_swapper_abci.rounds import (
    CeloSwapperAbciApp,
    DecisionMakingPayload,
    DecisionMakingRound,
    FinishedDecisionMakingPayload,
    FinishedDecisionMakingRound,
    MarketDataCollectionPayload,
    MarketDataCollectionRound,
    MechRequestPreparationPayload,
    MechRequestPreparationRound,
    StrategyEvaluationPayload,
    StrategyEvaluationRound,
    SwapPreparationPayload,
    SwapPreparationRound,
    SynchronizedData,
)
from packages.valory.skills.abstract_round_abci.base import AbstractRound
from packages.valory.skills.abstract_round_abci.behaviours import (
    AbstractRoundBehaviour,
    BaseBehaviour,
)


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


class DecisionMakingBehaviour(CeloSwapperBaseBehaviour):
    """DecisionMakingBehaviour"""

    matching_round: Type[AbstractRound] = DecisionMakingRound

    # TODO: implement logic required to set payload content for synchronization
    def async_act(self) -> Generator:
        """Do the act, supporting asynchronous execution."""

        with self.context.benchmark_tool.measure(self.behaviour_id).local():
            sender = self.context.agent_address
            payload = DecisionMakingPayload(sender=sender, content=...)

        with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()

        self.set_done()


class FinishedDecisionMakingBehaviour(CeloSwapperBaseBehaviour):
    """FinishedDecisionMakingBehaviour"""

    matching_round: Type[AbstractRound] = FinishedDecisionMakingRound

    # TODO: implement logic required to set payload content for synchronization
    def async_act(self) -> Generator:
        """Do the act, supporting asynchronous execution."""

        with self.context.benchmark_tool.measure(self.behaviour_id).local():
            sender = self.context.agent_address
            payload = FinishedDecisionMakingPayload(sender=sender, content=...)

        with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()

        self.set_done()


class MarketDataCollectionBehaviour(CeloSwapperBaseBehaviour):
    """MarketDataCollectionBehaviour"""

    matching_round: Type[AbstractRound] = MarketDataCollectionRound

    # TODO: implement logic required to set payload content for synchronization
    def async_act(self) -> Generator:
        """Do the act, supporting asynchronous execution."""

        with self.context.benchmark_tool.measure(self.behaviour_id).local():
            sender = self.context.agent_address
            payload = MarketDataCollectionPayload(sender=sender, content=...)

        with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()

        self.set_done()


class MechRequestPreparationBehaviour(CeloSwapperBaseBehaviour):
    """MechRequestPreparationBehaviour"""

    matching_round: Type[AbstractRound] = MechRequestPreparationRound

    # TODO: implement logic required to set payload content for synchronization
    def async_act(self) -> Generator:
        """Do the act, supporting asynchronous execution."""

        with self.context.benchmark_tool.measure(self.behaviour_id).local():
            sender = self.context.agent_address
            payload = MechRequestPreparationPayload(sender=sender, content=...)

        with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()

        self.set_done()


class StrategyEvaluationBehaviour(CeloSwapperBaseBehaviour):
    """StrategyEvaluationBehaviour"""

    matching_round: Type[AbstractRound] = StrategyEvaluationRound

    # TODO: implement logic required to set payload content for synchronization
    def async_act(self) -> Generator:
        """Do the act, supporting asynchronous execution."""

        with self.context.benchmark_tool.measure(self.behaviour_id).local():
            sender = self.context.agent_address
            payload = StrategyEvaluationPayload(sender=sender, content=...)

        with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()

        self.set_done()


class SwapPreparationBehaviour(CeloSwapperBaseBehaviour):
    """SwapPreparationBehaviour"""

    matching_round: Type[AbstractRound] = SwapPreparationRound

    # TODO: implement logic required to set payload content for synchronization
    def async_act(self) -> Generator:
        """Do the act, supporting asynchronous execution."""

        with self.context.benchmark_tool.measure(self.behaviour_id).local():
            sender = self.context.agent_address
            payload = SwapPreparationPayload(sender=sender, content=...)

        with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()

        self.set_done()


class CeloSwapperRoundBehaviour(AbstractRoundBehaviour):
    """CeloSwapperRoundBehaviour"""

    initial_behaviour_cls = MarketDataCollectionBehaviour
    abci_app_cls = CeloSwapperAbciApp  # type: ignore
    behaviours: Set[Type[BaseBehaviour]] = [
        DecisionMakingBehaviour,
        FinishedDecisionMakingBehaviour,
        MarketDataCollectionBehaviour,
        MechRequestPreparationBehaviour,
        StrategyEvaluationBehaviour,
        SwapPreparationBehaviour,
    ]
