//! Stamps the binary with the git revision it was BUILT from (core request 16; the
//! `reference-289` run recorded "4f6487a-dirty" because the revision used to be read from the
//! working tree when the run finished, not from the code the binary was compiled from).
use std::process::Command;

fn git(args: &[&str]) -> Option<String> {
    let out = Command::new("git").args(args).output().ok()?;
    out.status.success().then(|| String::from_utf8_lossy(&out.stdout).trim().to_string())
}

fn main() {
    let rev = match git(&["rev-parse", "--short", "HEAD"]) {
        Some(rev) => {
            // Dirty if any tracked file under the engine differs from HEAD.
            let dirty = git(&["status", "--porcelain", "--untracked-files=no", "--", "../.."]).is_some_and(|s| !s.is_empty());
            if dirty { format!("{rev}-dirty") } else { rev }
        }
        None => "unversioned".into(),
    };
    println!("cargo:rustc-env=MH370_BUILD_REVISION={rev}");
    // Rebuild when HEAD moves or the index changes (a commit, a checkout, a staged edit).
    if let Some(dir) = git(&["rev-parse", "--absolute-git-dir"]) {
        println!("cargo:rerun-if-changed={dir}/HEAD");
        println!("cargo:rerun-if-changed={dir}/index");
        if let Some(r) = git(&["symbolic-ref", "-q", "HEAD"]) {
            println!("cargo:rerun-if-changed={dir}/{r}");
        }
    }
    println!("cargo:rerun-if-changed=build.rs");
    // And when any engine source changes, so the "-dirty" mark tracks the code compiled.
    for dir in ["src", "../flight/src", "../satcom/src", "../hypothesis/src", "../geo/src", "../../hypotheses"] {
        if std::path::Path::new(dir).exists() {
            println!("cargo:rerun-if-changed={dir}");
        }
    }
}
