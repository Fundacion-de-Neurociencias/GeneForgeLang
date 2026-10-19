# F002 verification feedback 1 (2026-10-19)

Verdict: FAIL at 17fd3e5. Evidence: `.autodev/evidence/F002/verdict.json`.

The contract checks D1-D10 hold: tests, lint, D8 on origin/main, cffconvert, DOI, AST and smoke run. The FAIL is rubric G8.2 / QB-8: README.md, the main file this feature cleans, still states things without evidence.

1. **Plugin System example does not run (blocking).**
   - Did: `hasattr(geneforgelang.plugins, "BasePlugin")` and `hasattr(geneforgelang.plugins, "register_plugin")` in the project venv.
   - Expected: the example works, or carries `<!-- does not run yet: F010 -->` like the Quick Start block.
   - Got: both False. The base class is `BaseGFLPlugin` (`src/geneforgelang/plugins/base.py:7`); `register_plugin` is in `src/geneforgelang/plugins/plugin_registry.py:1002`. The block is unmarked.
   - Fix: mark it or rewrite it against the real API. Widen `test_readme_python_block_is_honest` so every python block importing from `geneforgelang` is either marked or has importable names.
2. **Dead links advertised as resources (blocking).**
   - Did: `curl -L` on the README Support links.
   - Got: `https://geneforgelang.readthedocs.io` 404 ("Comprehensive guides"); `https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/discussions` 404 ("Community support"). Issues returns 200.
   - Fix: remove both or point to existing pages (docs/index.md, Issues).
3. **Non-blocking.** `examples/real_project/Manuscript_GeneForge_v2_Beta.md:14` keeps "revolutionary" and "two comprehensive real-world applications executed on the GeneForge WebApp", which its own banner calls unsupported. Reword as illustrative simulated workflows.
4. **Non-blocking.** Acceptance item 1 is still literally unmet (C6, C11-C13 prevented; C15-C20 open). Get the D10 deviation confirmed by the planner or the owner.
5. **Release gate, not this feature.** `.autodev/` is tracked on `autodev/integration` and on this branch although `publish_autodev_state = false`. A PR to public `main` must exclude it (governance auditor, finding 1).
