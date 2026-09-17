use std::process::Command;
use tauri::Manager;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    .setup(|app| {
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }
      Ok(())
    })
    .invoke_handler(tauri::generate_handler![
      check_docker,
      start_docker_containers,
      stop_docker_containers,
      check_containers_status
    ])
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}

#[tauri::command]
fn check_docker() -> Result<bool, String> {
  let result = Command::new("docker")
    .arg("ps")
    .output();

  match result {
    Ok(_) => Ok(true),
    Err(_) => Ok(false),
  }
}

#[tauri::command]
fn start_docker_containers() -> Result<String, String> {
  let result = Command::new("docker-compose")
    .arg("up")
    .arg("-d")
    .current_dir("..")
    .output();

  match result {
    Ok(output) => {
      if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
      } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
      }
    }
    Err(e) => Err(e.to_string()),
  }
}

#[tauri::command]
fn stop_docker_containers() -> Result<String, String> {
  let result = Command::new("docker-compose")
    .arg("down")
    .current_dir("..")
    .output();

  match result {
    Ok(output) => {
      if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
      } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
      }
    }
    Err(e) => Err(e.to_string()),
  }
}

#[tauri::command]
fn check_containers_status() -> Result<String, String> {
  let result = Command::new("docker-compose")
    .arg("ps")
    .current_dir("..")
    .output();

  match result {
    Ok(output) => {
      if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
      } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
      }
    }
    Err(e) => Err(e.to_string()),
  }
}
