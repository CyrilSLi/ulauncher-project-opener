from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction

import shlex
from pathlib import Path
from rapidfuzz import fuzz, process, utils

project_dir = Path("~/Projects").expanduser()
nested_prefix = "0_"
cmd = "codium {path}"

def safe_iterdir(path):
    try:
        for f in path.iterdir():
            if f.is_dir() and not f.is_symlink():
                yield f
    except OSError:
        pass

def basename(path):
    return path.rsplit("/", 1)[-1]

def fuzz_processor(s):
    return utils.default_process(basename(s))

class ProjectOpener(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query = event.get_argument() or ""
        projects = [f.name for f in safe_iterdir(project_dir)]
        while nested := [x for x in projects if basename(x).startswith(nested_prefix)]:
            for i in nested:
                projects.remove(i)
                projects.extend([str(f.relative_to(project_dir)) for f in safe_iterdir(project_dir / i)])

        return RenderResultListAction([
            ExtensionSmallResultItem(
                icon="images/vscodium.png",
                name=f"{i[0]} ⭐" if i[1] == 100 else i[0],
                on_enter=RunScriptAction(cmd.format(path=shlex.quote(str(project_dir / i[0]))))
            ) for i in process.extract(query, projects, scorer=fuzz.WRatio, processor=fuzz_processor, limit=10)
        ])

if __name__ == '__main__':
    ProjectOpener().run()