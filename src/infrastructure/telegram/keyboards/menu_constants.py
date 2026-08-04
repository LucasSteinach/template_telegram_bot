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
            message_text="What do you want to tell me?",
            button_text="Input example",
            type="action",
        ),
        MenuItem(
            id="option_2",
            message_text="Option 2 menu",
            button_text="option 2",
            type="menu",
            children=[
                MenuItem(
                    id="sub_option_2",
                    message_text="Sub option 2 menu",
                    button_text="sup option 2",
                    type="menu",
                )
            ],
        ),
    ],
)
