from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction

from pathlib import Path
from rapidfuzz import fuzz, process, utils

project_dir = Path("~/Projects").expanduser()
nested_prefix = "0_"
cmd = 'codium "{path}"'

def basename(path):
    return path.rsplit("/", 1)[-1]

def fuzz_processor(s):
    return utils.default_process(basename(s))

def fuzz_ratio(query, choice, **kwargs):
    if query.casefold() == basename(choice).casefold():
        return 100
    return fuzz.WRatio(query, choice) 

class ProjectOpener(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query = event.get_argument() or ""
        projects = [f.name for f in project_dir.iterdir() if f.is_dir()]
        while True:
            for i in filter(lambda x: basename(x).startswith(nested_prefix), projects):
                projects.remove(i)
                projects.extend([str(f.relative_to(project_dir)) for f in (project_dir / i).iterdir() if f.is_dir()])
            else:
                break

        return RenderResultListAction([
            ExtensionSmallResultItem(
                icon="images/vscodium.png",
                name=f"{i[0]} ⭐" if i[1] == 100 else i[0],
                on_enter=RunScriptAction(cmd.format(path=str(project_dir / i[0])))
            ) for i in process.extract(query, projects, scorer=fuzz_ratio, processor=fuzz_processor, limit=10)
        ])

if __name__ == '__main__':
    ProjectOpener().run()