---
title: OptimaTrade Environment Server
emoji: 🏏
colorFrom: green
colorTo: green
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
---

# OptimaTrade: AI Trading Bot Environment

OptimaTrade (formerly AlphaEnv) is a high-performance Reinforcement Learning environment designed for training autonomous trading agents. It simulates real-time market dynamics and portfolio management, challenging AI agents to maximize net worth through strategic Buy, Sell, and Hold decisions.

## Quick Start

The simplest way to use the Price Navigator environment is through the `FirstRlDemoEnv` class:

```python
from first_rl_demo import FirstRlDemoAction, FirstRlDemoEnv, TradingActionType

with FirstRlDemoEnv(base_url="http://localhost:8000") as env:
    # Reset to start fresh
    result = env.reset()
    print(f"Start Price: ${result.observation.price}")

    # Step 1: Buy
    result = env.step(FirstRlDemoAction(action=TradingActionType.BUY))
    print(f"Bought at ${result.observation.price}")
    
    # Step 2: Hold
    result = env.step(FirstRlDemoAction(action=TradingActionType.HOLD))
    print(f"Current Net Worth: ${result.observation.net_worth}")
```

## Environment Details

### Action
**FirstRlDemoAction**: Choose one of three market actions
- `action` (str): "BUY", "SELL", or "HOLD"

### Observation
**FirstRlDemoObservation**: Real-time portfolio state
- `price` (float): Current asset price
- `balance` (float): Cash on hand
- `holdings` (int): Number of shares owned
- `net_worth` (float): Cash + (Holdings * Price)
- `step` (int): Current time step

### Reward
The reward is the **change in net worth** from the previous step.
- If the price goes up while holding, reward is positive.
- If you sell for a profit, reward tracks the realized value.

## Advanced Usage

### Connecting to an Existing Server

If you already have a First Rl Demo environment server running, you can connect directly:

```python
from first_rl_demo import FirstRlDemoAction, FirstRlDemoEnv, TradingActionType

# Connect to existing server
first_rl_demoenv = FirstRlDemoEnv(base_url="<ENV_HTTP_URL_HERE>")

# Use as normal
result = first_rl_demoenv.reset()
result = first_rl_demoenv.step(FirstRlDemoAction(action=TradingActionType.HOLD))
```

Note: When connecting to an existing server, `first_rl_demoenv.close()` will NOT stop the server.

### Using the Context Manager

The client supports context manager usage for automatic connection management:

```python
from first_rl_demo import FirstRlDemoAction, FirstRlDemoEnv, TradingActionType

# Connect with context manager (auto-connects and closes)
with FirstRlDemoEnv(base_url="http://localhost:8000") as env:
    result = env.reset()
    print(f"Start Price: ${result.observation.price}")
    # Multiple steps
    for action_type in [TradingActionType.BUY, TradingActionType.HOLD, TradingActionType.SELL]:
        result = env.step(FirstRlDemoAction(action=action_type))
        print(f"Action: {action_type}, Net Worth: ${result.observation.net_worth}")
```

The client uses WebSocket connections for:
- **Lower latency**: No HTTP connection overhead per request
- **Persistent session**: Server maintains your environment state
- **Efficient for episodes**: Better for many sequential steps

### Concurrent WebSocket Sessions

The server supports multiple concurrent WebSocket connections. To enable this,
modify `server/app.py` to use factory mode:

```python
# In server/app.py - use factory mode for concurrent sessions
app = create_app(
    FirstRlDemoEnvironment,  # Pass class, not instance
    FirstRlDemoAction,
    FirstRlDemoObservation,
    max_concurrent_envs=4,  # Allow 4 concurrent sessions
)
```

Then multiple clients can connect simultaneously:

```python
from first_rl_demo import FirstRlDemoAction, FirstRlDemoEnv
from concurrent.futures import ThreadPoolExecutor

def run_episode(client_id: int):
    with FirstRlDemoEnv(base_url="http://localhost:8000") as env:
        result = env.reset()
        for i in range(10):
            result = env.step(FirstRlDemoAction(action=TradingActionType.HOLD))
        return client_id, result.observation.net_worth

# Run 4 episodes concurrently
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(run_episode, range(4)))
```

## Development & Testing

### Direct Environment Testing

Test the environment logic directly without starting the HTTP server:

```bash
# From the server directory
python3 server/first_rl_demo_environment.py
```

This verifies that:
- Environment resets correctly
- Step executes actions properly
- State tracking works
- Rewards are calculated correctly

### Running Locally

Run the server locally for development:

```bash
uvicorn server.app:app --reload
```

## Project Structure

```
first_rl_demo/
├── .dockerignore         # Docker build exclusions
├── __init__.py            # Module exports
├── README.md              # This file
├── openenv.yaml           # OpenEnv manifest
├── pyproject.toml         # Project metadata and dependencies
├── uv.lock                # Locked dependencies (generated)
├── client.py              # FirstRlDemoEnv client
├── models.py              # Action and Observation models
└── server/
    ├── __init__.py        # Server module exports
    ├── first_rl_demo_environment.py  # Core environment logic
    ├── app.py             # FastAPI application (HTTP + WebSocket endpoints)
    └── Dockerfile         # Container image definition
```
