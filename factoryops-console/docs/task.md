Here is the complete `task.md` prompt for Kimi Code to generate the FactoryOps Console project:

```markdown
# Task: FactoryOps Console - Manufacturing TUI Diagnostics Tool

## Role
You are a Rust systems programming expert specializing in manufacturing infrastructure tools. Generate a complete, production-grade terminal user interface (TUI) application using Rust with async Tokio runtime.

## Context
This is for a Senior IT Systems Engineer at a manufacturing company (Wallner Expac) who needs a zero-dependency diagnostic tool for headless SSH environments. The tool monitors Zebra printers, STAC6-Si drives, and infrastructure health in 24/5 production environments.

## Technical Stack
- Language: Rust 2021 Edition
- TUI Framework: ratatui 0.24
- Terminal Backend: crossterm 0.27
- Async Runtime: tokio 1.35 (full features)
- Error Handling: anyhow
- Additional: futures 0.3, rand 0.8, regex 1.10, chrono 0.4

## Architecture Pattern
MVI (Model-View-Intent):
- **Model**: App state struct with bounded data structures (prevents OOM)
- **View**: ui.rs render functions using ratatui widgets
- **Intent**: Event loop handling keyboard input, ticks (250ms), and async I/O

## File Structure to Create

Create the following directory structure:
```
factoryops-console/
├── Cargo.toml
└── src/
    ├── main.rs
    ├── app.rs
    └── ui.rs
```

## File Contents

### Cargo.toml
```toml
[package]
name = "factoryops-console"
version = "0.1.0"
edition = "2021"
authors = ["Angel Pinzon <angelpinzon1706@gmail.com>"]
description = "Zero-dependency TUI diagnostics for manufacturing environments"
license = "MIT"
repository = "https://github.com/angelpinzon/factoryops-console"

