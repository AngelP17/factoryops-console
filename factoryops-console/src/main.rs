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
