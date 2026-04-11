"""Main CLI script for the advanced test automation framework."""

import asyncio
import json
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

from .generators import TestGenerator, CodeGenerator
from .llm import LLMFactory
from .templates import TemplateFactory
from .agents import AgentChain
from .runners import ReportGenerator

console = Console()


@click.group()
def main():
    """Advanced Test Automation Framework - Generate comprehensive test suites using AI."""
    console.print(
        Panel.fit(
            "[bold blue]🤖 Advanced Test Automation Framework[/bold blue]\n"
            "[green]Powered by sophisticated prompting techniques and LLaMA 3.1[/green]",
            border_style="blue",
        )
    )


@main.command()
@click.option(
    "--programming-language",
    "-l",
    required=True,
    help="Programming language (Python, JavaScript, TypeScript, etc.)",
)
@click.option(
    "--testing-framework",
    "-f",
    required=True,
    help="Testing framework (pytest, jest, selenium, etc.)",
)
@click.option(
    "--test-cases",
    "-t",
    required=True,
    type=click.Path(exists=True),
    help="Path to test_cases.json file",
)
@click.option(
    "--category",
    "-c",
    required=True,
    help="Test category (API, Unit, WebUI, MobileUI, Edge, Performance, etc.)",
)
@click.option(
    "--knowledge-base",
    "-k",
    type=click.Path(exists=True),
    help="Path to knowledge base document",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path for generated test cases",
)
@click.option(
    "--generate-code",
    is_flag=True,
    default=False,
    help="Generate actual test code files",
)
@click.option(
    "--output-dir", type=click.Path(), help="Output directory for generated test files"
)
@click.option(
    "--llm-provider",
    default="ollama",
    type=click.Choice(["ollama", "openai"]),
    help="LLM provider to use",
)
@click.option(
    "--model",
    help="Specific model to use (defaults: llama3.1:8b-instruct-q8_0 for Ollama)",
)
@click.option(
    "--temperature",
    default=0.7,
    type=float,
    help="Temperature for LLM generation (0.0-1.0)",
)
@click.option("--max-tokens", type=int, help="Maximum tokens for generation")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def generate(
    programming_language: str,
    testing_framework: str,
    test_cases: str,
    category: str,
    knowledge_base: Optional[str],
    output: Optional[str],
    generate_code: bool,
    output_dir: Optional[str],
    llm_provider: str,
    model: Optional[str],
    temperature: float,
    max_tokens: Optional[int],
    verbose: bool,
):
    """Generate test cases for a specific category."""

    async def _generate():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            # Initialize generator
            progress.add_task("Initializing LLM provider...", total=None)

            try:
                generator = TestGenerator(llm_provider=llm_provider, model=model)
            except Exception as e:
                console.print(f"[red]Failed to initialize LLM: {e}[/red]")
                return

            # Validate LLM connection
            progress.add_task("Validating LLM connection...", total=None)
            if not await generator.validate_llm_connection():
                console.print("[red]LLM connection validation failed[/red]")
                return

            # Generate test cases
            progress.add_task(f"Generating {category} test cases...", total=None)

            try:
                result = await generator.generate_test_cases(
                    programming_language=programming_language,
                    testing_framework=testing_framework,
                    test_cases_file=test_cases,
                    category=category,
                    knowledge_base_file=knowledge_base,
                    output_file=output,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                # Display results
                metadata = result["generation_metadata"]
                test_count = len(result["test_cases"].get("test_cases", []))

                console.print(
                    f"\n[green]✓ Successfully generated {test_count} test cases[/green]"
                )

                if verbose:
                    console.print(f"\n[bold]Generation Details:[/bold]")
                    console.print(f"Provider: {metadata['llm_provider']}")
                    console.print(f"Model: {metadata['llm_model']}")
                    console.print(f"Template: {metadata['template_used']}")
                    console.print(f"Technique: {metadata['prompt_technique']}")
                    if metadata.get("token_usage"):
                        usage = metadata["token_usage"]
                        console.print(f"Tokens: {usage.get('total_tokens', 'N/A')}")

                # Generate code files if requested
                if generate_code:
                    progress.add_task("Generating test code files...", total=None)

                    code_generator = CodeGenerator(generator.llm)

                    if not output_dir:
                        output_dir = f"generated_tests_{category}"

                    try:
                        file_path = await code_generator.generate_test_file(
                            test_cases=result["test_cases"],
                            programming_language=programming_language,
                            testing_framework=testing_framework,
                            output_file=Path(output_dir) / f"test_{category}.py",
                        )
                        console.print(
                            f"[green]✓ Generated test file: {file_path}[/green]"
                        )

                    except Exception as e:
                        console.print(f"[red]Failed to generate test file: {e}[/red]")

            except Exception as e:
                console.print(f"[red]Test generation failed: {e}[/red]")

    asyncio.run(_generate())


@main.command()
@click.option(
    "--programming-language", "-l", required=True, help="Programming language"
)
@click.option("--testing-framework", "-f", required=True, help="Testing framework")
@click.option(
    "--test-cases",
    "-t",
    required=True,
    type=click.Path(exists=True),
    help="Path to test_cases.json file",
)
@click.option(
    "--categories", "-c", multiple=True, help="Test categories (can specify multiple)"
)
@click.option(
    "--all-categories", is_flag=True, help="Generate for all available categories"
)
@click.option(
    "--knowledge-base",
    "-k",
    type=click.Path(exists=True),
    help="Path to knowledge base document",
)
@click.option(
    "--output-dir",
    "-o",
    required=True,
    type=click.Path(),
    help="Output directory for all generated files",
)
@click.option(
    "--generate-code",
    is_flag=True,
    default=False,
    help="Generate actual test code files",
)
@click.option(
    "--llm-provider",
    default="ollama",
    type=click.Choice(["ollama", "openai"]),
    help="LLM provider to use",
)
@click.option("--model", help="Specific model to use")
@click.option(
    "--temperature", default=0.7, type=float, help="Temperature for LLM generation"
)
def generate_all(
    programming_language: str,
    testing_framework: str,
    test_cases: str,
    categories: tuple,
    all_categories: bool,
    knowledge_base: Optional[str],
    output_dir: str,
    generate_code: bool,
    llm_provider: str,
    model: Optional[str],
    temperature: float,
):
    """Generate test cases for multiple categories."""

    async def _generate_all():
        try:
            generator = TestGenerator(llm_provider=llm_provider, model=model)
        except Exception as e:
            console.print(f"[red]Failed to initialize LLM: {e}[/red]")
            return

        # Determine categories to generate
        if all_categories:
            target_categories = generator.get_available_categories()
        else:
            target_categories = list(categories)

        if not target_categories:
            console.print("[red]No categories specified[/red]")
            return

        console.print(
            f"[blue]Generating tests for categories: {', '.join(target_categories)}[/blue]\n"
        )

        # Generate for multiple categories
        results = await generator.generate_multiple_categories(
            programming_language=programming_language,
            testing_framework=testing_framework,
            test_cases_file=test_cases,
            categories=target_categories,
            knowledge_base_file=knowledge_base,
            output_dir=output_dir,
            temperature=temperature,
        )

        # Generate code files if requested
        if generate_code:
            console.print("\n[blue]Generating test code files...[/blue]")
            code_generator = CodeGenerator(generator.llm)

            await code_generator.generate_multiple_files(
                test_results=results,
                programming_language=programming_language,
                testing_framework=testing_framework,
                output_dir=Path(output_dir) / "test_files",
            )

        # Summary
        successful = sum(1 for r in results.values() if "error" not in r)
        total = len(results)
        console.print(
            f"\n[green]✓ Successfully generated {successful}/{total} test suites[/green]"
        )

    asyncio.run(_generate_all())


@main.command()
def list_categories():
    """List all available test categories."""
    factory = TemplateFactory()
    categories = factory.get_available_categories()

    table = Table(title="Available Test Categories")
    table.add_column("Category", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Prompting Technique", style="yellow")

    for category in categories:
        info = factory.get_category_info(category)
        if info:
            table.add_row(
                category,
                info["description"],
                info.get("prompting_technique", "Standard"),
            )

    console.print(table)


@main.command()
@click.argument("query")
def suggest_categories(query: str):
    """Suggest test categories based on a search query."""
    factory = TemplateFactory()
    suggestions = factory.suggest_categories(query)

    if suggestions:
        console.print(f"[green]Suggested categories for '{query}':[/green]")
        for suggestion in suggestions:
            info = factory.get_category_info(suggestion)
            console.print(
                f"  • [cyan]{suggestion}[/cyan]: {info['description'] if info else 'No description'}"
            )
    else:
        console.print(f"[yellow]No categories found matching '{query}'[/yellow]")


@main.command()
def check_llm():
    """Check LLM provider availability."""

    async def _check():
        providers = LLMFactory.get_available_providers()

        table = Table(title="LLM Provider Status")
        table.add_column("Provider", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Details", style="dim")

        for provider, available in providers.items():
            status = (
                "[green]✓ Available[/green]"
                if available
                else "[red]✗ Unavailable[/red]"
            )

            details = ""
            if provider == "ollama" and not available:
                details = "Check if Ollama is running on localhost:11434"
            elif provider == "openai" and not available:
                details = "Check OPENAI_API_KEY environment variable"

            table.add_row(provider.title(), status, details)

        console.print(table)

        # Test connection with best available provider
        best_provider = LLMFactory.get_best_available_provider()
        if best_provider:
            console.print(
                f"\n[green]Testing connection with {best_provider.provider_name}...[/green]"
            )

            try:
                response = await best_provider.generate(
                    "Say 'Hello from test automation framework!'",
                    temperature=0.1,
                    max_tokens=20,
                )
                console.print(f"[green]✓ Connection successful![/green]")
                console.print(f"Response: {response.content}")

            except Exception as e:
                console.print(f"[red]✗ Connection failed: {e}[/red]")
        else:
            console.print("[red]No LLM providers available[/red]")

    asyncio.run(_check())


@main.command()
@click.option(
    "--programming-language",
    "-l",
    required=True,
    help="Programming language (Python, JavaScript, TypeScript, etc.)",
)
@click.option(
    "--testing-framework",
    "-f",
    required=True,
    help="Testing framework (pytest, jest, selenium, etc.)",
)
@click.option(
    "--test-cases",
    "-t",
    required=True,
    type=click.Path(exists=True),
    help="Path to test_cases.json file",
)
@click.option(
    "--categories", "-c", multiple=True, help="Test categories (can specify multiple)"
)
@click.option(
    "--all-categories", is_flag=True, help="Generate for all available categories"
)
@click.option(
    "--knowledge-base",
    "-k",
    type=click.Path(exists=True),
    help="Path to knowledge base document",
)
@click.option(
    "--output-dir",
    "-o",
    required=True,
    type=click.Path(),
    help="Output directory for all generated files",
)
@click.option(
    "--llm-provider",
    default="ollama",
    type=click.Choice(["ollama", "openai"]),
    help="LLM provider to use",
)
@click.option("--model", help="Specific model to use")
@click.option(
    "--temperature", default=0.7, type=float, help="Temperature for LLM generation"
)
@click.option(
    "--strict-validation",
    is_flag=True,
    default=False,
    help="Enable strict validation mode",
)
@click.option(
    "--skip-execution", is_flag=True, default=False, help="Skip test execution stage"
)
@click.option(
    "--generate-reports",
    is_flag=True,
    default=True,
    help="Generate comprehensive reports",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def run_workflow(
    programming_language: str,
    testing_framework: str,
    test_cases: str,
    categories: tuple,
    all_categories: bool,
    knowledge_base: Optional[str],
    output_dir: str,
    llm_provider: str,
    model: Optional[str],
    temperature: float,
    strict_validation: bool,
    skip_execution: bool,
    generate_reports: bool,
    verbose: bool,
):
    """Run the complete test automation workflow with agent chain."""

    async def _run_workflow():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            # Initialize agent chain
            progress.add_task("Initializing agent chain...", total=None)

            try:
                agent_chain = AgentChain(llm_provider=llm_provider, model=model)
            except Exception as e:
                console.print(f"[red]Failed to initialize agent chain: {e}[/red]")
                return

            # Validate setup
            progress.add_task("Validating setup...", total=None)
            setup_validation = await agent_chain.validate_setup()

            if not setup_validation["llm_connection"]:
                console.print("[red]LLM connection validation failed[/red]")
                return

            # Determine categories
            if all_categories:
                target_categories = (
                    agent_chain.generation_agent.get_supported_categories()
                )
            else:
                target_categories = list(categories)

            if not target_categories:
                console.print("[red]No categories specified[/red]")
                return

            console.print(
                f"[blue]Running complete workflow for: {', '.join(target_categories)}[/blue]\n"
            )

            # Configure workflow
            workflow_config = {
                "generation": {
                    "temperature": temperature,
                },
                "validation": {
                    "strict_mode": strict_validation,
                },
                "execution": {
                    "enabled": not skip_execution,
                    "require_validation_pass": strict_validation,
                    "generate_html_report": True,
                    "generate_junit_xml": True,
                },
            }

            # Run complete workflow
            progress.add_task("Running agent chain workflow...", total=None)

            try:
                workflow_result = await agent_chain.run_complete_workflow(
                    programming_language=programming_language,
                    testing_framework=testing_framework,
                    test_cases_file=test_cases,
                    categories=target_categories,
                    knowledge_base_file=knowledge_base,
                    output_directory=output_dir,
                    workflow_config=workflow_config,
                )

                # Display results
                status = workflow_result["status"]
                if status == "completed":
                    console.print(
                        f"\n[green]✓ Workflow completed successfully![/green]"
                    )
                else:
                    console.print(
                        f"\n[red]✗ Workflow failed: {workflow_result.get('error', 'Unknown error')}[/red]"
                    )

                # Show summary
                overall_metrics = workflow_result.get("overall_metrics", {})
                console.print(f"\n[bold]Workflow Summary:[/bold]")
                console.print(
                    f"Categories Processed: {overall_metrics.get('categories_processed', 0)}"
                )
                console.print(
                    f"Total Test Cases: {overall_metrics.get('total_test_cases', 0)}"
                )
                console.print(
                    f"Validation Pass Rate: {overall_metrics.get('validation_pass_rate', 0):.1%}"
                )

                if overall_metrics.get("test_pass_rate") is not None:
                    console.print(
                        f"Test Execution Pass Rate: {overall_metrics['test_pass_rate']:.1%}"
                    )

                console.print(
                    f"Total Duration: {workflow_result.get('total_duration', 0):.2f} seconds"
                )
                console.print(
                    f"Output Directory: {workflow_result['output_directory']}"
                )

                # Generate comprehensive reports
                if generate_reports:
                    progress.add_task("Generating comprehensive reports...", total=None)

                    report_generator = ReportGenerator(agent_chain.llm)
                    report_result = (
                        await report_generator.generate_comprehensive_report(
                            workflow_results=workflow_result,
                            output_directory=Path(output_dir),
                            report_config={
                                "generate_html": True,
                                "generate_csv": True,
                                "generate_pdf": False,
                            },
                        )
                    )

                    console.print(f"\n[green]📊 Reports generated:[/green]")
                    for report_type, report_path in report_result[
                        "generated_reports"
                    ].items():
                        console.print(f"  {report_type.upper()}: {report_path}")

                # Show recommendations
                recommendations = workflow_result.get("recommendations", [])
                if recommendations and verbose:
                    console.print(f"\n[bold yellow]Recommendations:[/bold yellow]")
                    for i, rec in enumerate(recommendations, 1):
                        console.print(f"{i}. {rec}")

            except Exception as e:
                console.print(f"[red]Workflow execution failed: {e}[/red]")
                if verbose:
                    import traceback

                    console.print(f"[dim]{traceback.format_exc()}[/dim]")

    asyncio.run(_run_workflow())


@main.command()
@click.option(
    "--output",
    "-o",
    default="knowledge_base.md",
    type=click.Path(),
    help="Output file for knowledge base",
)
def create_knowledge_base(output: str):
    """Create a knowledge base document from the ecommerce application."""
    from ecommerce_cli.services import DataService

    try:
        service = DataService()

        # Generate comprehensive knowledge base
        kb_content = f"""# Ecommerce Application Knowledge Base

## Application Overview
This is a comprehensive ecommerce CLI application with the following key components:

### Core Entities

#### Products
- **Model**: Product with fields like name, description, price, category, stock_quantity, SKU, brand
- **Categories**: {', '.join([cat.value for cat in service._products.values().__iter__().__next__().category.__class__])}
- **Operations**: Create, read, update, delete, search by name/description/tags
- **Validation**: SKU format validation, price constraints, stock management

#### Users  
- **Model**: User with username, email, name, phone, role, address
- **Roles**: Admin, Customer, Seller
- **Operations**: Registration, authentication, profile management
- **Validation**: Email format, username uniqueness, phone format

#### Orders
- **Model**: Order with items, status, totals, addresses, payment info
- **Statuses**: Pending, Confirmed, Shipped, Delivered, Cancelled
- **Operations**: Create from cart, update status, track progress
- **Business Rules**: Stock reservation, price calculation, tax/shipping

#### Shopping Cart
- **Model**: Cart with items, quantities, totals
- **Operations**: Add/remove items, update quantities, checkout
- **Features**: Session persistence, expiration handling

#### Inventory
- **Model**: Inventory tracking with available/reserved quantities
- **Features**: Stock checks, reservations, reorder levels
- **Alerts**: Low stock notifications, restocking requirements

#### Reviews
- **Model**: Product reviews with ratings, comments, verification
- **Features**: Verified purchase validation, helpful votes
- **Validation**: Rating constraints (1-5), content requirements

### API Endpoints (CLI Commands)

#### Product Management
- `products list [--category] [--search]` - List/search products
- `products show <id>` - Get product details
- `products add` - Create new product

#### Order Management  
- `orders list [--user] [--status]` - List orders
- `orders show <id>` - Get order details
- `orders create --user <username>` - Create order from cart

#### User Management
- `users list` - List all users

#### Inventory Management
- `inventory status` - Check inventory levels
- `stats <product_id>` - Get product statistics

### Business Rules

1. **Stock Management**: Products must have sufficient inventory before order creation
2. **Price Calculations**: Total = subtotal + shipping + tax - discounts
3. **Order Workflow**: Cart → Order → Payment → Fulfillment → Delivery
4. **User Permissions**: Role-based access to different operations
5. **Data Integrity**: Referential integrity between orders, products, users

### Error Scenarios

1. **Insufficient Stock**: Orders fail if product stock is unavailable
2. **Invalid User Data**: Registration fails with invalid email/username formats
3. **Payment Processing**: Orders can fail during payment processing
4. **System Limits**: File size limits, rate limiting, concurrent access

### Performance Considerations

1. **Database Operations**: Efficient querying and indexing
2. **Search Operations**: Text search across product names, descriptions, tags
3. **Inventory Updates**: Concurrent stock management
4. **Large Datasets**: Pagination for large result sets

### Security Aspects

1. **Authentication**: User login and session management
2. **Authorization**: Role-based access control
3. **Data Validation**: Input sanitization and validation
4. **PII Protection**: Secure handling of customer data

### Integration Points

1. **Payment Processing**: External payment gateway integration
2. **Shipping**: Shipping provider APIs
3. **Notifications**: Email/SMS notification services
4. **Analytics**: Reporting and business intelligence

This knowledge base should be used to generate realistic test scenarios that cover all aspects of the ecommerce application.
"""

        with open(output, "w", encoding="utf-8") as f:
            f.write(kb_content)

        console.print(f"[green]✓ Knowledge base created: {output}[/green]")

    except Exception as e:
        console.print(f"[red]Failed to create knowledge base: {e}[/red]")


if __name__ == "__main__":
    main()
