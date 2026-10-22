"""The dialog asks only when a button is used."""

from types import SimpleNamespace
from unittest.mock import Mock

from gridplayer.params.actions import ACTIONS
from gridplayer.params.menu import SECTIONS
from gridplayer.player.managers.active_block import ActiveBlockManager
from gridplayer.plugins.subtitlecat.client import (
    DownloadOutcome,
    SearchOutcome,
    TranslateOutcome,
)
from gridplayer.plugins.subtitlecat.dialog import SubtitleCatDialog, open_subtitlecat
from gridplayer.plugins.subtitlecat.parse import (
    LanguageRow,
    SearchHit,
    TranslateRequest,
)


def test_the_menu_item_sits_after_subtitle_delay():
    subtitles = next(
        item
        for item in SECTIONS["video_active"]
        if isinstance(item, tuple) and item[0] == "Subtitles"
    )

    assert subtitles[1] == "Subtitle Track"
    assert subtitles[-1] == "Find Subtitles on SubtitleCat"
    action = ACTIONS["Find Subtitles on SubtitleCat"]
    assert action["func"] == ("active", "subtitlecat.find")
    assert action["title"]


def test_the_flag_reads_the_setting_only(monkeypatch):
    monkeypatch.setattr(
        "gridplayer.settings.Settings",
        lambda: _Settings({"plugins/subtitlecat": False}),
    )
    manager = ActiveBlockManager.__new__(ActiveBlockManager)

    assert manager.is_subtitlecat_enabled() is False


def test_sign_in_and_sign_up_open_only_those_pages(monkeypatch):
    opened = []
    monkeypatch.setattr(
        "gridplayer.plugins.subtitlecat.dialog.QDesktopServices.openUrl",
        lambda url: opened.append(url.toString()),
    )

    open_subtitlecat("sign-in")
    open_subtitlecat("sign-up")
    open_subtitlecat("https://evil.example/phish")

    assert opened == [
        "https://www.subtitlecat.com/login.php",
        "https://www.subtitlecat.com/register.php",
    ]


def test_opening_the_dialog_does_not_search(tmp_path):
    client = _Client()
    dialog = _dialog(tmp_path, client)

    try:
        assert client.calls == []
        assert dialog._terms.text() == "Britains Got Talent"
    finally:
        dialog.close()


def test_an_empty_search_does_not_ask(tmp_path):
    client = _Client()
    dialog = _dialog(tmp_path, client)
    _inline(dialog)

    try:
        dialog._terms.setText("  ")
        dialog._search.click()

        assert client.calls == []
        assert "Enter a title" in dialog._status.toPlainText()
    finally:
        dialog.close()


def test_search_is_one_click(tmp_path):
    client = _Client()
    dialog = _dialog(tmp_path, client)
    calls = []

    def record(what, function, *args):
        calls.append(what)

    dialog._worker.run = record

    try:
        dialog._search.click()
        dialog._search.click()

        assert calls == ["search"]
    finally:
        dialog.close()


def test_download_saves_beside_the_video_and_loads_it(tmp_path):
    payload = b"1\n00:00:00,000 --> 00:00:01,000\nHi\n"
    client = _Client()
    client.download_result = DownloadOutcome("subtitle", payload, "", "Britain's.srt")
    block_subtitles = Mock()
    dialog = _dialog(tmp_path, client, subtitles=block_subtitles)
    _inline(dialog)

    try:
        dialog._download_url = "https://www.subtitlecat.com/subs/1/Britain%27s.srt"
        dialog._on_download()

        saved = tmp_path / "Britains.srt"
        assert saved.read_bytes() == payload
        block_subtitles.add_external.assert_called_once()
        assert block_subtitles.add_external.call_args.args[0] == [saved.resolve()]
        assert "Britains.srt" in dialog._status.toPlainText()
        assert client.calls == [("download",)]
    finally:
        dialog.close()


