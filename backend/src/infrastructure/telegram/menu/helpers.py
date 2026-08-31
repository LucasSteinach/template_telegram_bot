from src.infrastructure.telegram.menu.menu import MENU, MenuItem


def get_path_to_item(search_id: str, item: MenuItem = MENU) -> str | None:
    if search_id == item.id:
        return item.id

    for child in item.children:
        child_path = get_path_to_item(search_id, child)
        if child_path is not None:
            return f"{item.id}.{child_path}"

    return None


def get_menu_item(item_id: str) -> MenuItem | None:
    path = get_path_to_item(item_id)
    item = MENU

    if path == "root":
        return item

    for part in path.split("."):
        if part == "root":
            continue
        item = next(c for c in item.children if c.id == part)

    return item
