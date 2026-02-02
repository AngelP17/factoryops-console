# FactoryOps Console Architecture

## System Overview

```mermaid
flowchart TB
    subgraph External["External Environment"]
        SSH["SSH Session"]
        PRINTERS["Zebra Printers<br/>TCP 9100"]
        DRIVES["STAC6 Drives<br/>Modbus/Telnet"]
        SCANNERS["Barcode Scanners<br/>TCP"]
    end
    
    subgraph Console["FactoryOps Console"]
        subgraph Terminal["Terminal Management"]
            RAW["Raw Mode<br/>enable_raw_mode()"]
            ALT["Alternate Screen<br/>EnterAlternateScreen"]
            GUARD["Terminal Guard<br/>Drop trait"]
        end
        
        subgraph Async["Async Runtime (Tokio)"]
            MAIN["main()<br/>#[tokio::main]"]
            LOOP["Event Loop<br/>tokio::select!"]
        end
        
        subgraph State["Application State (app.rs)"]
            APP["App struct"]
            CPU["CPU History<br/>Vec&lt;u64&gt;"]
            MEM["Memory History<br/>Vec&lt;u64&gt;"]
            DEV["Device List<br/>Vec&lt;Device&gt;"]
            LOG["Log Buffer<br/>VecDeque&lt;String&gt;"]
        end
        
        subgraph Render["UI Layer (ui.rs)"]
            LAYOUT["Layout Builder"]
            SPARK["Sparkline Charts"]
            TABLE["Device Table"]
            LIST["Log List"]
        end
    end
    
    SSH --> Terminal
    Terminal --> Async
    Async --> State
    State --> Render
    Render --> SSH
    
    PRINTERS -.->|"TCP Check"| State
    DRIVES -.->|"TCP Check"| State
    SCANNERS -.->|"TCP Check"| State
    
    style External fill:#4a5568,stroke:#718096,color:#e2e8f0
    style Console fill:#1a202c,stroke:#2d3748,color:#e2e8f0
    style Terminal fill:#c53030,stroke:#e53e3e,color:#fff
    style Async fill:#2b6cb0,stroke:#4299e1,color:#fff
    style State fill:#38a169,stroke:#48bb78,color:#fff
    style Render fill:#805ad5,stroke:#9f7aea,color:#fff
```

## Event Flow (MVI Pattern)

```mermaid
sequenceDiagram
    participant User
    participant Terminal
    participant EventLoop
    participant App
    participant UI
    
    User->>Terminal: SSH connect
    Terminal->>Terminal: enable_raw_mode()
    Terminal->>EventLoop: Start tokio runtime
    
    loop Every 250ms (Tick)
        EventLoop->>App: Event::Tick
        App->>App: Update metrics
        App->>UI: render(frame, app)
        UI->>Terminal: Draw widgets
    end
    
    loop Every 3s (Device Check)
        EventLoop->>App: simulate_device_checks()
        App->>App: Update device status
        App->>App: Log status changes
    end
    
    User->>Terminal: Key press
    Terminal->>EventLoop: Event::Input
    EventLoop->>App: on_key(keycode)
    
    alt Key == 'q' or Esc
        App->>App: should_quit = true
        App->>Terminal: restore_terminal()
        Terminal->>User: Clean exit
    else Key == Arrow
        App->>App: Scroll logs
    end
```

## Data Flow

```mermaid
flowchart LR
    subgraph Inputs
        KEY["Keyboard<br/>crossterm"]
        TICK["Tick Timer<br/>250ms"]
        DEV["Device Timer<br/>3s"]
    end
    
    subgraph Processing
        SELECT["tokio::select!<br/>biased"]
        HANDLER["Event Handler"]
    end
    
    subgraph State
        direction TB
        APP["App State"]
        APP --> CPU["CPU Vec"]
        APP --> MEM["Memory Vec"]
        APP --> DEVS["Devices Vec"]
        APP --> LOGS["Logs VecDeque"]
    end
    
    subgraph Output
        FRAME["Frame Buffer"]
        TTY["Terminal"]
    end
    
    KEY --> SELECT
    TICK --> SELECT
    DEV --> SELECT
    SELECT --> HANDLER
    HANDLER --> State
    State --> FRAME
    FRAME --> TTY
    
    style Inputs fill:#ecc94b,stroke:#d69e2e,color:#1a202c
    style Processing fill:#4299e1,stroke:#2b6cb0,color:#fff
    style State fill:#48bb78,stroke:#38a169,color:#fff
    style Output fill:#9f7aea,stroke:#805ad5,color:#fff
```

