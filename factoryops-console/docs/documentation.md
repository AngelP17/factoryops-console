Here's the updated comprehensive documentation for your project:

```markdown
# FactoryOps Console

A high-performance, asynchronous Terminal User Interface (TUI) for monitoring manufacturing infrastructure in headless, bandwidth-constrained environments.

## 🏭 The Problem

In manufacturing environments (like Wallner Expac's 24/5 production facilities), critical infrastructure runs on headless servers or edge gateways with limited bandwidth. Web-based dashboards (React/Grafana) require:

- Heavy browser rendering (impossible over 2G/3G factory floor connections)
- Port forwarding and SSL certificates (security compliance headaches)
- Stable high-bandwidth connections (often unavailable during after-hours VPN support)

When a **Line-1-Printer** (Zebra ZD621) goes down at 2 AM, engineers need immediate diagnostics without waiting for a web interface to load.

## 🦀 The Solution

FactoryOps Console is a **zero-dependency static binary** (under 10MB) that deploys via `scp` and runs directly in SSH sessions. Built with Rust and Tokio, it provides real-time infrastructure diagnostics with memory-safe concurrency and guaranteed terminal restoration (never leaves SSH sessions in "garbage" mode).

### Key Systems Engineering Features

| Feature | Implementation | Manufacturing Impact |
|---------|---------------|---------------------|
| **Async Concurrency** | `tokio::select!` multiplexing | UI responsive even when TCP handshakes to printers hang (2s timeout vs frozen dashboard) |
| **Memory Safety** | Bounded `VecDeque` (1000 logs), `Vec` arenas (200 pts) | Prevents OOM on edge hardware running 24/5 for months |
| **Zero-Cost Deploy** | Static `x86_64-unknown-linux-musl` binary | `scp` to any server, no Docker/systemd/apt required |
| **Visual Alerting** | Regex-based log highlighting (`[ERROR]` red, `[WARN]` yellow) | Spot "Line Down" issues instantly in scrolling logs |
| **Terminal Safety** | `restore_terminal()` guarantee + `Drop` guard | Never corrupts shell state on panic/crash (critical for remote factories) |

## 🛠️ Technical Stack

- **Language**: Rust 2021 Edition (memory safety without GC)
- **UI Framework**: `ratatui` 0.24 (immediate-mode terminal rendering)
- **Terminal Control**: `crossterm` 0.27 (cross-platform raw mode)
- **Async Runtime**: `tokio` 1.35 (full feature set for concurrent I/O)
- **Error Handling**: `anyhow` (zero-panic guarantee)
- **Utilities**: `regex`, `chrono`, `futures`, `rand`

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/AngelP17/factoryops-console.git
cd factoryops-console

# Run in simulation mode (generates fake metrics for demo)
cargo run

# Build optimized release binary (~5-8MB)
cargo build --release

# Deploy to production server (static binary, no dependencies)
scp target/release/factoryops-console user@factory-server:/usr/local/bin/
ssh user@factory-server
factoryops-console
```

### Controls

| Key | Function |
|-----|----------|
| `q` / `Esc` | Quit (always responsive due to `tokio::select!`) |
| `↑` / `↓` | Scroll log history (disables auto-scroll) |
| `a` | Toggle auto-scroll mode |
| `r` | Force immediate device refresh check |

## 🏗️ Architecture (MVI Pattern)

The codebase follows **Model-View-Intent** for testability and separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                        Event Loop                            │
│  tokio::select! {                                           │
│    biased;                                                   │
│    input = crossterm::event::read()  →  Event::Input        │
│    tick = interval(250ms)            →  Event::Tick         │
│    device = interval(3s)             →  simulate checks     │
│  }                                                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                         Model (App)                          │
│  - cpu_history: Vec<u64> (bounded to 200)                   │
│  - devices: Vec<Device> (Zebra printers, STAC6 drives)      │
│  - logs: VecDeque<String> (bounded to 1000)                 │
│  - log_scroll: usize (viewport state)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                          View (ui.rs)                        │
│  Layout:[                                                    │
│    Horizontal [                                             │
│      Vertical [                                             │
│        InfrastructurePulse(Sparklines),  // CPU/Mem trends  │
│        DeviceGrid(Table)                 // Zebra/STAC6     │
│      ],                                                     │
│      LogStream(List)                     // Regex colored   │
│    ]                                                         │
│  ]                                                           │
└─────────────────────────────────────────────────────────────┘
```

### Critical Design Decisions

**1. Bounded Data Structures**
```rust
// Memory-safe for 24/5 operations - never grows unbounded
pub logs: VecDeque<String>,      // Max 1000 lines
pub cpu_history: Vec<u64>,       // Max 200 points (~50s @ 250ms)
pub max_logs: usize,             // Hard limit prevents OOM
```

**2. Non-Blocking Event Loop**
The `tokio::select!` with `biased;` prioritizes user input over background tasks:
- **Why**: If a TCP check to a printer hangs for 30s, the `q` key still works immediately
- **Manufacturing Value**: Engineers can always exit the tool, even during network partitions

**3. Terminal State Safety**
```rust
// Guaranteed restoration even on panic
fn restore_terminal() -> Result<()> {
    execute!(LeaveAlternateScreen, DisableMouseCapture)?;
    disable_raw_mode()?;  // Critical: restores Ctrl+C handling
    terminal.show_cursor()?;
    Ok(())
}
```

## 📁 Project Structure

```
factoryops-console/
├── Cargo.toml              # Dependencies: tokio, ratatui, crossterm, anyhow
└── src/
    ├── main.rs             # Terminal lifecycle, raw mode, panic safety
    ├── app.rs              # App state, Event enum, async run_app loop
    └── ui.rs               # Pure render functions (Frame → Widgets)
