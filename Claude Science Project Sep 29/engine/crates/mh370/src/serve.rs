//! The local app: a small HTTP server on the loopback interface that runs the filter in
//! this process and serves `ui/index.html`.
//!
//! There is no second estimator behind it. A run made here loads the same configuration
//! files as `make report`, merges the app's controls as one more override table, and
//! writes the same artifacts to `runs/`, so any run can be repeated from the command line.

use crate::filter::Progress;
use crate::{describe, summary, Hooks};
use serde_json::{json, Value};
use std::collections::HashMap;
use std::io::{BufRead, BufReader, Read, Write};
use std::net::{Ipv4Addr, SocketAddr, TcpListener, TcpStream};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::time::Instant;

const UI: &str = include_str!("../ui/index.html");
const DEFAULT_PORT: u16 = 8370;
/// Measured here: seconds per particle-epoch on one thread, and the fixed cost of reading
/// the weather and declination grids. Both only feed the run-time estimate.
const SECONDS_PER_PARTICLE_EPOCH: f64 = 3.8e-5;
const LOAD_SECONDS: f64 = 8.0;

pub fn main(args: &[String]) -> Result<(), String> {
    let root = describe::root_from(args)?;
    let port = match args.iter().position(|a| a == "--port") {
        Some(i) => args.get(i + 1).ok_or("--port needs a number")?.parse().map_err(|_| "--port needs a number")?,
        None => DEFAULT_PORT,
    };
    // Loopback only: this is a local tool, not a service.
    let listener = (port..port + 10)
        .find_map(|p| TcpListener::bind(SocketAddr::from((Ipv4Addr::LOCALHOST, p))).ok())
        .ok_or_else(|| format!("ports {port}-{} are all in use", port + 9))?;
    let url = format!("http://127.0.0.1:{}", listener.local_addr().map_err(|e| e.to_string())?.port());
    println!("MH370 particle filter: {url}");
    println!("working from {}", root.display());
    if !args.iter().any(|a| a == "--no-open") {
        open_browser(&url);
    }
    let state = Arc::new(App { root, runs: Mutex::new(HashMap::new()), next: Mutex::new(0) });
    for stream in listener.incoming() {
        let Ok(stream) = stream else { continue };
        let state = Arc::clone(&state);
        std::thread::spawn(move || {
            if let Err(e) = handle(&state, stream) {
                eprintln!("request failed: {e}");
            }
        });
    }
    Ok(())
}

struct App {
    root: PathBuf,
    runs: Mutex<HashMap<String, Run>>,
    next: Mutex<u32>,
}

struct Run {
    id: String,
    name: String,
    out: PathBuf,
    engine: String,
    config_paths: Vec<PathBuf>,
    overrides: String,
    status: &'static str,
    error: Option<String>,
    steps_done: usize,
    steps_total: usize,
    particles: usize,
    events: Vec<Value>,
    summary: Option<Value>,
    started: Instant,
    runtime_s: Option<f64>,
    cancel: Arc<AtomicBool>,
}

impl Run {
    fn json(&self) -> Value {
        json!({
            "id": self.id, "name": self.name, "engine": self.engine, "out": self.out,
            "config_paths": self.config_paths, "overrides": self.overrides,
            "status": self.status, "error": self.error,
            "steps_done": self.steps_done, "steps_total": self.steps_total, "particles": self.particles,
            "elapsed_s": self.runtime_s.unwrap_or_else(|| self.started.elapsed().as_secs_f64()),
            "events": self.events,
            "summary": self.summary,
        })
    }
}

