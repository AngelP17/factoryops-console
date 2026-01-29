use anyhow::Result;
use crossterm::event::{Event as CEvent, EventStream, KeyCode, KeyEventKind};
use futures::{FutureExt, StreamExt};
use ratatui::backend::Backend;
use ratatui::Terminal;
use std::collections::VecDeque;
use std::time::{Duration, Instant};

use crate::ui;

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
    pub fn display(&self) -> (&'static str, String) {
        match self {
            DeviceStatus::Online => ("●", "Online".to_string()),
            DeviceStatus::HighLatency(ms) => ("◐", format!("Latency {}ms", ms)),
            DeviceStatus::Offline => ("○", "Offline".to_string()),
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
        
        // Collect updates first to avoid borrow conflicts
        let updates: Vec<(usize, DeviceStatus)> = self.devices
            .iter()
            .enumerate()
            .filter_map(|(idx, device)| {
                let roll = rng.gen_range(0..100);
                let new_status = if roll < 70 {
                    DeviceStatus::Online
                } else if roll < 90 {
                    let latency = rng.gen_range(100..800);
                    DeviceStatus::HighLatency(latency)
                } else {
                    DeviceStatus::Offline
                };
                
                let current_status = device.status;
                if current_status != new_status || 
                   matches!(new_status, DeviceStatus::HighLatency(_)) {
                    Some((idx, new_status))
                } else {
                    None
                }
            })
            .collect();
        
        // Apply updates after iteration is complete
        for (idx, new_status) in updates {
            self.update_device(idx, new_status);
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
