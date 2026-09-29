//! Discover hypotheses: every `hypotheses/<name>/` directory containing `hypothesis.toml`
//! and `lib.rs` becomes module `<name>` (dashes -> underscores) in the registry. Directories
//! starting with `_` (the template) are skipped. Adding a hypothesis therefore never
//! touches a shared file.

use std::fmt::Write as _;
use std::path::Path;

fn main() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"));
    println!("cargo:rerun-if-changed={}", root.display());
    let mut names: Vec<String> = std::fs::read_dir(root)
        .unwrap()
        .filter_map(|e| e.ok())
        .filter(|e| e.path().join("hypothesis.toml").is_file() && e.path().join("lib.rs").is_file())
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .filter(|n| !n.starts_with('_'))
        .collect();
    names.sort();

    let mut out = String::new();
    for name in &names {
        let dir = root.join(name);
        println!("cargo:rerun-if-changed={}", dir.display());
        assert!(
            name.chars().all(|c| c.is_ascii_lowercase() || c.is_ascii_digit() || c == '-'),
            "hypothesis directory `{name}` must be kebab-case"
        );
        // A hypothesis sees only the hypothesis API, geo, serde and toml, never another hypothesis.
        for file in rust_files(&dir) {
            let text = std::fs::read_to_string(&file).unwrap();
            assert!(
                !text.contains("crate::") && !text.contains("super::super"),
                "{}: hypotheses may not reference other hypotheses or the registry",
                file.display()
            );
        }
        let lib = dir.join("lib.rs");
        writeln!(out, "#[path = {:?}]\npub mod {};", lib.display().to_string(), ident(name)).unwrap();
    }
    writeln!(out, "\n/// Names of all hypotheses, sorted.\npub const NAMES: &[&str] = &{names:?};\n").unwrap();
    writeln!(out, "/// Construct a hypothesis from its parameter table.").unwrap();
    writeln!(out, "pub fn construct(name: &str, params: &toml::Value) -> Result<Box<dyn hypothesis::Hypothesis>, String> {{").unwrap();
    writeln!(out, "    match name {{").unwrap();
    for name in &names {
        writeln!(out, "        {name:?} => {}::new(params),", ident(name)).unwrap();
    }
    writeln!(out, "        other => Err(format!(\"unknown hypothesis `{{other}}`; known: {{NAMES:?}}\")),\n    }}\n}}\n").unwrap();
    writeln!(out, "/// The hypothesis.toml metadata of a hypothesis.").unwrap();
    writeln!(out, "pub fn metadata(name: &str) -> Option<&'static str> {{\n    match name {{").unwrap();
    for name in &names {
        let meta = root.join(name).join("hypothesis.toml");
        writeln!(out, "        {name:?} => Some(include_str!({:?})),", meta.display().to_string()).unwrap();
    }
    writeln!(out, "        _ => None,\n    }}\n}}").unwrap();
    std::fs::write(Path::new(&std::env::var("OUT_DIR").unwrap()).join("registry.rs"), out).unwrap();
}

fn ident(name: &str) -> String {
    name.replace('-', "_")
}

fn rust_files(dir: &Path) -> Vec<std::path::PathBuf> {
    let mut files = Vec::new();
    for entry in std::fs::read_dir(dir).unwrap().filter_map(|e| e.ok()) {
        let path = entry.path();
        if path.is_dir() {
            files.extend(rust_files(&path));
        } else if path.extension().is_some_and(|e| e == "rs") {
            files.push(path);
        }
    }
    files
}
