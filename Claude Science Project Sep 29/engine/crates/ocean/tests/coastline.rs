//! Tests for the polygon coastline (`gshhg::PolygonCoast`): land test against brute-force ray
//! casting, beaching segment and chainage, segment contiguity, land-mask snapping through the
//! integrator, and (when the GSHHG file is present) the real coast at the debris find sites.

use mh370_ocean::analytic::Uniform;
use mh370_ocean::field::{FieldGap, FieldMeta, VectorField};
use mh370_ocean::gshhg::Ring;
use mh370_ocean::*;
use rand::{Rng, SeedableRng};

const T0: f64 = 1_394_236_800.0; // 2014-03-08T00:00:00Z
const DAY: f64 = SECONDS_PER_DAY;

fn opts() -> PolygonCoastOptions {
    PolygonCoastOptions { bbox: [50.0, 70.0, -30.0, -10.0], ..PolygonCoastOptions::default() }
}

/// Square island 60-61 E, 21-20 S, anticlockwise; its east side is named segment 1.
fn square() -> PolygonCoast {
    let ring = Ring { id: 7, points: vec![[60.0, -21.0], [61.0, -21.0], [61.0, -20.0], [60.0, -20.0]] };
    let named = vec![NamedSegment { id: 1, name: "east".into(), boxes: vec![[60.9, 61.1, -21.1, -19.9]] }];
    PolygonCoast::from_rings(vec![ring], named, opts(), "test square".into())
}

/// A non-convex star around (65 E, 15 S), 60 vertices, radius 0.3-1.0 deg.
fn star() -> Vec<LonLat> {
    (0..60)
        .map(|k| {
            let a = k as f64 / 60.0 * std::f64::consts::TAU;
            let r = if k % 2 == 0 { 1.0 } else { 0.3 + 0.2 * ((k / 2) % 3) as f64 };
            [65.0 + r * a.cos(), -15.0 + r * a.sin()]
        })
        .collect()
}

fn brute_inside(poly: &[LonLat], p: LonLat) -> bool {
    let mut inside = false;
    for i in 0..poly.len() {
        let (a, b) = (poly[i], poly[(i + 1) % poly.len()]);
        if (a[1] > p[1]) != (b[1] > p[1]) && p[0] > a[0] + (p[1] - a[1]) / (b[1] - a[1]) * (b[0] - a[0]) {
            inside = !inside;
        }
    }
    inside
}

#[test]
fn is_land_matches_brute_force_ray_casting() {
    let poly = star();
    let rings = vec![Ring { id: 3, points: poly.clone() }, Ring { id: 7, points: vec![[60.0, -21.0], [61.0, -21.0], [61.0, -20.0], [60.0, -20.0]] }];
    let c = PolygonCoast::from_rings(rings, vec![], opts(), "test".into());
    let sq = [[60.0, -21.0], [61.0, -21.0], [61.0, -20.0], [60.0, -20.0]];
    let mut g = rand_chacha::ChaCha8Rng::seed_from_u64(5);
    let mut land = 0;
    for _ in 0..50_000 {
        let p = [g.gen_range(59.5..66.5), g.gen_range(-21.5..-13.5)];
        let want = brute_inside(&poly, p) || brute_inside(&sq, p);
        assert_eq!(c.is_land(p), want, "{p:?}");
        land += want as usize;
    }
    assert!(land > 2_000, "only {land} land samples");
    let [coastal, landc, sea] = c.cell_census();
    assert!(coastal > 0 && landc > 0 && sea > 0);
}

#[test]
fn beaching_carries_named_segment_and_chainage() {
    let c = square();
    assert!(c.is_land([60.5, -20.5]) && !c.is_land([61.01, -20.5]) && !c.is_land([59.99, -20.5]));
    // Origin is the start of the named run, vertex (61, -21); the east side runs north from it.
    let h = c.first_crossing([62.0, -20.5], [60.5, -20.5]).expect("crossing");
    assert_eq!((h.segment, h.line), (1, 7));
    assert!((h.point[0] - 61.0).abs() < 1e-12 && (h.point[1] + 20.5).abs() < 1e-12);
    assert!((h.fraction - 1.0 / 1.5).abs() < 1e-12);
    let half = EARTH_RADIUS_M * 0.5f64.to_radians();
    assert!((h.chainage_m - half).abs() < 1e-6 * half, "{}", h.chainage_m);
    assert_eq!(h.snapped_m, 0.0);
    // From land, or wholly at sea: no crossing.
    assert!(c.first_crossing([60.5, -20.5], [62.0, -20.5]).is_none());
    assert!(c.first_crossing([62.0, -20.5], [61.5, -20.5]).is_none());
    // The other three sides are unnamed pieces of about 100 km from id 100, chainage continuing.
    let h2 = c.first_crossing([60.5, -19.0], [60.5, -20.5]).unwrap();
    assert!(h2.segment >= 100);
    let top = distance_m([61.0, -21.0], [61.0, -20.0]) + distance_m([61.0, -20.0], [60.5, -20.0]);
    assert!((h2.chainage_m - top).abs() < 1e-6 * top, "{} vs {top}", h2.chainage_m);
}

