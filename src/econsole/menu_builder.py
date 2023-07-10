from abc import ABC, abstractmethod
from typing import Any

from empire_commons.types_ import NULL


class OperationError(Exception):
    def __init__(self):
        super().__init__("Invalid operation")


class LazyProgrammerException(Exception):
    def __init__(self, value):
        super().__init__()
        self.value = value


class AbstractMenu(ABC):
    def __init__(self, title: str):
        self.title = title
        self.menu_items = []
        self.default = NULL
        self.initialise()

    @abstractmethod
    def initialise(self):
        pass

    def update_menu_items(self):
        pass

    def display(self):
        repeat: bool = True
        while repeat:
            self.update_menu_items()
            print()
            print(self.title)
            if self.default != NULL:
                print(f"\tDefault value is: {self.default}")

            for index, item in enumerate(self.menu_items):
                if item.isVisible:
                    print(f"{index}. {item.description}")

            inp = input("Select Option: ")
            try:
                menu_item = self.menu_items[int(inp)]
                if menu_item.isVisible:
                    repeat = menu_item.run()
                else:
                    raise OperationError()
            except ValueError:
                if self.default != NULL:
                    raise LazyProgrammerException(value=self.default)
                print("Invalid option, you need to enter a number.", inp)
                repeat = True
            except IndexError:
                print(f"Invalid option. Option {inp} doesn't exist.")
                repeat = True
            except OperationError:
                print(f"Invalid option. Option at {inp} is hidden.")
                repeat = True

    def add_menu_item(self, menu_item: "MenuItem"):
        if not self.menu_items.__contains__(menu_item):
            self.menu_items.append(menu_item)
        else:
            raise ValueError(f"Menu item with id {menu_item.id} already exists!.")

    def add_hidden_menu_item(self, menu_item: "MenuItem"):
        self.add_menu_item(menu_item.hide())

    def show_menu_item(self, item_id: int):
        try:
            menu_item = MenuItem(item_id)
            index = self.menu_items.index(menu_item)
            self.menu_items[index].show()
        except ValueError:
            print(f"Error showing menu item. Menu item with ID {item_id} hasn't been added to this menu.")

    def hide_menu_item(self, item_id: int):
        try:
            menu_item = MenuItem(item_id)
            index = self.menu_items.index(menu_item)
            self.menu_items[index].hide()
        except ValueError:
            print(f"Error hiding menu item. Menu item with ID {item_id} hasn't been added to this menu.")


class MenuItem:
    def __init__(
        self,
        id_: int,
        description: str = "",
        action: callable(None) = None,
        menu: AbstractMenu = None,
        action_args: tuple[Any, ...] = (),
        action_kwargs: dict[str, Any] = None,
    ):
        action_kwargs = action_kwargs or {}

        self.id: int = id_
        self.description: str = description
        self.action = action
        self.action_args = action_args
        self.action_kwargs = action_kwargs
        self.menu: AbstractMenu = menu
        self.isExitOption: bool = False
        self.isVisible: bool = True

    def hide(self) -> "MenuItem":
        self.isVisible = False
        return self

    def show(self) -> "MenuItem":
        self.isVisible = True
        return self

    def set_as_exit_option(self) -> "MenuItem":
        self.isExitOption = True
        return self

    def run(self) -> bool:
        if self.action is not None:
            try:
                self.action(*self.action_args, **self.action_kwargs)
            except:
                self.action()

        elif self.menu is not None:
            self.menu.display()

        return not self.isExitOption

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class _Menu(AbstractMenu):
    def __init__(self, title: str, button_results_mapping: dict[int, Any]):
        super().__init__(title)
        self.button_results_mapping = button_results_mapping

    def initialise(self):
        pass


def build_menu(title: str, text: str, buttons: list[tuple[str, Any]], default: Any = NULL) -> Any:
    """
    Main function to build a simple menu. Example: ::

        z = build_menu(
            'le title',
            'le text',
            [
                ('roger', 'GERMAINE'),
                ('raymond', 'SOLANGE')
            ]
        )

        print(z)

    :param title:
    :param text:
    :param buttons: a list of tuples where tuple indices: 0 -> button text, 1 -> the value to return when the button is selected
    :param default:
    :return:
    """
    mapping: dict[int, Any] = {}
    menu = _Menu(f"{title}: {text}", mapping)
    count: int = 100
    selected: int = -1

    def _set_selected(value: int):
        nonlocal selected
        selected = int(value)

    for button in buttons:
        mapping[count] = button[1]
        menu.add_menu_item(MenuItem(count, button[0], _set_selected, action_args=(count,)).set_as_exit_option())
        count += 1

    try:
        menu.display()
    except LazyProgrammerException as error:
        return error.value

    return mapping[selected]


if __name__ == "__main__":
    z = build_menu("le title", "le text", [("roger", "GERMAINE"), ("raymond", "SOLANGE")])

    print(z)
