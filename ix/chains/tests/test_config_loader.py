from copy import deepcopy
from pathlib import Path

import pytest
from unittest.mock import MagicMock

from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import LanguageParser
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import TextSplitter
from langchain.vectorstores import Redis

from ix.chains.fixture_src.agents import OPENAI_FUNCTIONS_AGENT_CLASS_PATH
from ix.chains.fixture_src.chains import CONVERSATIONAL_RETRIEVAL_CHAIN_CLASS_PATH
from ix.chains.fixture_src.document_loaders import GENERIC_LOADER_CLASS_PATH
from ix.chains.fixture_src.embeddings import OPENAI_EMBEDDINGS_CLASS_PATH
from ix.chains.fixture_src.parsers import LANGUAGE_PARSER_CLASS_PATH
from ix.chains.fixture_src.text_splitter import RECURSIVE_CHARACTER_SPLITTER_CLASS_PATH
from ix.chains.fixture_src.vectorstores import (
    REDIS_VECTORSTORE_CLASS_PATH,
)
from ix.chains.loaders.context import IxContext
from langchain.agents import AgentExecutor
from langchain.base_language import BaseLanguageModel
from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryBufferMemory,
    CombinedMemory,
)
from langchain.schema import BaseChatMessageHistory, BaseMemory
from langchain.tools import BaseTool

from ix.chains.fixture_src.tools import GOOGLE_SEARCH
from ix.chains.loaders.memory import get_memory_session
from ix.chains.loaders.text_splitter import TextSplitterShim
from ix.chains.loaders.tools import extract_tool_kwargs
from ix.chains.tests.mock_memory import MockMemory
from ix.memory.artifacts import ArtifactMemory


class TestLoadLLM:
    pass


OPENAI_LLM = {
    "class_path": "langchain.chat_models.openai.ChatOpenAI",
    "config": {"verbose": True},
}

MOCK_MEMORY = {
    "class_path": "ix.chains.tests.mock_memory.MockMemory",
    "config": {"value_map": {"mock_memory_input": "mock memory"}},
}

MEMORY = {
    "class_path": "langchain.memory.ConversationBufferMemory",
    "config": {
        "input_key": "user_input",
        "memory_key": "chat_history",
    },
}

MEMORY_WITH_BACKEND = {
    "class_path": "langchain.memory.ConversationBufferMemory",
    "config": {
        "input_key": "user_input",
        "memory_key": "chat_history",
        "chat_memory": {
            "class_path": "langchain.memory.RedisChatMessageHistory",
            "config": {"url": "redis://redis:6379/0", "session_scope": "task"},
        },
    },
}

MEMORY_WITH_LLM = {
    "class_path": "langchain.memory.summary_buffer.ConversationSummaryBufferMemory",
    "config": {
        "input_key": "user_input",
        "memory_key": "chat_summary",
        "llm": {
            "class_path": "langchain.chat_models.openai.ChatOpenAI",
        },
    },
}

AGENT_MEMORY = {
    "class_path": "langchain.memory.ConversationBufferMemory",
    "config": {
        "input_key": "user_input",
        "memory_key": "chat_history",
        # agent requires return_messages=True
        "return_messages": True,
    },
}

MEMORY_WITH_SCOPE = {
    "class_path": "ix.memory.artifacts.ArtifactMemory",
    "config": {
        "memory_key": "chat_history",
        "session_scope": "chat",
        "session_prefix": "tests",
    },
}

CHAT_MESSAGES = [
    {
        "role": "system",
        "template": "You are a test bot.",
    },
    {
        "role": "user",
        "template": "{user_input}",
        "input_variables": ["user_input"],
    },
]

CHAT_MESSAGES_WITH_CHAT_HISTORY = [
    {
        "role": "system",
        "template": "You are a test bot! HISTORY: {chat_history}",
        "input_variables": ["chat_history"],
    },
    {
        "role": "user",
        "template": "{user_input}",
        "input_variables": ["user_input"],
    },
]

PROMPT_CHAT = {
    "class_path": "langchain.prompts.chat.ChatPromptTemplate",
    "config": {
        "messages": CHAT_MESSAGES,
    },
}

