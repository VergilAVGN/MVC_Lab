from __future__ import annotations
import re
from django import forms
from PIL import Image
from .models import Recipe, Comment

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ["name", "ingredients", "instructions", "image","image_url"]
        widgets = {
            "image_url": forms.HiddenInput(),
        }
    def clean_name(self) -> str:
        name: str = (self.cleaned_data.get("name") or "").strip()
        if len(name) < 3:
            raise forms.ValidationError("Name must be at least 3 characters long.")
        if len(name) > 100:
            raise forms.ValidationError("Name is too long (max 100 characters).")
        return name
    def clean_ingredients(self) -> str:
        # Wait for format as in JS: strings in the format "- item"
        raw: str = (self.cleaned_data.get("ingredients") or "").replace("\r\n", "\n").strip()
        if not raw:
            raise forms.ValidationError("Ingredients are required.")
        lines = [ln.strip() for ln in raw.split("\n") if ln.strip()]
        if len(lines) < 2:
            raise forms.ValidationError("Please add at least 2 ingredients.")
        bad = [ln for ln in lines if not re.match(r"^-\s+\S", ln)]
        if bad:
            raise forms.ValidationError(
                "Ingredients must be one per line in format: '- ingredient'."
            )
        return "\n".join(lines)
    def clean_instructions(self) -> str:
        # Wait for format as in JS: "1. Step", "2. Step", ...
        raw: str = (self.cleaned_data.get("instructions") or "").replace("\r\n", "\n").strip()
        if not raw:
            raise forms.ValidationError("Instructions are required.")
        lines = [ln.strip() for ln in raw.split("\n") if ln.strip()]
        if len(lines) < 1:
            raise forms.ValidationError("Please add at least 1 instruction step.")
        # Wait for syntax and sequential numbering
        for i, ln in enumerate(lines, start=1):
            m = re.match(r"^(\d+)\.\s+(\S.*)$", ln)
            if not m:
                raise forms.ValidationError(
                    "Each instruction must be on a new line in format: '1. Do something'."
                )
            num = int(m.group(1))
            if num != i:
                raise forms.ValidationError(
                    f"Instruction steps must be numbered sequentially (expected {i}.)."
                )
        return "\n".join(lines)
    def clean_image(self):
        image = self.cleaned_data.get("image")
        if not image:
            return image
        # size limit: 5MB
        if image.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Image is too large (max 5MB).")
        # content_type — fast check, but not the main protection
        content_type = getattr(image, "content_type", "")
        if content_type and not content_type.startswith("image/"):
            raise forms.ValidationError("Only images can be uploaded.")
        # Real content check
        try:
            image.seek(0)
            img = Image.open(image)
            img.verify()  # checks that this is really an image and not a corrupted file
        except Exception:
            raise forms.ValidationError("File is corrupted or not an image.")
        finally:
            # after verify() the file needs to be reset to the beginning so Django can save it
            try:
                image.seek(0)
            except Exception:
                pass
        return image

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Write a comment...',
            }),
        }

    def clean_text(self) -> str:
        text = (self.cleaned_data.get('text') or '').strip()
        if len(text) < 3:
            raise forms.ValidationError('Comment must be at least 3 characters.')
        if len(text) > 500:
            raise forms.ValidationError('Comment is too long (max 500 characters).')
        return text