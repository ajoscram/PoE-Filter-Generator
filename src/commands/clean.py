import web, console

NAME = "clean"

DELETING_CACHE_MESSAGE = "Deleting cache..."
CACHE_DELETED_MESSAGE = "Cache deleted."
CACHE_NOT_DELETED_MESSAGE = "The cache folder wasn't found. Nothing was deleted!"

def execute(_):
    """Deletes all files cached from web downloads."""
    console.write(DELETING_CACHE_MESSAGE)
    deleted = web.clear_cache()
    completion_message = CACHE_DELETED_MESSAGE if deleted else CACHE_NOT_DELETED_MESSAGE
    console.write(completion_message, done=True)