PROMPT_WITH_CHAT_HISTORY = {
    "class_path": "langchain.prompts.chat.ChatPromptTemplate",
    "config": {
        "messages": CHAT_MESSAGES_WITH_CHAT_HISTORY,
    },
}

LLM_CHAIN = {
    "class_path": "ix.chains.llm_chain.LLMChain",
    "config": {
        "prompt": PROMPT_CHAT,
        "llm": {
            "class_path": "langchain.chat_models.openai.ChatOpenAI",
        },
    },
}

LLM_REPLY = {
    "class_path": "ix.chains.llm_chain.LLMReply",
    "config": {
        "prompt": PROMPT_CHAT,
        "llm": {
            "class_path": "langchain.chat_models.openai.ChatOpenAI",
        },
    },
}

LLM_REPLY_WITH_HISTORY = {
    "class_path": "ix.chains.llm_chain.LLMReply",
    "config": {
        "prompt": PROMPT_WITH_CHAT_HISTORY,
        "llm": {
            "class_path": "langchain.chat_models.openai.ChatOpenAI",
        },
    },
}

LLM_REPLY_WITH_HISTORY_AND_MEMORY = {
    "class_path": "ix.chains.llm_chain.LLMReply",
    "config": {
        "prompt": PROMPT_WITH_CHAT_HISTORY,
        "memory": MEMORY,
        "llm": {
            "class_path": "langchain.chat_models.openai.ChatOpenAI",
        },
    },
}


@pytest.mark.django_db
class TestLoadMemory:
    def test_load_memory(self, load_chain):
        instance = load_chain(MEMORY)
        assert isinstance(instance, ConversationBufferMemory)

    def test_load_multiple(self, load_chain, mock_openai_key):
        """Test loading multiple memories into a CombinedMemory"""
        MEMORY2 = deepcopy(MEMORY)
        MEMORY2["config"]["memory_key"] = "chat_history2"

        LLM_CONFIG = deepcopy(LLM_REPLY_WITH_HISTORY)
        LLM_CONFIG["config"]["memory"] = [MEMORY, MEMORY2]
        chain = load_chain(LLM_CONFIG)
        instance = chain.memory
        assert isinstance(instance, CombinedMemory)
        assert len(instance.memories) == 2
        assert instance.memories[0].memory_key == "chat_history"
        assert instance.memories[1].memory_key == "chat_history2"

    def test_load_backend(self, load_chain):
        """
        A memory class can have a backend that separates memory logic from
        the storage system. ChatMemory works this way.
        """
        instance = load_chain(MEMORY_WITH_BACKEND)
        assert isinstance(instance, ConversationBufferMemory)
        assert isinstance(instance.chat_memory, BaseChatMessageHistory)

    def test_load_memory_with_scope(self, chat, load_chain):
        """
        Test loading with a scope.

        Not all memories support sessions, for example ChatMemory
        adds scoping to the backend.
        """
        chat = chat["chat"]
        chat_id = chat.task.leading_chats.first().id
        instance = load_chain(MEMORY_WITH_SCOPE)
        assert isinstance(instance, ArtifactMemory)
        assert instance.session_id == f"tests_chat_{chat_id}"

    def test_load_llm(self, load_chain, mock_openai):
        """
        Memory classes may optionally load an llm. (e.g. SummaryMemory)
        """
        instance = load_chain(MEMORY_WITH_LLM)
        assert isinstance(instance, ConversationSummaryBufferMemory)
        assert isinstance(instance.llm, BaseLanguageModel)

    def test_load_class_with_config(self, chat, mocker, load_chain):
        """
        Test loading a class whose config is defined in MEMORY_CLASSES.
        This tests configuring an external class with the required config
        to integrate into Ix
        """
        chat = chat["chat"]
        chat_id = chat.task.leading_chats.first().id

        # patch MEMORY_CLASSES to setup the test
        from ix.chains.loaders import memory

        mock_memory_classes = {
            MockMemory: {
                "supports_session": True,
            }
        }
        mocker.patch.object(memory, "MEMORY_CLASSES", mock_memory_classes)

        # load a memory that will use the mock class config
        instance = load_chain(
            {
                "class_path": "ix.chains.tests.mock_memory.MockMemory",
                "config": {
                    "session_scope": "chat",
                    "session_prefix": "tests",
                },
            },
        )
        assert isinstance(instance, MockMemory)
        assert instance.session_id == f"tests_chat_{chat_id}"


