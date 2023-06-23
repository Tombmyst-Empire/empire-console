from asyncio import get_event_loop
from typing import Any, Callable, Sequence

from prompt_toolkit import Application
from prompt_toolkit.completion import Completer
from prompt_toolkit.eventloop import run_in_executor_with_context
from prompt_toolkit.filters import FilterOrBool
from prompt_toolkit.layout import D, HSplit
from prompt_toolkit.shortcuts.dialogs import (_create_app, button_dialog,
                                              checkboxlist_dialog,
                                              input_dialog, message_dialog,
                                              radiolist_dialog, yes_no_dialog)
from prompt_toolkit.styles import BaseStyle
from prompt_toolkit.validation import Validator
from prompt_toolkit.widgets import Box, Dialog, Label, ProgressBar, TextArea

from econsole.console_menu_builder import build_menu


class ConsoleDialogs:
    @staticmethod
    def show_message_box(title: str, text: str, button_text: str = "OK", style: BaseStyle | None = None):
        try:
            message_dialog(title=title, text=text, ok_text=button_text, style=style).run()
        except Exception:
            print(title.upper() + ":", text)

    @staticmethod
    def show_input_dialog(
        title: str,
        text: str,
        ok_button_text: str = "OK",
        cancel_button_text: str = "Cancel",
        completer: Completer | None = None,
        validator: Validator | None = None,
        password: FilterOrBool = False,
        style: BaseStyle | None = None,
        default_text: str = "",
    ) -> str:
        try:
            return input_dialog(
                title=title,
                text=text,
                ok_text=ok_button_text,
                cancel_text=cancel_button_text,
                completer=completer,
                validator=validator,
                password=password,
                style=style,
                default=default_text,
            ).run()
        except Exception:
            print(title.upper())
            return input(text + ": ")

    @staticmethod
    def confirm_dialog(title: str, text: str, yes_button_text: str = "Yes", no_button_text: str = "No", style: BaseStyle | None = None) -> bool:
        try:
            return yes_no_dialog(title=title, text=text, yes_text=yes_button_text, no_text=no_button_text, style=style).run()
        except Exception:
            print(title.upper())
            result: str = input(text + " (Y/n): ")
            if result.lower() == "n":
                return False

            return True

    @staticmethod
    def buttons_dialog(title: str, text: str, buttons: list[tuple[str, Any]], style: BaseStyle | None = None) -> Any:
        """
        Displays a dialog with the provided buttons.

        Buttons should be provided as a list of tuples,
        where index 0 is the button text and index 1 is
        the return value.

        :returns The selected button return value
        """
        try:
            return button_dialog(title=title, text=text, buttons=buttons, style=style).run()
        except Exception:
            return build_menu(title, text, buttons)

    @staticmethod
    def radio_buttons_dialog(
        title: str,
        text: str,
        *buttons: tuple[str, Any],
        ok_button_text: str = "OK",
        cancel_button_text: str = "Cancel",
        default: Any = None,
        style: BaseStyle | None = None,
    ) -> Any:
        try:
            return radiolist_dialog(
                title=title,
                text=text,
                values=[(button[1], button[0]) for button in buttons],
                ok_text=ok_button_text,
                cancel_text=cancel_button_text,
                default=default,
                style=style,
            ).run()
        except Exception:
            buttons = list(buttons)
            result = build_menu(title, text, buttons + [("Cancel", "CANCELLED")])
            if result == "CANCELLED":
                return None

            return result

    @staticmethod
    def checkbox_dialog(
        title: str,
        text: str,
        *values: tuple[str, Any],
        ok_button_text: str = "OK",
        cancel_button_text: str = "Cancel",
        default_values: Sequence[Any] | None = None,
        style: BaseStyle | None = None,
    ) -> list[Any]:
        return checkboxlist_dialog(
            title=title,
            text=text,
            values=[(value[1], value[0]) for value in values],
            ok_text=ok_button_text,
            cancel_text=cancel_button_text,
            default_values=default_values,
            style=style,
        ).run()

    @staticmethod
    def progress_bar_dialog(
        title: str, text: str, run_callback: Callable[[Callable[[int], None], Callable[[str], None]], None], style: BaseStyle | None = None
    ) -> Application:
        """
        Callback example: ::

            def worker(set_percentage, log_text):
            '''
            This worker function is called by `progress_dialog`. It will run in a
            background thread.
            The `set_percentage` function can be used to update the progress bar, while
            the `log_text` function can be used to log text in the logging window.
            '''
            percentage = 0
            for dirpath, dirnames, filenames in os.walk("../.."):
                for f in filenames:
                    log_text(f"{dirpath} / {f}")
                    set_percentage(percentage + 1)
                    percentage += 2
                    time.sleep(0.1)

                    if percentage == 100:
                        break
                if percentage == 100:
                    break

            # Show 100% for a second, before quitting.
            set_percentage(100)
            time.sleep(1)

        :param title:
        :param text:
        :param run_callback:
        :param style:
        :return:
        """

        loop = get_event_loop()
        progressbar = ProgressBar()
        text_area = TextArea(
            focusable=False,
            # Prefer this text area as big as possible, to avoid having a window
            # that keeps resizing when we add text to it.
            height=D(preferred=10**10),
        )

        dialog = Dialog(
            body=HSplit(
                [
                    Box(Label(text=text)),
                    Box(text_area, padding=D.exact(1)),
                    progressbar,
                ]
            ),
            title=title,
            with_background=True,
        )
        app = _create_app(dialog, style)

        def set_percentage(value: int) -> None:
            progressbar.percentage = int(value)
            app.invalidate()

        def log_text(text: str) -> None:
            loop.call_soon_threadsafe(text_area.buffer.insert_text, text)
            app.invalidate()

        # Run the callback in the executor. When done, set a return value for the
        # UI, so that it quits.
        def start() -> None:
            try:
                run_callback(set_percentage, log_text)
            finally:
                app.exit()

        def pre_run() -> None:
            run_in_executor_with_context(start)

        app.pre_run_callables.append(pre_run)

        return app
