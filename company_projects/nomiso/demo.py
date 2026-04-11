"""
Demo script for the Advanced Test Automation Framework.

This script demonstrates the complete workflow:
1. Test case generation using sophisticated prompting techniques
2. Validation of generated test cases
3. Test execution and reporting
"""

import asyncio
from pathlib import Path

from test_automation.agents import AgentChain
from test_automation.runners import ReportGenerator


async def demo_complete_workflow():
    """Demonstrate the complete test automation workflow."""
    print("🤖 Advanced Test Automation Framework Demo")
    print("=" * 50)

    # Configuration
    config = {
        "programming_language": "Python",
        "testing_framework": "pytest",
        "test_cases_file": "data/test_cases.json",
        "knowledge_base_file": "knowledge_base/ecommerce_knowledge_base.md",
        "categories": ["api", "unit", "positive", "negative"],
        "output_directory": "demo_output",
        "llm_provider": "ollama",
        "model": "llama3.1:8b-instruct-q8_0",
    }

    print(f"Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    print()

    try:
        # Initialize agent chain
        print("🔧 Initializing agent chain...")
        agent_chain = AgentChain(
            llm_provider=config["llm_provider"], model=config["model"]
        )

        # Validate setup
        print("✅ Validating setup...")
        setup_validation = await agent_chain.validate_setup()

        if not setup_validation["llm_connection"]:
            print(
                "❌ LLM connection failed. Please ensure Ollama is running with llama3.1:8b-instruct-q8_0 model."
            )
            return

        print("✅ Setup validation successful!")
        print()

        # Run complete workflow
        print("🚀 Running complete test automation workflow...")

        workflow_config = {
            "generation": {
                "temperature": 0.7,
            },
            "validation": {
                "strict_mode": False,
            },
            "execution": {
                "enabled": True,
                "require_validation_pass": False,
                "generate_html_report": True,
            },
        }

        workflow_result = await agent_chain.run_complete_workflow(
            programming_language=config["programming_language"],
            testing_framework=config["testing_framework"],
            test_cases_file=config["test_cases_file"],
            categories=config["categories"],
            knowledge_base_file=config["knowledge_base_file"],
            output_directory=config["output_directory"],
            workflow_config=workflow_config,
        )

        # Display results
        print("\n📊 Workflow Results:")
        print(f"Status: {workflow_result['status']}")
        print(f"Total Duration: {workflow_result.get('total_duration', 0):.2f} seconds")

        # Show stage results
        stages = workflow_result.get("stages", {})
        for stage_name, stage_data in stages.items():
            status = stage_data.get("status", "unknown")
            duration = stage_data.get("duration", 0)
            print(f"  {stage_name.title()}: {status} ({duration:.2f}s)")

        # Show metrics
        overall_metrics = workflow_result.get("overall_metrics", {})
        if overall_metrics:
            print(f"\n📈 Overall Metrics:")
            print(
                f"  Categories Processed: {overall_metrics.get('categories_processed', 0)}"
            )
            print(f"  Total Test Cases: {overall_metrics.get('total_test_cases', 0)}")
            print(
                f"  Validation Pass Rate: {overall_metrics.get('validation_pass_rate', 0):.1%}"
            )
            if overall_metrics.get("test_pass_rate") is not None:
                print(
                    f"  Test Execution Pass Rate: {overall_metrics['test_pass_rate']:.1%}"
                )

        # Generate comprehensive reports
        print(f"\n📋 Generating comprehensive reports...")
        report_generator = ReportGenerator(agent_chain.llm)

        report_result = await report_generator.generate_comprehensive_report(
            workflow_results=workflow_result,
            output_directory=Path(config["output_directory"]),
            report_config={
                "generate_html": True,
                "generate_csv": True,
                "generate_pdf": False,
            },
        )

        print(f"📁 Reports generated in: {config['output_directory']}")
        for report_type, report_path in report_result["generated_reports"].items():
            print(f"  {report_type.upper()}: {report_path}")

        # Show recommendations
        recommendations = workflow_result.get("recommendations", [])
        if recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")

        print(f"\n✅ Demo completed successfully!")
        print(
            f"Check the '{config['output_directory']}' directory for all generated files."
        )

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback

        print(traceback.format_exc())


async def demo_individual_stages():
    """Demonstrate individual workflow stages."""
    print("\n🔬 Demonstrating Individual Stages")
    print("=" * 40)

    try:
        # Initialize agent chain
        agent_chain = AgentChain(
            llm_provider="ollama", model="llama3.1:8b-instruct-q8_0"
        )

        # Stage 1: Generation only
        print("1️⃣ Test Generation Only...")
        generation_result = await agent_chain.run_generation_only(
            programming_language="Python",
            testing_framework="pytest",
            test_cases_file="data/test_cases.json",
            categories=["api"],
            knowledge_base_file="knowledge_base/ecommerce_knowledge_base.md",
        )

        print(f"   Generation Success: {generation_result.success}")
        if generation_result.success:
            stats = generation_result.data.get("statistics", {})
            print(f"   Test Cases Generated: {stats.get('total_test_cases', 0)}")

        # Stage 2: Validation only
        if generation_result.success:
            print("2️⃣ Validation Only...")
            validation_result = await agent_chain.run_validation_only(
                generated_tests=generation_result.data["generated_tests"]
            )

            print(f"   Validation Success: {validation_result.success}")
            if validation_result.success:
                metrics = validation_result.data.get("metrics", {})
                print(f"   Pass Rate: {metrics.get('pass_rate', 0):.1%}")

        print("✅ Individual stages demo completed!")

    except Exception as e:
        print(f"❌ Individual stages demo failed: {e}")


def show_available_categories():
    """Show all available test categories and their information."""
    print("\n📋 Available Test Categories")
    print("=" * 30)

    from test_automation.templates import TemplateFactory

    factory = TemplateFactory()
    categories = factory.get_available_categories()

    for category in categories:
        info = factory.get_category_info(category)
        if info:
            print(f"🔹 {category}")
            print(f"   Description: {info['description']}")
            print(f"   Technique: {info.get('prompting_technique', 'Standard')}")
            print()


def show_prompting_techniques():
    """Show the sophisticated prompting techniques used."""
    print("\n🧠 Sophisticated Prompting Techniques")
    print("=" * 40)

    techniques = {
        "Chain-of-Thought (CoT)": {
            "description": "Step-by-step reasoning for complex test scenarios",
            "use_cases": ["API testing", "Functional testing"],
            "benefits": ["Systematic analysis", "Comprehensive coverage"],
        },
        "Few-Shot Learning": {
            "description": "Learning from examples to generate consistent patterns",
            "use_cases": ["Unit testing", "Positive testing"],
            "benefits": ["Pattern consistency", "Quality examples"],
        },
        "Tree-of-Thoughts (ToT)": {
            "description": "Exploring multiple reasoning paths for comprehensive coverage",
            "use_cases": ["WebUI testing", "Negative testing", "E2E testing"],
            "benefits": ["Multi-path exploration", "Comprehensive scenarios"],
        },
        "Role-Based Prompting": {
            "description": "Acting as domain experts for specialized knowledge",
            "use_cases": ["Mobile UI testing", "Happy path testing"],
            "benefits": ["Expert perspective", "Domain knowledge"],
        },
        "Metacognitive Prompting": {
            "description": "Self-reflection on test quality and failure modes",
            "use_cases": ["Edge case testing"],
            "benefits": ["Quality assessment", "Critical thinking"],
        },
    }

    for technique, details in techniques.items():
        print(f"🧠 {technique}")
        print(f"   Description: {details['description']}")
        print(f"   Use Cases: {', '.join(details['use_cases'])}")
        print(f"   Benefits: {', '.join(details['benefits'])}")
        print()


async def main():
    """Main demo function."""
    print("🎯 Welcome to the Advanced Test Automation Framework Demo!")
    print()

    # Show available categories
    show_available_categories()

    # Show prompting techniques
    show_prompting_techniques()

    # Run complete workflow demo
    await demo_complete_workflow()

    # Run individual stages demo
    await demo_individual_stages()

    print(
        "\n🎉 Demo completed! Thank you for exploring the Advanced Test Automation Framework."
    )
    print("\nTo run your own tests, use:")
    print("  uv run python -m test_automation.main run-workflow --help")


if __name__ == "__main__":
    asyncio.run(main())
