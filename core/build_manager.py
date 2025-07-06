import os
from pathlib import Path
from utils.project_scanner import scan_cpp_files
from utils.file_handler import read_file, write_file
from core.llm_client import LLMClient

PROMPT_DIR = Path(__file__).parent.parent / "prompts"
CPP_PROJECT_DIR = Path(__file__).parent.parent / "cpp-project"
TESTS_DIR = Path(__file__).parent.parent / "tests"

class BuildManager:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.cpp_files = scan_cpp_files(CPP_PROJECT_DIR)
        TESTS_DIR.mkdir(exist_ok=True)

    def generate_initial_tests(self):
        """Generate initial unit tests for each C++ file using the LLM."""
        prompt_path = PROMPT_DIR / "initial_generation.yaml"
        for cpp_file in self.cpp_files:
            code = read_file(cpp_file)
            prompt = self._load_yaml_prompt(prompt_path)
            test_code = self.llm.generate_tests(code, prompt)
            test_file = TESTS_DIR / f"test_{cpp_file.stem}.cc"
            write_file(test_file, test_code)

    def refine_tests(self):
        """Refine generated tests using the LLM."""
        prompt_path = PROMPT_DIR / "refinement.yaml"
        for test_file in TESTS_DIR.glob("test_*.cc"):
            test_code = read_file(test_file)
            prompt = self._load_yaml_prompt(prompt_path)
            refined_code = self.llm.refine_tests(test_code, prompt)
            write_file(test_file, refined_code)

    def build_and_debug(self, max_iterations=10):
        """Continuously build, test, and apply LLM fixes until all tests pass or max_iterations is reached."""
        import subprocess
        from core.coverage_analyzer import CoverageAnalyzer
        import shutil
        import sys
        
        for iteration in range(max_iterations):
            print(f"[utg-pipeline] === Iteration {iteration+1} ===")
            # 1. Build all .cc files in cpp-project and tests into a single test binary with coverage flags
            cpp_files = list((CPP_PROJECT_DIR).glob("*.cc"))
            test_files = list((TESTS_DIR).glob("test_*.cc"))
            all_sources = cpp_files + test_files
            binary_path = TESTS_DIR / "test_all"
            compile_cmd = [
                "g++", "-std=c++17", "-fprofile-arcs", "-ftest-coverage", "-lgtest", "-lgtest_main", "-pthread",
                "-o", str(binary_path)
            ] + [str(f) for f in all_sources]
            print(f"[utg-pipeline] Compiling: {' '.join(compile_cmd)}")
            try:
                result = subprocess.run(compile_cmd, capture_output=True, text=True)
            except Exception as e:
                print(f"[utg-pipeline] Build failed: {e}")
                return
            if result.returncode != 0:
                print("[utg-pipeline] Build failed. Error log:")
                print(result.stderr)
                # Feed build log to LLM for fix suggestions
                self._handle_build_failure(result.stderr, all_sources)
                continue
            print("[utg-pipeline] Build succeeded.")

            # 2. Run the test binary
            print(f"[utg-pipeline] Running tests: {binary_path}")
            test_proc = subprocess.run([str(binary_path)], capture_output=True, text=True)
            print("[utg-pipeline] Test output:")
            print(test_proc.stdout)
            if test_proc.returncode != 0:
                print("[utg-pipeline] Test failures detected. Error log:")
                print(test_proc.stderr)
                # Feed test log to LLM for test refinement
                self._handle_test_failure(test_proc.stdout + "\n" + test_proc.stderr)
                continue

            # 3. Run coverage analysis
            print("[utg-pipeline] Running coverage analysis...")
            cov = CoverageAnalyzer(build_dir=TESTS_DIR, tests_dir=TESTS_DIR)
            try:
                coverage_summary = cov.run_coverage()
                print("[utg-pipeline] Coverage summary:")
                print(coverage_summary)
            except Exception as e:
                print(f"[utg-pipeline] Coverage analysis failed: {e}")
                coverage_summary = None

            # 4. Optionally, feed coverage summary to LLM for further test refinement
            if coverage_summary:
                self._handle_coverage_feedback(coverage_summary)

            print("[utg-pipeline] All tests passed. Exiting loop.")
            break
        else:
            print("[utg-pipeline] Max iterations reached. Some issues may remain.")

    def _handle_build_failure(self, build_log, sources):
        """Feed build log and code to LLM for fix suggestions."""
        prompt_path = PROMPT_DIR / "build_fix.yaml"
        prompt = self._load_yaml_prompt(prompt_path)
        code_blobs = "\n\n".join([read_file(f) for f in sources])
        feedback = f"Build log:\n{build_log}\n\nCode:\n{code_blobs}"
        suggestions = self.llm.refine_tests(feedback, prompt)
        print("[utg-pipeline] LLM build fix suggestions:")
        print(suggestions)

    def _handle_test_failure(self, test_log):
        """Feed test log to LLM for test refinement."""
        prompt_path = PROMPT_DIR / "refinement.yaml"
        prompt = self._load_yaml_prompt(prompt_path)
        # For each test file, ask LLM to refine
        for test_file in TESTS_DIR.glob("test_*.cc"):
            test_code = read_file(test_file)
            feedback = f"Test log:\n{test_log}\n\nTest code:\n{test_code}"
            refined_code = self.llm.refine_tests(feedback, prompt)
            write_file(test_file, refined_code)
        print("[utg-pipeline] Tests refined by LLM.")

    def _handle_coverage_feedback(self, coverage_summary):
        """Feed coverage summary to LLM for test improvement."""
        prompt_path = PROMPT_DIR / "refinement.yaml"
        prompt = self._load_yaml_prompt(prompt_path)
        for test_file in TESTS_DIR.glob("test_*.cc"):
            test_code = read_file(test_file)
            feedback = f"Coverage summary:\n{coverage_summary}\n\nTest code:\n{test_code}"
            refined_code = self.llm.refine_tests(feedback, prompt)
            write_file(test_file, refined_code)
        print("[utg-pipeline] Tests refined based on coverage feedback.")

    def _load_yaml_prompt(self, path):
        import yaml
        with open(path, 'r') as f:
            return yaml.safe_load(f)

# Example usage (to be called from main.py):
# from core.llm_client import LLMClient
# manager = BuildManager(LLMClient())
# manager.generate_initial_tests()
# manager.refine_tests()
# manager.build_and_debug()
