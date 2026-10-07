# Public deployment

## Recommended target: Render free web service

The project includes `Dockerfile` and `render.yaml`. It binds to Render's `PORT`, serves over the platform HTTPS
endpoint, runs as an unprivileged container user, and defaults to `PULSE_DEMO_MODE=fixture`.

Fixture mode is recommended for the public judging URL: it is deterministic, needs no secret, and cannot sign or
broadcast. The authenticated live proof should be shown from the sanitized local audit in the video.

## Owner-controlled deployment steps

1. Publish this directory as a new public GitHub repository named `pulse-market-hours-agent`.
2. In Render, choose **New > Blueprint**, connect that repository, and select `render.yaml`.
3. Confirm the free plan and deploy. Do not add Binance credentials for the fixture demo.
4. Open `/api/health`; verify `mode` is `fixture` and `secrets_exposed` is `false`.
5. Test all four cases, receipt download, and replay; keep the URL available through judging.

If live mode is later required, add credentials only as Render secret environment variables. Never place them in
GitHub, Docker build arguments, frontend code, screenshots, or video output.
