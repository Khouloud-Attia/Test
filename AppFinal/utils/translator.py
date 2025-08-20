import json
import os

class Translator:
    def __init__(self, lang="en"):
        self.lang = lang
        self.translations = {}
        self.load_translations()

    def load_translations(self):
        path = f"translations/{self.lang}.json"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
        else:
            self.translations = {}

    def set_language(self, lang):
        self.lang = lang
        self.load_translations()

    def t(self, key):
        return self.translations.get(key, key)
