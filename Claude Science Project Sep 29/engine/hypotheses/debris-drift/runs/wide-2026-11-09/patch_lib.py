"""Add the default-off option `restrict_to_classes` to the debris-drift module (lib.rs). Usage: python3 patch_lib.py lib.rs"""
import sys
p = sys.argv[1]; s = open(p).read()
a = '''    #[serde(default)]
    date_overrides: Vec<DateOverride>,
'''
a2 = '''    #[serde(default)]
    date_overrides: Vec<DateOverride>,
    /// Keep only the scored finds of the named classes (evidence mode). A class without a scored find is not
    /// transported, so a run for one class costs about that class's share. Empty (default) keeps every class:
    /// byte-identical. Shadow finds of a dropped class must be removed from the configuration.
    #[serde(default)]
    restrict_to_classes: Vec<String>,
'''
assert s.count(a) == 1; s = s.replace(a, a2)
b = '''        let class = p.classes.iter().position(|c| c.motion_classes.contains(&r.motion_class)).ok_or(format!("debris-drift: no class serves motion_class `{}`", r.motion_class))?;
        let at = [r.longitude_deg, r.latitude_deg];
        let segment = map.locate(at).ok_or(format!("debris-drift: find `{}` lies in no declared segment", r.object_id))?;'''
b2 = '''        let class = p.classes.iter().position(|c| c.motion_classes.contains(&r.motion_class)).ok_or(format!("debris-drift: no class serves motion_class `{}`", r.motion_class))?;
        if !p.restrict_to_classes.is_empty() && !p.restrict_to_classes.contains(&p.classes[class].name) {
            continue;
        }
        let at = [r.longitude_deg, r.latitude_deg];
        let segment = map.locate(at).ok_or(format!("debris-drift: find `{}` lies in no declared segment", r.object_id))?;'''
assert s.count(b) == 1; s = s.replace(b, b2)
c = '''    if p.classes.is_empty() || p.env_seeds.is_empty() {
        return Err("debris-drift: need at least one object class and one environment realisation".into());
    }
'''
c2 = c + '''    for n in &p.restrict_to_classes {
        if !p.classes.iter().any(|c| &c.name == n) {
            return Err(format!("debris-drift: restrict_to_classes names unknown class `{n}`"));
        }
    }
'''
assert s.count(c) == 1; s = s.replace(c, c2)
open(p, 'w').write(s); print('patched', p)
