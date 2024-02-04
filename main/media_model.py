from pathlib import Path

from PIL import Image
from django.db import models

BASE_DIR = Path(__file__).resolve().parent.parent


class Media(models.Model):
    file = models.FileField()
    resized_file = models.FileField(blank=True, null=True)
    alt = models.CharField(max_length=100, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file.name

    def save(self, *args, **kwargs):
        if self.resized_file:
            size = kwargs.pop("size", (350, 350))
            rf = Image.open(self.resized_file)
            new_rf = rf.resize(size)
            file_name = f"{size[0]}x{size[1]}-{self.resized_file}"
            new_rf.save(f"{BASE_DIR}/media/{file_name}", optimize=True)
            self.resized_file = file_name

        super(Media, self).save(*args, **kwargs)
