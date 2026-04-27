use serde::{Deserialize, Serialize};
use std::process::Command;

#[derive(Serialize, Deserialize)]
struct GenRequest {
    prompt: String,
    model: String,
    aspect: String,
    duration: u32,
    count: u32,
}

#[derive(Serialize, Deserialize)]
struct GenResponse {
    success: bool,
    message: String,
    video_path: Option<String>,
}

/// Spawn Python sidecar to run gen workflow.
/// Sidecar binary expected at resources/python_sidecar.exe.
#[tauri::command]
fn gen_video(req: GenRequest) -> Result<GenResponse, String> {
    // For now: stub. Real impl spawns python_sidecar.exe with JSON args.
    println!("[gen_video] prompt={} model={}", req.prompt, req.model);
    Ok(GenResponse {
        success: true,
        message: format!("Stub: would generate '{}' with {}", req.prompt, req.model),
        video_path: None,
    })
}

#[tauri::command]
fn bulk_login(accounts: Vec<String>) -> Result<String, String> {
    println!("[bulk_login] {} accounts", accounts.len());
    Ok(format!("Queued {} accounts for login", accounts.len()))
}

#[tauri::command]
fn open_output_folder() -> Result<(), String> {
    // Would open file explorer at output dir
    Ok(())
}

#[tauri::command]
fn get_app_info() -> serde_json::Value {
    serde_json::json!({
        "name": "VEO Pipeline Pro",
        "version": env!("CARGO_PKG_VERSION"),
        "author": "Truong Hoa",
        "zalo": "0345431884"
    })
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_process::init())
        .plugin(tauri_plugin_updater::Builder::new().build())
        .invoke_handler(tauri::generate_handler![
            gen_video,
            bulk_login,
            open_output_folder,
            get_app_info,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
