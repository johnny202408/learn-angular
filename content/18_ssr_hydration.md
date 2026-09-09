# Chapter 18. Server-side rendering and hydration

Compass, as it stands, is a *client-rendered* application. When a user first visits, the browser downloads a nearly-empty HTML shell, downloads a bundle of JavaScript, and only then does Angular boot up and render the page. Users on fast networks see this as a brief flash of nothing before the app appears. Users on slow networks see it as a long blank screen. Search-engine crawlers may see it as an empty page and index nothing.

Server-side rendering (SSR) fixes both. The server runs your Angular app, produces the fully-rendered HTML for the requested URL, and sends that back to the browser. The user sees content immediately. Angular then boots up on the client and *hydrates* the page — attaching event handlers to the existing DOM rather than re-rendering it from scratch.

This chapter turns Compass into an SSR app. It is one of the shortest chapters in the book because Angular has done most of the work. `ng add @angular/ssr` gets you 80% of the way.

## SSR, client rendering, and static generation

Three modes, and the naming varies across ecosystems:

- **Client-side rendering (CSR)**: server sends a shell; the browser downloads JS and renders. Simple; slow first paint.
- **Server-side rendering (SSR)**: server renders each request. First paint is fast; the server does work per request.
- **Static site generation (SSG) / prerendering**: server renders every route once, at build time, and serves the static HTML. First paint is fast and the server does zero per-request work — but every URL must be known at build time.

