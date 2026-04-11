#!/usr/bin/env python3
"""
Source Code Knowledge Base Generator for the AI-Powered Unit Test Case Generation System.
This script reads and analyzes the full-stack-fastapi source code and generates a knowledge_base.json file.
"""

import os
import sys
import json
import ast
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import asdict

# Add the parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.models import CodeUnit, UnitComponentType
from core.knowledge_analyzer import KnowledgeBaseAnalyzer


class SourceCodeKnowledgeBaseGenerator:
    """Generates a knowledge base by analyzing the actual source code from full-stack-fastapi."""
    
    def __init__(self, codebase_path: str = "../full-stack-fastapi-template"):
        self.codebase_path = Path(codebase_path)
        self.analyzer = KnowledgeBaseAnalyzer()
        self.knowledge_base = {
            "metadata": {
                "generated_by": "AI-Powered Unit Test Case Generation System",
                "version": "1.0.0",
                "codebase_path": str(self.codebase_path.absolute()),
                "total_files_analyzed": 0,
                "total_units_found": 0,
                "generation_timestamp": None
            },
            "code_units": [],
            "file_structure": {},
            "dependencies": {},
            "statistics": {},
            "testing_patterns": {},
            "api_endpoints": [],
            "database_models": [],
            "business_logic": [],
            "validation_rules": [],
            "error_handling": [],
            "security_features": []
        }
    
    def analyze_codebase(self) -> bool:
        """Analyze the entire codebase and extract code units."""
        print(f"🔍 Analyzing source code at: {self.codebase_path}")
        
        if not self.codebase_path.exists():
            print(f"❌ Codebase path does not exist: {self.codebase_path}")
            return False
        
        # Find all Python files
        python_files = list(self.codebase_path.rglob("*.py"))
        print(f"📁 Found {len(python_files)} Python files")
        
        if not python_files:
            print("❌ No Python files found in the codebase")
            return False
        
        # Analyze the entire codebase
        print("  🔍 Analyzing codebase structure...")
        try:
            units = self.analyzer.analyze_codebase(str(self.codebase_path))
            if units:
                self.knowledge_base["code_units"].extend(units)
                total_units = len(units)
                print(f"    ✅ Found {total_units} code units")
            else:
                print(f"    ℹ️  No code units found")
                
        except Exception as e:
            print(f"    ❌ Error analyzing codebase: {e}")
            return False
        
        # Update metadata
        self.knowledge_base["metadata"]["total_files_analyzed"] = len(python_files)
        self.knowledge_base["metadata"]["total_units_found"] = total_units
        
        print(f"\n📊 Analysis complete: {total_units} code units found in {len(python_files)} files")
        return True
    
    def analyze_file_structure(self):
        """Analyze the file structure of the codebase."""
        print("\n📁 Analyzing file structure...")
        
        structure = {}
        for file_path in self.codebase_path.rglob("*"):
            if file_path.is_file():
                relative_path = str(file_path.relative_to(self.codebase_path))
                file_type = file_path.suffix
                
                # Categorize files
                if file_type == ".py":
                    category = "python"
                elif file_type in [".json", ".yaml", ".yml"]:
                    category = "config"
                elif file_type in [".md", ".txt"]:
                    category = "documentation"
                elif file_type in [".html", ".css", ".js"]:
                    category = "frontend"
                else:
                    category = "other"
                
                if category not in structure:
                    structure[category] = []
                structure[category].append(relative_path)
        
        self.knowledge_base["file_structure"] = structure
        
        # Print summary
        for category, files in structure.items():
            print(f"  📂 {category.capitalize()}: {len(files)} files")
    
    def analyze_dependencies(self):
        """Analyze dependencies from requirements files."""
        print("\n📦 Analyzing dependencies...")
        
        requirements_files = [
            self.codebase_path / "requirements.txt",
            self.codebase_path / "backend" / "requirements.txt",
            self.codebase_path / "frontend" / "package.json"
        ]
        
        dependencies = {}
        
        for req_file in requirements_files:
            if req_file.exists():
                try:
                    if req_file.suffix == ".txt":
                        # Python requirements
                        with open(req_file, 'r') as f:
                            lines = f.readlines()
                            deps = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
                            dependencies[str(req_file.relative_to(self.codebase_path))] = deps
                    elif req_file.name == "package.json":
                        # Node.js dependencies
                        with open(req_file, 'r') as f:
                            data = json.load(f)
                            deps = list(data.get("dependencies", {}).keys())
                            dev_deps = list(data.get("devDependencies", {}).keys())
                            dependencies[str(req_file.relative_to(self.codebase_path))] = {
                                "dependencies": deps,
                                "devDependencies": dev_deps
                            }
                except Exception as e:
                    print(f"    ❌ Error reading {req_file}: {e}")
        
        self.knowledge_base["dependencies"] = dependencies
        
        # Print summary
        for file_path, deps in dependencies.items():
            if isinstance(deps, list):
                print(f"  📄 {file_path}: {len(deps)} dependencies")
            else:
                total = len(deps.get("dependencies", [])) + len(deps.get("devDependencies", []))
                print(f"  📄 {file_path}: {total} dependencies")
    
    def extract_testing_patterns(self):
        """Extract testing patterns from the analyzed code units."""
        print("\n🧪 Extracting testing patterns from source code...")
        
        patterns = {
            "boundary_testing": [],
            "null_testing": [],
            "authentication": [],
            "validation": [],
            "error_handling": [],
            "business_logic": [],
            "api_endpoints": [],
            "database_operations": []
        }
        
        for unit in self.knowledge_base["code_units"]:
            # Analyze function/method names and content for testing patterns
            unit_name = unit.name.lower()
            unit_path = unit.file_path.lower()
            
            # Authentication patterns
            if any(keyword in unit_name for keyword in ["auth", "login", "register", "password", "token", "session"]):
                patterns["authentication"].append(f"{unit.name}: {unit.business_logic}")
            
            # Validation patterns
            if any(keyword in unit_name for keyword in ["validate", "check", "verify", "sanitize"]):
                patterns["validation"].append(f"{unit.name}: {unit.business_logic}")
            
            # Error handling patterns
            if any(keyword in unit_name for keyword in ["error", "exception", "handle", "catch"]):
                patterns["error_handling"].append(f"{unit.name}: {unit.business_logic}")
            
            # API endpoint patterns
            if "api" in unit_path or "router" in unit_path or "endpoint" in unit_path:
                patterns["api_endpoints"].append(f"{unit.name}: {unit.signature}")
            
            # Database operation patterns
            if any(keyword in unit_name for keyword in ["create", "read", "update", "delete", "query", "db"]):
                patterns["database_operations"].append(f"{unit.name}: {unit.business_logic}")
            
            # Business logic patterns
            if unit.business_logic and unit.business_logic != "No business logic identified":
                patterns["business_logic"].append(f"{unit.name}: {unit.business_logic}")
        
        # Add common testing scenarios based on extracted patterns
        if patterns["validation"]:
            patterns["boundary_testing"] = [
                "empty fields",
                "maximum field length",
                "minimum field length", 
                "special characters",
                "unicode characters",
                "leading/trailing whitespace"
            ]
        
        if patterns["authentication"]:
            patterns["null_testing"] = [
                "null values",
                "undefined values",
                "empty strings",
                "missing required fields",
                "expired tokens",
                "invalid credentials"
            ]
        
        self.knowledge_base["testing_patterns"] = patterns
        
        # Print summary
        for pattern_type, scenarios in patterns.items():
            if scenarios:
                print(f"  🧪 {pattern_type.replace('_', ' ').title()}: {len(scenarios)} patterns")
    
    def extract_api_endpoints(self):
        """Extract API endpoints from the codebase."""
        print("\n🔗 Extracting API endpoints...")
        
        endpoints = []
        for unit in self.knowledge_base["code_units"]:
            if "api" in unit.file_path.lower() or "router" in unit.file_path.lower():
                endpoints.append({
                    "name": unit.name,
                    "file": unit.file_path,
                    "signature": unit.signature,
                    "dependencies": unit.dependencies,
                    "business_logic": unit.business_logic
                })
        
        self.knowledge_base["api_endpoints"] = endpoints
        print(f"  🔗 Found {len(endpoints)} API endpoints")
    
    def extract_database_models(self):
        """Extract database models from the codebase."""
        print("\n🗄️  Extracting database models...")
        
        models = []
        for unit in self.knowledge_base["code_units"]:
            # Look for model-related classes and functions
            if any(keyword in unit.name.lower() for keyword in ["model", "schema", "table", "entity", "crud", "database"]):
                models.append({
                    "name": unit.name,
                    "file": unit.file_path,
                    "dependencies": unit.dependencies,
                    "business_logic": unit.business_logic
                })
        
        self.knowledge_base["database_models"] = models
        print(f"  🗄️  Found {len(models)} database models")
    
    def generate_statistics(self):
        """Generate statistics about the codebase."""
        print("\n📊 Generating statistics...")
        
        stats = {
            "unit_types": {},
            "file_distribution": {},
            "complexity_analysis": {}
        }
        
        # Count unit types
        for unit in self.knowledge_base["code_units"]:
            unit_type = unit.component_type.value
            stats["unit_types"][unit_type] = stats["unit_types"].get(unit_type, 0) + 1
        
        # File distribution
        for unit in self.knowledge_base["code_units"]:
            file_path = unit.file_path
            if file_path not in stats["file_distribution"]:
                stats["file_distribution"][file_path] = 0
            stats["file_distribution"][file_path] += 1
        
        # Complexity analysis
        total_functions = 0
        total_classes = 0
        
        for unit in self.knowledge_base["code_units"]:
            if unit.component_type in [UnitComponentType.PURE_FUNCTION, UnitComponentType.BUSINESS_LOGIC]:
                total_functions += 1
            elif unit.component_type == UnitComponentType.STATE_MANAGEMENT:
                total_classes += 1
        
        stats["complexity_analysis"] = {
            "total_functions": total_functions,
            "total_classes": total_classes,
            "average_units_per_file": len(self.knowledge_base["code_units"]) / max(1, self.knowledge_base["metadata"]["total_files_analyzed"])
        }
        
        self.knowledge_base["statistics"] = stats
        
        # Print summary
        print(f"  🔢 Unit Types: {dict(stats['unit_types'])}")
        print(f"  📁 Files with most units: {sorted(stats['file_distribution'].items(), key=lambda x: x[1], reverse=True)[:5]}")
        print(f"  📊 Complexity: {stats['complexity_analysis']}")
    
    def save_knowledge_base(self, output_path: str = "knowledge_base.json") -> bool:
        """Save the knowledge base to a JSON file."""
        print(f"\n💾 Saving knowledge base to: {output_path}")
        
        try:
            # Convert dataclass objects to dictionaries
            serializable_units = []
            for unit in self.knowledge_base["code_units"]:
                unit_dict = asdict(unit)
                # Convert enum values to strings
                unit_dict["component_type"] = unit.component_type.value
                serializable_units.append(unit_dict)
            
            # Create serializable knowledge base
            serializable_kb = self.knowledge_base.copy()
            serializable_kb["code_units"] = serializable_units
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_kb, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Knowledge base saved successfully!")
            print(f"📁 File size: {os.path.getsize(output_path) / 1024:.1f} KB")
            return True
            
        except Exception as e:
            print(f"❌ Error saving knowledge base: {e}")
            return False
    
    def generate_summary_report(self) -> str:
        """Generate a human-readable summary report."""
        metadata = self.knowledge_base["metadata"]
        stats = self.knowledge_base["statistics"]
        
        report = f"""
📋 SOURCE CODE KNOWLEDGE BASE GENERATION SUMMARY
{'=' * 60}

🏗️  Codebase Analysis:
   • Path: {metadata['codebase_path']}
   • Files Analyzed: {metadata['total_files_analyzed']}
   • Code Units Found: {metadata['total_units_found']}

📊 Unit Type Distribution:
"""
        
        for unit_type, count in stats.get("unit_types", {}).items():
            report += f"   • {unit_type}: {count}\n"
        
        report += f"""
📁 File Structure:
   • Python Files: {len(self.knowledge_base['file_structure'].get('python', []))}
   • Configuration Files: {len(self.knowledge_base['file_structure'].get('config', []))}
   • Documentation Files: {len(self.knowledge_base['file_structure'].get('documentation', []))}
   • Frontend Files: {len(self.knowledge_base['file_structure'].get('frontend', []))}

🔗 Dependencies:
   • Python Requirements: {len(self.knowledge_base['dependencies'])} files
   • Total Dependencies: {sum(len(deps) if isinstance(deps, list) else len(deps.get('dependencies', [])) + len(deps.get('devDependencies', [])) for deps in self.knowledge_base['dependencies'].values())}

🧪 Testing Patterns Extracted:
   • API Endpoints: {len(self.knowledge_base['api_endpoints'])}
   • Database Models: {len(self.knowledge_base['database_models'])}
   • Authentication: {len(self.knowledge_base['testing_patterns'].get('authentication', []))}
   • Validation: {len(self.knowledge_base['testing_patterns'].get('validation', []))}
   • Error Handling: {len(self.knowledge_base['testing_patterns'].get('error_handling', []))}

💡 Next Steps:
   1. Use knowledge_base.json with the AI system for test generation
   2. The AI will use the extracted code patterns to generate targeted test cases
   3. Customize the knowledge base by editing the JSON file
   4. Re-run analysis when the codebase changes
"""
        
        return report
    
    def run_full_analysis(self) -> bool:
        """Run the complete knowledge base generation process."""
        print("🚀 Starting Source Code Knowledge Base Generation")
        print("=" * 60)
        
        # Step 1: Analyze codebase
        if not self.analyze_codebase():
            return False
        
        # Step 2: Analyze file structure
        self.analyze_file_structure()
        
        # Step 3: Analyze dependencies
        self.analyze_dependencies()
        
        # Step 4: Extract testing patterns
        self.extract_testing_patterns()
        
        # Step 5: Extract API endpoints
        self.extract_api_endpoints()
        
        # Step 6: Extract database models
        self.extract_database_models()
        
        # Step 7: Generate statistics
        self.generate_statistics()
        
        # Step 8: Save knowledge base
        if not self.save_knowledge_base():
            return False
        
        # Step 9: Generate summary report
        summary = self.generate_summary_report()
        print(summary)
        
        return True


def main():
    """Main function to run the source code knowledge base generator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate knowledge base by analyzing full-stack-fastapi source code")
    parser.add_argument("--codebase-path", default="../full-stack-fastapi-template", 
                       help="Path to the full-stack-fastapi codebase")
    parser.add_argument("--output", default="knowledge_base.json",
                       help="Output file for the knowledge base")
    
    args = parser.parse_args()
    
    # Create generator
    generator = SourceCodeKnowledgeBaseGenerator(args.codebase_path)
    
    # Run analysis
    success = generator.run_full_analysis()
    
    if success:
        print("\n🎉 Source code knowledge base generation completed successfully!")
        print(f"📁 Knowledge base saved to: {args.output}")
        print("\n💡 You can now use this knowledge base with the AI system to generate test cases!")
        print("   The AI will use the extracted code patterns to generate targeted test cases!")
    else:
        print("\n❌ Knowledge base generation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
