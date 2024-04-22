import re
from datetime import datetime, timedelta

import PySimpleGUI as sg

from timermute.db.MuteUserDB import MuteUserDB
from timermute.db.MuteWordDB import MuteWordDB


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


def popup_get_text(message, title=None, default_text='', password_char='', size=(None, None), button_color=None,
                   background_color=None, text_color=None, icon=None, font=None, no_titlebar=False,
                   grab_anywhere=False, keep_on_top=None, location=(None, None), relative_location=(None, None), image=None, modal=True):
    """sg.popup_get_text のラッパー

    Notes:
        テキストボックスにデフォルトでフォーカスをセットする
        image はサポートしていないので利用するときは追加すること
    """
    layout = [[sg.Text(message, auto_size_text=True, text_color=text_color, background_color=background_color)],
              [sg.Input(default_text=default_text, size=size, key="-INPUT-", password_char=password_char, focus=True)],
              [sg.Button("Ok", size=(6, 1), bind_return_key=True), sg.Button("Cancel", size=(6, 1))]]

    window = sg.Window(title=title or message, layout=layout, icon=icon, auto_size_text=True, button_color=button_color, no_titlebar=no_titlebar,
                       background_color=background_color, grab_anywhere=grab_anywhere, keep_on_top=keep_on_top, location=location, relative_location=relative_location, finalize=True, modal=modal, font=font)

    window["-INPUT-"].set_focus(True)

    button, values = window.read()
    window.close()
    del window
    if button != "Ok":
        return None
    else:
        path = values["-INPUT-"]
        return path


def popup_get_interval(message="", title=None, default_text='', password_char='', size=(None, None), button_color=None,
                       background_color=None, text_color=None, icon=None, font=None, no_titlebar=False,
                       grab_anywhere=False, keep_on_top=None, location=(None, None), relative_location=(None, None), image=None, modal=True) -> int | None:
    message = message or "At what time will it be unmuted?"
    combo_list = ["minutes later", "hours later", "days later", "weeks later", "months later", "years later"]
    radio_column_layout = sg.Column([
        [sg.Radio("no limit", 1, key="-R0-")],
        [sg.Radio("1 hours", 1, key="-R1-")],
        [sg.Radio("2 hours", 1, key="-R2-")],
        [sg.Radio("6 hours", 1, key="-R3-")],
        [sg.Radio("12 hours", 1, key="-R4-")],
        [sg.Radio("24 hours", 1, key="-R5-")],
        [sg.Input("", key="-R6-", size=(15, 2)), sg.Combo(combo_list, combo_list[1], key="-R7-", size=(10, 2))],
    ])
    layout = [[sg.Text(message, auto_size_text=True, text_color=text_color, background_color=background_color)],
              [radio_column_layout],
              [sg.Button("Submit", size=(6, 1), bind_return_key=True), sg.Button("Cancel", size=(6, 1))]]

    window = sg.Window(title=title or message, layout=layout, icon=icon, auto_size_text=True, button_color=button_color, no_titlebar=no_titlebar,
                       background_color=background_color, grab_anywhere=grab_anywhere, keep_on_top=keep_on_top, location=location, relative_location=relative_location, finalize=True, modal=modal, font=font)

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
    radio_button_value = [
        1, 2, 6, 12, 24
    ]
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


def update_mute_word_table(window: sg.Window, mute_word_db: MuteWordDB) -> None:
    """mute_word テーブルを更新する
    """
    # TODO::index保存

    # ミュートワード取得
    # 更新日時で降順ソートする
    mute_word_list = mute_word_db.select()
    mute_word_list_1 = [r for r in mute_word_list if r.status == "unmuted"]
    mute_word_list_1.sort(key=lambda r: r.updated_at)
    mute_word_list_1.reverse()
    mute_word_list_2 = [r for r in mute_word_list if r.status == "muted"]
    mute_word_list_2.sort(key=lambda r: r.updated_at)
    mute_word_list_2.reverse()

    table_data = [r.to_unmuted_table_list() for r in mute_word_list_1]
    window["-LIST_1-"].update(values=table_data)
    table_data = [r.to_muted_table_list() for r in mute_word_list_2]
    window["-LIST_2-"].update(values=table_data)

    # 新着マイリストの背景色とテキスト色を変更する
    # update(values=list_data)で更新されるとデフォルトに戻る？
    # 強調したいindexのみ適用すればそれ以外はデフォルトになる
    # for i in include_new_index_list:
    #     window["-LIST-"].Widget.itemconfig(i, fg="black", bg="light pink")

    # indexをセットしてスクロール
    # scroll_to_indexは強制的にindexを一番上に表示するのでWidget.seeを使用
    # window["-LIST_1-"].Widget.see(index_1)
    # window["-LIST_1-"].update(set_to_index=index_1)
    return


def update_mute_user_table(window: sg.Window, mute_user_db: MuteUserDB) -> None:
    """mute_user テーブルを更新する
    """
    # TODO::index保存

    # ミュートユーザー取得
    # 更新日時で降順ソートする
    mute_user_list = mute_user_db.select()
    mute_user_list_1 = [r for r in mute_user_list if r.status == "unmuted"]
    mute_user_list_1.sort(key=lambda r: r.updated_at)
    mute_user_list_1.reverse()
    mute_user_list_2 = [r for r in mute_user_list if r.status == "muted"]
    mute_user_list_2.sort(key=lambda r: r.updated_at)
    mute_user_list_2.reverse()

    table_data = [r.to_unmuted_table_list() for r in mute_user_list_1]
    window["-LIST_3-"].update(values=table_data)
    table_data = [r.to_muted_table_list() for r in mute_user_list_2]
    window["-LIST_4-"].update(values=table_data)

    # 新着マイリストの背景色とテキスト色を変更する
    # update(values=list_data)で更新されるとデフォルトに戻る？
    # 強調したいindexのみ適用すればそれ以外はデフォルトになる
    # for i in include_new_index_list:
    #     window["-LIST-"].Widget.itemconfig(i, fg="black", bg="light pink")

    # indexをセットしてスクロール
    # scroll_to_indexは強制的にindexを一番上に表示するのでWidget.seeを使用
    # window["-LIST_1-"].Widget.see(index_1)
    # window["-LIST_1-"].update(set_to_index=index_1)
    return


if __name__ == "__main__":
    from timermute.ui.MainWindow import MainWindow
    mw = MainWindow()
    mw.run()
