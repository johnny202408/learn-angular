# Chapter 19. Deployment

Compass is finished. It runs on your laptop against `json-server`. To have any value, it needs to live somewhere on the internet where you (and, if you want, others) can reach it. This chapter walks through the choices — static hosting, Node hosting, containers — and takes Compass live on one of them.

## The two shapes of an Angular app in production

Whatever hosting you pick, an Angular app in production is one of two shapes.

**Static bundle.** `ng build` produces `dist/compass/browser/` — a folder of HTML, JS, and CSS. Serving that folder from any static file server is enough. This is the shape of a client-rendered Compass or a prerendered SSG build.

**Node server.** With SSR enabled, `ng build` also produces `dist/compass/server/` — a Node.js server. Running `node dist/compass/server/server.mjs` starts an Express server that renders each request and serves the built assets. This shape needs Node hosting.

The rest of the chapter is: which hosting for which shape.

## What Compass needs from its backend

Before hosting the frontend, remember: Compass talks to a backend. `json-server` is a development toy; it is not something to run in production. For a real deployment, replace it with:

- A real REST or GraphQL API you own.
- A backend-as-a-service (Firebase, Supabase, PocketBase).
- A serverless API (Cloudflare Workers, Vercel Functions, AWS Lambda + API Gateway).

The Angular side of Compass doesn't care which. As long as the endpoints in `TasksApi` return the same shape, everything works.

For this chapter we assume you have chosen one and it exposes an API at `https://api.compass.example`. Update the `BASE_URL` constant in `tasks-api.ts`, or (better) turn it into a build-time environment variable — see the *Environment configuration* section below.

## Hosting a static Angular build

If Compass is client-rendered (no SSR), any static host works. The mechanics differ; the principle is the same: upload `dist/compass/browser/` and configure the host to fall back to `index.html` for unmatched routes.

The last point matters. Angular's client-side router expects the browser to load `index.html` for any URL and let Angular figure out the route. If the host returns 404 for `/stats`, users cannot deep-link. Every static host has a way to configure this fallback; it is often called "SPA mode" or "rewrite to index."

Three good static hosts:

**Netlify.** Drag-and-drop the folder onto app.netlify.com, or push to GitHub and connect the repo. Netlify auto-detects Angular, runs `ng build`, and serves `dist/compass/browser/`. Configure fallback in `netlify.toml`:

```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

**Vercel.** Similar workflow. `vercel.json`:

```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

**Cloudflare Pages.** Connect a Git repo; Cloudflare builds and serves globally on their edge network. Fallback via `_redirects`:

```
/*    /index.html   200
```

All three have free tiers generous enough for personal projects, custom domains, HTTPS, and CI-triggered deployments. The picks are close in features; pick one and try it.

## Hosting SSR Compass

An SSR Compass ships a Node server. That excludes pure static hosts and requires one of:

**Vercel, with the Node runtime.** Angular's SSR output works out of the box on Vercel; deploy the whole repo, and Vercel will build the SSR bundle and run the server on demand.

**Firebase Hosting + Cloud Functions.** Angular has first-party integration; `ng deploy` from `@angular/fire` uploads the browser assets to Firebase Hosting and the server bundle as a Cloud Function.

**A container on any cloud.** Build a small Docker image, deploy it to Fly.io, Railway, Render, DigitalOcean's App Platform, AWS ECS, Google Cloud Run, or any equivalent. This is the most flexible; it is also the most work.

Here is a minimal Dockerfile that works for Angular SSR:

```Dockerfile
FROM node:20-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-slim AS runtime
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
COPY package*.json ./
EXPOSE 4000
CMD ["node", "dist/compass/server/server.mjs"]
```

Build and run locally:

```bash
docker build -t compass .
docker run -p 4000:4000 compass
```

Push the image to a registry and deploy on the host of choice.

## Environment configuration

Compass's `BASE_URL` should not be hardcoded. Angular projects handle this with environment files.

Create `src/environments/environment.ts`:

```ts
export const environment = {
  production: false,
  apiBaseUrl: 'http://localhost:3000',
};
```

And `src/environments/environment.prod.ts`:

```ts
export const environment = {
  production: true,
  apiBaseUrl: 'https://api.compass.example',
};
```

Configure `angular.json` to substitute the file at build time. In the `configurations.production.fileReplacements` array (which is usually already there):

```json
"fileReplacements": [
  {
    "replace": "src/environments/environment.ts",
    "with": "src/environments/environment.prod.ts"
  }
]
```

Import and use:

```ts
import { environment } from '../environments/environment';
// ...
const BASE_URL = environment.apiBaseUrl;
```

`ng build --configuration production` swaps in the prod values. `ng serve` uses the dev values.

For secrets — API keys, tokens — do not check them into environment files. Anything Angular ships to the browser is public. Put secrets on the backend, expose only the frontend-safe values.

## HTTPS, CORS, and cookies

