import subprocess
from pathlib import Path
import os

class CoverageAnalyzer:
    def __init__(self, build_dir, tests_dir):
        self.build_dir = Path(build_dir)
        self.tests_dir = Path(tests_dir)

    def run_coverage(self):
        """
        Run tests and collect coverage using gcov/lcov. Returns coverage summary as string.
        Assumes the project is built with coverage flags.
        """
        # Run tests
        test_binaries = list(self.tests_dir.glob("test_*"))
        results = []
        for test_bin in test_binaries:
            if test_bin.is_file() and os.access(test_bin, os.X_OK):
                proc = subprocess.run([str(test_bin)], capture_output=True, text=True)
                results.append(proc.stdout)

        # Run lcov to collect coverage
        lcov_info = self.build_dir / "coverage.info"
        subprocess.run(["lcov", "--capture", "--directory", str(self.build_dir), "--output-file", str(lcov_info)], check=True)
        # Generate summary
        summary = subprocess.run(["lcov", "--summary", str(lcov_info)], capture_output=True, text=True)
        return summary.stdout
