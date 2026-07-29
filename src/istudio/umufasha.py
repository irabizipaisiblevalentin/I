"""I STUDIO — AI Assistant (Umufasha / UBWENGE Integration)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .ibikoreshingiro import (
    AICompletionRequest,
    ChatMessage,
    DocumentPosition,
    PROJECT_TEMPLATES,
    ProjectType,
)


class AIAssistant:
    def __init__(self):
        self._conversations: Dict[str, List[ChatMessage]] = {}
        self._active_conversation: Optional[str] = None
        self._listeners: Dict[str, List[callable]] = {}
        self._project_context: Optional[str] = None

    def create_conversation(self, conversation_id: Optional[str] = None) -> str:
        cid = conversation_id or f"conv_{len(self._conversations) + 1}"
        if cid not in self._conversations:
            self._conversations[cid] = []
        self._active_conversation = cid
        return cid

    def send_message(self, message: str, conversation_id: Optional[str] = None) -> str:
        cid = conversation_id or self._active_conversation
        if not cid or cid not in self._conversations:
            cid = self.create_conversation(conversation_id)

        user_msg = ChatMessage(role="user", content=message)
        self._conversations[cid].append(user_msg)

        response = self._generate_response(message, cid)
        assistant_msg = ChatMessage(role="assistant", content=response)
        self._conversations[cid].append(assistant_msg)

        return response

    def set_project_context(self, project_type: ProjectType) -> None:
        template = PROJECT_TEMPLATES.get(project_type)
        if template and template.ai_context:
            self._project_context = template.ai_context
            greeting = ChatMessage(
                role="system",
                content=f"[Project context: {template.display_name}] {template.ai_context}",
            )
            if self._active_conversation and self._active_conversation in self._conversations:
                self._conversations[self._active_conversation].insert(0, greeting)

    def get_project_context(self) -> Optional[str]:
        return self._project_context

    def _generate_response(self, message: str, conversation_id: str) -> str:
        message_lower = message.lower()
        words = set(message_lower.split())

        context_hint = ""
        if self._project_context:
            context_hint = f" (project: {self._project_context[:60]}...)"

        if "hello" in words or "hi" in words or message_lower.startswith("hi "):
            return f"Muraho! I'm I Studio AI Assistant{context_hint}. How can I help you with your code today?"

        if "explain" in message_lower or "what does" in message_lower:
            return f"I can help explain code concepts{context_hint}. Could you share the specific code or concept you'd like explained?"

        if "refactor" in message_lower or "improve" in message_lower:
            return f"I'd be happy to help refactor your code{context_hint}. Please share the code you'd like improved."

        if "debug" in message_lower or "error" in message_lower:
            return f"Let's debug that together{context_hint}. Could you share the error message and relevant code?"

        if "generate" in message_lower or "write" in message_lower or "create" in message_lower:
            return f"I can help generate code{context_hint}. What would you like me to create?"

        if "test" in message_lower:
            return f"I can help write tests{context_hint}. What functionality would you like to test?"

        if "document" in message_lower:
            return f"I can help generate documentation{context_hint}. Which code would you like documented?"

        return f"I'm your AI coding assistant{context_hint}. I can help with code generation, explanation, debugging, refactoring, testing, and documentation. What do you need help with?"

    def get_conversation(self, conversation_id: str) -> List[ChatMessage]:
        return self._conversations.get(conversation_id, [])

    def get_active_conversation(self) -> Optional[str]:
        return self._active_conversation

    def list_conversations(self) -> Dict[str, int]:
        return {cid: len(msgs) for cid, msgs in self._conversations.items()}

    def clear_conversation(self, conversation_id: Optional[str] = None) -> None:
        if conversation_id:
            self._conversations.pop(conversation_id, None)
        else:
            self._conversations.clear()
            self._active_conversation = None

    def complete_code(self, request: AICompletionRequest) -> str:
        lines = request.code.split("\n")
        cursor_line = lines[request.cursor_position.line] if request.cursor_position.line < len(lines) else ""
        context = "\n".join(lines[:request.cursor_position.line + 1])

        stripped = cursor_line.strip()

        if "function " in cursor_line or "def " in cursor_line:
            return "    pass\n"
        if "class " in cursor_line:
            return "    pass\n"

        if stripped.endswith(":") or stripped.endswith("{"):
            return "    pass\n"

        if any("function " in l or "def " in l for l in lines[:request.cursor_position.line]):
            return "    pass\n"
        if any("class " in l for l in lines[:request.cursor_position.line]):
            return "    pass\n"

        if "for " in cursor_line or any("for " in l for l in lines[max(0, request.cursor_position.line - 1):request.cursor_position.line + 1]):
            return "    pass\n"
        if "if " in cursor_line or any(l.strip().startswith("if ") for l in lines[max(0, request.cursor_position.line - 1):request.cursor_position.line + 1]):
            return "    pass\n"

        if cursor_line.strip().startswith("import") or cursor_line.strip().startswith("from"):
            return ""

        return ""

    def on(self, event: str, handler: callable) -> None:
        self._listeners.setdefault(event, []).append(handler)

    def _emit(self, event: str, data: Dict[str, Any]) -> None:
        for handler in self._listeners.get(event, []):
            try:
                handler(data)
            except Exception:
                pass
