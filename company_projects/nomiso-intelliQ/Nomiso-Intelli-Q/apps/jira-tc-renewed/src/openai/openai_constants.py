from enum import Enum
from src.configuration.config import Constant


class OpenAIConstants():

    O1_CONFIG = {'model': 'o1', 'timeout': 180, 'reasoning_effort': 'medium'}
    O1_MINI_CONFIG = {'model': 'o1-mini', 'timeout': 180, 'reasoning_effort': 'high'}
    O3_MINI_CONFIG = {'model': 'o3-mini', 'timeout': 180, 'reasoning_effort': 'high'}
    OPENAI_GPT_4O_CONFIG = {'model': 'gpt-4o', 'max_tokens': 16000, 'timeout': 180}
    OPENAI_GPT_4O_MINI_CONFIG = {'model': 'gpt-4o-mini', 'max_tokens': 16000, 'timeout': 180}
    O4_MINI_CONFIG = {'model': 'o4-mini', 'timeout': 180, 'reasoning_effort': 'high'}
    GPT_41_CONFIG = {'model': 'gpt-4.1','max_tokens': 16000, 'timeout': 180 }

    @staticmethod
    def get_model(agent: str):
        if agent == Constant.OPENAIO1AGENT.value:
            model_architecture = {
                'user_story_llm': OpenAIConstants.O1_CONFIG,
            }
        elif agent == Constant.OPENAIO1MINIAGENT.value:
            model_architecture = {
                'user_story_llm': OpenAIConstants.O1_MINI_CONFIG,
            }
        elif agent == Constant.OPENAIO3MINIAGENT.value:
            model_architecture = {
                'user_story_llm': OpenAIConstants.O3_MINI_CONFIG,
            }
        elif agent == Constant.OPENAIGPT4OAGENT.value:
            model_architecture = {
                'user_story_llm': OpenAIConstants.OPENAI_GPT_4O_CONFIG,
            }
        elif agent == Constant.OPENAIO4MINIAGENT.value:
            model_architecture = {
                'user_story_llm': OpenAIConstants.O4_MINI_CONFIG,
            }
        elif agent == Constant.GPT_41_CONFIG.value:
            model_architecture = {
                'user_story_llm': OpenAIConstants.GPT_41_CONFIG,
            }
        else:
            model_architecture = {
                'user_story_llm': OpenAIConstants.OPENAI_GPT_4O_MINI_CONFIG,
            }
        return model_architecture
