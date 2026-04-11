"""
Knowledge base analyzer for extracting unit-level insights from codebase.
"""

import ast
import os
from typing import List, Dict, Any
from pathlib import Path
from models.models import CodeUnit, UnitComponentType, UserStory


class KnowledgeBaseAnalyzer:
    """Analyzes codebase to extract testable units."""
    
    def __init__(self):
        self.code_units = []
        self.analyzed_files = set()
    
    def analyze_codebase(self, codebase_path: str) -> List[CodeUnit]:
        """Analyze the codebase to extract testable units."""
        if not os.path.exists(codebase_path):
            return self._get_default_code_units()
        
        self.code_units = []
        self.analyzed_files.clear()
        
        # Walk through the codebase
        for root, dirs, files in os.walk(codebase_path):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    file_path = os.path.join(root, file)
                    self._analyze_python_file(file_path)
        
        return self.code_units if self.code_units else self._get_default_code_units()
    
    def _analyze_python_file(self, file_path: str) -> None:
        """Analyze a single Python file to extract code units."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            relative_path = os.path.relpath(file_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self._extract_function_unit(node, relative_path, content)
                elif isinstance(node, ast.ClassDef):
                    self._extract_class_methods(node, relative_path, content)
                    
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def _extract_function_unit(self, node: ast.FunctionDef, file_path: str, content: str) -> None:
        """Extract a function as a code unit."""
        # Determine component type based on function characteristics
        component_type = self._classify_function_type(node, content)
        
        # Extract dependencies
        dependencies = self._extract_dependencies(node, content)
        
        # Extract parameters
        parameters = self._extract_parameters(node)
        
        # Determine return type
        return_type = self._extract_return_type(node)
        
        # Extract business logic description
        business_logic = self._extract_business_logic(node, content)
        
        # Identify potential error conditions
        error_conditions = self._identify_error_conditions(node, content)
        
        code_unit = CodeUnit(
            name=node.name,
            file_path=file_path,
            component_type=component_type,
            signature="{}({}) -> {}".format(node.name, self._format_signature(node), return_type),
            dependencies=dependencies,
            return_type=return_type,
            parameters=parameters,
            business_logic=business_logic,
            error_conditions=error_conditions
        )
        
        self.code_units.append(code_unit)
    
    def _extract_class_methods(self, node: ast.ClassDef, file_path: str, content: str) -> None:
        """Extract class methods as code units."""
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                # Determine component type for methods
                component_type = self._classify_method_type(item, content)
                
                # Extract dependencies
                dependencies = self._extract_dependencies(item, content)
                dependencies.append(f"Class: {node.name}")
                
                # Extract parameters
                parameters = self._extract_parameters(item)
                
                # Determine return type
                return_type = self._extract_return_type(item)
                
                # Extract business logic description
                business_logic = self._extract_business_logic(item, content)
                
                # Identify potential error conditions
                error_conditions = self._identify_error_conditions(item, content)
                
                code_unit = CodeUnit(
                    name="{}.{}".format(node.name, item.name),
                    file_path=file_path,
                    component_type=component_type,
                    signature="{}.{}({}) -> {}".format(node.name, item.name, self._format_signature(item), return_type),
                    dependencies=dependencies,
                    return_type=return_type,
                    parameters=parameters,
                    business_logic=business_logic,
                    error_conditions=error_conditions
                )
                
                self.code_units.append(code_unit)
    
    def _classify_function_type(self, node: ast.FunctionDef, content: str) -> UnitComponentType:
        """Classify the function type based on its characteristics."""
        function_text = content[node.lineno-1:node.end_lineno]
        
        # Check for pure function characteristics
        if self._is_pure_function(node, function_text):
            return UnitComponentType.PURE_FUNCTION
        
        # Check for validation logic
        if any(keyword in function_text.lower() for keyword in ['validate', 'check', 'verify', 'is_valid']):
            return UnitComponentType.VALIDATION_COMPONENT
        
        # Check for data transformation
        if any(keyword in function_text.lower() for keyword in ['transform', 'convert', 'format', 'parse']):
            return UnitComponentType.DATA_TRANSFORMATION
        
        # Check for algorithm/mathematical operations
        if any(keyword in function_text.lower() for keyword in ['calculate', 'compute', 'algorithm', 'math']):
            return UnitComponentType.ALGORITHM
        
        # Default to business logic
        return UnitComponentType.BUSINESS_LOGIC
    
    def _classify_method_type(self, node: ast.FunctionDef, content: str) -> UnitComponentType:
        """Classify the method type based on its characteristics."""
        method_text = content[node.lineno-1:node.end_lineno]
        
        # Check for state management methods
        if any(keyword in method_text.lower() for keyword in ['save', 'update', 'delete', 'create', 'set_', 'get_']):
            return UnitComponentType.STATE_MANAGEMENT
        
        # Check for validation methods
        if any(keyword in method_text.lower() for keyword in ['validate', 'check', 'verify']):
            return UnitComponentType.VALIDATION_COMPONENT
        
        # Check for business logic methods
        if any(keyword in method_text.lower() for keyword in ['process', 'handle', 'execute', 'perform']):
            return UnitComponentType.BUSINESS_LOGIC
        
        # Default to business logic
        return UnitComponentType.BUSINESS_LOGIC
    
    def _is_pure_function(self, node: ast.FunctionDef, function_text: str) -> bool:
        """Check if a function is pure (no side effects)."""
        # Check for common side effect indicators
        side_effect_keywords = [
            'print', 'log', 'file', 'open', 'write', 'read', 'database', 'db',
            'session', 'request', 'http', 'api', 'email', 'send', 'save'
        ]
        
        return not any(keyword in function_text.lower() for keyword in side_effect_keywords)
    
    def _extract_dependencies(self, node: ast.FunctionDef, content: str) -> List[str]:
        """Extract dependencies from function imports and usage."""
        dependencies = []
        
        # Look for import statements in the file
        try:
            tree = ast.parse(content)
            for item in ast.walk(tree):
                if isinstance(item, ast.Import):
                    for alias in item.names:
                        dependencies.append(alias.name)
                elif isinstance(item, ast.ImportFrom):
                    if item.module:
                        dependencies.append(item.module)
        except:
            pass
        
        return list(set(dependencies))
    
    def _extract_parameters(self, node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """Extract function parameters with type information."""
        parameters = []
        
        for arg in node.args.args:
            param_info = {
                "name": arg.arg,
                "type": "Any",  # Default type
                "required": True
            }
            
            # Check for type annotations
            if arg.annotation:
                param_info["type"] = ast.unparse(arg.annotation)
            
            # Check if it's a self parameter (for methods)
            if arg.arg == "self":
                param_info["required"] = False
            
            parameters.append(param_info)
        
        return parameters
    
    def _extract_return_type(self, node: ast.FunctionDef) -> str:
        """Extract the return type of the function."""
        if node.returns:
            try:
                return ast.unparse(node.returns)
            except AttributeError:
                return type(node.returns).__name__
        return "Any"
    
    def _extract_business_logic(self, node: ast.FunctionDef, content: str) -> str:
        """Extract a description of the business logic from the function."""
        # Look for docstring
        if ast.get_docstring(node):
            return ast.get_docstring(node)
        
        # Look for comments above the function
        lines = content.split('\n')
        if node.lineno > 1:
            comment_lines = []
            for i in range(node.lineno - 2, max(0, node.lineno - 5), -1):
                line = lines[i].strip()
                if line.startswith("#") and line:
                    comment_lines.insert(0, line[1:].strip())
                elif line:
                    break
            
            if comment_lines:
                return ' '.join(comment_lines)
        
        # Default description based on function name
        return "Function {} performs business logic operations".format(node.name)
    
    def _identify_error_conditions(self, node: ast.FunctionDef, content: str) -> List[str]:
        """Identify potential error conditions in the function."""
        error_conditions = []
        function_text = content[node.lineno-1:node.end_lineno].lower()
        
        # Look for common error patterns
        if 'raise' in function_text:
            error_conditions.append("Exception raising")
        
        if 'assert' in function_text:
            error_conditions.append("Assertion failures")
        
        if 'if not' in function_text or 'if not ' in function_text:
            error_conditions.append("Validation failures")
        
        if 'try' in function_text and 'except' in function_text:
            error_conditions.append("Exception handling")
        
        return error_conditions
    
    def _format_signature(self, node: ast.FunctionDef) -> str:
        """Format the function signature for display."""
        args = []
        for arg in node.args.args:
            if arg.annotation:
                # Use a simple string representation for Python 3.7 compatibility
                try:
                    args.append("{}: {}".format(arg.arg, ast.unparse(arg.annotation)))
                except AttributeError:
                    args.append("{}: {}".format(arg.arg, type(arg.annotation).__name__))
            else:
                args.append(arg.arg)
        
        return ", ".join(args)
    
    def _get_default_code_units(self) -> List[CodeUnit]:
        """Return default code units when codebase analysis fails."""
        return [
            CodeUnit(
                name="render_email_template",
                file_path="app/utils.py",
                component_type=UnitComponentType.PURE_FUNCTION,
                signature="render_email_template(*, template_name: str, context: dict[str, Any]) -> str",
                dependencies=["jinja2.Template", "pathlib.Path"],
                return_type="str",
                parameters=[
                    {"name": "template_name", "type": "str", "required": True},
                    {"name": "context", "type": "dict[str, Any]", "required": True}
                ],
                business_logic="Renders email template using Jinja2 with provided context",
                error_conditions=["Template file not found", "Invalid template syntax"]
            ),
            CodeUnit(
                name="authenticate",
                file_path="app/crud.py",
                component_type=UnitComponentType.BUSINESS_LOGIC,
                signature="authenticate(*, session: Session, email: str, password: str) -> User | None",
                dependencies=["Session", "get_user_by_email", "verify_password"],
                return_type="User | None",
                parameters=[
                    {"name": "session", "type": "Session", "required": True},
                    {"name": "email", "type": "str", "required": True},
                    {"name": "password", "type": "str", "required": True}
                ],
                business_logic="Authenticates user credentials against database",
                error_conditions=["User not found", "Invalid password", "Database error"]
            )
        ]
    
    def map_story_to_units(self, user_story: UserStory) -> List[CodeUnit]:
        """Map user story requirements to relevant code units."""
        # Simple keyword-based mapping for demonstration
        # In production, this would use more sophisticated NLP techniques
        
        story_text = "{} {} {}".format(user_story.title, user_story.description, ' '.join(user_story.acceptance_criteria))
        story_text = story_text.lower()
        
        relevant_units = []
        
        for unit in self.code_units:
            # Check if unit name matches story keywords
            if any(keyword in story_text for keyword in unit.name.lower().split('_')):
                relevant_units.append(unit)
            # Check if business logic matches story keywords
            elif any(keyword in story_text for keyword in unit.business_logic.lower().split()):
                relevant_units.append(unit)
            # Check if file path contains relevant keywords
            elif any(keyword in story_text for keyword in unit.file_path.lower().split('/')):
                relevant_units.append(unit)
        
        return relevant_units if relevant_units else self.code_units[:2]  # Default to first 2 units
