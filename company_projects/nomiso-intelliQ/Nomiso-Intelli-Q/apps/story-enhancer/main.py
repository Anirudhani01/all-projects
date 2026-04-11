from core.story_processor import StoryProcessor

def main():
    """
    Main entry point for the story processing application.

    This function initializes the StoryProcessor and triggers the processing
    of all documents in the configured input directory.
    """
    processor = StoryProcessor()
    processor.process_all_documents()

if __name__ == "__main__":
    main()