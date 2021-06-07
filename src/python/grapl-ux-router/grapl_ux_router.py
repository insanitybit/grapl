from __future__ import annotations

import gzip as web_compress
import json
import logging
import os
import sys
import time
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, TypeVar, Union, cast

import boto3
from chalice import Chalice, Response
from grapl_common.env_helpers import S3ResourceFactory

if TYPE_CHECKING:
    from mypy_boto3_s3.service_resource import Bucket

    pass

GRAPL_LOG_LEVEL = os.environ.get("GRAPL_LOG_LEVEL", "ERROR")
UX_BUCKET_NAME = os.environ["UX_BUCKET_NAME"]

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(GRAPL_LOG_LEVEL)
LOGGER.addHandler(logging.StreamHandler(stream=sys.stdout))

CONTENT_ENCODING = "gzip"

# Must never hold more than 15 values
MEDIA_TYPE_MAP = {
    "json": "application/json",
    "ico": "image/x-icon",
    "png": "image/png",
    "html": "text/html",
    "txt": "text/plain",
    "css": "text/css",
    "js": "text/javascript",
    "chunk.js": "text/javascript",
    "chunk.css": "text/css",
    "map": "application/json",
    "": "application/octet-stream",
}


class LazyUxBucket:
    def __init__(self) -> None:
        self.ux_bucket: Optional[Bucket] = None

    def get(self) -> Bucket:
        if self.ux_bucket is None:
            self.ux_bucket = self._retrieve_bucket()
        return self.ux_bucket

    def get_resource(self, resource_name: str) -> Optional[bytes]:
        bucket = self.get()
        start = int(time.time())
        try:
            obj = bucket.Object(resource_name)
            # todo: We could just compress right here instead of allocating this intermediary
            # Or we could compress the files in s3?
            retrieved = cast(bytes, obj.get()['Body'].read())
            end = int(time.time())
            LOGGER.debug(f"retrieved object {resource_name} after {end - start}")
        except bucket.meta.client.exceptions.AccessDenied as e:
            end = int(time.time())
            LOGGER.warning(f"Failed to retrieve object: {e} after {end - start}")
            return None
        except bucket.meta.client.exceptions.NoSuchKey as e:
            end = int(time.time())
            LOGGER.debug(f"Failed to retrieve object: {e} after {end - start}")
            return None
        except Exception as e:
            # TODO: We should only return None in cases where the object doesn't exist
            end = int(time.time())
            LOGGER.warning(f"Failed to retrieve object: {e} after {end - start}")
            raise

        return retrieved

    def _retrieve_bucket(self) -> Bucket:
        s3 = S3ResourceFactory(boto3).from_env()
        return s3.Bucket(UX_BUCKET_NAME)


UX_BUCKET = LazyUxBucket()


app = Chalice(app_name="grapl-ux-edge")

# If we ever have more than 16 binary types we need to
# instead explicitly set it for every response
# https://aws.github.io/chalice/api.html#APIGateway.binary_types
if len(MEDIA_TYPE_MAP) >= 14:
    LOGGER.error("MEDIA_TYPE_MAP length is too high")
elif len(MEDIA_TYPE_MAP) >= 11:
    LOGGER.warning("MEDIA_TYPE_MAP length is too high")
for _media_type in MEDIA_TYPE_MAP.values():
    app.api.binary_types.append(_media_type)

# TODO: We should toggle app.debug with a flag

# Sometimes we pass in a dict. Sometimes we pass the string "True". Weird.
Res = Union[Dict[str, Any], str]


def respond(
    err: Optional[str],
    res: Optional[Res] = None,
    headers: Optional[Dict[str, Any]] = None,
) -> Response:

    if not headers:
        headers = {}

    compressed_body = web_compress.compress(
        json.dumps({"error": err} if err else {"success": res}).encode()
    )

    return Response(
        body=compressed_body,
        status_code=400 if err else 200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "false",
            "Content-Type": "application/json",
            "Content-Encoding": CONTENT_ENCODING,
            "Access-Control-Allow-Methods": "GET,OPTIONS",
            "X-Requested-With": "*",
            "Access-Control-Allow-Headers": "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With",
            **headers,
        },
    )


RouteFn = TypeVar("RouteFn", bound=Callable[..., Response])


def no_auth(path: str) -> Callable[[RouteFn], RouteFn]:
    # TODO: Investigate this; it should not be required!
    path = "/{proxy+}" + path

    def route_wrapper(route_fn: RouteFn) -> RouteFn:
        @app.route(path, methods=["OPTIONS", "GET"])
        def inner_route() -> Response:
            if app.current_request.method == "OPTIONS":
                return respond(None, {})
            try:
                return route_fn()
            except Exception as e:
                LOGGER.error(f"path {path} had an error: {e}")
                return respond("Unexpected Error")

        return cast(RouteFn, inner_route)

    return route_wrapper


def not_found() -> Response:
    body = json.dumps({"Error": "Not Found"}).encode("utf8")
    return Response(
        status_code=404,
        body=web_compress.compress(body),
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "false",
            "Access-Control-Allow-Methods": "GET,OPTIONS",
            "X-Requested-With": "*",
            "Access-Control-Allow-Headers": "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With",
        },
    )


def get_media_type(resource_name: str) -> str:
    name_parts = resource_name.split(".")
    for i, _name_part in enumerate(name_parts):
        name = ".".join(name_parts[i:])
        media_type = MEDIA_TYPE_MAP.get(name)
        if media_type:
            return media_type
    return "application/octet-stream"


def _route_to_resource(resource_name: str) -> Response:
    LOGGER.info(f"fetching {resource_name}")
    resource = UX_BUCKET.get_resource(resource_name)
    if not resource:
        return not_found()
    content_type = get_media_type(resource_name)
    LOGGER.debug(
        f"setting content-type:  content_type: {content_type} resource_name: {resource_name}"
    )
    return Response(
        body=web_compress.compress(resource),
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "false",
            "Content-Type": content_type,
            "Content-Encoding": CONTENT_ENCODING,
            "Cache-Control": "max-age=60",
            "Access-Control-Allow-Methods": "GET,OPTIONS",
            "X-Requested-With": "*",
            "Access-Control-Allow-Headers": "Content-Encoding, Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With",
        },
    )


@app.route("/prod/{proxy+}", methods=["OPTIONS", "GET"])
def prod_nop_route() -> Response:
    LOGGER.info(f'nop_route {app.current_request.context["path"]}')
    if app.current_request.method == "OPTIONS":
        return respond(None, {})

    path = app.current_request.context["path"]
    if path == "/prod/":
        return _route_to_resource("index.html")
    elif path.startswith("/prod/"):
        resource_name = path.split("/prod/")[1]
        return _route_to_resource(resource_name)
    else:
        return _route_to_resource(path)


@app.route("/{proxy+}", methods=["OPTIONS", "GET"])
def nop_route() -> Response:
    LOGGER.info(f'nop_route {app.current_request.context["path"]}')
    if app.current_request.method == "OPTIONS":
        return respond(None, {})

    path = app.current_request.context["path"]
    if path == "/prod/":
        return _route_to_resource("index.html")
    elif path.startswith("/prod/"):
        resource_name = path.split("/prod/")[1]
        return _route_to_resource(resource_name)
    else:
        return _route_to_resource(path)


@app.route("/", methods=["OPTIONS", "GET"])
def root_nop_route() -> Response:
    LOGGER.info(f'root_nop_route {app.current_request.context["path"]}')
    if app.current_request.method == "OPTIONS":
        return respond(None, {})
    return _route_to_resource("index.html")
