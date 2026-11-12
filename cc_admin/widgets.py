###############
# Qiyas Sadıqov CC
###############

import json

from django import forms

from . import icons


def _merge(attrs, extra):
    attrs = dict(attrs or {})
    for key, value in extra.items():
        if key == "class" and attrs.get("class"):
            attrs["class"] = f"{attrs['class']} {value}"
        else:
            attrs.setdefault(key, value)
    return attrs


class SwitchWidget(forms.CheckboxInput):
    def __init__(self, attrs=None, check_test=None):
        super().__init__(_merge(attrs, {"class": "cc-switch", "role": "switch"}), check_test)


class ColorWidget(forms.TextInput):
    def __init__(self, attrs=None):
        super().__init__(_merge(attrs, {"data-cc-color": "", "class": "cc-color-text", "maxlength": "9", "spellcheck": "false"}))


class SegmentedWidget(forms.RadioSelect):
    def __init__(self, attrs=None, choices=()):
        super().__init__(_merge(attrs, {"data-cc-segmented": ""}), choices)


RICH_ICONS = {
    "bold": "type",
    "italic": "italic",
    "underline": "underline",
    "strike": "strikethrough",
    "h2": "heading-2",
    "h3": "heading-3",
    "quote": "text-quote",
    "ul": "list",
    "ol": "list-ordered",
    "code": "code",
    "link": "link",
    "clear": "remove-formatting",
}


class RichTextWidget(forms.Textarea):
    def __init__(self, attrs=None, toolbar=None):
        self.toolbar = list(toolbar or ["bold", "italic", "underline", "h2", "h3", "ul", "ol", "quote", "link", "code", "clear"])
        super().__init__(_merge(attrs, {"data-cc-rich": ",".join(self.toolbar)}))

    def render(self, name, value, attrs=None, renderer=None):
        for tool in self.toolbar:
            icons.use(RICH_ICONS.get(tool))
        return super().render(name, value, attrs, renderer)


class CodeWidget(forms.Textarea):
    def __init__(self, attrs=None, language=""):
        super().__init__(_merge(attrs, {"data-cc-code": language, "class": "cc-code", "spellcheck": "false", "rows": 12}))


class JSONWidget(CodeWidget):
    def __init__(self, attrs=None):
        super().__init__(attrs, "json")

    def format_value(self, value):
        if value in (None, ""):
            return ""
        try:
            return json.dumps(json.loads(value), indent=2, ensure_ascii=False)
        except (TypeError, ValueError):
            return value


class ImageWidget(forms.ClearableFileInput):
    def __init__(self, attrs=None):
        super().__init__(_merge(attrs, {"data-cc-preview": "", "accept": "image/*"}))


class CounterTextarea(forms.Textarea):
    def __init__(self, attrs=None, limit=None):
        extra = {"data-cc-count": ""}
        if limit:
            extra["maxlength"] = str(limit)
        super().__init__(_merge(attrs, extra))


__all__ = ["CodeWidget", "ColorWidget", "CounterTextarea", "ImageWidget", "JSONWidget", "RichTextWidget", "SegmentedWidget", "SwitchWidget"]