@pytest.mark.django_db
class TestLoadChatMemoryBackend:
    def test_load_chat_memory_backend(self, chat, load_chain):
        chat = chat["chat"]
        chat_id = chat.task.leading_chats.first().id

        # Config
        config = {
            "class_path": "langchain.memory.RedisChatMessageHistory",
            "config": {
                "url": "redis://redis:6379/0",
                "session_scope": "chat",
                "session_prefix": "tests",
            },
        }

        # Run
        backend = load_chain(config)
        assert backend.session_id == f"tests_chat_{chat_id}"

    def test_load_defaults(self, chat, load_chain):
        """
        ChatMemoryBackend should always load session_id. If `session` isn't present then
        load the `chat` scope by default.
        """
        chat = chat["chat"]
        chat_id = chat.task.leading_chats.first().id

        # Config
        config = {
            "class_path": "langchain.memory.RedisChatMessageHistory",
            "config": {
                "url": "redis://redis:6379/0",
            },
        }

        # Run
        backend = load_chain(config)
        assert backend.session_id == f"chat_{chat_id}"


@pytest.mark.django_db
class TestGetMemorySession:
    """Test parsing the session scope from the chain config and runtime context."""

    @pytest.mark.parametrize(
        "config, cls, expected",
        [
            # No scope - defaults to chat
            (
                {
                    "session_scope": "",
                    "session_prefix": "123",
                    "session_key": "session_id",
                },
                BaseChatMessageHistory,
                ("123_chat_1000", "session_id"),
            ),
            (
                {
                    "session_scope": None,
                    "session_prefix": "123",
                    "session_key": "session_id",
                },
                BaseChatMessageHistory,
                ("123_chat_1000", "session_id"),
            ),
            (
                {"session_prefix": "123", "session_key": "session_id"},
                BaseChatMessageHistory,
                ("123_chat_1000", "session_id"),
            ),
            # agent, task, user scopes
            (
                {
                    "session_scope": "agent",
                    "session_prefix": "456",
                    "session_key": "session_id",
                },
                BaseMemory,
                ("456_agent_1001", "session_id"),
            ),
            (
                {
                    "session_scope": "task",
                    "session_prefix": "789",
                    "session_key": "session_id",
                },
                BaseMemory,
                ("789_task_1002", "session_id"),
            ),
            (
                {
                    "session_scope": "user",
                    "session_prefix": "321",
                    "session_key": "session_id",
                },
                BaseChatMessageHistory,
                ("321_user_1003", "session_id"),
            ),
            # custom session_id_key
            (
                {"session_scope": "chat", "session_key": "chat_session"},
                BaseChatMessageHistory,
                ("chat_1000", "chat_session"),
            ),
            # no session prefix
            (
                {"session_scope": "chat", "session_key": "session_id"},
                BaseChatMessageHistory,
                ("chat_1000", "session_id"),
            ),
            # custom session prefix
            (
                {"session_scope": "chat", "session_prefix": "static_session_id"},
                BaseChatMessageHistory,
                ("static_session_id_chat_1000", "session_id"),
            ),
        ],
    )
    def test_get_memory_session(self, task, config, cls, expected):
        """Test various scope configurations."""
        context = MagicMock()
        context.task = task
        context.chat_id = "1000"
        context.agent.id = "1001"
        context.task.id = "1002"
        context.user_id = "1003"

        result = get_memory_session(config, context, cls)
        assert result == expected

    def test_parse_scope_unsupported_scope(self, task):
        config = {
            "session_scope": "unsupported_scope",
            "session_id": "123",
            "session_id_key": "session_id",
        }
        cls = BaseChatMessageHistory
        context = IxContext(agent=task.agent, chain=task.chain, task=task)
        with pytest.raises(ValueError) as excinfo:
            get_memory_session(config, context, cls)
        assert "unknown scope" in str(excinfo.value)


class TestLoadChain:
    def test_load_chain(self):
        pass


