from enum import Enum

class Constant(Enum):
    OPENAI = "openai"
    OPENAIO1AGENT = "openai-o1"
    OPENAIO1MINIAGENT = "openai-o1-mini"
    OPENAIO3MINIAGENT = "openai-o3-mini"
    OPENAIGPT4OAGENT = "openai-gpt-4o"
    OPENAIGPT4OMINIAGENT = "openai-gpt-4o-mini"
    LOGGERNAME = "TestCaseGenerator"
    OPENAIO4MINIAGENT = "openai-o4-mini"
    GPT_41_CONFIG = "openai-gpt-4.1"

    # CLAUDE = "claude"
    # CLAUDE35SONNET = "claude-3-5-sonnet"
    # CLAUDE37SONNET = "claude-3-7-sonnet"