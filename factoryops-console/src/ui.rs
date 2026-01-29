use ratatui::{
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

pub fn render(f: &mut Frame, app: &App) {
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

fn render_infrastructure_panel(f: &mut Frame, app: &App, area: Rect) {
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

fn render_device_grid(f: &mut Frame, app: &App, area: Rect) {
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
    
    let table = Table::new(rows)
    .widths(&[
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

fn render_log_panel(f: &mut Frame, app: &App, area: Rect) {
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