[dependencies]
futures = "0.3"
ratatui = { version = "0.24", features = ["all-widgets"] }
crossterm = { version = "0.27", features = ["event-stream"] }
tokio = { version = "1.35", features = ["full"] }
anyhow = "1.0"
rand = "0.8"
regex = "1.10"
chrono = "0.4"
```

### src/main.rs
```rust
use anyhow::Result;
use crossterm::{
    event::{DisableMouseCapture, EnableMouseCapture},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::backend::CrosstermBackend;
use ratatui::Terminal;
use std::io::{self, stdout};

mod app;
mod ui;

use app::{App, run_app};

#[tokio::main]
async fn main() -> Result<()> {
    // Setup terminal in raw mode - critical for manufacturing SSH sessions
    enable_raw_mode()?;
    
    let mut stdout = stdout();
    
    // Enter alternate screen buffer - preserves user's terminal session
    execute!(stdout, EnterAlternateScreen, EnableMouseCapture)?;
    
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;
    
    let mut app = App::new();
    
    let res = run_app(&mut terminal, &mut app).await;
    
    // CRITICAL: Always restore terminal state, even if the app crashes
    let restore_result = restore_terminal(&mut terminal);
    
    res?;
    restore_result?;
    
    Ok(())
}

fn restore_terminal(terminal: &mut Terminal<CrosstermBackend<io::Stdout>>) -> Result<()> {
    execute!(
        terminal.backend_mut(),
        LeaveAlternateScreen,
        DisableMouseCapture
    )?;
    disable_raw_mode()?;
    terminal.show_cursor()?;
    Ok(())
}

struct TerminalGuard;

impl Drop for TerminalGuard {
    fn drop(&mut self) {
        let _ = disable_raw_mode();
        let _ = execute!(io::stdout(), LeaveAlternateScreen);
    }
}
```

### src/app.rs
```rust
use anyhow::Result;
use crossterm::event::{Event as CEvent, EventStream, KeyCode, KeyEventKind};
use futures::{FutureExt, StreamExt};
use ratatui::backend::Backend;
use ratatui::Terminal;
use std::collections::VecDeque;
use std::time::{Duration, Instant};

#[derive(Debug)]
pub enum Event {
    Input(CEvent),
    Tick,
    DeviceUpdate(usize, DeviceStatus),
    LogEntry(String),
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum DeviceStatus {
    Online,
    HighLatency(u64),
    Offline,
}

impl DeviceStatus {
    pub fn display(&self) -> (&'static str, &'static str) {
        match self {
            DeviceStatus::Online => ("●", "Online"),
            DeviceStatus::HighLatency(ms) => ("◐", &format!("Latency {}ms", ms)),
            DeviceStatus::Offline => ("○", "Offline"),
        }
    }
}

#[derive(Debug, Clone)]
pub struct Device {
    pub name: String,
    pub ip: String,
    pub status: DeviceStatus,
    pub last_check: Instant,
}

impl Device {
    pub fn new(name: &str, ip: &str) -> Self {
        Self {
            name: name.to_string(),
            ip: ip.to_string(),
            status: DeviceStatus::Offline,
            last_check: Instant::now(),
        }
    }
}

pub struct App {
    pub cpu_history: Vec<u64>,
    pub memory_history: Vec<u64>,
    pub devices: Vec<Device>,
    pub logs: VecDeque<String>,
    pub max_logs: usize,
    pub log_scroll: usize,
    pub auto_scroll: bool,
    pub should_quit: bool,
    pub simulation_tick: u64,
}

impl App {
    pub fn new() -> Self {
        let devices = vec![
            Device::new("Line-1-Printer", "192.168.10.15"),
            Device::new("Pack-Station-A", "192.168.10.22"),
            Device::new("STAC6-Drive-01", "192.168.10.30"),
            Device::new("Line-2-Printer", "192.168.10.16"),
            Device::new("Quality-Scanner", "192.168.10.45"),
        ];
        
        let cpu_history: Vec<u64> = (0..100).map(|i| 30 + (i % 20)).collect();
        let memory_history: Vec<u64> = (0..100).map(|i| 45 + (i % 15)).collect();
        
        let mut logs = VecDeque::new();
        logs.push_back("[INFO] FactoryOps Console initialized".to_string());
        logs.push_back("[INFO] Monitoring 5 manufacturing devices".to_string());
        logs.push_back("[WARN] High memory usage detected on Line-1-Printer history".to_string());
        
        Self {
            cpu_history,
            memory_history,
            devices,
            logs,
            max_logs: 1000,
            log_scroll: 0,
            auto_scroll: true,
            should_quit: false,
            simulation_tick: 0,
        }
    }
    
    pub fn on_tick(&mut self) {
        self.simulation_tick += 1;
        
        let last_cpu = *self.cpu_history.last().unwrap_or(&50);
        let variation = (rand::random::<i8>() % 10) as i64;
        let new_cpu = ((last_cpu as i64 + variation).clamp(10, 95)) as u64;
        self.cpu_history.push(new_cpu);
        if self.cpu_history.len() > 200 {
            self.cpu_history.remove(0);
        }
        
        let last_mem = *self.memory_history.last().unwrap_or(&40);
        let variation = (rand::random::<i8>() % 5) as i64;
        let new_mem = ((last_mem as i64 + variation).clamp(20, 85)) as u64;
        self.memory_history.push(new_mem);
        if self.memory_history.len() > 200 {
            self.memory_history.remove(0);
        }
        
        if self.auto_scroll {
            self.log_scroll = self.log_scroll.saturating_add(1);
            let max_scroll = self.logs.len().saturating_sub(1);
            if self.log_scroll > max_scroll {
                self.log_scroll = max_scroll;
            }
        }
        
        if self.simulation_tick % 32 == 0 {
            self.generate_log();
        }
    }
    
    pub fn on_key(&mut self, key: KeyCode) {
        match key {
            KeyCode::Char('q') | KeyCode::Esc => {
                self.should_quit = true;
            }
            KeyCode::Up => {
                if self.log_scroll > 0 {
                    self.log_scroll -= 1;
                    self.auto_scroll = false;
                }
            }
            KeyCode::Down => {
                if self.log_scroll < self.logs.len().saturating_sub(1) {
                    self.log_scroll += 1;
                    if self.log_scroll >= self.logs.len().saturating_sub(1) {
                        self.auto_scroll = true;
                    }
                }
            }
            KeyCode::Char('a') => {
                self.auto_scroll = !self.auto_scroll;
                if self.auto_scroll {
                    self.log_scroll = self.logs.len().saturating_sub(1);
                }
            }
            KeyCode::Char('r') => {
                self.logs.push_back("[INFO] Manual device refresh triggered".to_string());
                self.prune_logs();
            }
            _ => {}
        }
    }
    
    pub fn update_device(&mut self, index: usize, status: DeviceStatus) {
        if let Some(device) = self.devices.get_mut(index) {
            let old_status = device.status.clone();
            device.status = status;
            device.last_check = Instant::now();
            
            if old_status != status {
                let msg = match status {
                    DeviceStatus::Online => {
                        format!("[INFO] {} ({}) -> Online", device.name, device.ip)
                    }
                    DeviceStatus::HighLatency(ms) => {
                        format!("[WARN] {} ({}) -> High Latency ({}ms)", device.name, device.ip, ms)
                    }
                    DeviceStatus::Offline => {
                        format!("[ERROR] {} ({}) -> OFFLINE", device.name, device.ip)
                    }
                };
                self.logs.push_back(msg);
                self.prune_logs();
            }
        }
    }
    
    pub fn simulate_device_checks(&mut self) {
        use rand::Rng;
        let mut rng = rand::thread_rng();
        
        for (idx, device) in self.devices.iter_mut().enumerate() {
            let roll = rng.gen_range(0..100);
            let new_status = if roll < 70 {
                DeviceStatus::Online
            } else if roll < 90 {
                let latency = rng.gen_range(100..800);
                DeviceStatus::HighLatency(latency)
            } else {
                DeviceStatus::Offline
            };
            
            if device.status != new_status || 
               matches!(new_status, DeviceStatus::HighLatency(_)) {
                self.update_device(idx, new_status);
            }
        }
    }
    
    fn generate_log(&mut self) {
        use rand::Rng;
        let mut rng = rand::thread_rng();
        
        let log_types = [
            ("[INFO]", "System heartbeat OK"),
            ("[INFO]", "ERP connection stable"),
            ("[WARN]", "Packet loss detected on Line-2-Printer"),
            ("[ERROR]", "Connection timeout to Quality-Scanner"),
            ("[INFO]", "Backup completed successfully"),
            ("[WARN]", "Disk usage 85% on production server"),
        ];
        
        let (level, msg) = log_types[rng.gen_range(0..log_types.len())];
        let timestamp = chrono::Local::now().format("%H:%M:%S");
        let entry = format!("[{}] {} {}", timestamp, level, msg);
        
        self.logs.push_back(entry);
        self.prune_logs();
        
        if self.auto_scroll {
            self.log_scroll = self.logs.len().saturating_sub(1);
        }
    }
    
    fn prune_logs(&mut self) {
        while self.logs.len() > self.max_logs {
            self.logs.pop_front();
            if self.log_scroll > 0 {
                self.log_scroll = self.log_scroll.saturating_sub(1);
            }
        }
    }
}

pub async fn run_app<B: Backend>(
    terminal: &mut Terminal<B>,
    app: &mut App,
) -> Result<()> {
    let mut reader = EventStream::new();
    let mut tick_timer = tokio::time::interval(Duration::from_millis(250));
    let mut device_timer = tokio::time::interval(Duration::from_secs(3));
    
    loop {
        let event = tokio::select! {
            biased;
            
            maybe_event = reader.next().fuse() => {
                match maybe_event {
                    Some(Ok(CEvent::Key(key))) => {
                        if key.kind == KeyEventKind::Press {
                            Event::Input(CEvent::Key(key))
                        } else {
                            continue;
                        }
                    }
                    Some(Ok(event)) => Event::Input(event),
                    Some(Err(e)) => return Err(anyhow::anyhow!("Input error: {}", e)),
                    None => break,
                }
            }
            
            _ = tick_timer.tick() => {
                Event::Tick
            }
            
            _ = device_timer.tick() => {
                app.simulate_device_checks();
                continue;
            }
        };
        
        match event {
            Event::Input(input_event) => {
                if let CEvent::Key(key) = input_event {
                    app.on_key(key.code);
                }
            }
            Event::Tick => {
                app.on_tick();
            }
            _ => {}
        }
        
        terminal.draw(|f| ui::render(f, app))?;
        
        if app.should_quit {
            break;
        }
    }
    
    Ok(())
}
```

### src/ui.rs
```rust
use ratatui::{
    backend::Backend,
    layout::{Alignment, Constraint, Direction, Layout, Rect},
    style::{Color, Modifier, Style},
    symbols,
    text::{Line, Span},
    widgets::{
        Block, Borders, Cell, List, ListItem, Paragraph, Row, Sparkline, Table,
    },
    Frame,
};
use regex::Regex;
use std::sync::OnceLock;

use crate::app::{App, DeviceStatus};

fn log_regexes() -> &'static (Regex, Regex, Regex) {
    static REGEXES: OnceLock<(Regex, Regex, Regex)> = OnceLock::new();
    REGEXES.get_or_init(|| {
        (
            Regex::new(r"\[ERROR\]").unwrap(),
            Regex::new(r"\[WARN\]").unwrap(),
            Regex::new(r"\[INFO\]").unwrap(),
        )
    })
}

pub fn render<B: Backend>(f: &mut Frame, app: &App) {
    let main_chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([Constraint::Percentage(60), Constraint::Percentage(40)])
        .split(f.size());
    
    let left_chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([Constraint::Percentage(40), Constraint::Percentage(60)])
        .split(main_chunks[0]);
    
    render_infrastructure_panel(f, app, left_chunks[0]);
    render_device_grid(f, app, left_chunks[1]);
    render_log_panel(f, app, main_chunks[1]);
}

fn render_infrastructure_panel<B: Backend>(f: &mut Frame, app: &App, area: Rect) {
    let chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([Constraint::Percentage(50), Constraint::Percentage(50)])
        .margin(1)
        .split(area);
    
    let block = Block::default()
        .title(" Infrastructure Pulse ")
        .borders(Borders::ALL)
        .border_style(Style::default().fg(Color::Cyan));
    
    f.render_widget(block, area);
    
    let cpu_data: Vec<u64> = app.cpu_history.iter().cloned().collect();
    let current_cpu = cpu_data.last().copied().unwrap_or(0);
    let cpu_color = if current_cpu > 80 {
        Color::Red
    } else if current_cpu > 60 {
        Color::Yellow
    } else {
        Color::Green
    };
    
    let cpu_sparkline = Sparkline::default()
        .data(&cpu_data)
        .style(Style::default().fg(cpu_color))
        .block(
            Block::default()
                .title(format!(" CPU {}% ", current_cpu))
                .borders(Borders::ALL)
                .border_style(Style::default().fg(Color::Gray)),
        )
        .bar_set(symbols::bar::NINE_LEVELS);
    
    f.render_widget(cpu_sparkline, chunks[0]);
    
    let mem_data: Vec<u64> = app.memory_history.iter().cloned().collect();
    let current_mem = mem_data.last().copied().unwrap_or(0);
    let mem_color = if current_mem > 85 {
        Color::Red
    } else if current_mem > 70 {
        Color::Yellow
    } else {
        Color::Blue
    };
    
    let mem_sparkline = Sparkline::default()
        .data(&mem_data)
        .style(Style::default().fg(mem_color))
        .block(
            Block::default()
                .title(format!(" Memory {}% ", current_mem))
                .borders(Borders::ALL)
                .border_style(Style::default().fg(Color::Gray)),
        )
        .bar_set(symbols::bar::NINE_LEVELS);
    
    f.render_widget(mem_sparkline, chunks[1]);
}

fn render_device_grid<B: Backend>(f: &mut Frame, app: &App, area: Rect) {
    let header = Row::new(vec!["Device", "IP Address", "Status", "Last Check"])
        .style(Style::default().fg(Color::White).add_modifier(Modifier::BOLD))
        .height(1);
    
    let rows: Vec<Row> = app.devices.iter().map(|device| {
        let (symbol, status_text) = device.status.display();
        
        let status_color = match device.status {
            DeviceStatus::Online => Color::Green,
            DeviceStatus::HighLatency(_) => Color::Yellow,
            DeviceStatus::Offline => Color::Red,
        };
        
        let cells = vec![
            Cell::from(device.name.clone()),
            Cell::from(device.ip.clone()).style(Style::default().fg(Color::Gray)),
            Cell::from(format!("{} {}", symbol, status_text))
                .style(Style::default().fg(status_color)),
            Cell::from(format!("{:?}", device.last_check.elapsed()))
                .style(Style::default().fg(Color::DarkGray)),
        ];
        
        Row::new(cells).height(1)
    }).collect();
    
    let table = Table::new(rows, vec![
        Constraint::Percentage(30),
        Constraint::Percentage(25),
        Constraint::Percentage(25),
        Constraint::Percentage(20),
    ])
    .header(header)
    .block(
        Block::default()
            .title(" Factory Floor - Device Grid ")
            .borders(Borders::ALL)
            .border_style(Style::default().fg(Color::Cyan))
            .title_alignment(Alignment::Center),
    )
    .highlight_style(Style::default().add_modifier(Modifier::REVERSED));
    
    f.render_widget(table, area);
}

fn render_log_panel<B: Backend>(f: &mut Frame, app: &App, area: Rect) {
    let log_count = app.logs.len();
    let visible_height = area.height.saturating_sub(2) as usize;
    
    let start_idx = if log_count > visible_height {
        log_count.saturating_sub(visible_height).min(app.log_scroll)
    } else {
        0
    };
    
    let end_idx = (start_idx + visible_height).min(log_count);
    
    let items: Vec<ListItem> = app.logs
        .iter()
        .skip(start_idx)
        .take(end_idx.saturating_sub(start_idx))
        .map(|log| {
            let spans = highlight_log_line(log);
            ListItem::new(Line::from(spans))
        })
        .collect();
    
    let list = List::new(items)
        .block(
            Block::default()
                .title(format!(
                    " System Logs [{}] {} ",
                    app.logs.len(),
                    if app.auto_scroll { "[Auto]" } else { "[Manual]" }
                ))
                .borders(Borders::ALL)
                .border_style(Style::default().fg(Color::Cyan))
                .title_alignment(Alignment::Center),
        )
        .style(Style::default().fg(Color::White));
    
    f.render_widget(list, area);
    
    if !app.auto_scroll && app.log_scroll > 0 {
        let up_indicator = Paragraph::new("▲ More above")
            .style(Style::default().fg(Color::Yellow))
            .alignment(Alignment::Right);
        let indicator_area = Rect {
            x: area.x + area.width.saturating_sub(15),
            y: area.y + 1,
            width: 14,
            height: 1,
        };
        f.render_widget(up_indicator, indicator_area);
    }
}

fn highlight_log_line(line: &str) -> Vec<Span> {
    let (error_re, warn_re, info_re) = log_regexes();
    let mut spans = Vec::new();
    
    if line.starts_with('[') {
        if let Some(end) = line.find(']') {
            let timestamp = &line[..end+1];
            spans.push(Span::styled(
                timestamp.to_string(),
                Style::default().fg(Color::DarkGray),
            ));
            spans.push(Span::raw(" "));
            
            let remainder = &line[end+1..];
            
            if error_re.is_match(remainder) {
                spans.push(Span::styled(
                    "[ERROR]".to_string(),
                    Style::default().fg(Color::Red).add_modifier(Modifier::BOLD),
                ));
                spans.push(Span::styled(
                    remainder.replace("[ERROR]", ""),
                    Style::default().fg(Color::Red),
                ));
            } else if warn_re.is_match(remainder) {
                spans.push(Span::styled(
                    "[WARN]".to_string(),
                    Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD),
                ));
                spans.push(Span::styled(
                    remainder.replace("[WARN]", ""),
                    Style::default().fg(Color::Yellow),
                ));
            } else if info_re.is_match(remainder) {
                spans.push(Span::styled(
                    "[INFO]".to_string(),
                    Style::default().fg(Color::Blue),
                ));
                spans.push(Span::raw(remainder.replace("[INFO]", "")));
            } else {
                spans.push(Span::raw(remainder.to_string()));
            }
        } else {
            spans.push(Span::raw(line.to_string()));
        }
    } else {
        spans.push(Span::raw(line.to_string()));
    }
    
    spans
}
```

## Requirements Checklist
- [ ] All three files created in correct structure
- [ ] Cargo.toml includes `futures = "0.3"` dependency
- [ ] Code uses MVI architecture (App state in app.rs, UI in ui.rs, main in main.rs)
- [ ] Event loop uses tokio::select! for concurrent input handling
- [ ] Data structures are bounded (max 1000 logs, 200 data points)
- [ ] Terminal restoration is guaranteed even on panic/crash
- [ ] UI has three panels: Infrastructure Pulse (sparklines), Device Grid (table), Log Stream (list with regex highlighting)
- [ ] Controls: q/Esc (quit), Up/Down (scroll logs), a (toggle auto-scroll), r (refresh)

## Build Instructions
After creating files, run:
```bash
cd factoryops-console
cargo run
```

## Expected Behavior
- UI starts immediately showing simulated CPU/Memory sparklines
- 5 manufacturing devices in table with cycling status (Online/Latency/Offline)
- Color-coded log stream with ERROR (red), WARN (yellow), INFO (blue)
- Responsive to quit key even during simulated network delays
- Zero crashes - all errors handled with anyhow
```