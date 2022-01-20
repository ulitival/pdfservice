DROP TABLE IF EXISTS status;
DROP TABLE IF EXISTS document;
DROP TABLE IF EXISTS page;

CREATE TABLE status (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name varchar(80) NOT NULL
);

INSERT INTO status (name) VALUES ('processing');
INSERT INTO status (name) VALUES ('done');
INSERT INTO status (name) VALUES ('failed');
INSERT INTO status (name) VALUES ('pending');

CREATE TABLE document
(
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    status_id bigint REFERENCES status ON DELETE RESTRICT,
    num_pages integer NOT NULL,
    creation_time timestamp NOT NULL,
    processing_start_time timestamp,
    processing_finished_time timestamp
);

CREATE TABLE page (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    p_number integer NOT NULL,
    page bytea NOT NULL,
    document_id uuid REFERENCES document ON DELETE CASCADE
);

CREATE INDEX "p_document_id" ON "page" ("document_id");

-- let's add a user that will have w/r access to the tables above
CREATE USER pdfservice_user WITH ENCRYPTED PASSWORD 'pdfservice_user';
GRANT ALL ON document, page TO pdfservice_user;
GRANT SELECT ON status TO pdfservice_user;