## Memory Management

```mermaid
graph TD
    subgraph Bounded["Bounded Data Structures"]
        CPU["cpu_history<br/>Max: 200 points<br/>~1.6KB"]
        MEM["memory_history<br/>Max: 200 points<br/>~1.6KB"]
        LOGS["logs<br/>Max: 1000 entries<br/>~100KB avg"]
        DEVS["devices<br/>Fixed: 5 items<br/>~1KB"]
    end
    
    subgraph Lifecycle["Memory Lifecycle"]
        PUSH["New data pushed"]
        CHECK["Check bounds"]
        PRUNE["Prune oldest"]
    end
    
    PUSH --> CHECK
    CHECK -->|"len > max"| PRUNE
    CHECK -->|"len <= max"| PUSH
    
    CPU --> Lifecycle
    MEM --> Lifecycle
    LOGS --> Lifecycle
    
    style Bounded fill:#38a169,stroke:#48bb78,color:#fff
    style Lifecycle fill:#4299e1,stroke:#2b6cb0,color:#fff
```

## Terminal State Safety

```mermaid
stateDiagram-v2
    [*] --> Normal: Program Start
    Normal --> RawMode: enable_raw_mode()
    RawMode --> AltScreen: EnterAlternateScreen
    AltScreen --> Running: Event Loop
    
    Running --> Restored: User Quit (q/Esc)
    Running --> Restored: Panic (TerminalGuard Drop)
    Running --> Restored: Error (restore_terminal)
    
    Restored --> Normal: disable_raw_mode()
    Normal --> [*]: Program Exit
    
    note right of RawMode
        No echo
        No line buffering
        Ctrl+C disabled
    end note
    
    note right of Restored
        Always executes
        Even on panic
        Cursor restored
    end note
```

## Module Dependency Graph

```mermaid
graph TB
    MAIN["main.rs"]
    APP["app.rs"]
    UI["ui.rs"]
    
    subgraph External["External Crates"]
        TOKIO["tokio"]
        RATATUI["ratatui"]
        CROSSTERM["crossterm"]
        ANYHOW["anyhow"]
        REGEX["regex"]
        CHRONO["chrono"]
        RAND["rand"]
        FUTURES["futures"]
    end
    
    MAIN --> APP
    MAIN --> UI
    APP --> UI
    
    MAIN --> TOKIO
    MAIN --> CROSSTERM
    MAIN --> RATATUI
    MAIN --> ANYHOW
    
    APP --> TOKIO
    APP --> CROSSTERM
    APP --> RATATUI
    APP --> FUTURES
    APP --> RAND
    APP --> CHRONO
    APP --> ANYHOW
    
    UI --> RATATUI
    UI --> REGEX
    
    style MAIN fill:#c53030,stroke:#e53e3e,color:#fff
    style APP fill:#d69e2e,stroke:#ecc94b,color:#1a202c
    style UI fill:#2b6cb0,stroke:#4299e1,color:#fff
    style External fill:#4a5568,stroke:#718096,color:#e2e8f0
```

## Device Status State Machine

```mermaid
stateDiagram-v2
    [*] --> Offline: Initial State
    
    Offline --> Online: TCP Connect < 100ms
    Offline --> HighLatency: TCP Connect 100-2000ms
    
    Online --> HighLatency: Latency > 100ms
    Online --> Offline: Connection Timeout
    
    HighLatency --> Online: Latency < 100ms
    HighLatency --> Offline: Connection Timeout
    
    note right of Online
        🟢 Green indicator
        Device responsive
    end note
    
    note right of HighLatency
        🟡 Yellow indicator
        Shows latency (ms)
    end note
    
    note right of Offline
        🔴 Red indicator
        Connection failed
    end note
```
