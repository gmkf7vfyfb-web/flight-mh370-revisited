//! The source grid: a numerical device for evaluating the drift likelihood at many impact
//! samples (brief section 4). It is not a second sample set and not a smoothing assumption.
//!
//! The extent is DERIVED from an impact (or reference) posterior given as weighted cells, at a
//! configurable coverage level (brief section 5): cells are ranked by density per unit area and
//! taken until the coverage is reached (a highest-density region), then every grid node within
//! `margin_nm` of a selected cell is a release node. Connected groups of nodes are components;
//! the one carrying most posterior mass is the main band, the others are islands (the detached
//! northern mode), released only when `include_island` is set and labelled as a sensitivity.
//! The posterior decides WHERE nodes go, never what the likelihood is worth.

const NM_PER_DEG: f64 = 60.0;

#[derive(Debug, Clone, Copy)]
pub struct WeightedCell {
    pub lat: f64,
    pub lon: f64,
    pub mass: f64,
}

#[derive(Debug, Clone)]
pub struct SourceGrid {
    pub lat0: f64,
    pub lon0: f64,
    pub dlat: f64,
    pub dlon: f64,
    pub nlat: usize,
    pub nlon: usize,
    pub spacing_nm: f64,
    /// Release node (main band, plus islands when included).
    pub active: Vec<bool>,
    /// Component index per node (-1 outside the support).
    #[cfg_attr(not(test), allow(dead_code))]
    pub component: Vec<i32>,
    /// Posterior mass inside the coverage region attributed to each component.
    pub component_mass: Vec<f64>,
    pub main_component: usize,
    /// Mass actually covered by the selected highest-density cells.
    pub covered_mass: f64,
}

impl SourceGrid {
    pub fn index(&self, i: usize, j: usize) -> usize {
        i * self.nlon + j
    }
    pub fn node(&self, k: usize) -> (f64, f64) {
        let (i, j) = (k / self.nlon, k % self.nlon);
        (self.lat0 + i as f64 * self.dlat, self.lon0 + j as f64 * self.dlon)
    }
    pub fn n_active(&self) -> usize {
        self.active.iter().filter(|a| **a).count()
    }
    #[cfg_attr(not(test), allow(dead_code))]
    pub fn component_nodes(&self, c: usize) -> usize {
        self.component.iter().filter(|&&x| x == c as i32).count()
    }

