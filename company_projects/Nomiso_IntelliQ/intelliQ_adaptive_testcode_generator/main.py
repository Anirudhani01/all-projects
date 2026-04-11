import argparse
import sys

def run_appium(args):
    # Import here to avoid unnecessary dependencies if not used
    from test_framework.appium_test_generator import main as appium_main
    appium_main()

def run_selenium(args):
    from selenium_script_generator.selenium_test_generator import main as selenium_main
    selenium_main()

def main():
    parser = argparse.ArgumentParser(
        description="Unified entry point for Appium and Selenium script generation."
    )
    parser.add_argument(
        "--framework",
        choices=["appium", "selenium"],
        required=True,
        help="Choose which framework's script generation to run."
    )
    # Optionally, add more arguments here and pass them to the respective main functions

    args, unknown = parser.parse_known_args()

    if args.framework == "appium":
        run_appium(args)
    elif args.framework == "selenium":
        run_selenium(args)
    else:
        print("Unknown framework selected.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
