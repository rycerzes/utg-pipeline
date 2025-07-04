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

    def build_and_debug(self):
        """Build the project with tests, handle build issues, and improve coverage."""
        # Placeholder: implement build, log collection, and LLM feedback loop
        pass

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
