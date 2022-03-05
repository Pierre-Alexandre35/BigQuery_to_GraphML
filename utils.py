# pylint: disable=missing-module-docstring, missing-function-docstring
def clean_id(text):
    transformations = {
        " ": "_",
        "[": ".",
        "]": "",
        "(": ".",
        ")": "",
        "/": ".",
        "€": "",
        ";": "",
        "+": "",
        "&amp;": "amp"
    }
    for i, j in transformations.items():
        text = text.replace(i, j)
    return text.lower()