def test_translate_stays_off_until_the_setting_is_on(tmp_path):
    client = _Client()
    dialog = _dialog(tmp_path, client, translate=False)
    _inline(dialog)

    try:
        dialog._languages = (
            LanguageRow(
                "sq",
                "Albanian",
                None,
                TranslateRequest("sq", "A.srt", "/subs/1/"),
            ),
        )
        dialog._language_list.addItem("Albanian")
        dialog._language_list.setCurrentRow(0)
        dialog._on_translate()

        assert client.calls == []
        assert dialog._translate.isVisible() is False
    finally:
        dialog.close()


def test_a_translate_click_shows_the_sites_sentence(tmp_path):
    sentence = (
        "You are out of free translations. You can either wait one hour, "
        "or sign up to a VIP account for unlimited translations!"
    )
    client = _Client()
    client.translate_result = TranslateOutcome(sentence)
    dialog = _dialog(tmp_path, client, translate=True)
    _inline(dialog)

    try:
        dialog._page_url = "https://www.subtitlecat.com/subs/1/A.html"
        dialog._languages = (
            LanguageRow(
                "sq",
                "Albanian",
                None,
                TranslateRequest("sq", "A.srt", "/subs/1/"),
            ),
        )
        dialog._language_list.addItem("Albanian")
        dialog._language_list.setCurrentRow(0)
        dialog._translate.click()

        assert dialog._status.toPlainText() == sentence
        assert client.calls == [("translate",)]
    finally:
        dialog.close()


def test_languages_put_the_preferred_one_first(tmp_path):
    client = _Client()
    client.page_result_rows = (
        LanguageRow("en", "English", "https://www.subtitlecat.com/a-en.srt", None),
        LanguageRow("ja", "Japanese", "https://www.subtitlecat.com/a-ja.srt", None),
    )
    dialog = _dialog(tmp_path, client, languages="ja, en")
    _inline(dialog)
    dialog._hits = (
        SearchHit(
            "Sintel",
            "https://www.subtitlecat.com/subs/1/A.html",
            "2 KB",
            "1",
            "2",
            "English",
        ),
    )
    dialog._results.addItem("Sintel")
    dialog._results.setCurrentRow(0)

    try:
        dialog._languages_button.click()
        labels = [
            dialog._language_list.item(row).text()
            for row in range(dialog._language_list.count())
        ]

        assert labels[0].startswith("Japanese")
        assert client.calls == [("page",)]
    finally:
        dialog.close()


class _Client:
    def __init__(self):
        self.calls = []
        self.download_result = DownloadOutcome("message", b"", "no file", "")
        self.translate_result = TranslateOutcome("no")
        self.page_result_rows = ()

    def search(self, terms, referer=None):
        self.calls.append(("search",))
        return SearchOutcome((), "")

    def page(self, url, referer=None):
        self.calls.append(("page",))
        from gridplayer.plugins.subtitlecat.client import PageOutcome

        return PageOutcome(self.page_result_rows, "")

    def download(self, url, referer):
        self.calls.append(("download",))
        return self.download_result

    def translate(self, request, page_url):
        self.calls.append(("translate",))
        return self.translate_result


class _Settings:
    def __init__(self, values):
        self._values = values

    def get(self, key):
        return self._values[key]


def _dialog(tmp_path, client, subtitles=None, translate=False, languages="en"):
    video = tmp_path / "Britain's Got Talent.mkv"
    video.write_bytes(b"v")
    block = SimpleNamespace(
        video_params=SimpleNamespace(
            uri=video,
            title=None,
            subtitle_languages=languages,
        ),
        subtitles=subtitles,
    )

    def get(key):
        values = {
            "plugins/subtitlecat": True,
            "plugins/subtitlecat_translate": translate,
            "player/language": "en_US",
        }
        return values[key]

    return SubtitleCatDialog(block, client=client, settings_get=get)


def _inline(dialog):
    def run(what, function, *args):
        try:
            result = function(*args)
        except Exception as exc:
            dialog._finished(what, None, exc)
        else:
            dialog._finished(what, result, None)

    dialog._worker.run = run
