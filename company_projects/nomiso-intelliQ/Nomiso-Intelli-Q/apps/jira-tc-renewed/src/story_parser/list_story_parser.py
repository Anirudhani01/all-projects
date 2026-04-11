import json
from src.logger.logger import AppLogger

class UserStoryParser:
    """
    Parses a JSON file containing user story details and extracts:
    - User story (title, description)
    - Acceptance criteria
    - Pre-conditions
    - Post-conditions
    """
    
    def __init__(self, userStory):
        self.userStory = userStory
        self.data = None
        self.count = 0
        self.user_story = {}
        self.acceptance_criteria = []
        self.pre_conditions = []
        self.post_conditions = []
        self.logger = AppLogger(__name__).get_logger()
        self.logger.info(f"Initialized UserStoryParser ")

    def load_data(self):
        """Load and parse the JSON file"""
        # self.logger.info(f"Loading data from : {self.count} UserStory")
        self.count += 1
        try:
            # with open(self.file_path, 'r') as file:
            self.data = self.userStory
            self._parse_components()
            self.logger.info("Successfully loaded and parsed user story data")
        # except FileNotFoundError:
        #     self.logger.error(f"File not found: {self.file_path}", exc_info=True)
        #     raise ValueError(f"File not found: {self.file_path}")
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON format in file", exc_info=True)
            raise ValueError("Invalid JSON format")
        except Exception as e:
            self.logger.error(f"Unexpected error loading file: {str(e)}", exc_info=True)
            raise

    def _parse_components(self):
        """Extract components from parsed JSON data"""
        # self.logger.info("Starting component parsing")
        # print(self.data)
        story_data = self.data.get('user_story', {})
        # self.logger.info("Extracting user story details")
        self.user_story = {
            'id': story_data.get('id'),
            # 'title': story_data.get('title'),
            'story': story_data.get('story'),
            'acceptance_criteria': story_data.get('acceptanceCriteria', [])
        }

        # Extract other components
        # self.logger.info("Extracting pre/post conditions")
        # self.pre_conditions = self.data.get('pre_conditions', [])
        # self.post_conditions = self.data.get('post_conditions', [])

        # self.logger.info(f"Parsed components: {len(self.acceptance_criteria)} acceptance criteria ")
                    #    f"{len(self.pre_conditions)} pre-conditions, "
                    #    f"{len(self.post_conditions)} post-conditions")

    def get_user_story(self) -> str:
        """Return complete user story structure"""
        # self.logger.info("Retrieving full user story structure")
        return self.user_story

    # def get_story_title(self) -> str:
    #     """Return user story title"""
    #     self.logger.info("Retrieving story title")
    #     return self.user_story.get('title')

    def get_story_text(self) -> str:
        """Return user story description"""
        # self.logger.info("Retrieving story text")
        return self.user_story.get('story')

    def get_acceptance_criteria(self) -> list[str]:
        """Return list of acceptance criteria"""
        # self.logger.info("Retrieving acceptance criteria")
        return self.user_story.get('acceptance_criteria', [])

    # def get_pre_conditions(self) -> list[str]:
    #     """Return list of pre-conditions"""
    #     self.logger.info("Retrieving pre-conditions")
    #     return self.pre_conditions

    # def get_post_conditions(self) -> list[str]:
    #     """Return list of post-conditions"""
    #     self.logger.info("Retrieving post-conditions")
    #     return self.post_conditions
    
    def get_story_id(self) -> str:
        """Return the id of the user story"""
        # self.logger.info("Retrieving story ID")
        return self.user_story.get('id')
# Example usage
if False:
    try:
        parser = UserStoryParser("train/user_test1.json")
        parser.load_data()
        
        print("User story Id:", parser.get_story_id())
        print("User Story Title:", parser.get_story_title())
        print("\nStory Description:", parser.get_story_description())
        print("\nAcceptance Criteria:")
        for idx, criterion in enumerate(parser.get_acceptance_criteria(), 1):
            print(f"{idx}. {criterion}")
            
        print("\nPre-conditions:")
        for idx, condition in enumerate(parser.get_pre_conditions(), 1):
            print(f"{idx}. {condition}")
            
        print("\nPost-conditions:")
        for idx, condition in enumerate(parser.get_post_conditions(), 1):
            print(f"{idx}. {condition}")
            
    except Exception as e:
        print(f"Error: {str(e)}")