fn handle(app: &Arc<App>, mut stream: TcpStream) -> Result<(), String> {
    let mut reader = BufReader::new(stream.try_clone().map_err(|e| e.to_string())?);
    let mut line = String::new();
    if reader.read_line(&mut line).map_err(|e| e.to_string())? == 0 {
        return Ok(());
    }
    let mut parts = line.split_whitespace();
    let (method, target) = (parts.next().unwrap_or("").to_string(), parts.next().unwrap_or("/").to_string());
    let mut length = 0usize;
    loop {
        let mut header = String::new();
        if reader.read_line(&mut header).map_err(|e| e.to_string())? == 0 || header.trim().is_empty() {
            break;
        }
        if let Some(value) = header.to_ascii_lowercase().strip_prefix("content-length:") {
            length = value.trim().parse().unwrap_or(0);
        }
    }
    let mut body = vec![0u8; length];
    if length > 0 {
        reader.read_exact(&mut body).map_err(|e| e.to_string())?;
    }
    let (path, query) = target.split_once('?').unwrap_or((target.as_str(), ""));
    let body: Value = serde_json::from_slice(&body).unwrap_or(Value::Null);

    let response = route(app, &method, path, query, &body);
    match response {
        Ok(Response::Html(text)) => write_response(&mut stream, "200 OK", "text/html; charset=utf-8", text.as_bytes()),
        Ok(Response::Json(value)) => {
            let text = serde_json::to_string(&value).map_err(|e| e.to_string())?;
            write_response(&mut stream, "200 OK", "application/json", text.as_bytes())
        }
        Ok(Response::NotFound) => write_response(&mut stream, "404 Not Found", "text/plain", b"not found"),
        Err(e) => {
            let text = serde_json::to_string(&json!({"error": e})).unwrap_or_default();
            write_response(&mut stream, "400 Bad Request", "application/json", text.as_bytes())
        }
    }
}

enum Response {
    Html(String),
    Json(Value),
    NotFound,
}

fn route(app: &Arc<App>, method: &str, path: &str, query: &str, body: &Value) -> Result<Response, String> {
    match (method, path) {
        ("GET", "/") => Ok(Response::Html(UI.to_string())),
        ("GET", "/api/describe") => Ok(Response::Json(describe::describe(&app.root)?)),
        ("POST", "/api/run") => Ok(Response::Json(start(app, body)?)),
        ("GET", "/api/runs") => {
            let runs = app.runs.lock().map_err(|e| e.to_string())?;
            let mut list: Vec<Value> = runs.values().map(Run::json).collect();
            list.sort_by_key(|r| r["id"].as_str().unwrap_or("").to_string());
            Ok(Response::Json(json!(list)))
        }
        ("GET", "/api/run") => {
            let id = param(query, "id").ok_or("id is required")?;
            let runs = app.runs.lock().map_err(|e| e.to_string())?;
            Ok(runs.get(&id).map(|r| Response::Json(r.json())).unwrap_or(Response::NotFound))
        }
        ("POST", "/api/quit") => {
            // The app runs without a terminal, so the window closes the process.
            std::thread::spawn(|| {
                std::thread::sleep(std::time::Duration::from_millis(200));
                std::process::exit(0);
            });
            Ok(Response::Json(json!({"quitting": true})))
        }
        ("POST", "/api/cancel") => {
            let id = param(query, "id").ok_or("id is required")?;
            let runs = app.runs.lock().map_err(|e| e.to_string())?;
            if let Some(run) = runs.get(&id) {
                run.cancel.store(true, Ordering::Relaxed);
            }
            Ok(Response::Json(json!({"cancelling": id})))
        }
        ("GET", "/api/summary") => {
            let name = param(query, "run").ok_or("run is required")?;
            Ok(Response::Json(stored_summary(&app.root, &name)?))
        }
        ("GET", "/api/estimate") => {
            let particles: f64 = param(query, "particles").and_then(|p| p.parse().ok()).unwrap_or(0.0);
            let replicates: f64 = param(query, "replicates").and_then(|p| p.parse().ok()).unwrap_or(1.0);
            Ok(Response::Json(estimate(particles, replicates)))
        }
        _ => Ok(Response::NotFound),
    }
}

