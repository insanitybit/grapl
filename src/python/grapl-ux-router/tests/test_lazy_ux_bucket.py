import unittest
import os
from typing import cast
from unittest import TestCase
import boto3
import pytest
from grapl_common.grapl_logger import get_module_grapl_logger
from grapl_ux_router.src.lazy_ux_bucket import LazyUxBucket

LOGGER = get_module_grapl_logger()
UX_BUCKET_NAME = os.environ["UX_BUCKET_NAME"]


@pytest.mark.integration_test
class TestLazyUXBucket(unittest.TestCase):
    def test_get_resource(self):
        put_s3_object("index.html", INDEX_HTML)
        bucket = LazyUxBucket()



def put_s3_object(path: str, data: bytes)
    s3 = S3ResourceFactory(boto3).from_env()
    bucket = s3.Bucket(UX_BUCKET_NAME)
    bucket.put_object(Body=data, Key=path)

INDEX_HTML = b'''
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta
      name="description"
      content="Grapl: A Graph Analytics Platform for Detection & Response"
    />
    <!-- <link rel="apple-touch-icon" href="%PUBLIC_URL%/logo192.png" /> -->
    <!--
      manifest.json provides metadata used when your web app is installed on a
      user's mobile device or desktop. See https://developers.google.com/web/fundamentals/web-app-manifest/
    -->
    <link rel="manifest" href="./grapl_logo.png" />
    <!--
      Notice the use of %PUBLIC_URL% in the tags above.
      It will be replaced with the URL of the `public` folder during the build.
      Only files inside the `public` folder can be referenced from the HTML.
      Unlike "/favicon.ico" or "favicon.ico", "%PUBLIC_URL%/favicon.ico" will
      work correctly both with client-side routing and a non-root public URL.
      Learn how to configure a non-root public URL by running `npm run build`.
    -->
    <link rel="icon" href ="./grapl_logo.png">
    <title>Grapl</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
    <!--
      This HTML file is a template.
      If you open it directly in the browser, you will see an empty page.
      You can add webfonts, meta tags, or analytics to this file.
      The build step will place the bundled scripts into the <body> tag.
      To begin the development, run `npm start` or `yarn start`.
      To create a production bundle, use `npm run build` or `yarn build`.
    -->
  </body>
</html>
'''
