from invoke import collection

from . import (
    download,
)


namespace = collection.Collection(download)
