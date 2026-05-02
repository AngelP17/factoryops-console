[README.md](https://github.com/user-attachments/files/27305055/README.md)
# FactoryOps Console

[![Rust](https://img.shields.io/badge/Rust-2021-orange)](https://www.rust-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A high-performance, asynchronous Terminal User Interface (TUI) for monitoring manufacturing infrastructure in headless, bandwidth-constrained environments.

## 🏭 Overview

Zero-dependency static binary (~3MB) that deploys via `scp` and runs directly in SSH sessions. Built with Rust and Tokio for real-time infrastructure diagnostics.

## 📸 Screenshots

### Main Dashboard

Real-time infrastructure monitoring with CPU/Memory sparklines, factory floor device grid, and system logs.

![FactoryOps Console - Main Dashboard](docs/screenshots/factoryops-main.png)

### Device Detail View

Per-device diagnostics showing network I/O, latency percentiles, packet loss, and thermal data.

![FactoryOps Console - Device Detail](docs/screenshots/factoryops-device-detail.png)

## 🚀 Quick Start

```bash
# Run in simulation mode
cargo run

# Build release binary (~3MB)
cargo build --release

# Deploy to production
scp target/release/factoryops-console user@factory-server:/usr/local/bin/
```

## ⌨️ Controls

| Key | Function |
|-----|----------|
| `q` / `Esc` | Quit |
| `↑` / `↓` | Scroll logs |
| `a` | Toggle auto-scroll |
| `r` | Force device refresh |

## 🏗️ Architecture

```mermaid
graph TB
    subgraph Terminal["Terminal Layer"]
        STDIN[("stdin")]
        STDOUT[("stdout")]
        RAW["Raw Mode"]
    end
    
    subgraph EventLoop["Async Event Loop"]
        SELECT["tokio::select!"]
        INPUT["Input Events"]
        TICK["Tick Timer (250ms)"]
        DEVICE["Device Timer (3s)"]
    end
    
    subgraph Model["App State"]
        CPU["cpu_history<br/>Vec&lt;u64&gt; (200)"]
        MEM["memory_history<br/>Vec&lt;u64&gt; (200)"]
        DEVICES["devices<br/>Vec&lt;Device&gt;"]
        LOGS["logs<br/>VecDeque (1000)"]
    end
    
    subgraph View["UI Rendering"]
        INFRA["Infrastructure Panel<br/>Sparklines"]
        GRID["Device Grid<br/>Table"]
        LOGP["Log Panel<br/>List + Regex"]
    end
    
    STDIN --> SELECT
    SELECT --> INPUT
    SELECT --> TICK
    SELECT --> DEVICE
    INPUT --> Model
    TICK --> Model
    DEVICE --> Model
    Model --> View
    View --> STDOUT
    
    style Terminal fill:#2d3748,stroke:#4a5568,color:#e2e8f0
    style EventLoop fill:#1a365d,stroke:#2b6cb0,color:#bee3f8
    style Model fill:#22543d,stroke:#38a169,color:#c6f6d5
    style View fill:#553c9a,stroke:#805ad5,color:#d6bcfa
```

## 📦 Module Structure

```mermaid
graph LR
    subgraph src["src/"]
        MAIN["main.rs<br/>Entry + Terminal"]
        APP["app.rs<br/>State + Events"]
        UI["ui.rs<br/>Rendering"]
    end
    
    MAIN --> APP
    MAIN --> UI
    APP --> UI
    
    style MAIN fill:#c53030,stroke:#e53e3e,color:#fff
    style APP fill:#d69e2e,stroke:#ecc94b,color:#1a202c
    style UI fill:#2b6cb0,stroke:#4299e1,color:#fff
```

## 🔩 Device Monitoring

Pre-configured manufacturing equipment:

| Device | IP | Protocol |
|--------|-----|----------|
| Line-1-Printer | 192.168.10.15 | TCP 9100 |
| Pack-Station-A | 192.168.10.22 | TCP |
| STAC6-Drive-01 | 192.168.10.30 | Modbus |
| Line-2-Printer | 192.168.10.16 | TCP 9100 |
| Quality-Scanner | 192.168.10.45 | TCP |

## 🛠️ Tech Stack

- **Rust** 2021 Edition
- **ratatui** – Terminal UI
- **crossterm** – Cross-platform terminal control
- **tokio** – Async runtime

## 📚 Documentation

See [docs/documentation.md](docs/documentation.md) for full technical details.

## 📜 License

MIT – Open source for manufacturing engineering community

---

**Author**: Angel Pinzon | [apinzon.dev](https://apinzon.dev)
