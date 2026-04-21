# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Data models for the OptimaTrade Trading Environment.

The environment simulates a stock price and tracks an agent's balance/holdings.
"""

from enum import Enum
from openenv.core.env_server.types import Action, Observation
from pydantic import Field


class TradingActionType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class FirstRlDemoAction(Action):
    """Action for the Trading environment."""

    action: TradingActionType = Field(..., description="Action to take: BUY, SELL, or HOLD")


class FirstRlDemoObservation(Observation):
    """Observation from the Trading environment."""

    price: float = Field(..., description="Current price of the asset")
    balance: float = Field(..., description="Current cash balance")
    holdings: int = Field(..., description="Number of shares currently held")
    net_worth: float = Field(..., description="Total value (balance + holdings * price)")
    step: int = Field(..., description="Current step in the episode")