#[test]
fn segments_tile_each_line_without_gaps() {
    let rings = vec![Ring { id: 3, points: star() }, Ring { id: 7, points: vec![[60.0, -21.0], [61.0, -21.0], [61.0, -20.0], [60.0, -20.0]] }];
    let named = vec![NamedSegment { id: 2, name: "star-east".into(), boxes: vec![[65.5, 66.5, -15.6, -14.4]] }];
    let c = PolygonCoast::from_rings(rings, named, opts(), "test".into());
    let segs = c.segments();
    for r in c.ring_infos() {
        let mut s: Vec<_> = segs.iter().filter(|e| e.line == r.line).collect();
        s.sort_by(|a, b| a.start_m.partial_cmp(&b.start_m).unwrap());
        assert_eq!(s[0].start_m, 0.0);
        assert!((s[s.len() - 1].end_m - r.length_m).abs() < 1e-6);
        for w in s.windows(2) {
            assert!((w[0].end_m - w[1].start_m).abs() < 1e-6, "{:?}", w);
        }
    }
    assert!(segs.iter().any(|e| e.segment == 2 && e.line == 3));
    // Locating each vertex of the star gives a chainage that increases around the ring from its
    // origin, with the single jump at the origin.
    let ri = c.ring_index(3).unwrap();
    let info = c.ring_infos()[ri].clone();
    let pts = c.ring_points(ri).to_vec();
    let mut prev = None;
    for j in 1..pts.len() {
        let k = (info.origin + j) % pts.len();
        let h = c.locate(pts[k], 1.0).unwrap();
        assert!(h.snapped_m < 1e-6);
        if let Some(p) = prev {
            assert!(h.chainage_m > p, "chainage not increasing at vertex {k}");
        }
        prev = Some(h.chainage_m);
    }
}

/// A current whose product land mask extends `offshore_deg` east of the square island.
struct Masked {
    inner: Uniform,
    mask_east_of_lon: f64,
}

impl VectorField for Masked {
    fn sample(&self, t: f64, p: LonLat) -> Result<[f64; 2], FieldGap> {
        if p[0] < self.mask_east_of_lon && p[1] > -21.2 && p[1] < -19.8 { Err(FieldGap::Land) } else { self.inner.sample(t, p) }
    }
    fn meta(&self) -> &FieldMeta {
        self.inner.meta()
    }
}

fn run_west(coast: &dyn Coastline) -> Track {
    let c = Masked { inner: Uniform::current(-0.2, 0.0), mask_east_of_lon: 61.1 };
    let spec = RunSpec {
        forcing: Forcing { current: &c, stokes: None, wind10: None },
        coast,
        domain: Domain { lon_min: 50.0, lon_max: 70.0, lat_min: -30.0, lat_max: -10.0 },
        step_s: 3600.0,
        output_times: vec![T0 + 10.0 * DAY],
        diffusion: Diffusion::None,
        ocean_error: OceanErrorModel::none(),
        refloat: Refloat::Off,
        seed: 1,
        leeway_absorbs_stokes: false,
        accept_partial_stokes_overlap: false,
        explicit_residual: false,
        threads: 1,
    };
    integrate(&spec, &[Particle::new([62.0, -20.5], T0, ObjectResponse::new(0.0, 0.0))]).unwrap().tracks.remove(0)
}

use mh370_ocean::integrate::Track;

