# Setting Things Up

PDF rendering service has a few binary dependencies that are required for pdf processing, namely for conversion a pdf page to an image. The package names below
are valid for Debian; they may differ slightly on other GNU/Linux
distros:

``` shell
# apt-get update
# apt-get install -qq \
 build-essential imagemagick \
 fonts-liberation ghostscript --no-install-recommends
```

On Mac OS X, use Homebrew to install `imagemagick` and `ghostscript`. The `fonts-liberation` is optional and I am note even sure that it exists for Mac OS X.

Now that we have installed all the necessary OS-level dependencies,
let’s move on to installing the python project itself. It is currently
using `poetry` as a dependency management and packaging tool of choice.
If you would like to install the project using `pip` directly which is
useful to know for some use-cases such as building a docker image with
`pdfservice` and without `poetry`. For the impatient the way how to install `pdfservice` without using `poetry` can be found inside the `.docker/Dockerfile`.

# Install Using Poetry

### First, you should install `pyenv`:

``` shell
# curl https://pyenv.run | bash
```

After `pyenv` is successfully installed you may run `make setup` that will initiate project's setup, i.e. picking up defined in the `.python-verion` file version of python interpreter and as well set up `poetry` specific settings.

### Initiate the project

From within the project’s root folder you may try
`poetry install` as also defined in the Makefile as `make init`.
That should work directly without any issues.
From that moment you can freely make changes in the code and basically your development environment is ready.

## Configurable options

There are few configurable parameters for image conversion that can be set via environment variables. Those are:

* `PDFSERVICE_NORM_WIDTH` specifies the output width of a resulting image after a pdf page was converted.
* `PDFSERVICE_NORM_HEIGHT` specifies the output height of a resulting image after a pdf page was converted.
* `PDFSERVICE_IMAGE_RESOLUTION` specifies the resulting resolution for pdf to image conversion. The bigger number the better quality of an output image but slower processing time. It's up to you to find an accessible trade-off.

## Starting a pdfservice instance

Among other things, `pdfservice` has a CLI that allows you to easily set up a simple REST
API and a `dramatiq` actor.

``` shell
$ pdfservice api --workers 1 --host localhost --port 8000 --timeout 0
$ pdfservice processor --processes 1 --threads 1
```

Now, you should see your API listening on `localhost:8080`:

``` shell
$ curl -H "Accept: application/json" http://localhost:8000/v1/documents/f3b69ba3-78d9-4c22-8f81-656c75a0b7df
```

above is a hypothetical example of how a request can look like. Most likely if you try to run it after you API server booted you will get an `404` error.

## API upgrade strategy

Inside the `pdf_rendering_service.api` package you can find the API structure. It was designed in a such way that we can easily introduce a new version of the contract, let's say later a new `v2` version of API was implemented. It would be located inside the `pdf_rendering_service.api.v2` package and expose a Flask Blueprint. That blueprint then is registered in the Flask `app` (located in `pdf_rendering_service.api.application`) instance both as the default one and the one with the `/v2` prefix. At this point we would have two contracts the old one `v1` accessible via prefix `/v1` and the new one `v2` accessible via prefix `/v2`. At the moment when the old `v1` becomes obsolete and is no longer needed, we can "deregister" its Blueprint from the `app` and remove the `pdf_rendering_service.api.v1` package and that's it.


## Security concerns

It was not specified in the task requirements, but I don't think that allowing anyone to access any document/page is a good idea from security point of view. Ideally we would like to restrict access so only owners of documents can have rights to get normalized pages back. Nevertheless, this is out of scope of this project and may be implemented in the future.

## Further improvements

As we store images as binary data in the database we would ideally want to remove them from time to time. That will prevent our database to grow in size to the point when it became really slow.

For that as a next step in development a cleaner worker should be introduced. This cleaner will remove documents that are older than a particular number of days, let's say a one day. The database is already ready for that as we store times when document was created, picked up for processing or finished. The worker then just need to get in regular intervals document records from the database and compare finished time with the current one.

Having times stored in the database can also help to mitigate problematic documents. For instance documents that are being processed for unreasonable long time or documents that were never picked up by a pdf processor worker. There might be a reporter worker, that will report all the suspicious cases.

## Logging

All the logging is done in a way that it outputs information to stdout. If it's necessary this can be changed, for example logs can be redirected to a centralized logging system or can be stored to a file.

## Differences compared to the task's requirements

To the 'status' table were added two values: "failed" and "pending".
   
* "failed" status means that document was not processed, and an exception arose.
* "pending" status is set in a moment when a document is uploaded. The status means that we acked the document, but a pdf normalization process has not started yet.