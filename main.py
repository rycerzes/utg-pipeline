def main():
    from core.llm_client import LLMClient
    from core.build_manager import BuildManager

    llm_client = LLMClient()
    manager = BuildManager(llm_client)

    print("[utg-pipeline] Generating initial tests...")
    manager.generate_initial_tests()

    print("[utg-pipeline] Refining tests...")
    manager.refine_tests()

    print("[utg-pipeline] Building and debugging...")
    manager.build_and_debug()

    print("[utg-pipeline] Done.")


if __name__ == "__main__":
    main()
