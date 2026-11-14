# Form widgets

`cc_admin.widgets` has a few form widgets that fit the themes. They are ordinary Django widgets, so you can use them in any form: through `formfield_overrides`, in `formfield_for_dbfield`, or in a `ModelForm` you give to the admin.

```python
from cc_admin.widgets import (
    CodeWidget,
    ColorWidget,
    CounterTextarea,
    ImageWidget,
    JSONWidget,
    RichTextWidget,
    SegmentedWidget,
    SwitchWidget,
)
```

## SwitchWidget

A toggle switch for booleans.

```python
from django.db import models


class ProductAdmin(ModelAdmin):
    formfield_overrides = {models.BooleanField: {"widget": SwitchWidget}}
```

To use switches for every `BooleanField` in every `cc_admin.admin.ModelAdmin`, set `"FORMS": {"switches": True}` instead.

## SegmentedWidget

Radio choices drawn as one row of buttons. Best for three to six short options.

```python
class ProductAdmin(ModelAdmin):
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "status":
            kwargs["widget"] = SegmentedWidget(choices=db_field.choices)
        return super().formfield_for_dbfield(db_field, request, **kwargs)
```

## ColorWidget

A text input for a hex colour with a colour picker next to it. It accepts up to nine characters, so `#rrggbbaa` works.

```python
class CategoryAdmin(ModelAdmin):
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "hex_color":
            kwargs["widget"] = ColorWidget
        return super().formfield_for_dbfield(db_field, request, **kwargs)
```

## RichTextWidget

A small editor for HTML text with a toolbar. Pasted HTML is cleaned up, so text copied from a web page or a word processor does not bring its styles along.

```python
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = "__all__"
        widgets = {"body": RichTextWidget(toolbar=["bold", "italic", "h2", "ul", "ol", "link", "clear"])}
```

The toolbar buttons are `bold`, `italic`, `underline`, `strike`, `h2`, `h3`, `quote`, `ul`, `ol`, `code`, `link` and `clear`. Without `toolbar` you get all of them except `strike`.

The widget stores HTML in a normal text field. If people other than your staff can write to that field, clean the HTML on the way out, for example with `nh3` or `bleach`, before you show it on your site.

## CodeWidget

A monospace textarea where {kbd}`Tab` indents instead of moving to the next field. `language` is written to the field's `data-cc-code` attribute, which you can use in your own CSS or JavaScript:

```python
widgets = {"template": CodeWidget(language="html")}
```

## JSONWidget

A `CodeWidget` for JSON. It pretty prints the stored value and marks the field while the text is not valid JSON. It is used for every `JSONField` in `cc_admin.admin.ModelAdmin` unless you set `"FORMS": {"json_editor": False}`.

## ImageWidget

A file input that shows the current image and a preview of a newly chosen file before you save.

```python
formfield_overrides = {models.ImageField: {"widget": ImageWidget}}
```

## CounterTextarea

A textarea with a live character count. Give `limit` to also set `maxlength`:

```python
widgets = {"summary": CounterTextarea(limit=280)}
```

Text inputs with a `max_length` already show a counter while you type, unless `"FORMS": {"char_counter": False}`.

## Restyled Django widgets

You do not need to do anything for these. With the app installed, Django's own widgets match the theme: date and time pickers, the related object buttons (add, change, view, delete) next to foreign keys, `filter_horizontal` and `filter_vertical`, autocomplete fields, file inputs and select boxes.
