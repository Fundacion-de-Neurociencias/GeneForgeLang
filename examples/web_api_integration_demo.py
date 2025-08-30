"""Comprehensive Web Interface and API Server Integration Demo.

This demonstration showcases the complete GeneForgeLang web and API stack:
- FastAPI REST API server setup and testing
- Gradio web interface launch and interaction
- Client SDK usage for programmatic access
- End-to-end workflow examples
- Performance benchmarking and monitoring
"""

import asyncio
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test GFL samples
DEMO_SAMPLES = {
    "Basic CRISPR Experiment": """
experiment:
  tool: CRISPR_cas9
  type: gene_editing
  params:
    target_gene: TP53
    guide_rna: GTCGACTTCGTACGTACGTA
    vector: lentiviral

analyze:
  strategy: knockout_validation
  thresholds:
    efficiency: 0.8
""",
    "RNA-seq Differential Expression": """
experiment:
  tool: illumina_novaseq
  type: rna_seq
  params:
    samples: 24
    reads_per_sample: 30M
    library_type: paired_end

analyze:
  strategy: differential_expression
  thresholds:
    p_value: 0.01
    log2FoldChange: 1.5
    fdr: 0.05
""",
    "Protein Structure Prediction": """
experiment:
  tool: alphafold2
  type: protein_structure
  params:
    target_gene: BRCA1
    analysis_type: domain_prediction
    confidence_threshold: 0.7

analyze:
  strategy: functional_domains
  params:
    domain_types:
      - kinase
      - nuclear_localization
      - dna_binding
""",
    "Epigenetic ChIP-seq": """
experiment:
  tool: chip_seq
  type: epigenetic_analysis
  params:
    target_modification: H3K4me3
    genome: hg38
    peak_caller: macs2

analyze:
  strategy: peak_calling
  thresholds:
    p_value: 0.001
    fold_enrichment: 2.0
""",
}


