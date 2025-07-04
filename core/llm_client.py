
from litellm import completion

class LLMClient:
    def __init__(self, model_name="qwen2.5-coder", api_base="http://172.21.0.3:11434"):
        """
        model_name: the base model name, e.g. 'llama2', 'codellama', etc.
        api_base: the Ollama server URL.
        """
        self.model_name = model_name
        self.api_base = api_base

    def generate_tests(self, code, prompt):
        """
        Send C++ code and YAML prompt to the LLM to generate unit tests.
        Returns the generated test code as a string.
        """
        messages = [
            {"role": "system", "content": str(prompt)},
            {"role": "user", "content": code}
        ]
        response = completion(
            model=f"ollama_chat/{self.model_name}",
            messages=messages,
            api_base=self.api_base
        )
        return response["choices"][0]["message"]["content"]

    def refine_tests(self, test_code, prompt):
        """
        Send generated test code and YAML prompt to the LLM for refinement.
        Returns the refined test code as a string.
        """
        messages = [
            {"role": "system", "content": str(prompt)},
            {"role": "user", "content": test_code}
        ]
        response = completion(
            model=f"ollama_chat/{self.model_name}",
            messages=messages,
            api_base=self.api_base
        )
        return response["choices"][0]["message"]["content"]
