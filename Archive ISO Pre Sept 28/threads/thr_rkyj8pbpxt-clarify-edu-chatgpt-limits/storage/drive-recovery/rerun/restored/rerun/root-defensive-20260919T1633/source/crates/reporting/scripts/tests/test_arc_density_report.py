"""Independent area/normalization checks for pooling saved flight estimates."""
import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arc_density_report import A_KM, E2, project, inverse, pool, area_grid, ranked_area, complexity_by_latitude


class ArcDensityControls(unittest.TestCase):
    def test_count_and_latitude_joint_probabilities(self):
        _,_,mass,joint,conditional=complexity_by_latitude(
            np.array([-35.2,-35.1,-32.5,-32.4]), np.array([.1,.3,.2,.4]), np.array([0,1,0,1]))
        nonempty=mass>0
        np.testing.assert_allclose(mass[nonempty],[.4,.6],atol=1e-14)
        np.testing.assert_allclose(joint[:,nonempty],[[.1,.2],[.3,.4]],atol=1e-14)
        np.testing.assert_allclose(conditional[:,nonempty],[[.25,1/3],[.75,2/3]],atol=1e-14)
        self.assertTrue(np.all(conditional[:,~nonempty] == 0))
        # A rare latitude bin must survive beside unit-scale probability.
        _,_,mass,joint,conditional=complexity_by_latitude(
            np.array([-35.,-10.]), np.array([1.,1e-20]), np.array([1,4]))
        self.assertEqual(mass[-1],1e-20)
        self.assertEqual(joint[4,-1],1e-20)
        self.assertEqual(conditional[4,-1],1.)

    def test_equal_area_against_ellipsoid_surface_element(self):
        # Independently calculated meridian radius × parallel radius, with
        # derivatives in radians, must equal the projection's area Jacobian.
        for lat in [-60., -35., 0., 40.]:
            eps=1e-6; degrees=np.rad2deg(eps)
            x1,y1=project(lat-degrees,90-degrees)
            x2,y2=project(lat+degrees,90+degrees)
            jacobian=(x2-x1)*(y2-y1)/(4*eps*eps)
            phi=np.deg2rad(lat)
            surface=A_KM**2*(1-E2)*np.cos(phi)/(1-E2*np.sin(phi)**2)**2
            self.assertAlmostEqual(jacobian/surface,1,places=8)
            x,y=project(lat,95.)
            recovered_lat,recovered_lon=inverse(x,y)
            self.assertAlmostEqual(float(recovered_lat),lat,places=10)
            self.assertAlmostEqual(float(recovered_lon),95.,places=10)

    def test_unnormalized_pool_and_cell_mass(self):
        # Two equal-effort raw-measure estimates [2,0] and [1,5] combine
        # directly to normalized [3,5]/8. Normalizing each first without its
        # evidence gives a different answer and must not pass this fixture.
        points=np.array([[-35.,90.],[-34.,91.]])
        runs=[{'summary':{'initial_particles':2,'log_evidence':np.log(1.)},
               'points':points,'weight':np.array([1.,0.])},
              {'summary':{'initial_particles':2,'log_evidence':np.log(3.)},
               'points':points,'weight':np.array([1/6,5/6])}]
        xy,w=pool(runs)
        self.assertAlmostEqual(float(w[xy[:,0]==-35].sum()),3/8,places=14)
        # The same eight raw contributions can instead be organized as runs
        # of sizes two and six, both with mean unnormalized mass one.
        unequal=[runs[0],dict(runs[1],summary={'initial_particles':6,'log_evidence':0.})]
        xy,weighted=pool(unequal)
        self.assertAlmostEqual(float(weighted[xy[:,0]==-35].sum()),3/8,places=14)
        lat,lon=inverse(np.array([2.5,7.5,2.5,7.5]),np.array([2.5,2.5,7.5,7.5]))
        _,_,mass=area_grid(np.c_[lat,lon],np.ones(4)/4,5)
        self.assertAlmostEqual(float((mass/25*25).sum()),1.,places=14)
        self.assertEqual(ranked_area(mass,5)['0.5']['area_km2'],50.)


if __name__=='__main__':unittest.main()
