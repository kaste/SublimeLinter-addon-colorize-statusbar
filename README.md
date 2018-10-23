
Add-on to SublimeLinter which will do various UI blinking so you always know if your current file is green or red.



# Features

* It will set global flags which in turn can be used by a theme to indicate if a view/window has errors or warnings or is green to commit.

E.g. if you want to tint your status bar, you could add something like this 
to your `.sublime-theme` file. (Do this in your local override in the User folder.)

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

* It popups tooltips if you enter a line with lint errors.

* It shows annotations/phantoms as well.

You really can't get more visual distraction ;-)


# Install

I would recommend you just clone this repository into your packages folder.
If you want to go fancy, you can also do this:

1. Open up the command palette (`ctrl+shift+p`), and find `Package Control: Add Repository`. Then enter the URL of this repo: `https://github.com/kaste/SublimeLinter-addon-alt-ui/` in the input field.
2. Open up the command palette again and find `Package Control: Install Package`, and just search for `SublimeLinter-addon-alt-ui`. (just a normal install)