    /// `cell_deg` is the side of the input cells; `coverage` in (0, 1].
    pub fn from_posterior(cells: &[WeightedCell], cell_deg: f64, coverage: f64, spacing_nm: f64, margin_nm: f64, include_island: bool) -> Result<SourceGrid, String> {
        if !(coverage > 0.0 && coverage <= 1.0) || spacing_nm <= 0.0 || margin_nm < 0.0 {
            return Err(format!("source grid: bad coverage {coverage}, spacing {spacing_nm} or margin {margin_nm}"));
        }
        let total: f64 = cells.iter().map(|c| c.mass).sum();
        if !(total > 0.0) {
            return Err("source grid: posterior has no mass".into());
        }
        // Highest-density region by density per unit area (cells are equal in degrees).
        let mut order: Vec<usize> = (0..cells.len()).filter(|&k| cells[k].mass > 0.0).collect();
        let dens = |c: &WeightedCell| c.mass / c.lat.to_radians().cos();
        order.sort_by(|&a, &b| dens(&cells[b]).partial_cmp(&dens(&cells[a])).unwrap());
        let mut sel = Vec::new();
        let mut cum = 0.0;
        for &k in &order {
            if cum >= coverage * total {
                break;
            }
            cum += cells[k].mass;
            sel.push(k);
        }
        let half = 0.5 * cell_deg;
        let lat_min = sel.iter().map(|&k| cells[k].lat).fold(f64::INFINITY, f64::min) - half;
        let lat_max = sel.iter().map(|&k| cells[k].lat).fold(f64::NEG_INFINITY, f64::max) + half;
        let lon_min = sel.iter().map(|&k| cells[k].lon).fold(f64::INFINITY, f64::min) - half;
        let lon_max = sel.iter().map(|&k| cells[k].lon).fold(f64::NEG_INFINITY, f64::max) + half;
        let mid = 0.5 * (lat_min + lat_max);
        let dlat = spacing_nm / NM_PER_DEG;
        let dlon = spacing_nm / (NM_PER_DEG * mid.to_radians().cos());
        let pad_lat = margin_nm / NM_PER_DEG + dlat;
        let pad_lon = margin_nm / (NM_PER_DEG * mid.to_radians().cos()) + dlon;
        let lat0 = lat_min - pad_lat;
        let lon0 = lon_min - pad_lon;
        let nlat = ((lat_max + pad_lat - lat0) / dlat).ceil() as usize + 1;
        let nlon = ((lon_max + pad_lon - lon0) / dlon).ceil() as usize + 1;
        let mut support = vec![false; nlat * nlon];
        let mut owner = vec![usize::MAX; sel.len()];
        // A node is in the support if it lies within margin of the selected cell (distance from
        // the node to the cell rectangle, in NM).
        for (s, &k) in sel.iter().enumerate() {
            let c = &cells[k];
            let cosl = c.lat.to_radians().cos();
            let reach_lat = half + margin_nm / NM_PER_DEG;
            let reach_lon = half + margin_nm / (NM_PER_DEG * cosl);
            let i_lo = (((c.lat - reach_lat - lat0) / dlat).floor().max(0.0)) as usize;
            let i_hi = (((c.lat + reach_lat - lat0) / dlat).ceil() as usize).min(nlat - 1);
            let j_lo = (((c.lon - reach_lon - lon0) / dlon).floor().max(0.0)) as usize;
            let j_hi = (((c.lon + reach_lon - lon0) / dlon).ceil() as usize).min(nlon - 1);
            let mut best = (f64::INFINITY, usize::MAX);
            for i in i_lo..=i_hi {
                for j in j_lo..=j_hi {
                    let (la, lo) = (lat0 + i as f64 * dlat, lon0 + j as f64 * dlon);
                    let dy = ((la - c.lat).abs() - half).max(0.0) * NM_PER_DEG;
                    let dx = ((lo - c.lon).abs() - half).max(0.0) * NM_PER_DEG * cosl;
                    let d = (dx * dx + dy * dy).sqrt();
                    if d <= margin_nm + 1e-9 {
                        support[i * nlon + j] = true;
                    }
                    let dc = ((la - c.lat) * NM_PER_DEG).hypot((lo - c.lon) * NM_PER_DEG * cosl);
                    if dc < best.0 {
                        best = (dc, i * nlon + j);
                    }
                }
            }
            support[best.1] = true;
            owner[s] = best.1;
        }
        // 4-connected components.
        let mut component = vec![-1_i32; nlat * nlon];
        let mut ncomp = 0;
        for start in 0..support.len() {
            if !support[start] || component[start] >= 0 {
                continue;
            }
            let mut stack = vec![start];
            component[start] = ncomp;
            while let Some(k) = stack.pop() {
                let (i, j) = (k / nlon, k % nlon);
                let mut nb = Vec::with_capacity(4);
                if i > 0 { nb.push(k - nlon); }
                if i + 1 < nlat { nb.push(k + nlon); }
                if j > 0 { nb.push(k - 1); }
                if j + 1 < nlon { nb.push(k + 1); }
                for n in nb {
                    if support[n] && component[n] < 0 {
                        component[n] = ncomp;
                        stack.push(n);
                    }
                }
            }
            ncomp += 1;
        }
        let mut component_mass = vec![0.0; ncomp as usize];
        for (s, &k) in sel.iter().enumerate() {
            component_mass[component[owner[s]] as usize] += cells[k].mass / total;
        }
        let main_component = (0..component_mass.len())
            .max_by(|&a, &b| component_mass[a].partial_cmp(&component_mass[b]).unwrap())
            .unwrap();
        let active = component
            .iter()
            .map(|&c| c >= 0 && (c as usize == main_component || include_island))
            .collect();
        Ok(SourceGrid { lat0, lon0, dlat, dlon, nlat, nlon, spacing_nm, active, component, component_mass, main_component, covered_mass: cum / total })
    }

    /// A rectangular grid with every node active (tests and synthetic studies).
    #[cfg_attr(not(test), allow(dead_code))]
    pub fn rectangle(lat0: f64, lon0: f64, nlat: usize, nlon: usize, spacing_nm: f64) -> SourceGrid {
        let dlat = spacing_nm / NM_PER_DEG;
        let dlon = spacing_nm / (NM_PER_DEG * (lat0 + 0.5 * dlat * (nlat as f64 - 1.0)).to_radians().cos());
        let n = nlat * nlon;
        SourceGrid { lat0, lon0, dlat, dlon, nlat, nlon, spacing_nm, active: vec![true; n], component: vec![0; n], component_mass: vec![1.0], main_component: 0, covered_mass: 1.0 }
    }
}