class TestExtractToolKwargs:
    @pytest.fixture
    def kwargs(self):
        return {
            "return_direct": False,
            "verbose": False,
            "tool_key1": "tool_value1",
            "tool_key2": "tool_value2",
        }

    def test_extract_tool_kwargs_returns_dict(self, kwargs):
        result = extract_tool_kwargs(kwargs)
        assert isinstance(result, dict)

    def test_extract_tool_kwargs_only_includes_tool_kwargs(self, kwargs):
        node_kwargs = kwargs.copy()
        tool_kwargs = extract_tool_kwargs(node_kwargs)
        expected_node_kwargs = {"tool_key1": "tool_value1", "tool_key2": "tool_value2"}
        expected_tool_kwargs = {
            "return_direct": False,
            "verbose": False,
        }
        assert tool_kwargs == expected_tool_kwargs
        assert expected_node_kwargs == node_kwargs


GOOGLE_SEARCH_CONFIG = {
    "class_path": GOOGLE_SEARCH["class_path"],
    "name": "tester",
    "description": "test",
    "config": {},
}


@pytest.fixture()
def mock_google_api_key(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "MOCK_KEY")
    monkeypatch.setenv("GOOGLE_CSE_ID", "MOCK_ID")


@pytest.mark.django_db
class TestGoogleTools:
    async def test_load_tools(self, aload_chain, mock_google_api_key):
        """Test that tools can be loaded."""
        config = {
            "class_path": GOOGLE_SEARCH["class_path"],
            "name": "tester",
            "description": "test",
            "config": {},
        }

        instance = await aload_chain(config)
        assert isinstance(instance, BaseTool)


@pytest.mark.django_db
class TestLoadAgents:
    # list of known agents. This list may not be exhaustive
    # of all agents available since functions are dynamically
    # loaded from LangChain code.
    KNOWN_AGENTS = [
        "initialize_zero_shot_react_description",
        "initialize_conversational_react_description",
        "initialize_chat_zero_shot_react_description",
        "initialize_chat_conversational_react_description",
        "initialize_structured_chat_zero_shot_react_description",
        "initialize_openai_functions",
        "initialize_openai_multi_functions",
    ]

    def test_init_functions(self):
        """Test that agent init wrappers were generated."""
        from ix.chains.loaders.agents import FUNCTION_NAMES

        for name in self.KNOWN_AGENTS:
            assert name in FUNCTION_NAMES

    async def test_load_agents(self, aload_chain, mock_openai, mock_google_api_key):
        """Test that agent can be loaded."""

        agents = [
            "initialize_zero_shot_react_description",
            "initialize_conversational_react_description",
            "initialize_chat_zero_shot_react_description",
            "initialize_chat_conversational_react_description",
            "initialize_structured_chat_zero_shot_react_description",
            "initialize_openai_functions",
            "initialize_openai_multi_functions",
        ]

        for name in agents:
            config = {
                "class_path": f"ix.chains.loaders.agents.{name}",
                "name": "tester",
                "description": "test",
                "config": {"tools": [GOOGLE_SEARCH_CONFIG], "llm": OPENAI_LLM},
            }

            instance = await aload_chain(config)
            assert isinstance(instance, AgentExecutor)

    async def test_agent_memory(self, mock_openai, aload_chain, mock_google_api_key):
        config = {
            "class_path": OPENAI_FUNCTIONS_AGENT_CLASS_PATH,
            "name": "tester",
            "description": "test",
            "config": {
                "tools": [GOOGLE_SEARCH_CONFIG],
                "llm": OPENAI_LLM,
                "memory": AGENT_MEMORY,
            },
        }
        executor = await aload_chain(config)
        assert isinstance(executor, AgentExecutor)  # sanity check

        # 1. test that prompt includes placeholders
        # 2. test that memory keys are correct
        # 3. test that memory is loaded for agent
        result = await executor.acall(inputs={"input": "foo", "user_input": "bar"})

        # verify response contains memory
        assert result["chat_history"][0].content == "bar"
        assert result["chat_history"][1].content == "mock llm response"

        # call second time to smoke test
        await executor.acall(inputs={"input": "foo", "user_input": "bar"})

    async def test_agent_memory_misconfigured(
        self, mock_openai, aload_chain, mock_google_api_key
    ):
        """test agent/memory misconfigurations that should raise errors
        - memory class must have `return_messages=True`
        """
        config = {
            "class_path": "ix.chains.loaders.agents.initialize_zero_shot_react_description",
            "name": "tester",
            "description": "test",
            "config": {
                "tools": [GOOGLE_SEARCH_CONFIG],
                "llm": OPENAI_LLM,
                "memory": MEMORY,
            },
        }
        with pytest.raises(ValueError) as excinfo:
            await aload_chain(config)
            assert "Agents require return_messages=True" in str(excinfo.value)


