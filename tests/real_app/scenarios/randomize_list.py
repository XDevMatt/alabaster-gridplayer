"""Randomize, as in MPC-HC's playlist: a list cell's list mixed once, the
item playing first, and Next going straight down from there; from the
cell's own action and from the List window's button."""


def scenario(d):
    d.open(d.media.list_m3u)
    d.wait_until(lambda: len(d.cells) == 1 and d.cells[0].is_playable, "it plays")
    cell = d.cells[0]

    d.act(cell, "Play Next File")
    d.wait_until(lambda: cell.navigation.list_place_txt == "2/3", "on the second")
    playing = cell.list_item.key

    d.act(cell, "Randomize List")
    d.pump()
    d.check(
        "the item playing goes first",
        cell.media_list.items[0].key == playing,
        [item.title for item in cell.media_list.items],
    )
    d.check("said to be first", cell.navigation.list_place_txt == "1/3")

    second = cell.media_list.items[1].key
    d.act(cell, "Play Next File")
    d.wait_until(lambda: cell.navigation.list_place_txt == "2/3", "Next plays row 2")
    d.check("the second row's item", cell.list_item.key == second)
    d.wait_until(lambda: cell.is_playable, "and it plays")

    d.act(cell, "List")
    d.wait_until(
        lambda: [w for w in d.windows() if type(w).__name__ == "MediaListDialog"],
        "the List window is open",
    )
    window = next(w for w in d.windows() if type(w).__name__ == "MediaListDialog")
    button = window._randomize_button
    d.check("a Randomize button", button.text() == "Randomize", button.text())

    playing = cell.list_item.key
    button.click()
    d.pump()
    d.check(
        "the item playing goes first again", cell.media_list.items[0].key == playing
    )
    d.check("and said to be", cell.navigation.list_place_txt == "1/3")
    d.shot("list_window_randomized", window)
    # kept with OK: Cancel, or closing the window, puts the list back
    window.accept()
    d.pump()
    d.check("kept", cell.media_list.items[0].key == playing)
    d.check("still first", cell.navigation.list_place_txt == "1/3")

    d.note("end")
