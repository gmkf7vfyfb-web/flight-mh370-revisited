#!/usr/bin/env python3
"""External-asset fixture tests for the native PHaRLAP IRI2020 helper."""

from __future__ import annotations

import ctypes
import json
import math
import os
from pathlib import Path
import subprocess
import unittest


ARCHIVE_SHA256 = "76064dc26d638918c65bed977f9581b0c64bc5dfbdd1f6d3c6bb3758f1d9e400"
DATA_MANIFEST_SHA256 = "5da7f44900ffb7855beb3673fae61bb632e652f83971f5b887d18ef08a7534c7"


class IriRequest(ctypes.Structure):
    _fields_ = [
        ("latitude_deg", ctypes.c_double),
        ("longitude_deg", ctypes.c_double),
        ("year", ctypes.c_int32),
        ("month", ctypes.c_int32),
        ("day", ctypes.c_int32),
        ("hour", ctypes.c_int32),
        ("minute", ctypes.c_int32),
        ("second", ctypes.c_double),
        ("height_start_km", ctypes.c_double),
        ("height_step_km", ctypes.c_double),
        ("height_count", ctypes.c_int32),
        ("r12", ctypes.c_double),
    ]


def external_paths() -> tuple[Path, Path, Path] | None:
    home_text = os.environ.get("PHARLAP_HOME")
    cli_text = os.environ.get("PHARLAP_IRI2020_CLI")
    library_text = os.environ.get("PHARLAP_IRI2020_LIBRARY")
    if not home_text or not cli_text or not library_text:
        return None
    paths = (Path(home_text), Path(cli_text), Path(library_text))
    if not all(path.exists() for path in paths):
        return None
    return paths


@unittest.skipUnless(
    external_paths() is not None,
    "set PHARLAP_HOME, PHARLAP_IRI2020_CLI, and PHARLAP_IRI2020_LIBRARY",
)
class PharlapIri2020Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        paths = external_paths()
        assert paths is not None
        cls.pharlap_home, cls.cli, cls.library_path = paths

    def base_command(self, utc: str = "2014-03-08T00:00:00Z") -> list[str]:
        return [
            str(self.cli),
            "--lat-deg",
            "-30",
            "--lon-deg",
            "90",
            "--utc",
            utc,
            "--height-start-km",
            "100",
            "--height-step-km",
            "10",
            "--height-count",
            "41",
            "--data-root",
            str(self.pharlap_home / "dat"),
        ]

    def run_profile(self) -> dict:
        completed = subprocess.run(
            self.base_command(),
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout)

    def assert_relative(self, actual: float, expected: float) -> None:
        self.assertTrue(math.isfinite(actual))
        self.assertAlmostEqual(actual, expected, delta=abs(expected) * 3e-6)

    def test_help_uses_real_line_breaks(self) -> None:
        completed = subprocess.run(
            [str(self.cli), "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertGreater(len(completed.stdout.splitlines()), 3)
        self.assertNotIn(r"\n", completed.stdout)

    def test_historical_profile_matches_verified_fixture(self) -> None:
        result = self.run_profile()
        density = result["profiles"]["electron_density_m3"]
        extra = result["iono_extra"]

        self.assertEqual(result["schema"], "pharlap-iri2020-profile-v1")
        self.assertEqual(result["input"]["r12"], -1)
        self.assertEqual(
            result["input"]["r12_mode"], "historical_or_projected_indices"
        )
        self.assertEqual(len(result["profiles"]), 16)
        self.assertEqual(len(density), 41)
        self.assertEqual(result["profiles"]["height_km"][20], 300)
        self.assert_relative(density[0], 2.19484549e10)
        self.assert_relative(density[20], 2.73383801e11)
        self.assert_relative(density[40], 8.28074230e10)
        self.assert_relative(extra[0], 2.82978517e11)
        self.assert_relative(extra[1], 275.058929)
        fof2_mhz = 8.98e-6 * math.sqrt(extra[0])
        self.assert_relative(fof2_mhz, 4.77697611)

    def test_output_records_external_dependency_identity(self) -> None:
        metadata = self.run_profile()["metadata"]
        self.assertEqual(metadata["pharlap_release"], "4.7.4")
        self.assertEqual(metadata["libiri2020_sha256"], ARCHIVE_SHA256)
        self.assertEqual(metadata["iri_data_manifest_sha256"], DATA_MANIFEST_SHA256)
        self.assertEqual(
            Path(metadata["data_root"]).resolve(),
            (self.pharlap_home / "dat").resolve(),
        )

    def test_out_of_coverage_date_is_rejected_before_model_call(self) -> None:
        completed = subprocess.run(
            self.base_command("1900-01-01T00:00:00Z"),
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "")
        self.assertIn("coverage", completed.stderr)

    def test_shared_library_batch_abi(self) -> None:
        library = ctypes.CDLL(str(self.library_path))
        library.pharlap_iri2020_set_data_root.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        library.pharlap_iri2020_set_data_root.restype = ctypes.c_int
        library.pharlap_iri2020_profiles.argtypes = [
            ctypes.POINTER(IriRequest),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
        ]
        library.pharlap_iri2020_profiles.restype = ctypes.c_int

        error = ctypes.create_string_buffer(512)
        status = library.pharlap_iri2020_set_data_root(
            os.fsencode(self.pharlap_home / "dat"), error, len(error)
        )
        self.assertEqual(status, 0, error.value.decode())

        requests = (IriRequest * 2)(
            IriRequest(-30.0, 90.0, 2014, 3, 8, 0, 0, 0.0, 100.0, 10.0, 41, -1.0),
            IriRequest(-28.0, 92.0, 2014, 3, 8, 0, 0, 0.0, 100.0, 10.0, 41, -1.0),
        )
        profile_stride = 15 * 41
        extra_stride = 100
        profiles = (ctypes.c_float * (2 * profile_stride))()
        extras = (ctypes.c_float * (2 * extra_stride))()
        failed_request = ctypes.c_size_t(0)
        status = library.pharlap_iri2020_profiles(
            requests,
            2,
            profiles,
            profile_stride,
            len(profiles),
            extras,
            extra_stride,
            len(extras),
            ctypes.byref(failed_request),
            error,
            len(error),
        )
        self.assertEqual(status, 0, error.value.decode())
        self.assertEqual(failed_request.value, ctypes.c_size_t(-1).value)
        self.assert_relative(profiles[20], 2.73383801e11)
        self.assertNotEqual(profiles[20], profiles[profile_stride + 20])
        self.assert_relative(extras[0], 2.82978517e11)


if __name__ == "__main__":
    unittest.main()
