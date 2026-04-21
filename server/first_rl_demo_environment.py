# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
First Rl Demo Environment Implementation.

A simple test environment that echoes back messages sent to it.
Perfect for testing HTTP server infrastructure.
"""

import random
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import FirstRlDemoAction, FirstRlDemoObservation, TradingActionType
except (ModuleNotFoundError, ImportError):
    from models import FirstRlDemoAction, FirstRlDemoObservation, TradingActionType


class FirstRlDemoEnvironment(Environment):
    """
    A simple Trading environment.

    The environment simulates a stock price and tracks an agent's balance/holdings.
    Reward is tied to the increase in Total Net Worth.
    """

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        """Initialize the trading environment."""
        self._reset_internal()

    def _reset_internal(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.price = 100.0
        self.balance = 1000.0
        self.holdings = 0
        self.last_net_worth = 1000.0

    def reset(self) -> FirstRlDemoObservation:
        """Reset the environment to starting conditions."""
        self._reset_internal()
        
        return FirstRlDemoObservation(
            price=self.price,
            balance=self.balance,
            holdings=self.holdings,
            net_worth=self.last_net_worth,
            step=0,
            done=False,
            reward=0.0
        )

    def step(self, action: FirstRlDemoAction) -> FirstRlDemoObservation:  # type: ignore[override]
        """
        Execute a trading step.
        BUY: Spend balance for 1 unit at current price.
        SELL: Sell 1 unit if held.
        HOLD: Do nothing.
        """
        self._state.step_count += 1
        
        # 1. Process Trading Action
        if action.action == TradingActionType.BUY:
            if self.balance >= self.price:
                self.balance -= self.price
                self.holdings += 1
        elif action.action == TradingActionType.SELL:
            if self.holdings > 0:
                self.balance += self.price
                self.holdings -= 1
        
        # 2. Update Price (Random Walk: -2% to +2.5% increase)
        price_change = self.price * random.uniform(-0.02, 0.025)
        self.price += price_change
        
        # 3. Calculate Reward
        current_net_worth = self.balance + (self.holdings * self.price)
        reward = current_net_worth - self.last_net_worth
        self.last_net_worth = current_net_worth

        # 4. Check Termination (e.g., after 50 steps)
        done = self._state.step_count >= 50

        return FirstRlDemoObservation(
            price=round(self.price, 2),
            balance=round(self.balance, 2),
            holdings=self.holdings,
            net_worth=round(current_net_worth, 2),
            step=self._state.step_count,
            done=done,
            reward=round(reward, 2),
            metadata={"price_change": round(price_change, 2)}
        )

    @property
    def state(self) -> State:
        """Get the current environment state."""
        return self._state
