import web, console, sys, json, utils
from core import ExpectedError, ERROR_EXIT_CODE
from commands.update import ASSET_DOWNLOAD_URL_FIELD as EXE_DOWNLOAD_URL_FIELD, DIRECTORY_FIELD, EXE_NAME, TAG_FIELD, NOTES_FIELD

_UNEXPECTED_DATA_ERROR = """The update process failed because the updater received unexpected data.
This is likely due to a breaking change between versions.
Please download the latest version manually from it's release page:

https://github.com/ajoscram/PoE-Filter-Generator/releases/latest

Sorry for the hassle!"""

_DOWNLOADING_EXE_MESSAGE = "Downloading the latest version's executable. This might take a while..."
_DELETING_CACHE_MESSAGE = "Deleting the previous version's cache..."
_SUCCESSFUL_UPDATE_MESSAGE = "Successfully updated to version {0}."

def main(args: list[str]):
    try:
        params = _load_params(args)
        download_url = _get_param(params, EXE_DOWNLOAD_URL_FIELD)
        exe_dir = _get_param(params, DIRECTORY_FIELD)
        tag = _get_param(params, TAG_FIELD)
        notes = _get_param(params, NOTES_FIELD)

        console.write(_DOWNLOADING_EXE_MESSAGE)
        web.download(download_url, exe_dir, EXE_NAME)

        console.write(_DELETING_CACHE_MESSAGE)
        web.clear_cache()
        
        console.write(_SUCCESSFUL_UPDATE_MESSAGE.format(tag), done=True)
        console.write(notes, markdown=True)
    
    except Exception as error:
        console.err(error)
        sys.exit(ERROR_EXIT_CODE)

def _get_param(params: dict[str], param_name: str):
    if not param_name in params:
        raise ExpectedError(_UNEXPECTED_DATA_ERROR)
    return params[param_name]

def _load_params(args: list[str]) -> dict[str]:
    if len(args) != 1:
        raise ExpectedError(_UNEXPECTED_DATA_ERROR)
    try:
        params_text = utils.b64_decode(args[0])    
        return json.loads(params_text)
    except json.JSONDecodeError as error:
        raise ExpectedError(_UNEXPECTED_DATA_ERROR) from error

if __name__ == "__main__":
    main(sys.argv[1:])