def check_server_availability(base_url: str = "http://127.0.0.1:8000") -> bool:
    """Check if API server is running."""
    try:
        import requests

        response = requests.get(f"{base_url}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def demo_api_server():
    """Demonstrate API server functionality."""
    print("\n" + "=" * 60)
    print("API SERVER DEMONSTRATION")
    print("=" * 60)

    # Check if server components are available
    try:
        from gfl.api_server import create_app, run_server
        from gfl.client_sdk import create_client, GFLClientError

        print("✅ API Server components available")

        # Check if server is running
        if check_server_availability():
            print("✅ API Server is running - testing client functionality")

            # Test client SDK
            try:
                client = create_client()

                # Health check
                health = client.health_check()
                print(f"📊 Server Health: {health.get('status', 'unknown')}")
                print(f"   Uptime: {health.get('uptime_seconds', 0):.1f}s")
                print(f"   Models: {len(health.get('available_models', []))}")

                # Test parsing
                for name, sample in list(DEMO_SAMPLES.items())[
                    :2
                ]:  # Test first 2 samples
                    print(f"\n🧪 Testing: {name}")

                    try:
                        # Parse
                        parse_result = client.parse(sample)
                        print(f"   Parse: ✅ ({parse_result.execution_time_ms:.1f}ms)")

                        # Validate
                        validation_result = client.validate(sample)
                        status = "✅" if validation_result.is_valid else "❌"
                        print(
                            f"   Validate: {status} ({validation_result.execution_time_ms:.1f}ms)"
                        )

                        if validation_result.errors:
                            print(f"   Errors: {len(validation_result.errors)}")

                        # Inference
                        inference_result = client.infer(sample, model_name="heuristic")
                        print(
                            f"   Inference: {inference_result.prediction} ({inference_result.confidence:.1%})"
                        )

                    except GFLClientError as e:
                        print(f"   ❌ Client Error: {e}")
                    except Exception as e:
                        print(f"   ❌ Error: {e}")

                # Test model listing
                try:
                    models = client.list_models()
                    print(f"\n🤖 Available Models ({len(models)}):")
                    for model in models:
                        status = "✅" if model.loaded else "⏳"
                        print(f"   {status} {model.name} ({model.type})")

                except Exception as e:
                    print(f"   ❌ Model listing error: {e}")

                # Test batch processing
                try:
                    print("\n📦 Batch Processing Test")
                    sample_list = list(DEMO_SAMPLES.values())[:3]

                    start_time = time.time()
                    batch_results = client.batch_inference(
                        sample_list, model_name="heuristic"
                    )
                    batch_time = time.time() - start_time

                    successful = sum(
                        1 for r in batch_results if r.get("success", False)
                    )
                    print(f"   Processed: {successful}/{len(batch_results)} samples")
                    print(f"   Total Time: {batch_time*1000:.1f}ms")
                    print(f"   Avg/Sample: {batch_time*1000/len(sample_list):.1f}ms")

                except Exception as e:
                    print(f"   ❌ Batch processing error: {e}")

                # Test statistics
                try:
                    stats = client.get_stats()
                    print("\n📈 Server Statistics:")
                    print(f"   Total Requests: {stats.get('requests_total', 0)}")
                    print(
                        f"   Success Rate: {stats.get('requests_successful', 0) / max(1, stats.get('requests_total', 1)) * 100:.1f}%"
                    )
                    print(f"   Uptime: {stats.get('uptime_seconds', 0):.1f}s")

                    endpoints = stats.get("endpoints_called", {})
                    if endpoints:
                        print("   Top Endpoints:")
                        for endpoint, count in sorted(
                            endpoints.items(), key=lambda x: x[1], reverse=True
                        )[:3]:
                            print(f"     {endpoint}: {count} calls")

                except Exception as e:
                    print(f"   ❌ Statistics error: {e}")

            except Exception as e:
                print(f"❌ Client testing failed: {e}")

        else:
            print("⚠️ API Server not running - showing server creation example")

            # Show how to create and configure the server
            try:
                app = create_app()
                print(f"✅ FastAPI app created: {app.title} v{app.version}")
                print(f"   Description: {app.description[:50]}...")
                print(f"   Docs URL: {app.docs_url}")

                print("\n💡 To start the server:")
                print("   Option 1: gfl-server --all")
                print("   Option 2: gfl-api --host 127.0.0.1 --port 8000")
                print("   Option 3: python -m gfl.api_server")

            except Exception as e:
                print(f"❌ Server creation failed: {e}")

    except ImportError as e:
        print(f"❌ API Server not available: {e}")
        print("💡 Install with: pip install -e .[server] or pip install -e .[full]")


def demo_web_interface():
    """Demonstrate web interface functionality."""
    print("\n" + "=" * 60)
    print("WEB INTERFACE DEMONSTRATION")
    print("=" * 60)

    try:
        from gfl.web_interface import (
            create_interface,
            initialize_inference_engine,
            parse_and_validate_gfl,
            get_available_models,
            get_system_stats,
            SAMPLE_GFL_CONTENT,
        )

        print("✅ Web Interface components available")

        # Test inference engine initialization
        print("\n🔧 Initializing Inference Engine...")
        success, message = initialize_inference_engine()
        print(f"   Status: {'✅' if success else '❌'}")
        print(f"   Details: {message}")

        # Test parsing and validation
        print("\n🧪 Testing Core Functions:")
        for i, (name, sample) in enumerate(list(DEMO_SAMPLES.items())[:2], 1):
            print(f"\n{i}. Testing: {name}")

            try:
                is_valid, result_msg, ast = parse_and_validate_gfl(sample)

                print(f"   Result: {'✅ Valid' if is_valid else '❌ Invalid'}")
                print(f"   Message: {result_msg.split(chr(10))[0]}")  # First line only

                if ast:
                    print(f"   AST Keys: {list(ast.keys())}")

            except Exception as e:
                print(f"   ❌ Error: {e}")

        # Test model management
        print("\n🤖 Available Models:")
        try:
            models = get_available_models()
            for model in models:
                print(f"   • {model}")
        except Exception as e:
            print(f"   ❌ Error getting models: {e}")

        # Test system statistics
        print("\n📊 System Statistics:")
        try:
            stats = get_system_stats()
            # Show first few lines of stats
            for line in stats.split("\\n")[:8]:
                if line.strip():
                    print(f"   {line}")
        except Exception as e:
            print(f"   ❌ Error getting stats: {e}")

        # Test sample content
        print("\n📋 Sample Content Available:")
        print(f"   Samples: {len(SAMPLE_GFL_CONTENT)}")
        for name in SAMPLE_GFL_CONTENT.keys():
            print(f"   • {name}")

        # Show interface creation (without launching)
        print("\n🖥️ Interface Creation:")
        try:
            create_interface()
            print("   ✅ Gradio interface created successfully")
            print("   Components: Multiple tabs with editor, inference, comparison")

            print("\n💡 To launch the web interface:")
            print("   Option 1: gfl-server --web-only")
            print("   Option 2: gfl-web --host 127.0.0.1 --port 7860")
            print("   Option 3: python -m gfl.web_interface")

        except Exception as e:
            print(f"   ❌ Interface creation failed: {e}")

    except ImportError as e:
        print(f"❌ Web Interface not available: {e}")
        print("💡 Install with: pip install -e .[apps] or pip install -e .[full]")


def demo_server_launcher():
    """Demonstrate server launcher functionality."""
    print("\n" + "=" * 60)
    print("SERVER LAUNCHER DEMONSTRATION")
    print("=" * 60)

    try:
        from gfl.server_launcher import (
            GFLServerManager,
            ServerProcess,
            check_dependencies,
            print_startup_banner,
        )

        print("✅ Server Launcher components available")

        # Check dependencies
        print("\n🔍 Dependency Check:")
        deps = check_dependencies()
        for dep_name, available in deps.items():
            status = "✅" if available else "❌"
            print(f"   {status} {dep_name}")

        # Test ServerProcess class
        print("\n⚙️ Server Process Management:")

        def dummy_server():
            time.sleep(0.1)  # Simulate server startup

        try:
            server_proc = ServerProcess(name="demo_server", target_func=dummy_server)

            print(f"   ✅ ServerProcess created: {server_proc.name}")
            print(
                f"   Initial state: {'Running' if server_proc.is_running() else 'Stopped'}"
            )

        except Exception as e:
            print(f"   ❌ ServerProcess error: {e}")

        # Test GFLServerManager
        print("\n📊 Server Manager:")
        try:
            manager = GFLServerManager()
            print("   ✅ Manager created")
            print(f"   Servers configured: {len(manager.servers)}")
            print(f"   Shutdown requested: {manager.shutdown_requested}")

        except Exception as e:
            print(f"   ❌ Manager error: {e}")

        # Show configuration example
        print("\n⚙️ Configuration Example:")
        config = {
            "api_enabled": True,
            "web_enabled": True,
            "api_host": "127.0.0.1",
            "api_port": 8000,
            "web_host": "127.0.0.1",
            "web_port": 7860,
            "debug": False,
        }

        try:
            print_startup_banner(config)
        except Exception:
            print(f"   Configuration display: {config}")

        print("\n💡 Server Launcher Commands:")
        print("   gfl-server --all                    # Both API and Web")
        print("   gfl-server --api-only               # API server only")
        print("   gfl-server --web-only               # Web interface only")
        print("   gfl-server --host 0.0.0.0 --share   # Public access")
        print("   gfl-server --check-deps             # Check dependencies")

    except ImportError as e:
        print(f"❌ Server Launcher not available: {e}")
        print("💡 Install with: pip install -e .[full]")


async def demo_async_client():
    """Demonstrate asynchronous client functionality."""
    print("\n" + "=" * 60)
    print("ASYNC CLIENT DEMONSTRATION")
    print("=" * 60)

    try:
        from gfl.client_sdk import create_async_client

        print("✅ Async Client components available")

        if check_server_availability():
            print("✅ API Server available - testing async operations")

            try:
                async with create_async_client() as client:
                    # Concurrent health checks
                    print("\n🔄 Concurrent Operations Test:")

                    start_time = time.time()

                    # Run multiple operations concurrently
                    tasks = []
                    for i in range(3):
                        task = asyncio.create_task(client.health_check())
                        tasks.append(task)

                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    concurrent_time = time.time() - start_time

                    successful_results = [r for r in results if isinstance(r, dict)]
                    print(f"   Concurrent requests: {len(tasks)}")
                    print(f"   Successful: {len(successful_results)}")
                    print(f"   Total time: {concurrent_time*1000:.1f}ms")
                    print(
                        f"   Avg per request: {concurrent_time*1000/len(tasks):.1f}ms"
                    )

                    # Test async parsing
                    if successful_results:
                        print("\n📋 Async Parsing Test:")
                        sample = list(DEMO_SAMPLES.values())[0]

                        parse_result = await client.parse(sample)
                        print(
                            f"   Parse result: {'✅' if parse_result.success else '❌'}"
                        )
                        print(
                            f"   Execution time: {parse_result.execution_time_ms:.1f}ms"
                        )

                        # Test async inference
                        inference_result = await client.infer(
                            sample, model_name="heuristic"
                        )
                        print(
                            f"   Inference: {inference_result.prediction} ({inference_result.confidence:.1%})"
                        )
                        print(
                            f"   Execution time: {inference_result.execution_time_ms:.1f}ms"
                        )

            except Exception as e:
                print(f"❌ Async client testing failed: {e}")

        else:
            print("⚠️ API Server not running - async client requires running server")
            print("💡 Start server with: gfl-server --api-only")

    except ImportError as e:
        print(f"❌ Async Client not available: {e}")
        print("💡 Install with: pip install httpx")


def demo_integration_workflow():
    """Demonstrate complete integration workflow."""
    print("\n" + "=" * 60)
    print("INTEGRATION WORKFLOW DEMONSTRATION")
    print("=" * 60)

    print("📋 Complete GeneForgeLang Web & API Stack Workflow:")
    print()

    # Step 1: Server Setup
    print("1️⃣ Server Setup:")
    print("   • Install dependencies: pip install -e .[full]")
    print("   • Start servers: gfl-server --all")
    print("   • Verify health: curl http://127.0.0.1:8000/health")
    print()

    # Step 2: Web Interface Access
    print("2️⃣ Web Interface Access:")
    print("   • Open browser: http://127.0.0.1:7860")
    print("   • Use GFL Editor tab for workflow design")
    print("   • Use AI Inference tab for model predictions")
    print("   • Use Model Comparison tab for analysis")
    print()

    # Step 3: API Integration
    print("3️⃣ API Integration:")
    print("   • REST API: http://127.0.0.1:8000/docs")
    print("   • Python SDK: from gfl.client_sdk import create_client")
    print("   • Async support: from gfl.client_sdk import create_async_client")
    print()

    # Step 4: Advanced Features
    print("4️⃣ Advanced Features:")
    print("   • Multi-model inference and comparison")
    print("   • Batch processing for large datasets")
    print("   • Real-time validation and error reporting")
    print("   • Performance monitoring and statistics")
    print()

    # Step 5: Production Deployment
    print("5️⃣ Production Deployment:")
    print("   • Configure reverse proxy (nginx)")
    print("   • Set up SSL/TLS certificates")
    print("   • Configure rate limiting and authentication")
    print("   • Set up monitoring and logging")
    print()

    print("🎯 Use Cases:")
    print("   • Interactive genomic workflow design")
    print("   • Automated pipeline validation")
    print("   • AI-powered experiment optimization")
    print("   • Large-scale batch analysis")
    print("   • Research collaboration platform")


def main():
    """Main demonstration function."""
    print("🧬 GeneForgeLang Web Interface & API Server Integration Demo")
    print("=" * 80)
    print()
    print("This comprehensive demonstration showcases the complete")
    print("GeneForgeLang web and API infrastructure including:")
    print()
    print("• 🌐 FastAPI REST API Server")
    print("• 🖥️  Gradio Web Interface")
    print("• 🔧 Unified Server Launcher")
    print("• 📡 Client SDK (Sync & Async)")
    print("• 🧪 Integration Testing")
    print("• ⚡ Performance Benchmarking")

    # Run all demonstrations
    demo_api_server()
    demo_web_interface()
    demo_server_launcher()

    # Run async demo
    try:
        asyncio.run(demo_async_client())
    except Exception as e:
        print(f"Async demo skipped: {e}")

    demo_integration_workflow()

    print("\n" + "=" * 80)
    print("🎉 DEMONSTRATION COMPLETE")
    print("=" * 80)
    print()
    print("The GeneForgeLang web interface and API server provide a")
    print("comprehensive platform for genomic workflow analysis with:")
    print()
    print("✅ RESTful API with OpenAPI documentation")
    print("✅ Interactive web interface with real-time validation")
    print("✅ Multi-model inference and comparison")
    print("✅ Batch processing and performance monitoring")
    print("✅ Type-safe client SDK with async support")
    print("✅ Production-ready deployment tools")
    print()
    print("🚀 Ready for Phase 4 and production deployment!")


if __name__ == "__main__":
    main()
