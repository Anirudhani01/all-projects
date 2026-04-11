import requests
from src.logger.logger import AppLogger

class UserStoryParser:
    def __init__(self, adf, issue_id, title):
        self.logger = AppLogger(__name__).get_logger()
        self.logger.info("Initializing UserStoryParser for fetching stories from JIRA API ...")
        self.adf = adf
        self.issue_id = issue_id
        self.title = title
        self.paragraphs = self._extract_paragraphs()
        self.logger.info(f"Extracted {len(self.paragraphs)} paragraph(s) from ADF.")

    def _extract_paragraphs(self):
        output = []
        try:
            for block in self.adf:
                block_type = block.get("type")
                content = block.get("content", [])

                if block_type in ["heading", "paragraph"]:
                    text = ''.join([c.get("text", "") for c in content if c.get("type") == "text"])
                    if text:
                        output.append(text.strip())
                elif block_type == "bulletList":
                    for item in block.get("content", []):
                        for p in item.get("content", []):
                            bullet_text = ''.join([c.get("text", "") for c in p.get("content", []) if c.get("type") == "text"])
                            if bullet_text:
                                output.append(f"- {bullet_text}")
        except Exception as e:
            self.logger.error(f"Error while extracting paragraphs: {str(e)}", exc_info=True)

        return output

    def parse(self):
        self.logger.info(f"Parsing user story for issue {self.issue_id} - {self.title}")

        story = ""
        acceptance_criteria = []
        current_section = None

        try:
            for line in self.paragraphs:
                normalized = line.strip().lower()

                if "acceptance criteria" in normalized:
                    current_section = "acceptance_criteria"
                    continue
                elif "user story" in normalized or normalized.startswith("as a"):
                    current_section = "user_story"
                    story = line.replace("User Story", "").strip()
                    continue

                if current_section == "user_story" and story == "":
                    story = line.strip()
                elif current_section == "acceptance_criteria":
                    acceptance_criteria.append(line.lstrip("-").strip())

            result = {
                "user_story": {
                    "id": self.issue_id,
                    # "title": self.title,
                    "story": self.title,
                    "acceptanceCriteria": acceptance_criteria
                }
            }

            self.logger.info(f"Successfully parsed story: {self.issue_id}")
            return result

        except Exception as e:
            self.logger.error(f"Error during user story parsing: {str(e)}", exc_info=True)
            return {}
