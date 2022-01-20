# Application prerequisites

The app is running inside Docker thus you need to have docker engine installed on a machine you want to run the application on.

# Build the application

After you prepared you developer environment following the instructions from `README.md` in the project's root directory you can build the `pdfservice` app. By invoking in the terminal `make build` poetry will take care of building as a result there will be both `sdist` and `wheel` distribution of the application inside the `dist` directory, located in the project's root directory.

The next step is to build a docker container with the `pdfservice` app, after we built the app we can run `docker-compose build api` to build an image or we can start the whole compose system, i.e. `pdfservice api`, `pdfservice processor`, `rabbitmq` broker and `postgresql` database by invoking `docker-compose up -d`. If `docker-compose` finds out that there is not `pdfservice` image available it will build the image first and then run it.

# Run the application

From the terminal run `docker-compose up -d` and wait for a minute until all the services are up and running.

# Process PDF files using REST API

### Send document

To start normalizing pdf files you can send them (one by one, bulk upload is not yet supported) to the `POST` `/documents` endpoint. Let's assume that you have started the application and everything works correctly, then you can invoke:

``` shell
$ curl -H "Content-Type: multipart/form-data" -F "file=@your_pdf_file.pdf" http://localhost:8000/documents
```

if it's a valid pdf then we can expect a response with the id that was assigned to that document

``` json
{
  "id": "69fecd88-7ad3-4d24-a943-54ee050e87ae"
}
```

### Check the document's processing status

Alright our document was sent and apparently something is happening to it, but how do we know when the processing is done? Simply call the `GET` `/documents/<document_id>` endpoint like this:

``` shell
$ curl -H "Accept: application/json" http://localhost:8000/documents/69fecd88-7ad3-4d24-a943-54ee050e87ae
```

in a response we can check the total number of pages in the document and as well its current processing status.

```json
{
  "status": "pending",
  "n_pages": 12
}
```

right, the document was acknowledged by the processor but processing hasn't started yet (workers may be busy with other tasks) that's why its status is `pending`.

At the moment when pdf processor pick up the document and start converting its pages to "normalized" images you will see that the status has changed to `processing` when calling the `GET` `/documents/<document_id>` endpoint.

```json
{
  "status": "processing",
  "n_pages": 12
}
```

When processing is done either successfully or unsuccessfully the status will change to `done` or `failed` depending on a result.

```json
{
  "status": "done",
  "n_pages": 12
}
```

### Retrieve document's page as a normalized image

Ok, now we see that the status has changed to `done` and that means our document was processed. 

Let's now get a normalized page using the API. For accessing individual page we need to call the `GET` `/documents/<document_id>/pages/<page_number>` endpoint.

``` shell
$ curl http://localhost:8000/documents/69fecd88-7ad3-4d24-a943-54ee050e87ae/pages/1 -o page_1.png
```

Please note, that this endpoint returns binary representation of an image. That's why we need to save the output to an image container, otherwise you'll get you terminal spammed by a lot of gibberish. `curl` is a quite smart tool thus it will warn you if you forget to specify a file where your image will be stored.

That's it. Now you know how you can upload your pdf files to get them "normalized".

