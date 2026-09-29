#!/usr/bin/env python3
"""Synthetic fixture for the native PHaRLAP spherical 2-D ray boundary."""

from __future__ import annotations

import ctypes
import math
import os
from pathlib import Path
import unittest


PROPAGATION_SHA256 = "f33616ee1ea695ab424b98a9ab5f6d9a8e0daf664d81f2822351788d40e627eb"
MATHS_SHA256 = "b5a894dd80b206c0e2d22f9ff543da398276135b278918de16ec2a7a76753eb3"
MAX_POINTS = 20_000
HOP_FIELDS = 22
PATH_FIELDS = 9


class RaySettings(ctypes.Structure):
    _fields_ = [
        ("bearing_deg", ctypes.c_double),
        ("earth_radius_km", ctypes.c_double),
        ("hop_count", ctypes.c_int32),
        ("tolerance", ctypes.c_double),
        ("minimum_step_km", ctypes.c_double),
        ("maximum_step_km", ctypes.c_double),
    ]


def library_path() -> Path | None:
    text = os.environ.get("PHARLAP_RAYTRACE_2D_SP_LIBRARY")
    if not text:
        return None
    path = Path(text)
    return path if path.exists() else None


@unittest.skipUnless(
    library_path() is not None,
    "set PHARLAP_RAYTRACE_2D_SP_LIBRARY to the built shared library",
)
class PharlapSphericalRaytraceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        path = library_path()
        assert path is not None
        cls.library = ctypes.CDLL(str(path))
        cls.library.pharlap_raytrace_2d_sp_set_ionosphere.argtypes = [
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        cls.library.pharlap_raytrace_2d_sp_set_ionosphere.restype = ctypes.c_int
        cls.library.pharlap_raytrace_2d_sp_trace.argtypes = [
            ctypes.POINTER(RaySettings),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_int32),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_int32),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_int32),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        cls.library.pharlap_raytrace_2d_sp_trace.restype = ctypes.c_int
        cls.library.pharlap_raytrace_2d_sp_clear_ionosphere.argtypes = []
        cls.library.pharlap_raytrace_2d_sp_propagation_archive_sha256.restype = (
            ctypes.c_char_p
        )
        cls.library.pharlap_raytrace_2d_sp_maths_archive_sha256.restype = (
            ctypes.c_char_p
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.library.pharlap_raytrace_2d_sp_clear_ionosphere()

    def setUp(self) -> None:
        self.range_count = 201
        self.height_count = 201
        value_count = self.range_count * self.height_count
        density = (ctypes.c_double * value_count)()
        for range_index in range(self.range_count):
            for height_index in range(self.height_count):
                height_km = 3.0 * height_index
                z = (height_km - 300.0) / 75.0
                density[range_index * self.height_count + height_index] = (
                    0.0 if height_km < 80.0 else 1.25e6 * math.exp(-(z * z))
                )
        error = ctypes.create_string_buffer(512)
        status = self.library.pharlap_raytrace_2d_sp_set_ionosphere(
            self.range_count,
            self.height_count,
            0.0,
            3.0,
            50.0,
            density,
            value_count,
            None,
            0,
            None,
            0,
            error,
            len(error),
        )
        self.assertEqual(status, 0, error.value.decode())

    def trace(self, bearing_deg: float) -> tuple[list[float], list[float], int, int]:
        settings = RaySettings(bearing_deg, 6371.2, 1, 1e-7, 0.025, 25.0)
        elevations = (ctypes.c_double * 1)(20.0)
        frequencies = (ctypes.c_double * 1)(10.0)
        hop_data = (ctypes.c_double * HOP_FIELDS)()
        labels = (ctypes.c_int32 * 1)()
        hops_attempted = (ctypes.c_int32 * 1)()
        path_data = (ctypes.c_double * (PATH_FIELDS * MAX_POINTS))()
        points = (ctypes.c_int32 * 1)()
        elapsed = ctypes.c_double()
        error = ctypes.create_string_buffer(512)
        status = self.library.pharlap_raytrace_2d_sp_trace(
            ctypes.byref(settings),
            1,
            elevations,
            1,
            frequencies,
            1,
            hop_data,
            len(hop_data),
            labels,
            len(labels),
            hops_attempted,
            len(hops_attempted),
            path_data,
            len(path_data),
            points,
            len(points),
            ctypes.byref(elapsed),
            error,
            len(error),
        )
        self.assertEqual(status, 0, error.value.decode())
        return list(hop_data), list(path_data), labels[0], points[0]

    def assert_relative(self, actual: float, expected: float) -> None:
        self.assertTrue(math.isfinite(actual))
        self.assertAlmostEqual(actual, expected, delta=abs(expected) * 3e-10)

    def assert_same_numeric_sequence(
        self, first: list[float], second: list[float]
    ) -> None:
        self.assertEqual(len(first), len(second))
        for first_value, second_value in zip(first, second, strict=True):
            if math.isnan(first_value) and math.isnan(second_value):
                continue
            self.assertEqual(first_value, second_value)

    def test_synthetic_ground_return_and_native_layout(self) -> None:
        hop, path, label, points = self.trace(324.7)
        self.assertEqual(label, 1)
        self.assertEqual(points, 80)
        self.assert_relative(hop[2], 1124.9340929149112)
        self.assert_relative(hop[3], 1238.5893823864571)
        self.assert_relative(hop[4], 199.77471243063155)
        self.assert_relative(hop[10], 1216.7201738709118)
        self.assert_relative(hop[13], 4.1104155592089873)
        terminal_base = (points - 1) * PATH_FIELDS
        self.assert_relative(path[terminal_base], hop[2])
        self.assertEqual(path[terminal_base + 1], 0.0)

    def test_bearing_does_not_change_path_when_irregularities_are_off(self) -> None:
        first_hop, first_path, first_label, first_points = self.trace(0.0)
        second_hop, second_path, second_label, second_points = self.trace(217.0)
        self.assertEqual((first_label, first_points), (second_label, second_points))
        self.assert_same_numeric_sequence(first_hop, second_hop)
        self.assert_same_numeric_sequence(
            first_path[: first_points * PATH_FIELDS],
            second_path[: second_points * PATH_FIELDS],
        )

    def test_archive_identities(self) -> None:
        self.assertEqual(
            self.library.pharlap_raytrace_2d_sp_propagation_archive_sha256()
            .decode(),
            PROPAGATION_SHA256,
        )
        self.assertEqual(
            self.library.pharlap_raytrace_2d_sp_maths_archive_sha256().decode(),
            MATHS_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
