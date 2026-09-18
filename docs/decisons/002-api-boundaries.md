# 002. API boundaries

## Decision

PDF validation lives in the extraction module, not the route, and checks
for the `%PDF-` magic number in the file's bytes rather than the
filename.

The endpoint takes an `UploadFile` rather than `bytes`.

Two distinct error responses: a file that is not a PDF at all returns
400, and a valid PDF with no readable text returns 422.

## Why

The rule "we do not parse non-PDFs" holds however the file arrives.
Putting the check in the route leaves a later batch job or queue
consumer unprotected. The route's only job is turning an HTTP request
into a function call and a result back into a response.

The magic number rather than the extension because the filename is
supplied by the caller and can say anything. A file arriving from S3 or
a queue may have no filename at all.

`UploadFile` streams and spills to disk past a threshold. Claim bundles
can be large, especially with photos attached, and loading each one
fully into memory does not survive concurrent uploads.

The two failures are genuinely different and the client should be able
to tell them apart. A scan with no text layer is a common real case and
needs a different message from a file that was never a PDF, because only
one of them is worth retrying with a better scan.

## Rejected

Checking in the route. Simpler today, silently unprotected the moment a
second entry point exists.

Checking the file extension. Trivially spoofed, and unavailable for any
non-HTTP source.

A single generic error response. Tells the client nothing about whether
a different file would help.

`bytes` for the upload. Loads the whole file into memory with no
threshold.