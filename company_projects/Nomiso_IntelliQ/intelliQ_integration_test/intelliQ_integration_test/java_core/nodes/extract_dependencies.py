import os
import re
import javalang
from common.agent_state import AgentState
from central_logger.logger import get_logger

logger = get_logger(__name__)

def extract_dependencies(state: AgentState) -> AgentState:
    """
    Extract internal and external dependency code based on analysis
    """
    logger.info(" Extracting dependencies")
    
    analysis = state.get('analysis', {})
    internal_calls = analysis.get('internal_calls', [])
    external_dependencies = normalize_dependencies(analysis.get('external_dependencies', []))
    
    # Extract internal dependencies
    internal_code = _extract_internal_dependencies(state['file_path'], internal_calls)
    
    # Extract external dependencies
    external_code = _extract_external_dependencies(state, external_dependencies)
    
    state['internal_code'] = internal_code
    state['external_code'] = external_code
    
    logger.info(f" Extracted {len(internal_calls)} internal and {len(external_dependencies)} external dependencies")
    

        
    return state


# -----------------------------
# 🔹 Normalization Helpers
# -----------------------------
def normalize_class_name(class_name: str) -> str:
    """
    Normalize class names to PascalCase.
    Example:
        studentService -> StudentService
        orderRepo -> OrderRepo
        cust_mgr -> CustMgr
    """
    if not class_name:
        return class_name

    # Already PascalCase
    if class_name[0].isupper():
        return class_name

    parts = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?![a-z])', class_name)
    normalized = ''.join(part.capitalize() for part in parts)
    return normalized


def normalize_dependencies(dependencies: list) -> list:
    """
    Normalize external dependency class names and fix FQNs.
    """
    for dep in dependencies:
        cls = dep.get("class")
        if cls:
            new_cls = normalize_class_name(cls)
            dep["class"] = new_cls

            if "fully_qualified_name" in dep and dep["fully_qualified_name"]:
                pkg, _, _ = dep["fully_qualified_name"].rpartition(".")
                dep["fully_qualified_name"] = f"{pkg}.{new_cls}"
    return dependencies


# -----------------------------
# 🔹 Extraction Logic
# -----------------------------
def _extract_internal_dependencies(file_path, internal_calls):
    """Extract internal method dependencies from the same file"""
    if not internal_calls:
        return ""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            java_code = f.read()
        
        lines = java_code.splitlines()
        tree = javalang.parse.parse(java_code)
        
        internal_methods = []
        for type_decl in tree.types:
            if isinstance(type_decl, javalang.tree.ClassDeclaration):
                for method in type_decl.methods:
                    if method.name in internal_calls:
                        method_code = _extract_method_lines_simple(lines, method)
                        if method_code:
                            internal_methods.append(f"// Internal method: {method.name}\n{method_code}")
        
        return "\n\n" + "="*80 + "\n\n".join(internal_methods)
        
    except Exception as e:
        logger.error(f"Error extracting internal dependencies: {e}")
        return ""


def _extract_external_dependencies(state, external_dependencies):
    """Extract external dependency code"""
    if not external_dependencies:
        return ""
    
    external_methods = []
    
    for dep in external_dependencies:
        if not dep.get('extract_code', False):
            continue
        
        class_name = dep.get('class', '')
        fqn = dep.get('fully_qualified_name', '')
        methods_called = dep.get('methods_called', [])
        
        # Try to find the Java file
        java_file_path = _find_java_file_by_fqn(fqn, state['file_path'])
        
        if java_file_path:
            extracted_code = _extract_methods_from_file(java_file_path, methods_called)
            if extracted_code:
                external_methods.append(f"// External class: {class_name}\n{extracted_code}")
    
    return "\n\n" + "="*80 + "\n\n".join(external_methods)


def _extract_method_lines_simple(lines, method):
    """Simple method extraction"""
    start_line = method.position.line - 1
    method_lines = []
    brace_count = 0
    method_started = False
    
    for line_idx in range(start_line, len(lines)):
        line = lines[line_idx]
        method_lines.append(line)
        
        open_braces = line.count('{')
        close_braces = line.count('}')
        brace_count += open_braces - close_braces
        
        if open_braces > 0:
            method_started = True
        
        if method_started and brace_count == 0:
            break
    
    return '\n'.join(method_lines)


