import web, console, os, json, utils
from core import ExpectedError

NAME = "update"

ASSET_DOWNLOAD_URL_FIELD = "browser_download_url"
DIRECTORY_FIELD = "directory"
NOTES_FIELD = "body"
TAG_FIELD = "tag_name"
EXE_NAME = "pfg.exe"

_LATEST_RELEASE_URL = "https://api.github.com/repos/ajoscram/PoE-Filter-Generator/releases/latest"
_UPDATER_EXE_NAME = "updater.exe"
_ASSETS_FIELD = "assets"
_ASSET_NAME_FIELD = "name"

_FAILED_TO_FIND_DOWNLOAD_URL_ERROR = "Failed to find the '{0}' download URL on the release information."
_DOWNLOADING_UPDATER_MESSAGE = "Downloading the latest version's updater. This might take a while..."
_EXECUTING_UPDATER_MESSAGE = "Executing the latest version's updater..."
_GETTING_RELEASE_MESSAGE = "Getting the latest release information..."
_RELEASE_NOTES_PREFIX = "# Release notes\n"

def execute(_):
    """Downloads and executes the updater found on the latest release.
    The updater is a separate program whose entry point can be found on `src/update.py`."""
    console.write(_GETTING_RELEASE_MESSAGE)
    release: dict[str] = web.get(_LATEST_RELEASE_URL)
    
    curr_dir = utils.get_execution_dir()
    updater_download_url = _get_download_url(release, _UPDATER_EXE_NAME)
    updater_params = _get_serialized_updater_params(release, curr_dir)
    updater_filepath = os.path.join(curr_dir, _UPDATER_EXE_NAME)
    
    console.write(_DOWNLOADING_UPDATER_MESSAGE)
    web.download(updater_download_url, curr_dir, _UPDATER_EXE_NAME)

    console.write(_EXECUTING_UPDATER_MESSAGE, done=True)
    os.execl(updater_filepath, updater_filepath, updater_params)

def _get_download_url(release: dict[str], asset_name: str):
    for asset in release[_ASSETS_FIELD]:
        if asset[_ASSET_NAME_FIELD] == asset_name:
            return asset[ASSET_DOWNLOAD_URL_FIELD]
    raise ExpectedError(_FAILED_TO_FIND_DOWNLOAD_URL_ERROR.format(asset_name))

def _get_serialized_updater_params(release: dict[str], curr_dir: str):
    params = {
        ASSET_DOWNLOAD_URL_FIELD: _get_download_url(release, EXE_NAME),
        NOTES_FIELD: _RELEASE_NOTES_PREFIX + release[NOTES_FIELD],
        TAG_FIELD: release[TAG_FIELD],
        DIRECTORY_FIELD: curr_dir }
    params_string = utils.b64_encode(json.dumps(params))
    return f'"{params_string}"'