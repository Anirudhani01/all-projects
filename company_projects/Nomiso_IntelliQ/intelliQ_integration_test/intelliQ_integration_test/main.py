import sys 
import argparse
import os
from dotenv import load_dotenv
from base_factory.test_generator_factory import TestGeneratorFactory

def validate_env():
    """Ensure required environment variables are set and valid."""
    required_vars = ["OPENAI_API_KEY", "MODEL", "TEMPERATURE", "MAX_TOKENS"]
    missing = [var for var in required_vars if var not in os.environ]
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

def main():
    # Load environment variables from current directory (where main.py and .env are both located)
    load_dotenv()
    
    # Handle both uppercase and lowercase variable names
    if 'model' in os.environ and 'MODEL' not in os.environ:
        os.environ['MODEL'] = os.environ['model']
    if 'temperature' in os.environ and 'TEMPERATURE' not in os.environ:
        os.environ['TEMPERATURE'] = os.environ['temperature']
    if 'max_tokens' in os.environ and 'MAX_TOKENS' not in os.environ:
        os.environ['MAX_TOKENS'] = os.environ['max_tokens']
    
    # Validate env config before continuing
    try:
        validate_env()
    except Exception as e:
        print(f" Error: {e}")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description="AI-Powered Multi-Language Integration Test Generator")
    parser.add_argument("--file", required=True, help="Path to source file")
    
    args = parser.parse_args()
    
    # Validate file exists
    if not os.path.exists(args.file):
        print(f" Error: File not found: {args.file}")
        sys.exit(1)
    
    # Detect language from file extension
    file_extension = os.path.splitext(args.file)[1].lower()
    
    if file_extension == '.java':
        lang = 'java'
    else:
        print(f" Error: Unsupported file type '{file_extension}'. Currently only .java files are supported")
        sys.exit(1)
    
    print(f"\n Starting {lang.title()} Test Generator")
    print(f" Target file: {args.file}")
    print(f" Language: {lang}")
    print(f" Mode: Fully Automated")
    
    try:
        # Create appropriate agent using factory
        agent = TestGeneratorFactory.create_agent(lang)
        
        # Generate test (fully automated)
        result = agent.generate_and_execute(args.file)
        
        if not result['success']:
            print(f"\n Failed to generate test:")
            for error in result.get('errors', []):
                print(f"  - {error}")
            sys.exit(1)
        
        # Final summary
        state = result.get('result', {})
        print(f"\n Success! Integration test generated and executed!")
        print(f" Test file: {state.get('test_file_path', 'Unknown')}")
        
        completed = state.get('completed_methods', [])
        skipped = state.get('skipped_methods', [])
        
        if completed:
            print(f" Completed methods: {completed}")
        if skipped:
            print(f" Skipped methods (due to retry limit): {skipped}")
        
        total = len(state.get('methods', []))
        done = len(completed)
        skip = len(skipped)
        print(f" Processing summary: {done} completed, {skip} skipped out of {total} total methods")
        
        print(f" You can now run your integration test with JUnit 5")
            
        sys.exit(0)
        
    except KeyboardInterrupt:
        print("\n Test generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f" Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