/// Start a run in a worker thread and return its record.
fn start(app: &Arc<App>, body: &Value) -> Result<Value, String> {
    let engine = body["engine"].as_str().unwrap_or("config/davey2016.toml").to_string();
    let mut config_paths = vec![app.root.join(&engine)];
    // Overrides named by the app are applied over the engine, in order, like the command line.
    for extra in body["overlays"].as_array().unwrap_or(&Vec::new()) {
        if let Some(p) = extra.as_str() {
            config_paths.push(app.root.join(p));
        }
    }
    // The app sends the override as TOML, the same text it displays, so that a run made
    // here is exactly a run made with that override file on the command line.
    let overrides = body["overrides_toml"].as_str().unwrap_or("").to_string();
    let table = match overrides.trim().is_empty() {
        true => None,
        false => Some(toml::from_str::<toml::Table>(&overrides).map_err(|e| format!("override: {e}"))?),
    };
    // Load once here so a bad configuration is reported before any work starts.
    let config = crate::config::load_with(&config_paths, table.clone())?;
    let replicates: usize = config.cases.iter().map(|c| c.seeds.as_ref().unwrap_or(&config.seeds).len()).sum();
    let particles: usize = config.particles_per_mode.iter().sum();
    let modes = config.particles_per_mode.iter().filter(|&&n| n > 0).count();

    let mut next = app.next.lock().map_err(|e| e.to_string())?;
    *next += 1;
    let id = format!("app-{:04}", *next);
    drop(next);
    let name = body["name"].as_str().filter(|s| !s.is_empty()).unwrap_or(&id).to_string();
    let out = app.root.join("runs").join(&name);

    let run = Run {
        id: id.clone(),
        name: name.clone(),
        out: out.clone(),
        engine,
        config_paths: config_paths.clone(),
        overrides,
        status: "running",
        error: None,
        steps_done: 0,
        // Twelve SATCOM epochs, one filtered step each, per mode per replicate.
        steps_total: replicates * modes * 12,
        particles: particles * replicates,
        events: Vec::new(),
        summary: None,
        started: Instant::now(),
        runtime_s: None,
        cancel: Arc::new(AtomicBool::new(false)),
    };
    let cancel = Arc::clone(&run.cancel);
    let record = run.json();
    app.runs.lock().map_err(|e| e.to_string())?.insert(id.clone(), run);

    let app = Arc::clone(app);
    std::thread::spawn(move || {
        let progress = |p: &Progress| {
            if let Ok(mut runs) = app.runs.lock() {
                if let Some(run) = runs.get_mut(&id) {
                    run.steps_done += 1;
                    run.events.push(json!(p));
                    let extra = run.events.len().saturating_sub(400);
                    run.events.drain(..extra);
                }
            }
        };
        let hooks = Hooks { overrides: table, progress: &progress, cancel: &cancel };
        let outcome = crate::run(&config_paths, &out, Some(&hooks));
        let summary = outcome.as_ref().ok().and_then(|_| stored_summary(&app.root, &name).ok());
        if let Ok(mut runs) = app.runs.lock() {
            if let Some(run) = runs.get_mut(&id) {
                run.runtime_s = Some(run.started.elapsed().as_secs_f64());
                match outcome {
                    Ok(_) => {
                        run.status = "done";
                        run.summary = summary;
                    }
                    Err(e) if e == "cancelled" => run.status = "cancelled",
                    Err(e) => {
                        run.status = "error";
                        run.error = Some(e);
                    }
                }
            }
        }
    });
    Ok(record)
}

/// A finished run's summary, built from its artifacts if it predates `summary.json`.
fn stored_summary(root: &Path, name: &str) -> Result<Value, String> {
    let dir = if Path::new(name).is_absolute() { PathBuf::from(name) } else { root.join(name) };
    let dir = if dir.join("run.json").is_file() { dir } else { root.join("runs").join(name) };
    let stored = dir.join("summary.json");
    if let Ok(text) = std::fs::read_to_string(&stored) {
        if let Ok(value) = serde_json::from_str::<Value>(&text) {
            // Runs made before the published curve was a configured input are rebuilt, so
            // that a comparison with it is available for every run in the list.
            if !value["reference"].is_null() || reference_curve(root).is_none() {
                return Ok(with_manifest(&dir, value));
            }
        }
    }
    let value = summary::rebuild(&dir, reference_curve(root))?;
    Ok(with_manifest(&dir, value))
}

/// The published curve named by the base configuration, if it is on disk.
fn reference_curve(root: &Path) -> Option<PathBuf> {
    let base = crate::config::load(&[root.join("config/davey2016.toml")]).ok()?;
    base.inputs.reference_curve.filter(|p| p.is_file())
}

