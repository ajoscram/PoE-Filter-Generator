import web, console, sys, json
from core import ExpectedError
from commands.update import ASSET_DOWNLOAD_URL_FIELD as EXE_DOWNLOAD_URL_FIELD, DIRECTORY_FIELD, EXE_NAME, TAG_FIELD, NOTES_FIELD

_UNEXPECTED_DATA_ERROR = """The update process failed because the updater received unexpected data.
This is likely due to a breaking change between versions.
Please download your update manually from it's release page:

https://github.com/ajoscram/PoE-Filter-Generator/releases/latest

Sorry for the hassle!"""

def main():
    try:
        if len(sys.argv) != 2:
            raise ExpectedError(_UNEXPECTED_DATA_ERROR)
        params = json.loads(sys.argv[1])
        
        download_url = _get_param(EXE_DOWNLOAD_URL_FIELD, params)
        exe_dir = _get_param(DIRECTORY_FIELD, params)
        tag = _get_param(TAG_FIELD, params)
        notes = _get_param(NOTES_FIELD, params)

        console.write("Downloading the latest version's executable. This might take a while...")
        web.download(download_url, exe_dir, EXE_NAME)
        
        console.write("Successfully updated to version {0}.".format(tag), done=True)
        console.write(notes, markdown=True)
    
    except Exception as error:
        console.err(error)

def _get_param(param_name: str, params: dict):
    if not param_name in params:
        raise ExpectedError(_UNEXPECTED_DATA_ERROR)
    return params[param_name]

if __name__ == "__main__":
    main()