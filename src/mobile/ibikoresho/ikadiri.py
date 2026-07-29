from __future__ import annotations

from typing import Any, Callable, Optional

from .buto import Buto
from .ikoresho import Ikoresho


class Ikadiri(Ikoresho):
    """Dialog component for showing modal overlays.

    Displays a title, message, and a set of action buttons.
    Supports being dismissed and can be configured as non-dismissable.

    Attributes:
        title: Dialog title text.
        message: Dialog body text.
        confirm_text: Label for the confirm action button.
        cancel_text: Label for the cancel action button.
        on_confirm: Callback when the user confirms.
        on_cancel: Callback when the user cancels or dismisses.
        dismissable: Whether the dialog can be dismissed by tapping
            outside or pressing back.
        actions: Custom list of action buttons (overrides confirm/cancel).
    """

    def __init__(
        self,
        title: str = "",
        message: str = "",
        confirm_text: str = "Yego",
        cancel_text: str = "Oya",
        on_confirm: Optional[Callable[[], Any]] = None,
        on_cancel: Optional[Callable[[], Any]] = None,
        dismissable: bool = True,
        actions: Optional[list[Buto]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._title: str = title
        self._message: str = message
        self._confirm_text: str = confirm_text
        self._cancel_text: str = cancel_text
        self._on_confirm: Optional[Callable[[], Any]] = on_confirm
        self._on_cancel: Optional[Callable[[], Any]] = on_cancel
        self._dismissable: bool = dismissable
        self._actions: list[Buto] = actions or []

    # --- Properties ---

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, value: str) -> None:
        self._message = value

    @property
    def confirm_text(self) -> str:
        return self._confirm_text

    @confirm_text.setter
    def confirm_text(self, value: str) -> None:
        self._confirm_text = value

    @property
    def cancel_text(self) -> str:
        return self._cancel_text

    @cancel_text.setter
    def cancel_text(self, value: str) -> None:
        self._cancel_text = value

    @property
    def on_confirm(self) -> Optional[Callable[[], Any]]:
        return self._on_confirm

    @on_confirm.setter
    def on_confirm(self, value: Optional[Callable[[], Any]]) -> None:
        self._on_confirm = value

    @property
    def on_cancel(self) -> Optional[Callable[[], Any]]:
        return self._on_cancel

    @on_cancel.setter
    def on_cancel(self, value: Optional[Callable[[], Any]]) -> None:
        self._on_cancel = value

    @property
    def dismissable(self) -> bool:
        return self._dismissable

    @dismissable.setter
    def dismissable(self, value: bool) -> None:
        self._dismissable = value

    @property
    def actions(self) -> list[Buto]:
        return list(self._actions)

    @actions.setter
    def actions(self, value: list[Buto]) -> None:
        self._actions = list(value)

    # --- Methods ---

    def show(self) -> None:
        self._visible = True

    def dismiss(self) -> None:
        self._visible = False
        if self._on_cancel is not None:
            self._on_cancel()

    def set_message(self, message: str) -> None:
        self._message = message

    def render(self) -> dict[str, Any]:
        return {
            "type": "Ikadiri",
            "title": self._title,
            "message": self._message,
            "confirm_text": self._confirm_text,
            "cancel_text": self._cancel_text,
            "dismissable": self._dismissable,
            "action_count": len(self._actions),
            "visible": self._visible,
        }


class IkadiriAlert(Ikadiri):
    """Alert dialog — a simple dialog with a single confirm button.

    Shows an informational message that the user must acknowledge.
    """

    def __init__(
        self,
        title: str = "Imenyesha",
        message: str = "",
        confirm_text: str = "Sawa",
        on_confirm: Optional[Callable[[], Any]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            title=title,
            message=message,
            confirm_text=confirm_text,
            on_confirm=on_confirm,
            **kwargs,
        )

    def render(self) -> dict[str, Any]:
        base = super().render()
        base["type"] = "IkadiriAlert"
        return base


class IkadiriConfirm(Ikadiri):
    """Confirmation dialog — asks the user to confirm or cancel.

    Displays both confirm and cancel buttons.
    """

    def __init__(
        self,
        title: str = "Emeza",
        message: str = "",
        confirm_text: str = "Emeza",
        cancel_text: str = "Reka",
        on_confirm: Optional[Callable[[], Any]] = None,
        on_cancel: Optional[Callable[[], Any]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            title=title,
            message=message,
            confirm_text=confirm_text,
            cancel_text=cancel_text,
            on_confirm=on_confirm,
            on_cancel=on_cancel,
            **kwargs,
        )

    def render(self) -> dict[str, Any]:
        base = super().render()
        base["type"] = "IkadiriConfirm"
        return base


class IkadiriPrompt(Ikadiri):
    """Prompt dialog — asks the user for text input.

    Provides a text field inside the dialog.

    Attributes:
        default_value: Initial value for the text field.
        placeholder: Placeholder text for the text field.
        on_submit: Callback with the entered text.
    """

    def __init__(
        self,
        title: str = "Andika",
        message: str = "",
        default_value: str = "",
        placeholder: str = "",
        on_submit: Optional[Callable[[str], Any]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(title=title, message=message, **kwargs)
        self._prompt_value: str = default_value
        self._prompt_placeholder: str = placeholder
        self._on_submit: Optional[Callable[[str], Any]] = on_submit

    @property
    def prompt_value(self) -> str:
        return self._prompt_value

    @prompt_value.setter
    def prompt_value(self, value: str) -> None:
        self._prompt_value = value

    @property
    def prompt_placeholder(self) -> str:
        return self._prompt_placeholder

    @prompt_placeholder.setter
    def prompt_placeholder(self, value: str) -> None:
        self._prompt_placeholder = value

    @property
    def on_submit(self) -> Optional[Callable[[str], Any]]:
        return self._on_submit

    @on_submit.setter
    def on_submit(self, value: Optional[Callable[[str], Any]]) -> None:
        self._on_submit = value

    def render(self) -> dict[str, Any]:
        base = super().render()
        base["type"] = "IkadiriPrompt"
        base["prompt_value"] = self._prompt_value
        base["prompt_placeholder"] = self._prompt_placeholder
        return base


class IkadiriCustom(Ikadiri):
    """Custom dialog — renders arbitrary content via a builder.

    Attributes:
        content_builder: Callable that returns the custom content
            component to display inside the dialog.
    """

    def __init__(
        self,
        title: str = "",
        content_builder: Optional[Callable[[], Ikoresho]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(title=title, **kwargs)
        self._content_builder: Optional[Callable[[], Ikoresho]] = content_builder

    @property
    def content_builder(self) -> Optional[Callable[[], Ikoresho]]:
        return self._content_builder

    @content_builder.setter
    def content_builder(self, value: Optional[Callable[[], Ikoresho]]) -> None:
        self._content_builder = value

    def render(self) -> dict[str, Any]:
        base = super().render()
        base["type"] = "IkadiriCustom"
        base["has_custom_content"] = self._content_builder is not None
        return base