TEST_DATA = Path("/var/app/test_data")
TEST_DOCUMENTS = TEST_DATA / "documents"

LANGUAGE_PARSER = {
    "class_path": LANGUAGE_PARSER_CLASS_PATH,
    "config": {
        "language": "python",
    },
}

DOCUMENT_LOADER = {
    "class_path": GENERIC_LOADER_CLASS_PATH,
    "config": {
        "parser": LANGUAGE_PARSER,
        "path": str(TEST_DOCUMENTS),
        "suffixes": [".py"],
    },
}

TEXT_SPLITTER = {
    "class_path": RECURSIVE_CHARACTER_SPLITTER_CLASS_PATH,
    "config": {"language": "python", "document_loader": DOCUMENT_LOADER},
}

EMBEDDINGS = {
    "class_path": OPENAI_EMBEDDINGS_CLASS_PATH,
    "config": {"model": "text-embedding-ada-002"},
}

REDIS_VECTORSTORE = {
    "class_path": REDIS_VECTORSTORE_CLASS_PATH,
    "config": {
        "embedding": EMBEDDINGS,
        "documents": TEXT_SPLITTER,
        "redis_url": "redis://redis:6379/0",
        "index_name": "tests",
    },
}

CONVERSATIONAL_RETRIEVAL_CHAIN = {
    "class_path": CONVERSATIONAL_RETRIEVAL_CHAIN_CLASS_PATH,
    "config": {"llm": OPENAI_LLM, "retriever": REDIS_VECTORSTORE},
}


@pytest.mark.django_db
class TestLoadRetrieval:
    """Test loading retrieval components.

    This is a test of loading mechanism for the various retrieval components.
    It is not an exhaustive test that all retrieval components work as expected.
    The tests verify that any special loading logic for the components is working.
    """

    async def test_load_language_parser(self, aload_chain):
        component = await aload_chain(LANGUAGE_PARSER)
        assert isinstance(component, LanguageParser)
        assert component.language == "python"

    async def test_load_document_loader(self, aload_chain):
        component = await aload_chain(DOCUMENT_LOADER)
        assert isinstance(component, GenericLoader)
        assert isinstance(component.blob_parser, LanguageParser)

        # non-exhaustive test of document loading
        documents = component.load()
        sources = {doc.metadata["source"] for doc in documents}
        expected_sources = {
            str(TEST_DOCUMENTS / "foo.py"),
            str(TEST_DOCUMENTS / "bar.py"),
        }
        assert sources == expected_sources

    async def test_load_text_splitter(self, aload_chain):
        component = await aload_chain(TEXT_SPLITTER)
        assert isinstance(component, TextSplitterShim)
        assert isinstance(component.document_loader, GenericLoader)
        assert isinstance(component.text_splitter, TextSplitter)

        # sanity check that the splitter splits text
        # does not test the actual splitting algorithm
        with open(TEST_DOCUMENTS / "foo.py", "r") as foo_file:
            foo_content = foo_file.read()
        split_texts = component.text_splitter.split_text(foo_content)
        assert len(split_texts) >= 1

    async def test_load_embeddings(self, aload_chain):
        component = await aload_chain(EMBEDDINGS)
        assert isinstance(component, OpenAIEmbeddings)

    async def test_load_vectorstore(
        self, clean_redis, aload_chain, mock_openai_embeddings
    ):
        component = await aload_chain(REDIS_VECTORSTORE)
        assert isinstance(component, Redis)

    async def test_load_conversational_chain(
        self, clean_redis, aload_chain, mock_openai_embeddings
    ):
        """Test loading a fully configured conversational chain."""
        component = await aload_chain(CONVERSATIONAL_RETRIEVAL_CHAIN)
        assert isinstance(component, ConversationalRetrievalChain)
