import os
import javalang
from typing import List
from common.agent_state import AgentState
from central_logger.logger import get_logger

logger = get_logger(__name__)

def parse_input(state: AgentState) -> AgentState:
    """
    Parse Java file and extract package, imports, and methods
    """
    logger.info(f" Parsing Java file: {state['file_path']}")
    
    try:
        if not os.path.exists(state['file_path']):
            raise FileNotFoundError(f"File not found: {state['file_path']}")
        
        with open(state['file_path'], 'r', encoding='utf-8') as f:
            java_code = f.read()
        
        # Parse Java code
        tree = javalang.parse.parse(java_code)
        
        # Extract package
        package = tree.package.name if tree.package else ""
        
        # Extract imports
        imports = []
        for imp in tree.imports:
            imports.append(f"import {imp.path};")
        
        # Extract methods
        methods = []
        for type_decl in tree.types:
            if isinstance(type_decl, javalang.tree.ClassDeclaration):
                for method in type_decl.methods:
                    # Extract method with its context
                    method_info = {
                        'name': method.name,
                        'signature': _extract_method_signature(method),
                        'line_start': method.position.line if method.position else 0,
                        'modifiers': method.modifiers,
                        'return_type': str(method.return_type) if method.return_type else 'void'
                    }
                    methods.append(method_info)
        
        # Update state
        state['package'] = package
        state['imports'] = '\n'.join(imports)
        state['methods'] = methods
        
        logger.info(f" Successfully parsed {len(methods)} methods from {state['file_path']}")
        return state
        
    except Exception as e:
        logger.error(f" Error parsing Java file: {e}")
        state['validation_errors'] = [f"Parse error: {str(e)}"]
        return state

def _extract_method_signature(method):
    """Extract method signature as string"""
    modifiers = ' '.join(method.modifiers) if method.modifiers else ''
    return_type = str(method.return_type) if method.return_type else 'void'
    params = ', '.join([f"{p.type} {p.name}" for p in method.parameters]) if method.parameters else ''
    
    return f"{modifiers} {return_type} {method.name}({params})".strip()