#[test]
fn land_mask_stranding_snaps_to_the_coast_within_the_declared_distance() {
    let c = square();
    let tr = run_west(&c);
    assert_eq!(tr.fate, Fate::Beached, "{:?}", tr.events);
    let Event::Beached { at, segment, line, snapped_m, chainage_m, .. } = tr.events[0] else { panic!("{:?}", tr.events) };
    assert_eq!((segment, line), (1, 7));
    assert!((at[0] - 61.0).abs() < 1e-9 && (at[1] + 20.5).abs() < 1e-9);
    // Stranded at the first position whose RK2 midpoint lies inside the mask (61.1 E): between
    // 0.1 and 0.1 + one step (720 m) east of the shore.
    let cos = 20.5f64.to_radians().cos();
    let tenth = EARTH_RADIUS_M * 0.1f64.to_radians() * cos;
    assert!(snapped_m > tenth - 1.0 && snapped_m < tenth + 720.0, "snapped {snapped_m}");
    assert!((chainage_m - EARTH_RADIUS_M * 0.5f64.to_radians()).abs() < 1.0);
    assert!(matches!(tr.snapshots[0], Snapshot::Beached { segment: 1, .. }));

    // Snap distance below the mask's offshore extent: the stranding stays a land-mask gap.
    let short = PolygonCoast::from_rings(
        vec![Ring { id: 7, points: vec![[60.0, -21.0], [61.0, -21.0], [61.0, -20.0], [60.0, -20.0]] }],
        vec![],
        PolygonCoastOptions { snap_max_m: 5_000.0, ..opts() },
        "test".into(),
    );
    let tr = run_west(&short);
    assert_eq!(tr.fate, Fate::FieldGap);
    assert!(matches!(tr.events[0], Event::FieldGap { gap: FieldGap::Land, .. }));
    // The analytic coasts do not snap: unchanged behaviour.
    assert_eq!(run_west(&NoCoast).fate, Fate::FieldGap);
}

fn gshhg_path() -> Option<std::path::PathBuf> {
    let p = std::env::var("MH370_GSHHG_F").unwrap_or_else(|_| "/Users/pete/Downloads/mh370-ocean-data/gshhg/gshhs_f.b".into());
    let p = std::path::PathBuf::from(p);
    if p.exists() { Some(p) } else { eprintln!("GSHHG file absent ({}): real-coast test skipped", p.display()); None }
}

#[test]
fn real_gshhg_coast_at_the_stringent_nine_find_sites() {
    let Some(path) = gshhg_path() else { return };
    let c = PolygonCoast::from_gshhg(&path, g1_segments(), PolygonCoastOptions::default()).unwrap();
    // Find coordinates from debris-evidence-audit.csv (drift, 9a9b0cc) and drift's segment.
    let finds = [
        ("reunion-right-flaperon", [55.649150, -20.916180], 1),
        ("mossel-bay-engine-cowling-roy", [22.149905, -34.093767], 4),
        ("paindane-right-flap-fairing", [35.499796, -24.078057], 3),
        ("vilanculos-horizontal-stabilizer-panel", [35.519020, -22.088570], 3),
        ("mauritius-left-outboard-flap", [57.701386, -20.023383], 2),
        ("rodrigues-door-closet-panel", [63.471632, -19.738711], 2),
        ("chidenguele-right-fan-cowling", [34.196373, -24.958022], 3),
        ("antsiraka-cabin-interior-panel", [49.726188, -16.862289], 5),
        ("pemba-right-outboard-flap", [39.868086, -5.056071], 6),
    ];
    for (name, p, seg) in finds {
        let h = c.locate(p, 5_000.0).unwrap_or_else(|| panic!("{name}: no shore within 5 km"));
        assert_eq!(h.segment, seg, "{name}");
    }
    // Reunion is one whole ring, all of it in S1 (with any islet in the S1 box).
    let reunion = c.locate([55.649150, -20.916180], 5_000.0).unwrap().line;
    let ri = c.ring_index(reunion).unwrap();
    let l = c.ring_infos()[ri].length_m;
    assert!(l > 180e3 && l < 280e3, "Reunion ring {l} m");
    let s1: Vec<_> = c.segments().into_iter().filter(|s| s.segment == 1).collect();
    let r1: Vec<_> = s1.iter().filter(|s| s.line == reunion).collect();
    assert_eq!(r1.len(), 1);
    assert!(r1[0].start_m == 0.0 && (r1[0].end_m - l).abs() < 1e-6);
    assert!(s1.iter().all(|s| s.end_m - s.start_m < 5e3 || s.line == reunion));
    assert!(c.is_land([55.5, -21.1]) && c.is_land([47.0, -19.0]) && c.is_land([25.0, -28.0]) && c.is_land([134.0, -25.0]));
    assert!(!c.is_land([78.0, -30.0]) && !c.is_land([88.0, -38.0]) && !c.is_land([56.0, -20.0]));
    // Mossel Bay -> Chidenguele along Africa's single line: chainage increases eastward then north.
    let a = c.locate([22.149905, -34.093767], 5_000.0).unwrap();
    let b = c.locate([34.196373, -24.958022], 5_000.0).unwrap();
    assert_eq!(a.line, b.line);
    assert!(b.chainage_m - a.chainage_m > 2.0e6 && b.chainage_m - a.chainage_m < 3.0e6, "{} km", (b.chainage_m - a.chainage_m) / 1e3);
    // A beaching run onto Reunion from the east.
    let h = c.first_crossing([56.0, -21.0], [55.6, -21.0]).unwrap();
    assert_eq!((h.segment, h.line), (1, reunion));
}
