
Add-on to SublimeLinter which will do various UI blinking so you always know if your current file is green or red.

** This includes a hack, and is a showcase plugin **


# Install

1. Open up the command palette (`ctrl+shift+p`), and find `Package Control: Add Repository`. Then enter the URL of this repo: `https://github.com/kaste/SublimeLinter-Annotations/` in the input field.
2. Open up the command palette again and find `Package Control: Install Package`, and just search for `SublimeLinter-Annotations`. (just a normal install)


# Usage

This plugin [monkeypatches](https://github.com/kaste/SublimeLinter-Annotations/blob/master/monkeypatch_sublimelinter.py) the original SublimeLinter.

* It will colorize your status bar if the current file your editing has warnings or errors. For this to work, you have to add the following to your theme file.

    {
        "class": "status_bar",
        "settings": ["has_lint_errors"],
        "layer0.tint": [215, 57, 18], // -00
    },
    {
        "class": "status_bar",
        "settings": ["has_lint_warnings"],
        "layer0.tint": [88, 31, 158], // -00
    },
    {
        "class": "label_control",
        "settings": ["has_lint_warnings"],
        "parents": [{"class": "status_bar"}],
        "color": [219, 221, 232], // 02
        "font.size": 14
    },
    {
        "class": "label_control",
        "settings": ["has_lint_errors"],
        "parents": [{"class": "status_bar"}],
        "color": [19, 21, 32], // 02
        "font.size": 14
    },

  You can adjust the colors to your liking.

* It shows tooltips for the line your on.

* It shows phantoms as well.

You can't get more visual distraction ;-)

