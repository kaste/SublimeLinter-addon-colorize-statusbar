
Add-on to SublimeLinter which help you to colorize the status bar (or some other theme-ish thing) when the current view has errors.

☝️ **NOTE: You have to do something to make this work. Read below** 👇


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
            "class": "label_control",
            "settings": ["has_lint_errors"],
            "parents": [{"class": "status_bar"}],
            "color": [19, 21, 32], // 02
            "font.size": 14
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

*OR* something like this

    {
        "class": "status_container",
        "settings": ["has_lint_errors"],
        "layer0.tint": [215, 57, 118, 190], // -00
    },
    {
        "class": "label_control",
        "settings": ["has_lint_errors"],
        "parents": [{"class": "status_container"}],
        "color": [219, 221, 232], // 02
    },

So you might try styling `status_bar` or `status_container`.  I use the latter.

You can adjust the colors to your liking of course.  Just notice the usage of the two special keys `has_lint_errors` and `has_lint_warnings`.

Maybe take a quick look at the [global settings](https://github.com/kaste/SublimeLinter-addon-colorize-statusbar/blob/master/SublimeLinter-addon-colorize-statusbar.sublime-settings).


# Install

I would recommend you just clone this repository into your packages folder.
If you want to go fancy, you can also do this:

1. Open up the command palette (`ctrl+shift+p`), and find `Package Control: Add Repository`. Then enter the URL of this repo: `https://github.com/kaste/SublimeLinter-addon-colorize-statusbar/` in the input field.
2. Open up the command palette again and find `Package Control: Install Package`, and just search for `SublimeLinter-addon-colorize-statusbar`. (just a normal install)

