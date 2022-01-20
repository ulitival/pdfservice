FROM python:3.9-slim
EXPOSE 8000

WORKDIR /app

RUN apt-get update \
    && apt-get install -qq build-essential imagemagick \
    fonts-liberation ghostscript --no-install-recommends \
    && apt-get clean

# apply some "hacks" to remove security restrictions for imagemagick because without them PDF
# conversion to images doesn't work
RUN sed -i '/disable ghostscript format types/,+6d' /etc/ImageMagick-6/policy.xml

# build app here
COPY dist/* ./dist/pdf_rendering_service/
COPY requirements.txt ./dist/

# install the application
RUN pip install pdf_rendering_service --find-links file:///app/dist/pdf_rendering_service -r dist/requirements.txt

RUN rm -r ./dist

# prepare an entrypoint for the app
ENTRYPOINT ["pdfservice"]