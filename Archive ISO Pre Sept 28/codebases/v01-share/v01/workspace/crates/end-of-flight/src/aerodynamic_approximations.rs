//! Named B772 attached-flow approximations for conditional release sensitivities.
//!
//! Neither family is a calibrated B777-200ER terminal-flight model.  They expose the two
//! independently audited public OpenAP parabolic polars as mutually exclusive conditionals;
//! they are never averaged or described as post-stall data.

use serde::{Deserialize, Serialize};

use crate::{AerodynamicModel, Degrees, MetresPerSecond, SquareMetres};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ConditionalB772AerodynamicFamily {
    OpenapV2_6_0AttachedFlow,
    OpenapPublished2020AttachedFlow,
}

impl ConditionalB772AerodynamicFamily {
    pub const fn evidence_status(self) -> &'static str {
        "conditional_attached_flow_proxy_not_b777_terminal_calibration"
    }

    pub fn model(self) -> AerodynamicModel {
        let (zero_lift_drag_coefficient, induced_drag_factor) = match self {
            Self::OpenapV2_6_0AttachedFlow => (0.024, 0.047),
            Self::OpenapPublished2020AttachedFlow => (0.034, 0.051),
        };
        AerodynamicModel {
            reference_area: SquareMetres(427.8),
            zero_lift_drag_coefficient,
            induced_drag_factor,
            // These wide limits are numerical bounds only. The selected release commands stay
            // inside attached-flow values; neither limit is asserted as a B777 stall coefficient.
            minimum_lift_coefficient: -1.5,
            maximum_lift_coefficient: 1.5,
            maximum_bank_angle: Degrees(60.0),
            minimum_true_airspeed: MetresPerSecond(50.0),
            maximum_true_airspeed: MetresPerSecond(700.0),
        }
    }

    pub fn parabolic_best_lift_to_drag(self) -> f64 {
        let model = self.model();
        1.0 / (4.0 * model.zero_lift_drag_coefficient * model.induced_drag_factor).sqrt()
    }

    pub fn parabolic_best_glide_lift_coefficient(self) -> f64 {
        let model = self.model();
        (model.zero_lift_drag_coefficient / model.induced_drag_factor).sqrt()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn audited_public_polar_comparators_are_exact_and_separate() {
        let current = ConditionalB772AerodynamicFamily::OpenapV2_6_0AttachedFlow;
        let published = ConditionalB772AerodynamicFamily::OpenapPublished2020AttachedFlow;
        assert!((current.parabolic_best_lift_to_drag() - 14.887_283_354).abs() < 1.0e-8);
        assert!((published.parabolic_best_lift_to_drag() - 12.007_302_661).abs() < 1.0e-8);
        assert_ne!(current.model(), published.model());
        assert!(current.parabolic_best_glide_lift_coefficient() < 1.0);
        assert!(published.parabolic_best_glide_lift_coefficient() < 1.0);
    }
}