Once Compass is on a domain and its backend is on another, three configurations become load-bearing.

**HTTPS everywhere.** Every good host provides it automatically. Do not deploy over HTTP; browsers block or degrade too many APIs (service workers, geolocation, cookies) over HTTP.

**CORS.** The backend must send `Access-Control-Allow-Origin: https://compass.example` (or the specific origins that are allowed). If Compass makes requests with cookies, `Access-Control-Allow-Credentials: true` and the origin must not be `*`.

**Cookies.** If auth uses cookies, they must be `Secure` (HTTPS-only), `HttpOnly` (JS-inaccessible), and `SameSite=Lax` or `Strict`. Cross-site cookies (`SameSite=None`) require a good reason and additional care.

Each of these has bitten teams once and taught them a lesson permanently. Configure them right the first time.

## Continuous deployment

Set up CI so pushes to `main` deploy Compass. Every host has a template.

GitHub Actions to Netlify:

```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run test -- --watch=false --browsers=ChromeHeadlessNoSandbox
      - run: npx playwright test
      - run: npm run build
      - uses: nwtgck/actions-netlify@v3
        with:
          publish-dir: 'dist/compass/browser'
          production-deploy: true
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

Push a commit; a few minutes later, production is updated.

## Preview environments

Ideally, every pull request gets its own preview URL. Netlify, Vercel, and Cloudflare Pages do this automatically for connected Git repos. Reviewers open the preview link, click around, and comment on real behavior rather than trying to imagine it from a diff.

If your host doesn't do this natively, GitHub Actions can build and push to a per-branch S3 bucket or Firebase channel. The setup is one afternoon and pays off forever.

## Custom domains

Every host we mentioned supports custom domains. The mechanics:

1. Buy a domain from a registrar (Namecheap, Cloudflare Registrar, etc.).
2. In the host, add the domain.
3. In the registrar, add the DNS records the host provides (usually a CNAME or two A records).
4. Wait a few minutes for DNS to propagate.
5. HTTPS certificate is provisioned automatically via Let's Encrypt.

Point `compass.yourname.dev` at Netlify; five minutes later, `https://compass.yourname.dev` serves Compass.

## Analytics and error reporting

Once Compass is public, you want to know when it breaks.

**Error reporting**: Sentry, Rollbar, Bugsnag, LogRocket. Each has an Angular SDK; you initialize it in `main.ts` and configure global error handling by providing `ErrorHandler`:

```ts
providers: [
  { provide: ErrorHandler, useClass: SentryErrorHandler },
],
```

**Analytics**: Plausible, Fathom, or Google Analytics. Load a script tag, or use their SDK. The Angular Router has a `Router.events` Observable that emits on every navigation; subscribe and record the URL if you want single-page tracking.

Both are optional; both are usually worth setting up before you tell anyone about your app.

## Performance monitoring

Real-user monitoring (RUM) tracks how the app performs for actual users, on their actual devices. Web Vitals — LCP, FID, CLS — are standardized metrics you can measure with `web-vitals` (the library):

```ts
import { onCLS, onFID, onLCP } from 'web-vitals';

onCLS(metric => sendToAnalytics(metric));
onFID(metric => sendToAnalytics(metric));
onLCP(metric => sendToAnalytics(metric));
```

Each host provides its own RUM if you prefer not to roll your own.

## Rolling back and staging

Every deployment can go wrong. Two safety nets you want early:

**One-click rollback.** All the hosts we listed let you rewind to a previous deploy. Practice using it before you need it.

**A staging environment.** A separate deployment (compass-staging.example) that mirrors production but with a test backend. Deploy to staging first, verify, promote to production. This is the difference between a Friday-evening deploy and a Friday-evening incident.

## Post-deploy: keeping Angular current

Angular ships a major version every six months. `ng update` handles most migrations:

```bash
ng update @angular/cli @angular/core
```

It runs migration schematics that adjust your code automatically for renamed APIs. Sometimes manual work is needed; the update output tells you what.

Stay one or two versions behind current if you value stability; stay on current if you want new features. Do not fall more than three versions behind — the upgrade path becomes painful.

## What comes next

Chapter 20 is the last chapter. It maps the Angular ecosystem beyond what Compass needed — Material, Nx, NgRx, Universal, Router extensions — and points you at what to read, watch, and try next.

### Exercises

1. Deploy Compass (client-rendered version) to Netlify, Vercel, or Cloudflare Pages. Include the SPA fallback so `/stats` doesn't 404. Share the URL with a friend and confirm it loads over their phone data.

2. Enable SSR (per Chapter 18), build the SSR bundle, and deploy to a host that supports Node (Vercel, Fly.io, or Cloud Run). Verify with `curl -sS https://your-url/task/t1 | grep -c task-detail` that the response contains rendered HTML.

3. Set up GitHub Actions to run tests, build, and deploy on every push to `main`. Break one test intentionally; verify that the deploy is skipped. Fix the test; watch it succeed.
