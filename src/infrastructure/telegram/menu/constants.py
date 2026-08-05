from dataclasses import dataclass, field
from typing import Literal

from src.infrastructure.telegram.callbacks import ActionId


@dataclass(frozen=True)
class MenuItem:
    id: str  # ==callback data
    message_text: str
    button_text: str
    type: Literal["action", "menu"]  # menu - navigation without outer or awaited action
    children: list["MenuItem"] = field(default_factory=list)

    @property
    def button_labels(self) -> list[str]:
        """
        Get button labels of the current menu level
        """
        return [c.button_text for c in self.children]


MENU = MenuItem(
    id="root",  # NOT A BUTTON
    message_text="Main menu",
    button_text="",
    type="menu",
    children=[
        MenuItem(
            id=ActionId.INPUT_EXAMPLE,
            message_text="I can repeat whatever you say. Want to test me?",
            button_text="Input example",
            type="action",
        ),
        MenuItem(
            id="support",
            message_text="Support menu",
            button_text="Support",
            type="menu",
            children=[
                MenuItem(
                    id=ActionId.CHAT,
                    message_text="Chat menu",
                    button_text="chat",
                    type="action",
                    children=[
                        MenuItem(
                            id=ActionId.CLOSE_CHAT,
                            message_text="not a menu part",
                            button_text="close case",
                            type="action",
                        )
                    ],
                ),
            ],
        ),
    ],
)
