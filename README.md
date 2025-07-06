# UTG Pipeline with Google Test

This project is an automated pipeline for generating **Google Test** unit tests for a C++ project. It leverages a Large Language Model (LLM) to create, refine, and debug test cases iteratively. The system is designed to be model-agnostic by using the **`litellm` library**, allowing it to connect to various LLM providers like **OpenAI**, **Anthropic**, or **Google**.

---

## How it Works

The pipeline's core is an iterative, prompt-driven workflow that generates C++ code for the Google Test framework.

The `BuildManager` orchestrates the process:

1.  **Initial Test Generation**: The pipeline first analyzes the source code in `cpp-project/`. It then instructs the LLM to generate an initial set of tests using the `prompts/initial_generation.yaml` template. The `LLMClient` sends this request to the configured LLM provider. The returned C++ code, formatted for a Google Test suite, is then saved as a new `.cc` file inside the `tests/` directory.

2.  **Iterative Build and Debug Cycle**: This is the central loop of the pipeline.
    * **Build**: The pipeline attempts to compile the newly created Google Test file (`tests/test_main.cc`) along with the original C++ project source.
    * **Debug**: If the compilation fails, the compiler errors are captured. These errors are then fed back to the LLM using the `prompts/build_fix.yaml` prompt. The LLM is asked to correct the Google Test code it previously wrote, and the build-and-debug cycle repeats until compilation is successful.

3.  **Test Refinement**: Once the tests build successfully, the `prompts/refinement.yaml` template can be used to ask the LLM to improve the quality, add more assertions, or handle edge cases within the generated Google Test suite.

---

## Test Coverage

Test coverage is a critical metric used to evaluate the effectiveness of the generated Google Test suite.

* **Measurement**: The C++ project is compiled with **gcov-style instrumentation flags**. This produces `.gcno` files, which are used to track code execution. After the compiled tests are run, a coverage report is generated.
* **Analysis**: The `CoverageAnalyzer` module processes this report to determine which lines of the source code were exercised by the Google Tests. This data provides a clear metric of the test suite's quality and can be used to guide further refinement, such as prompting the LLM to write tests for uncovered functions or branches.