def _find_java_file_by_fqn(fqn, current_file_path):
    """Find Java file by fully qualified name (with case correction + recursive search)"""
    search_paths = [
        "src/main/java",
        "src/test/java",
        "src/java",
        os.path.dirname(current_file_path),
        "."  # project root
    ]

    def try_resolve(fqn_try):
        relative_path = fqn_try.replace('.', os.sep) + '.java'
        for search_path in search_paths:
            full_path = os.path.join(search_path, relative_path)
            if os.path.exists(full_path):
                return full_path
        return None

    # 1. Try as-is
    result = try_resolve(fqn)
    if result:
        return result

    # 2. Retry with corrected class case (e.g. studentService -> StudentService)
    pkg, _, cls = fqn.rpartition('.')
    if cls and not cls[0].isupper():
        corrected_fqn = pkg + '.' + cls[0].upper() + cls[1:]
        result = try_resolve(corrected_fqn)
        if result:
            logger.info(f" Resolved FQN with case fix: {corrected_fqn} → {result}")
            return result

    # 3. Recursive fallback: walk entire project directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(current_file_path), ".."))
    class_name = cls[0].upper() + cls[1:] if cls else None
    for root, _, files in os.walk(project_root):
        for file in files:
            if file == f"{class_name}.java":
                candidate = os.path.join(root, file)
                logger.info(f" Found {class_name}.java via recursive search: {candidate}")
                return candidate

    logger.warning(f" Could not locate Java file for FQN: {fqn}")
    return None


def _extract_methods_from_file(java_file_path, method_names):
    """Extract specific methods from a Java file"""
    try:
        with open(java_file_path, 'r', encoding='utf-8') as f:
            java_code = f.read()
        
        lines = java_code.splitlines()
        tree = javalang.parse.parse(java_code)
        
        extracted_methods = []
        for type_decl in tree.types:
            if isinstance(type_decl, javalang.tree.ClassDeclaration):
                for method in type_decl.methods:
                    if method.name in method_names:
                        method_code = _extract_method_lines_simple(lines, method)
                        if method_code:
                            extracted_methods.append(f"// Method: {method.name}\n{method_code}")
        
        return "\n\n".join(extracted_methods)
        
    except Exception as e:
        logger.error(f"Error extracting methods from {java_file_path}: {e}")
        return ""


# -----------------------------
# 🔹 Enhanced Method Extraction (for test generation)
# -----------------------------
def extract_method_code(file_path, method_name):
    """Extract specific method code from Java file (public interface)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            java_code = f.read()

        lines = java_code.splitlines()
        tree = javalang.parse.parse(java_code)

        for type_decl in tree.types:
            if isinstance(type_decl, javalang.tree.ClassDeclaration):
                for method in type_decl.methods:
                    if method.name == method_name:
                        return _extract_method_lines_enhanced(lines, method)

        return None

    except Exception as e:
        logger.error(f"Error extracting method code: {e}")
        return None


def _extract_method_lines_enhanced(lines, method):
    """Extract method lines including JavaDoc and annotations"""
    start_line = method.position.line - 1
    method_lines = []

    # Extract JavaDoc and annotations
    i = start_line - 1
    comment_and_annotation_lines = []

    while i >= 0:
        line = lines[i].strip()
        if line == "":
            i -= 1
            continue
        if line.startswith("//") or line.startswith("@"):
            comment_and_annotation_lines.insert(0, lines[i])
            i -= 1
            continue
        if line.endswith("*/"):
            javadoc_lines = [lines[i]]
            i -= 1
            while i >= 0:
                javadoc_lines.insert(0, lines[i])
                if lines[i].strip().startswith("/**"):
                    break
                i -= 1
            comment_and_annotation_lines = javadoc_lines + comment_and_annotation_lines
            i -= 1
            continue
        if line.startswith("*") and not line.startswith("*/"):
            comment_and_annotation_lines.insert(0, lines[i])
            i -= 1
            continue
        break

    method_lines.extend(comment_and_annotation_lines)

    # Add method signature and body
    brace_count = 0
    method_started = False

    for line_idx in range(start_line, len(lines)):
        line = lines[line_idx]
        method_lines.append(line)
        open_braces = line.count('{')
        close_braces = line.count('}')
        brace_count += open_braces - close_braces
        if open_braces > 0:
            method_started = True
        if method_started and brace_count == 0:
            break

    return '\n'.join(method_lines)

def generate_test_file_path(state: AgentState, flow_name: str) -> str:
    """Generate test file path, enforcing IntegrationTest suffix."""
    original_path = state.get('file_path', '')
    if not original_path:
        logger.error("Original file path is empty")
        return ""

    normalized_path = original_path.replace('\\', '/')
    if 'src/main/java' in normalized_path:
        test_path = normalized_path.replace('src/main/java', 'src/test/java')
    else:
        package_parts = normalized_path.split('/')
        if 'org' in package_parts:
            org_idx = package_parts.index('org')
            package_path = '/'.join(package_parts[org_idx:])
            test_path = f"src/test/java/{package_path}"
        else:
            test_path = f"src/test/java/{os.path.basename(normalized_path)}"

    if '\\' in original_path:
        test_path = test_path.replace('/', '\\')

    base_dir = os.path.dirname(test_path)
    filename = f"{flow_name}IntegrationTest.java"
    return os.path.join(base_dir, filename)