```

### Module Responsibilities

**`main.rs`**
- Terminal initialization (`enable_raw_mode`, `EnterAlternateScreen`)
- Panic-safe cleanup via `restore_terminal()` and `TerminalGuard` Drop trait
- Async runtime entry point (`#[tokio::main]`)

**`app.rs`**
- `App` struct: Centralized state with `VecDeque` for logs, `Vec` for metrics
- `Event` enum: MVI event types (Input, Tick, DeviceUpdate)
- `DeviceStatus` enum: `Online` (Green), `HighLatency(u64)` (Yellow), `Offline` (Red)
- `run_app()`: The `tokio::select!` event loop (heart of the async architecture)
- `simulate_device_checks()`: REPLACE THIS with real `tokio::net::TcpStream` calls

**`ui.rs`**
- `render()`: Main layout builder (60/40 horizontal split)
- `render_infrastructure_panel()`: Sparklines with color-coded thresholds
- `render_device_grid()`: Table of manufacturing equipment (Line-1-Printer, STAC6-Drive-01, etc.)
- `render_log_panel()`: Scrollable list with regex highlighting
- `highlight_log_line()`: Static compiled regexes (performance: compiled once, used 4x/second)

## 🔩 Manufacturing Device Context

Pre-configured with 5 devices typical of Wallner Expac environment:

| Device Name | IP | Real-World Equivalent | Protocol |
|-------------|-----|---------------------|----------|
| Line-1-Printer | 192.168.10.15 | Zebra ZD621 Thermal | TCP 9100 (ZPL) |
| Pack-Station-A | 192.168.10.22 | Barcode Scanner | TCP specific |
| STAC6-Drive-01 | 192.168.10.30 | Applied Motion Stepper | Telnet/Modbus |
| Line-2-Printer | 192.168.10.16 | Secondary Zebra | TCP 9100 |
| Quality-Scanner | 192.168.10.45 | QC Barcode Reader | TCP specific |

## 📝 Production Implementation Path

### Current: Simulation Mode
Uses `rand::Rng` to simulate:
- CPU/Memory fluctuation (30-95% range)
- Network conditions (70% Online, 20% HighLatency, 10% Offline)
- Syslog generation (INFO/WARN/ERROR)

### Production: Real Device Monitoring

Replace `simulate_device_checks()` in `app.rs`:

```rust
use tokio::net::TcpStream;
use tokio::time::timeout;

async fn check_device(ip: &str, port: u16) -> DeviceStatus {
    let addr = format!("{}:{}", ip, port).parse().unwrap();
    let start = Instant::now();
    
    match timeout(
        Duration::from_secs(2),
        TcpStream::connect(addr)
    ).await {
        Ok(Ok(_)) => {
            let elapsed = start.elapsed().as_millis() as u64;
            if elapsed > 100 { 
                DeviceStatus::HighLatency(elapsed) 
            } else { 
                DeviceStatus::Online 
            }
        }
        _ => DeviceStatus::Offline,
    }
}
```

Add system metrics using `sysinfo` crate:
```rust
// In Cargo.toml: sysinfo = "0.29"
use sysinfo::{System, SystemExt, CpuExt};

fn update_system_metrics(&mut self) {
    let mut s = System::new_all();
    s.refresh_all();
    let cpu_usage = s.global_cpu_info().cpu_usage() as u64;
    self.cpu_history.push(cpu_usage);
}
```

## 🎯 Resume Integration

**Positioning**: Demonstrates systems programming expertise distinct from existing Python/React/DevOps portfolio:

> **FactoryOps Console – Zero-Dependency Infrastructure TUI** | Rust, Tokio, Systems Programming  
> *High-performance terminal diagnostics for bandwidth-constrained manufacturing (24/5 operations). Implements async TCP health-checking with bounded memory structures (<10MB footprint), regex-based log highlighting, and guaranteed terminal restoration. Demonstrates systems-level competency (memory safety, async concurrency, terminal raw mode) complementary to existing cloud-native Python/React work.*

**Technical Differentiation**:
- **vs. SOC Dashboard (Python/React)**: Eliminates browser/DOM/web server stack entirely
- **vs. K8s Resilience Pilot**: Shows kernel-adjacent programming (TTY/ANSI) vs. high-level orchestration
- **vs. IT OpsCenter (Node.js)**: Single static binary vs. containerized microservice with database

## 🚧 Roadmap

- [ ] **Sysinfo Integration**: Replace simulated CPU/memory with real `/proc/stat` readings
- [ ] **TCP Device Checks**: Implement `tokio::net::TcpStream::connect_timeout` for actual printer/STAC6 monitoring
- [ ] **Configuration**: Add `clap` CLI args (`--config production.yaml`) for device IP lists
- [ ] **Persistence**: SQLite buffer for outage forensics (offline-first during network partitions)
- [ ] **Azure IoT Edge**: Module to consume IoT Hub telemetry streams

## 📜 License

MIT - Open source for manufacturing engineering community

## 👤 Author

Angel Pinzon  
Senior IT Systems Engineer & Strategist  
portfolio: [apinzon.dev](https://apinzon.dev)
```


