use serde::{Deserialize, Serialize};

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
/// TODO: implement real sidecar spawn before shipping.
#[tauri::command]
fn gen_video(req: GenRequest) -> Result<GenResponse, String> {
    println!("[gen_video] prompt={} model={}", req.prompt, req.model);
    Err("gen_video not implemented in this build".into())
}

#[tauri::command]
fn bulk_login(accounts: Vec<String>) -> Result<String, String> {
    // Gioi han toi da 200 tai khoan de tranh qua tai
    if accounts.len() > 200 {
        return Err(format!(
            "Too many accounts: {} (max 200)",
            accounts.len()
        ));
    }
    println!("[bulk_login] {} accounts", accounts.len());
    Err("bulk_login not implemented".into())
}

#[tauri::command]
fn open_output_folder() -> Result<(), String> {
    Err("open_output_folder not implemented".into())
}

#[tauri::command]
fn get_app_info() -> serde_json::Value {
    // Doc tu env var khi build; tranh hardcode PII trong source code
    let owner = option_env!("VEO_OWNER_NAME").unwrap_or("");
    serde_json::json!({
        "name": env!("CARGO_PKG_NAME"),
        "version": env!("CARGO_PKG_VERSION"),
        "owner": owner,
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
