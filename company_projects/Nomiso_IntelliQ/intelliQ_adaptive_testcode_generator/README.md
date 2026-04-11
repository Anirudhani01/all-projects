# IntelliQ Adaptive Test Code Generator

This project provides a unified framework for generating and executing automated test scripts for both Appium (mobile) and Selenium (web) platforms using AI-driven code generation.

## Features

- Generate test scripts for Appium (mobile) and Selenium (web) from structured test case data.
- Modular architecture for easy extension and maintenance.
- Utilities for locator extraction, script management, and test execution.
- Unified entry point for both frameworks via `main.py`.

## Folder Structure

```
.
├── appium/                      # Appium-specific script generation and utilities
├── selenium_script_generator/   # Selenium-specific script generation and locator extraction
├── test_framework/              # Core framework, generators, runners, and utilities
├── main.py                      # Unified entry point for script generation
├── requirements.txt             # Python dependencies
├── .gitignore
└── README.md
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd intelliQ_adaptive_testcode_generator
   ```

2. **Set up a Python virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   - Create a `.env` file in the project root or relevant subfolders as needed.
   - Add required API keys and configuration (e.g., `OPENAI_API_KEY`, Appium/Selenium server URLs).

## Usage

Run the unified entry point to generate scripts for either Appium or Selenium:

```bash
# For Appium script generation
python main.py --framework appium

# For Selenium script generation
python main.py --framework selenium
```

Additional arguments may be required depending on your test case data and configuration. Refer to the documentation in `test_framework/appium_test_generator.py` and `selenium_script_generator/selenium_test_generator.py` for advanced usage.

## Configuration

- Place your test case JSON files and locator files in the appropriate directories as required by each framework.
- Update `.env` files with necessary credentials and settings.

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements or bug fixes.

## License

[MIT License](LICENSE) (or specify your license here)
