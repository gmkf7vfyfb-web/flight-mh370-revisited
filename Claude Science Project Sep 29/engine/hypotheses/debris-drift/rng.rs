//! Deterministic random numbers for this module (the hypothesis crate may not depend on `rand`).
//! xoshiro256** seeded through SplitMix64; normals by Box-Muller. Every ensemble derives its own
//! stream from (seed, node, case), so results do not depend on evaluation order or thread count.

pub struct Rng {
    s: [u64; 4],
}

fn splitmix(z: &mut u64) -> u64 {
    *z = z.wrapping_add(0x9E37_79B9_7F4A_7C15);
    let mut y = *z;
    y = (y ^ (y >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
    y = (y ^ (y >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
    y ^ (y >> 31)
}

impl Rng {
    pub fn new(seed: u64) -> Self {
        let mut z = seed;
        Rng { s: [splitmix(&mut z), splitmix(&mut z), splitmix(&mut z), splitmix(&mut z)] }
    }

    /// An independent stream for a tuple of identifiers.
    pub fn derive(parts: &[u64]) -> Self {
        let mut z = 0x243F_6A88_85A3_08D3_u64;
        let mut h = 0_u64;
        for &p in parts {
            z ^= p;
            h ^= splitmix(&mut z);
        }
        Rng::new(h)
    }

    pub fn next_u64(&mut self) -> u64 {
        let r = self.s[1].wrapping_mul(5).rotate_left(7).wrapping_mul(9);
        let t = self.s[1] << 17;
        self.s[2] ^= self.s[0];
        self.s[3] ^= self.s[1];
        self.s[1] ^= self.s[2];
        self.s[0] ^= self.s[3];
        self.s[2] ^= t;
        self.s[3] = self.s[3].rotate_left(45);
        r
    }

    /// Uniform on [0, 1).
    pub fn uniform(&mut self) -> f64 {
        (self.next_u64() >> 11) as f64 * (1.0 / (1_u64 << 53) as f64)
    }

    pub fn normal(&mut self) -> f64 {
        loop {
            let u1 = self.uniform();
            if u1 > 0.0 {
                let u2 = self.uniform();
                return (-2.0 * u1.ln()).sqrt() * (std::f64::consts::TAU * u2).cos();
            }
        }
    }
}
