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
from hexbytes import HexBytes
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
from packages.celo.contracts.erc_20.contract import ERC20Contract
from packages.celo.contracts.swap_router.contract import UniswapV3SwapRouterContract
from packages.valory.contracts.multisend.contract import (
    MultiSendContract,
    MultiSendOperation,
)
from packages.valory.protocols.contract_api import ContractApiMessage



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

        tx_list = []

        # swap_data = {
        #     "from_token": "CELO",
        #     "to_token": "cUSD",
        #     "amount": 10
        # }
        swap_data = self.synchronized_data.swap_data

        # Are we swapping from cUSD to CELO orthe other way around?
        # If we're going CELO -> cUSD we need to check our allowance

        if swap_data["from_token"] == "cUSD" and swap_data["to_token"] == "CELO":
            # Check allowance
            allowance = self.get_allowance()

            if allowance < swap_data["amount"]:

                # Increase allowance
                approve_tx_data = self.get_approve_tx_data()

                if not approve_tx_data:
                    return None

                tx_list.append(approve_tx_data)

        # Get swap tx data
        swap_tx_data = self.get_swap_tx_data()

        if not swap_tx_data:
            return None

        tx_list.append(swap_tx_data)

        # Do we need multicall?
        if len(tx_list) > 1:
            tx_data = self.get_multicall_data(tx_list)
        else:
            tx_data = tx_list[0]

        # Safe tx data
        safe_tx_hash = self.get_safe_tx_data(tx_data)

        if not safe_tx_hash:
            return None

        return safe_tx_hash


    def get_allowance(self):
        """Get the allowance"""
        contract_api_msg = yield from self.get_contract_api_response(
            performative=ContractApiMessage.Performative.GET_STATE,  # type: ignore
            contract_address=self.params.cusd_address,
            contract_id=str(ERC20Contract.contract_id),
            contract_callable="allowance",
            owner_address=self.params.safe_contract_address,
            spender_address=self.params.router_contract_address,
        )

        if contract_api_msg.performative != ContractApiMessage.Performative.STATE:
            self.context.logger.error("Could not read the allowance")
            return None

        return contract_api_msg.state.body["allowance"]


    def get_approve_tx_data(self):
        """Update the allowance"""
        contract_api_msg = yield from self.get_contract_api_response(
            performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,  # type: ignore
            contract_address=self.params.cusd_address,
            contract_id=str(ERC20Contract.contract_id),
            contract_callable="approve",
            owner_address=self.params.safe_contract_address,
            spender_address=self.params.router_contract_address,
        )

        if contract_api_msg.performative == ContractApiMessage.Performative.ERROR:
            self.context.logger.error(f"Could not read the allowance: {contract_api_msg}")
            return None

        return {
            "operation": MultiSendOperation.CALL,
            "to": self.params.cusd_address,
            "value": 0,
            "data": HexBytes(
                cast(bytes, contract_api_msg.raw_transaction.body["data"]).hex()
            ),
        }


    def get_swap_tx_data(self, amount_in):
        """get_allowance"""
        contract_api_msg = yield from self.get_contract_api_response(
            performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,  # type: ignore
            contract_address=self.params.swap_router_address,
            contract_id=str(UniswapV3SwapRouterContract.contract_id),
            contract_callable="exact_input_single",
            amount_in=amount_in,
            recipient=self.params.safe_contract_address,
        )

        if contract_api_msg.performative != ContractApiMessage.Performative.RAW_TRANSACTION:
            self.context.logger.error(f"Could not get the swap tx data: {contract_api_msg}")
            return None

        return {
            "operation": MultiSendOperation.CALL,
            "to": self.params.cusd_address,
            "value": 0,
            "data": HexBytes(
                cast(bytes, contract_api_msg.raw_transaction.body["data"]).hex()
            ),
        }


    def get_multisend_data(self, tx_list):
        """Get the tx data from the multisend contract"""
        contract_api_msg = yield from self.get_contract_api_response(
            performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,  # type: ignore
            contract_address=self.synchronized_data.safe_contract_address,
            contract_id=str(MultiSendContract.contract_id),
            contract_callable="get_tx_data",
            multi_send_txs=tx_list,
        )

        if contract_api_msg.performative != ContractApiMessage.Performative.RAW_TRANSACTION:
            self.context.logger.error(f"Could not get the multisend tx data: {contract_api_msg}")
            return None

        multisend_data = cast(str, contract_api_msg.raw_transaction.body["data"])
        multisend_data = multisend_data[2:]

        return multisend_data


    def get_safe_tx_data(self, tx_data):
        """Get the tx data from the Safe contract"""
        contract_api_msg = yield from self.get_contract_api_response(
            performative=ContractApiMessage.Performative.GET_RAW_TRANSACTION,  # type: ignore
            contract_address=self.synchronized_data.safe_contract_address,
            contract_id=str(GnosisSafeContract.contract_id),
            contract_callable="get_raw_safe_transaction_hash",
            to_address=self.synchronized_data.multisend_contract_address,
            value=0,
            data=bytes.fromhex(multisend_data),
            operation=SafeOperation.DELEGATE_CALL.value,
            safe_tx_gas=strategy["safe_tx_gas"]["enter"],
            safe_nonce=strategy["safe_nonce"],
        )
        safe_tx_hash = cast(str, contract_api_msg.raw_transaction.body["tx_hash"])
        safe_tx_hash = safe_tx_hash[2:]
        self.context.logger.info(f"Hash of the Safe transaction: {safe_tx_hash}")

        payload_string = hash_payload_to_hex(
            safe_tx_hash=safe_tx_hash,
            ether_value=0,
            safe_tx_gas=strategy["safe_tx_gas"]["enter"],
            to_address=self.synchronized_data.multisend_contract_address,
            data=bytes.fromhex(multisend_data),
            operation=SafeOperation.DELEGATE_CALL.value,
        )


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
