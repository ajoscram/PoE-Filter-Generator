import web
from core import ExpectedError
from rich.markdown import Markdown
from rich.console import Console

NAME = "update"

_LATEST_RELEASE_URL = "https://api.github.com/repos/ajoscram/PoE-Filter-Generator/releases/latest"

_NOTES_FIELD = "body"
_TAG_FIELD = "tag_name"
_ASSETS_FIELD = "assets"

_ASSET_NAME_FIELD = "name"
_ASSET_DOWNLOAD_URL = "browser_download_url"
_EXE_NAME = "pfg.exe"

def execute(_):
    release = web.get(_LATEST_RELEASE_URL)

    donwload_url = _get_download_url(release[_ASSETS_FIELD])
    # download and replace file here

    tag = release[_TAG_FIELD]
    notes = "# Release notes\n" + release[_NOTES_FIELD]
    notes_md = Markdown(notes)
    
    console = Console()
    console.print("Done! PFG was successfully updated to version {0}.".format(tag), '\n')
    console.print(notes_md)

def _get_download_url(assets: list[dict]):
    for asset in assets:
        if asset[_ASSET_NAME_FIELD] == _EXE_NAME:
            return asset[_ASSET_DOWNLOAD_URL]
    raise ExpectedError("Failed to find the update download URL on the release information. This is likely an unintended error and should be reported if possible.")

def _download_exe(url: str):
    pass