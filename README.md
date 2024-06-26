# ASGI Middleware for Umami Analytics

This project provides a middleware for your
[ASGI-compatible](https://asgi.readthedocs.io/en/latest/introduction.html) app
(e.g. FastAPI, Starlette) that automatically sends access events to your
[umami](https://umami.is/) instance. If you want to track your API clients
in a GDPR-friendly way, then this middleware is for you.

## Usage

For this middleware, you need (at least) the following information:

- The URL of your Umami API (e.g. `https://umami.example.com/api`
- The website GUID (e.g. `12345678-1234-1234-1234-123456789012`)

Install the package via pip:

```bash
pip install umami-asgi
```

Then, you can add the umami middleware to your ASGI app. Here is an example for
FastAPI:

```python
from fastapi import FastAPI
from umami_asgi import UmamiMiddleware

app = FastAPI()
app.add_middleware(
    UmamiMiddleware,
    api_url="https://umami.example.com/api",
    website_id="12345678-1234-1234-1234-123456789012"
)
```

For more extensive examples, see the `examples` directory.

## Try it out

In the `examples` directory, you can find examples for FastAPI and Starlette
that you can try out easily. First, create a `.env` file in the `examples`
directory with the following content:

```text
UMAMI_API_ENDPOINT="https://example.com/api"
UMAMI_SITE_ID="your-site-id"
```

Then, install the necessary dependencies and run the example:

```bash
pip install uvicorn python-dotenv fastapi starlette 

# FastAPI:
python -m uvicorn examples.fastapi_app:app --env-file examples/.env

# Starlette:
python -m uvicorn examples.starlette_app:app --env-file examples/.env
```

## Configuring the Middleware

The middleware has the following configuration options:

| Parameter          | Type                  | Description                                                                                                                                                                |
|--------------------|-----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `api_url`          | `str`                 | The URL of your Umami API endpoint (e.g. `https://umami.example.com/api`)                                                                                                  |
| `website_id`       | `str`                 | The GUID of your website in Umami  (e.g. `12345678-1234-1234-1234-123456789012`                                                                                            |
| `follow_redirects` | `Optional[bool]`      | Determines whether the POST request to the Umami API should follow redirects or not. Default is true.                                                                      |
| `proxy_enabled`    | `Optional[bool]`      | If true, the middleware trusts the headers `X-Forwarded-For`, `X-Forwarded-Host`, and `X-Real-IP`. Default is false.                                                       |
| `trusted_proxies`  | `Optional[List[str]]` | Hosts from which the headers mentioned above are trusted. Only used when `proxy_enabled` is set to true. If `0.0.0.0` is included, all hosts are trusted. Default is None. |

## Known issues

- Country tracking does not seem to work properly. If you need this feature,
  open an issue and I'll take a deeper look into it.
- Per-endpoint exclusion of tracking is not supported yet.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file
for details.
