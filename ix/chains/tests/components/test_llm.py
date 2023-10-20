from langchain.chat_models.fireworks import ChatFireworks
from langchain.llms.fireworks import Fireworks
import pytest
from langchain.llms import Ollama

from ix.chains.fixture_src.llm import (
    FIREWORKS_CHAT_LLM_CLASS_PATH,
    FIREWORKS_LLM_CLASS_PATH,
    OLLAMA_LLM_CLASS_PATH,
)

OLLAMA_LLM = {
    "class_path": OLLAMA_LLM_CLASS_PATH,
    "config": {"model": "llama2"},
}


@pytest.mark.django_db
class TestOllama:
    async def test_aload(self, aload_chain):
        component = await aload_chain(OLLAMA_LLM)
        assert isinstance(component, Ollama)


FIREWORKS_LLM = {
    "class_path": FIREWORKS_LLM_CLASS_PATH,
    "config": {
        "model": "accounts/fireworks/models/llama-v2-7b-chat",
        "fireworks_api_key": "mock key",
    },
}

FIREWORKS_CHAT_LLM = {
    "class_path": FIREWORKS_CHAT_LLM_CLASS_PATH,
    "config": {
        "model": "accounts/fireworks/models/llama-v2-7b-chat",
        "fireworks_api_key": "mock key",
    },
}


@pytest.mark.django_db
class TestFireworks:
    async def test_aload(self, aload_chain):
        component = await aload_chain(FIREWORKS_LLM)
        assert isinstance(component, Fireworks)


@pytest.mark.django_db
class TestFireworksChat:
    async def test_aload(self, aload_chain):
        component = await aload_chain(FIREWORKS_CHAT_LLM)
        assert isinstance(component, ChatFireworks)
