import os
import json
from pathlib import Path
from typing import List, Dict
from src.logger.logger import AppLogger  # Import your logger

class FileManager:
    logger = AppLogger(__name__).get_logger()

    @staticmethod
    def __ignore_file_on_name(filenames: List[str], file_ignore_list: List[str]) -> List[str]:
        try:
            filtered = [f for f in filenames if not any(ignored in f for ignored in file_ignore_list)]
            FileManager.logger.info(f"Ignored files by name filter: {file_ignore_list}, remaining files: {len(filtered)}")
            return filtered
        except Exception as e:
            FileManager.logger.error(f"File filtering by name failed: {e}", exc_info=True)
            return filenames

    @staticmethod
    def __ignore_file_on_ext(filenames: List[str], ext_ignore_list: List[str]) -> List[str]:
        try:
            filtered = [f for f in filenames if Path(f).suffix not in ext_ignore_list]
            FileManager.logger.info(f"Ignored files by extension filter: {ext_ignore_list}, remaining files: {len(filtered)}")
            return filtered
        except Exception as e:
            FileManager.logger.error(f"File filtering by extension failed: {e}", exc_info=True)
            return filenames
        
    @staticmethod
    def get_user_story_files(source_dir: str) -> list:
        try:
            files = [str(f) for f in Path(source_dir).glob("*.json")]
            FileManager.logger.info(f"Found {len(files)} user story JSON files in {source_dir}")
            return files
        except Exception as error:
            FileManager.logger.error(f"Error listing user stories: {error}", exc_info=True)
            return []

    @staticmethod
    def get_filtered_files(env_config: Dict, source_path: str) -> List[str]:
        try:
            file_paths = []
            dir_ignore_list = env_config.get('ignore', {}).get('ignore_dir', [])
            file_ignore_list = env_config.get('ignore', {}).get('ignore_file', [])
            ext_ignore_list = env_config.get('ignore', {}).get('ignore_ext', [])

            FileManager.logger.info(f"Applying ignore filters - dirs: {dir_ignore_list}, files: {file_ignore_list}, extensions: {ext_ignore_list}")

            for dirpath, _, filenames in os.walk(source_path):
                if any(ignored_dir in dirpath for ignored_dir in dir_ignore_list):
                    FileManager.logger.info(f"Ignoring directory: {dirpath}")
                    continue

                filtered_files = FileManager.__ignore_file_on_name(filenames, file_ignore_list)
                filtered_files = FileManager.__ignore_file_on_ext(filtered_files, ext_ignore_list)
                full_paths = [os.path.join(dirpath, f) for f in filtered_files]
                FileManager.logger.info(f"Adding {len(full_paths)} files from {dirpath}")
                file_paths.extend(full_paths)

            FileManager.logger.info(f"Total filtered files found: {len(file_paths)}")
            return file_paths
        except Exception as e:
            FileManager.logger.error(f"Error getting filtered files: {e}", exc_info=True)
            return []

    @staticmethod
    def read_json(file_path: str) -> Dict:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            FileManager.logger.info(f"Successfully read JSON file: {file_path}")
            return data
        except Exception as e:
            FileManager.logger.error(f"Failed to read JSON file {file_path}: {e}", exc_info=True)
            return {}

    @staticmethod
    def save_json(file_path: str, content: Dict) -> None:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=4, ensure_ascii=False)
            FileManager.logger.info(f"Saved JSON file: {file_path}")
        except Exception as e:
            FileManager.logger.error(f"Failed to save JSON file {file_path}: {e}", exc_info=True)

    @staticmethod
    def save_test_cases_by_id(output_dir: str, test_case_id: str, content: Dict) -> str:
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            file_path = output_path / f"{test_case_id}_test_cases.json"
            FileManager.save_json(str(file_path), content)
            FileManager.logger.info(f"Saved test cases for ID '{test_case_id}' at '{file_path}'")
            return str(file_path)
        except Exception as e:
            FileManager.logger.error(f"Failed to save test cases for {test_case_id}: {e}", exc_info=True)
            return ""

# Example usage
if False:
    env_config = {
        "ignore": {
            "ignore_dir": [".git", "__pycache__"],
            "ignore_file": ["temp", "backup"],
            "ignore_ext": [".tmp", ".bak"]
        }
    }
    source_dir = "train"
    output_dir = "prompts"

    files = FileManager.get_filtered_files(env_config, source_dir)
    FileManager.logger.info(f"Found {len(files)} user story files.")

    for file_path in files:
        data = FileManager.read_json(file_path)
        if not data:
            continue

        user_story_id = data.get("user_story", {}).get("id", "unknown_id")
        # Example: generate test cases here (replace with your logic)
        test_cases = {"test_cases_for": user_story_id, "cases": []}

        saved_path = FileManager.save_test_cases_by_id(output_dir, user_story_id, test_cases)
        FileManager.logger.info(f"Test cases saved to: {saved_path}")