/// Attach the parts of the manifest the app shows beside a result.
fn with_manifest(dir: &Path, mut summary: Value) -> Value {
    let manifest: Option<Value> = std::fs::read_to_string(dir.join("run.json")).ok().and_then(|t| serde_json::from_str(&t).ok());
    if let (Some(object), Some(manifest)) = (summary.as_object_mut(), manifest) {
        for key in ["config", "assumptions", "hypotheses", "code_revision", "runtime_s", "peak_memory_mib", "threads",
                    "reference_arcs", "prior", "epochs", "config_paths"] {
            if let Some(value) = manifest.get(key) {
                object.insert(key.to_string(), value.clone());
            }
        }
        object.insert("run".to_string(), json!(dir));
    }
    summary
}

/// Rough run time and memory for a proposed run size, from measurements on this machine.
fn estimate(particles: f64, replicates: f64) -> Value {
    let threads = rayon::current_num_threads().max(1) as f64;
    let seconds = LOAD_SECONDS + particles * replicates * 12.0 * SECONDS_PER_PARTICLE_EPOCH / threads;
    json!({
        "seconds": seconds,
        "memory_mib": particles * crate::filter::PARTICLE_BYTES as f64 / (1024.0 * 1024.0),
        "threads": threads,
        "note": "Estimate only: measured on a 6-thread machine at the published epoch count.",
    })
}

fn param(query: &str, key: &str) -> Option<String> {
    query.split('&').find_map(|pair| {
        let (k, v) = pair.split_once('=')?;
        (k == key).then(|| percent_decode(v))
    })
}

fn percent_decode(text: &str) -> String {
    let bytes = text.replace('+', " ").into_bytes();
    let mut out = Vec::with_capacity(bytes.len());
    let mut i = 0;
    while i < bytes.len() {
        if bytes[i] == b'%' && i + 2 < bytes.len() {
            if let Ok(byte) = u8::from_str_radix(&String::from_utf8_lossy(&bytes[i + 1..i + 3]), 16) {
                out.push(byte);
                i += 3;
                continue;
            }
        }
        out.push(bytes[i]);
        i += 1;
    }
    String::from_utf8_lossy(&out).to_string()
}

fn write_response(stream: &mut TcpStream, status: &str, kind: &str, body: &[u8]) -> Result<(), String> {
    let head = format!(
        "HTTP/1.1 {status}\r\nContent-Type: {kind}\r\nContent-Length: {}\r\nCache-Control: no-store\r\nConnection: close\r\n\r\n",
        body.len()
    );
    stream.write_all(head.as_bytes()).map_err(|e| e.to_string())?;
    stream.write_all(body).map_err(|e| e.to_string())?;
    stream.flush().map_err(|e| e.to_string())
}

fn open_browser(url: &str) {
    let opener = if cfg!(target_os = "macos") { "open" } else { "xdg-open" };
    let _ = std::process::Command::new(opener).arg(url).stdout(std::process::Stdio::null()).stderr(std::process::Stdio::null()).spawn();
}

#[cfg(test)]
mod tests {
    use super::*;

    /// What the app sends must load as a run configuration, with whole numbers still
    /// reaching float fields as floats.
    #[test]
    fn an_app_override_loads_as_a_run_configuration() {
        let sent = "particles_per_mode = [1000, 1000, 1000, 1000, 1000]\nseeds = [1]\n\
                    resample_ess_fraction = 0.5\n\n[[cases]]\nid = \"bto-bfo\"\nuse_bfo = true\n\n\
                    [environment]\nwind_scale = 0.0\n\n[dynamics]\nbank_angle_deg = 20.0\n";
        let table: toml::Table = toml::from_str(sent).unwrap();
        let dir = std::env::temp_dir().join("mh370-override-test");
        std::fs::create_dir_all(&dir).unwrap();
        let path = dir.join("override.toml");
        std::fs::write(&path, sent).unwrap();
        let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
        let config = crate::config::load_with(&[root.join("config/davey2016.toml"), path], Some(table)).unwrap();
        assert_eq!(config.particles_per_mode, [1000; 5]);
        assert_eq!(config.environment.wind_scale, 0.0);
        assert_eq!(config.dynamics.apply(flight::Parameters::default()).bank_angle_deg, 20.0);
    }

    #[test]
    fn query_parameters_are_decoded() {
        assert_eq!(param("run=runs%2Fdavey2016&id=7", "run").as_deref(), Some("runs/davey2016"));
        assert_eq!(param("run=a&id=7", "id").as_deref(), Some("7"));
        assert_eq!(param("run=a", "missing"), None);
    }
}
