from enum import Enum, auto
import re
from datetime import datetime, timedelta

import PySimpleGUI as sg


class Result(Enum):
    SUCCESS = auto()
    FAILED = auto()


def now():
    destination_format = "%Y-%m-%d %H:%M:%S"
    now_datetime = datetime.now()
    return now_datetime.strftime(destination_format)


def get_future_datetime(seconds: int) -> str:
    destination_format = "%Y-%m-%d %H:%M:%S"
    now_datetime = datetime.now()
    delta = timedelta(seconds=seconds)
    future_datetime = now_datetime + delta
    return future_datetime.strftime(destination_format)


def popup_get_text(
    message,
    title=None,
    default_text="",
    password_char="",
    size=(None, None),
    button_color=None,
    background_color=None,
    text_color=None,
    icon=None,
    font=None,
    no_titlebar=False,
    grab_anywhere=False,
    keep_on_top=None,
    location=(None, None),
    relative_location=(None, None),
    image=None,
    modal=True,
):
    """sg.popup_get_text のラッパー

    Notes:
        テキストボックスにデフォルトでフォーカスをセットする
        image はサポートしていないので利用するときは追加すること
    """
    layout = [
        [sg.Text(message, auto_size_text=True, text_color=text_color, background_color=background_color)],
        [sg.Input(default_text=default_text, size=size, key="-INPUT-", password_char=password_char, focus=True)],
        [sg.Button("Ok", size=(6, 1), bind_return_key=True), sg.Button("Cancel", size=(6, 1))],
    ]

    window = sg.Window(
        title=title or message,
        layout=layout,
        icon=icon,
        auto_size_text=True,
        button_color=button_color,
        no_titlebar=no_titlebar,
        background_color=background_color,
        grab_anywhere=grab_anywhere,
        keep_on_top=keep_on_top,
        location=location,
        relative_location=relative_location,
        finalize=True,
        modal=modal,
        font=font,
    )

    window["-INPUT-"].set_focus(True)

    button, values = window.read()
    window.close()
    del window
    if button != "Ok":
        return None
    else:
        path = values["-INPUT-"]
        return path


def popup_get_interval(
    message="",
    title=None,
    default_text="",
    password_char="",
    size=(None, None),
    button_color=None,
    background_color=None,
    text_color=None,
    icon=None,
    font=None,
    no_titlebar=False,
    grab_anywhere=False,
    keep_on_top=None,
    location=(None, None),
    relative_location=(None, None),
    image=None,
    modal=True,
) -> int | None:
    message = message or "At what time will it be unmuted?"
    combo_list = ["minutes later", "hours later", "days later", "weeks later", "months later", "years later"]
    radio_column_layout = sg.Column(
        [
            [sg.Radio("no limit", 1, key="-R0-")],
            [sg.Radio("1 hours", 1, key="-R1-")],
            [sg.Radio("2 hours", 1, key="-R2-")],
            [sg.Radio("6 hours", 1, key="-R3-")],
            [sg.Radio("12 hours", 1, key="-R4-")],
            [sg.Radio("24 hours", 1, key="-R5-")],
            [sg.Input("", key="-R6-", size=(15, 2)), sg.Combo(combo_list, combo_list[1], key="-R7-", size=(10, 2))],
        ]
    )
    layout = [[sg.Text(message, auto_size_text=True, text_color=text_color, background_color=background_color)], [radio_column_layout], [sg.Button("Submit", size=(6, 1), bind_return_key=True), sg.Button("Cancel", size=(6, 1))]]

    window = sg.Window(
        title=title or message,
        layout=layout,
        icon=icon,
        auto_size_text=True,
        button_color=button_color,
        no_titlebar=no_titlebar,
        background_color=background_color,
        grab_anywhere=grab_anywhere,
        keep_on_top=keep_on_top,
        location=location,
        relative_location=relative_location,
        finalize=True,
        modal=modal,
        font=font,
    )

    # window["-INPUT-"].set_focus(True)

    button, values = window.read()
    window.close()
    del window
    if button != "Submit":
        return None

    interval_minutes = -1
    radio_button_select_list = [
        values.get("-R1-", False),
        values.get("-R2-", False),
        values.get("-R3-", False),
        values.get("-R4-", False),
        values.get("-R5-", False),
    ]
    radio_button_value = [1, 2, 6, 12, 24]
    if values.get("-R0-", False):
        return None
    if any(radio_button_select_list):
        for i, v in enumerate(radio_button_select_list):
            if v:
                interval_minutes = radio_button_value[i] * 60  # min
                return interval_minutes
    if values.get("-R6-", "") != "" and values.get("-R7-", "") in combo_list:
        interval_str = values.get("-R6-", "")
        unit = values.get("-R7-", "")
        if not (interval_str and unit):
            return None
        if not re.search(r"^[0-9]*$", interval_str):
            return None
        interval_num = float(interval_str)
        match unit:
            case "minutes later":
                interval_minutes = interval_num  # min
            case "hours later":
                interval_minutes = interval_num * 60  # min
            case "days later":
                interval_minutes = interval_num * 60 * 24  # min
            case "weeks later":
                interval_minutes = interval_num * 60 * 24 * 7  # min
            case "months later":
                interval_minutes = interval_num * 60 * 24 * 31  # min
            case "years later":
                interval_minutes = interval_num * 60 * 24 * 31 * 12  # min
            case _:
                return None
        return interval_minutes
    return None


if __name__ == "__main__":
    from timermute.ui.main_window import MainWindow

    mw = MainWindow()
    mw.run()