Angular supports all three. You choose per route: some are prerendered (the marketing pages), some are SSR (personalized pages that need session data), some are CSR (heavy interactive tools that don't benefit from server rendering).

For Compass, the sensible mix is:

- Home page: CSR (personalized, no SEO need).
- Marketing / landing page (if we had one): SSG.
- Task detail: SSR when the URL is shared publicly; otherwise CSR is fine.

We will enable SSR globally in this chapter and let per-route configuration follow.

## Adding SSR to Compass

Run:

```bash
ng add @angular/ssr
```

The schematic does several things:

1. Adds `@angular/ssr` and Express as dependencies.
2. Creates `server.ts` at the project root — an Express server that renders Angular for each request.
3. Adds a `server` build target to `angular.json` and a `serve-ssr` script.
4. Modifies `main.ts` to accept both browser and server bootstraps.
5. Adds `app.config.server.ts` for server-only providers.
6. Enables hydration via `provideClientHydration()` in `app.config.ts`.

After it finishes:

```bash
npm run start:ssr        # dev server with SSR
npm run build            # builds both browser and server bundles
npm run serve:ssr:compass  # runs the built server
```

Open `http://localhost:4000` (the default SSR port). View the source of the page (right-click → View Source). You will see the fully-rendered task list in the HTML — not just an empty `<app-root>`. Refresh and inspect the network tab; the first response arrives already populated.

## Hydration: matching the client to the server

Once Angular boots on the client, it needs to *hydrate* the existing DOM instead of throwing it away and re-rendering. `provideClientHydration()` (added by the schematic) handles this. It matches the server-rendered nodes with the client-rendered component tree, attaches event listeners, and preserves any DOM state (like an input's value) that was already there.

Rules of the road:

- **Server and client must produce the same HTML.** Random content (`Math.random()`, `new Date()`) will differ, and hydration will warn about the mismatch. Wrap non-deterministic content in `@if (isBrowser())` (see below) so it renders only on the client.
- **DOM manipulation before hydration completes is dangerous.** Don't reach into `document` from a component constructor unless you know what you are doing.
- **Third-party libraries that manipulate the DOM directly (jQuery plugins, some chart libraries) don't work well with hydration.** Load them inside `afterNextRender`, or defer them entirely.

## Detecting the platform

Some code should only run in the browser. Angular gives you `isPlatformBrowser`:

```ts
import { inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

@Injectable({ providedIn: 'root' })
export class SomeService {
  private isBrowser = isPlatformBrowser(inject(PLATFORM_ID));

  loadPreference(): string {
    if (this.isBrowser) {
      return localStorage.getItem('pref') ?? 'default';
    }
    return 'default';
  }
}
```

On the server, `PLATFORM_ID` is `'server'`; on the client, `'browser'`. This lets you avoid calling browser APIs on the server, which would throw because `window`, `document`, and `localStorage` don't exist there.

For components: `afterNextRender` fires only on the client. Use it to run browser-specific initialization:

```ts
constructor() {
  afterNextRender(() => {
    // Runs on the client, once, after the first render.
    window.scrollTo(0, 0);
  });
}
```

## Transfer state: don't re-fetch what the server already had

When the server renders Compass's home page, it fetches tasks from the API. When the client then hydrates, it would re-fetch — the same data — from the same API, wasting a round trip.

Angular has *transfer state* to solve this. Wrap HTTP with `withHttpTransferCacheOptions` in `app.config.ts`:

```ts
import { provideHttpClient, withFetch, withInterceptors, withHttpTransferCacheOptions } from '@angular/common/http';

providers: [
  provideHttpClient(
    withFetch(),
    withInterceptors([authInterceptor]),
    withHttpTransferCacheOptions({
      includeHeaders: [],
      includePostRequests: false,
    }),
  ),
],
```

Angular serializes every HTTP GET's response into the initial HTML (inside a `<script>` tag). On the client, `HttpClient` checks that cache before hitting the network — a matching request returns the cached response immediately.

You can also transfer arbitrary state via `TransferState`:

```ts
import { makeStateKey, TransferState } from '@angular/core';

const TASKS_KEY = makeStateKey<Task[]>('tasks');

// On the server:
const transferState = inject(TransferState);
transferState.set(TASKS_KEY, tasks);

// On the client:
const initial = transferState.get(TASKS_KEY, []);
```

Compass will pick up transfer state automatically for its `HttpClient` calls, without extra plumbing.

## Prerendering specific routes

For routes whose content doesn't depend on the user, prerender at build time. Add them to `app.routes.server.ts` (created by the SSR schematic):

```ts
import { RenderMode, ServerRoute } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  { path: '', renderMode: RenderMode.Prerender },
  { path: 'stats', renderMode: RenderMode.Server },
  { path: 'task/:id', renderMode: RenderMode.Server },
];
```

`Prerender` runs at build time; `Server` runs per request; `Client` disables SSR for that route.

For dynamic segments like `task/:id`, provide a `getPrerenderParams` function that returns the ids to prerender at build time:

```ts
{
  path: 'task/:id',
  renderMode: RenderMode.Prerender,
  getPrerenderParams: async () => {
    const tasks = await fetchAllPublicTasks();
    return tasks.map(t => ({ id: t.id }));
  },
}
```

Compass's task detail is user-specific, so prerendering doesn't help; `RenderMode.Server` (SSR per request) is the right choice if we want the page shareable, or `RenderMode.Client` (client-only) if not.

## Testing SSR locally

`npm run build && npm run serve:ssr:compass` runs the production build against a local Node server. Open it, view source, confirm content is present.

For debugging server-only code, `console.log` in a component or service will appear in the terminal (server), not the browser (client). If you see nothing, remember the split.

## SEO metadata

Server-rendered pages let search engines see your content — but they also need metadata. Angular's `Title` and `Meta` services set the `<title>` and `<meta>` tags:

```ts
import { Title, Meta } from '@angular/platform-browser';

constructor() {
  const title = inject(Title);
  const meta = inject(Meta);
  title.setTitle('Compass — plan your day');
  meta.updateTag({ name: 'description', content: 'A calm daily planner.' });
  meta.updateTag({ property: 'og:image', content: 'https://compass.example/og.png' });
}
```

For per-page metadata, drive these from route data or resolvers. The `TitleStrategy` we introduced in Chapter 13 is the systematic way.

## When SSR is worth it

Not every Angular app benefits from SSR.

**SSR pays off when:**

- Your users often visit on slow networks.
- Search engines need to index the content.
- Social sharing (Open Graph, Twitter cards) is important.
- Your app has significant JS beyond what's on the visible portion of first paint.

**SSR is not worth it when:**

- The app is behind auth and never indexed.
- The heavy content is user-generated after first load (chat, editor, dashboard).
- Every page requires personalization that the server can't cheaply compute.
- You would need to duplicate significant server-side logic.

Compass benefits mildly from SSR — the app is small, and users typically bookmark it and load it from cache after the first visit. If you were building a public marketing site, SSR would be closer to essential.

## What comes next

Chapter 19 deploys Compass to the internet. Static hosting for a client-rendered Compass, Node hosting for the SSR variant, and CI to make deployment safe. Chapter 20 hands you the map for what to learn next.

### Exercises

1. Enable SSR on Compass, build it, and serve it. View source on the home page. Compare the size of the initial HTML response now versus before SSR (network tab, "Doc" filter, look at "Size"). Was there a meaningful change?

2. Add `provideClientHydration()` if it isn't there; then break hydration on purpose by adding `<span>{{ Math.random() }}</span>` to a component template. Open the console; you should see a hydration mismatch warning. Fix it by moving the random call behind an `afterNextRender`.

3. Add title and description meta tags to the task detail route, so a task's URL, when shared to Slack or a messaging app, unfurls with a useful preview. Test with the Facebook Sharing Debugger or the Twitter Card Validator on your deployed URL (Chapter 19 gets you deployed).
