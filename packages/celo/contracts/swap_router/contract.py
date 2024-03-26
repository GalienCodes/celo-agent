# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2021-2024 Valory AG
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

"""This module contains the class to connect to a Uniswap V2 Router02 contract."""
import logging
from typing import Any, Optional

from aea.common import JSONLike
from aea.configurations.base import PublicId
from aea.contracts.base import Contract
from aea_ledger_ethereum import EthereumApi


PUBLIC_ID = PublicId.from_str("celo/swap_router:0.1.0")

_logger = logging.getLogger(
    f"aea.packages.{PUBLIC_ID.author}.contracts.{PUBLIC_ID.name}.contract"
)


class UniswapV3SwapRouterContract(Contract):
    """The Uniswap V3 SwapRouter contract."""

    contract_id = PUBLIC_ID


    @classmethod
    def exact_input_single(
        cls,
        ledger_api: EthereumApi,
        contract_address: str,
        amount_in: int,
        recipient: str,
        sqrt_price_limit_x96: int=0,
        **kwargs: Any,
    ) -> Optional[JSONLike]:
        """Swap exact tokens for tokens."""
        contract_instance = cls.get_instance(ledger_api, contract_address)

        return ledger_api.build_transaction(
            contract_instance,
            "exactInputSingle",
            method_args=dict(
                amountIn=amount_in,
                recipient=recipient,
                sqrtPriceLimitX96=sqrt_price_limit_x96,
            ),
            tx_args=kwargs,
        )
