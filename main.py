from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction

import subprocess
from pathlib import Path
from rapidfuzz import fuzz, utils

def fuzzy_ls(path, query, prefix=""):
    return RenderResultListAction([
        ExtensionSmallResultItem(
            icon="images/vscodium.png",
            name=prefix + i,
            on_enter=ExtensionCustomAction({"name": i, "path": path / i}, keep_app_open=True)
        ) for i in sorted(
            (f.name for f in path.iterdir() if f.is_dir()),
            key=lambda x: fuzz.WRatio(query, x, processor=utils.default_process), reverse=True
        )
    ])

class ProjectOpener(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query = event.get_argument() or ""
        return fuzzy_ls(Path("~/Projects").expanduser(), query)

class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        name, path = event.get_data().values()
        if not name:
            return HideWindowAction()
        elif name.startswith("0_"): # Nested project directory
            return fuzzy_ls(path, "", prefix=name + "/")
        subprocess.Popen(["codium", str(path)])
        return HideWindowAction()

if __name__ == '__main__':
    ProjectOpener().run()