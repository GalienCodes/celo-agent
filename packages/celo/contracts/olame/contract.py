# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2024 MUhindo-Galien
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

"""This module contains the scaffold contract definition."""

from typing import Any

from aea.common import JSONLike
from aea.configurations.base import PublicId
from aea.contracts.base import Contract
from aea.crypto.base import LedgerApi
from aea_ledger_ethereum import EthereumApi

class AMMContract(Contract):
    """AMM contract."""

    contract_id = PublicId.from_str("valory/erc20:0.1.0")

    """ Allows the connected account to mint 1000 OLA tokens"""
    @classmethod
    def faucet(    
        cls,
        ledger_api: LedgerApi,
        token_contract_address: str
        )-> JSONLike:

        token_instance = cls.get_instance(
            ledger_api=ledger_api,
            contract_address= token_contract_address,
        )
        token_instance.functions.faucet()


    """ 
    Calculates the amount of output tokens for a given input amount and reserves.

    :param _swapAmountWei: true means you swap CEO for OLA tokens
    :param celoSelected: true means you swap CEO for OLA tokens
    :param celoBalance: CELO balance of the connected account
    :param reservedOlameToken: the reserve of Olame tokens held by the contract.
    :return token_to_be_received_after_swap: to be used when swapping
    """

    @classmethod
    def getAmountOfTokensReceivedFromSwap(
         cls,
        ledger_api: LedgerApi,
        amm_contract_address: str,
        _swapAmountWei:int,
        celoSelected:bool,
        celoBalance:int,
        reservedOlameToken:int
        )-> JSONLike:

        amm_instance = cls.get_instance(
            ledger_api=ledger_api,
            contract_address= amm_contract_address,
        )
        
       
        amountOfTokens
        if celoSelected:
            amountOfTokens =  amm_instance.functions.getAmountOfTokens(
            _swapAmountWei,
            celoBalance,
            reservedOlameToken
            )
        else :
            amountOfTokens = amm_instance.functions.getAmountOfTokens(
            _swapAmountWei,
            reservedOlameToken,
            celoBalance
            )
        return amountOfTokens
        

    """ 
    This function alows Swap from CELO to Olame if celoSelected is true 
    otherwise it swaps OLA to CELO


    :param _swapAmountWei: true means you swap CEO for OLA tokens
    :param token_to_be_received_after_swap: to be used when swapping
    """

    @classmethod
    def swap_tokens(
        cls,
        ledger_api: LedgerApi,
        amm_contract_address: str,
        token_contract_address: str,
        sender:str,
        swap_amount_wei,
        token_to_be_received_after_swap,
        celo_selected)-> JSONLike:

        amm_instance = cls.get_instance(
    
            ledger_api=ledger_api,
            contract_address= amm_contract_address,
        )

        token_instance = cls.get_instance(
            ledger_api=ledger_api,
            contract_address= token_contract_address,
        )

        if celo_selected:
             amm_instance.functions.celoToOlameToken(
            token_to_be_received_after_swap
            ).buildTransaction({'from': sender})
        else:
            token_instance.functions.approve(
             amm_contract_address,
            swap_amount_wei
            ).buildTransaction({'from': sender})
            
            token_instance.functions.olameTokenToCelo(
            swap_amount_wei,
            token_to_be_received_after_swap
            ).buildTransaction({'from': sender})
        

    
    