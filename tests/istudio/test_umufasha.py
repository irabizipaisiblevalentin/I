"""Tests for istudio.umufasha — AI Assistant."""

from __future__ import annotations

from src.istudio.umufasha import AIAssistant
from src.istudio.ibikoreshingiro import AICompletionRequest, DocumentPosition, ProjectType


def test_ai_assistant_init():
    ai = AIAssistant()
    assert ai.list_conversations() == {}
    assert ai.get_active_conversation() is None


def test_create_conversation():
    ai = AIAssistant()
    cid = ai.create_conversation("my-conv")
    assert cid == "my-conv"
    assert ai.get_active_conversation() == "my-conv"


def test_auto_create_conversation():
    ai = AIAssistant()
    response = ai.send_message("hello")
    assert len(ai.list_conversations()) == 1


def test_send_message():
    ai = AIAssistant()
    response = ai.send_message("Hello")
    assert "Muraho" in response or "hello" in response.lower()


def test_ai_code():
    ai = AIAssistant()
    response = ai.send_message("Write a function that adds two numbers")
    assert response is not None


def test_ai_debug():
    ai = AIAssistant()
    response = ai.send_message("Help me debug an error")
    assert "debug" in response.lower()


def test_ai_explain():
    ai = AIAssistant()
    response = ai.send_message("Explain what a class is")
    assert "explain" in response.lower()


def test_ai_refactor():
    ai = AIAssistant()
    response = ai.send_message("Refactor this code")
    assert "refactor" in response.lower()


def test_get_conversation():
    ai = AIAssistant()
    ai.send_message("First message", "conv1")
    ai.send_message("Second message", "conv1")
    msgs = ai.get_conversation("conv1")
    assert len(msgs) == 4  # 2 user + 2 assistant
    assert msgs[0].role == "user"
    assert msgs[1].role == "assistant"
    assert msgs[2].role == "user"
    assert msgs[3].role == "assistant"


def test_list_conversations():
    ai = AIAssistant()
    ai.send_message("msg1", "conv_a")
    ai.send_message("msg2", "conv_b")
    convs = ai.list_conversations()
    assert len(convs) == 2
    assert convs["conv_a"] == 2


def test_clear_conversation():
    ai = AIAssistant()
    ai.send_message("test", "conv1")
    assert "conv1" in ai.list_conversations()
    ai.clear_conversation("conv1")
    assert "conv1" not in ai.list_conversations()


def test_clear_all():
    ai = AIAssistant()
    ai.send_message("test", "conv1")
    ai.clear_conversation()
    assert ai.list_conversations() == {}


def test_complete_code_function():
    ai = AIAssistant()
    req = AICompletionRequest(
        code="function foo() {\n",
        language="i",
        cursor_position=DocumentPosition(line=1, column=0),
    )
    completion = ai.complete_code(req)
    assert "pass" in completion


def test_complete_code_class():
    ai = AIAssistant()
    req = AICompletionRequest(
        code="class Foo {\n",
        language="i",
        cursor_position=DocumentPosition(line=1, column=0),
    )
    completion = ai.complete_code(req)
    assert "pass" in completion


def test_complete_code_for_loop():
    ai = AIAssistant()
    req = AICompletionRequest(
        code="for (let i = 0; i < 10; i++) {",
        cursor_position=DocumentPosition(line=0, column=31),
    )
    completion = ai.complete_code(req)
    assert "pass" in completion


def test_complete_code_empty():
    ai = AIAssistant()
    req = AICompletionRequest(code="", cursor_position=DocumentPosition(line=0, column=0))
    completion = ai.complete_code(req)
    assert completion == ""


def test_complete_code_return():
    ai = AIAssistant()
    req = AICompletionRequest(
        code="return ",
        cursor_position=DocumentPosition(line=0, column=7),
    )
    completion = ai.complete_code(req)
    assert completion == ""


def test_set_project_context():
    ai = AIAssistant()
    assert ai.get_project_context() is None
    ai.set_project_context(ProjectType.WEBSITE)
    ctx = ai.get_project_context()
    assert ctx is not None
    assert "web" in ctx.lower() or "HTML" in ctx


def test_project_context_in_response():
    ai = AIAssistant()
    ai.set_project_context(ProjectType.GAME)
    response = ai.send_message("Hello")
    assert "project" in response.lower() or "game" in response.lower()
