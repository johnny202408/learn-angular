# Chapter 13. Routing: pages, params, guards, lazy loading

Compass has been a single screen. Real applications have several — a home, a settings, a detail view, sometimes dozens. Angular's *router* is the piece that turns one URL into one component tree, updates it as the user navigates, and lets pieces of the app react to which URL is active.

This chapter turns Compass into a multi-page app. We will add a home route that shows today's tasks, a stats route that will host our charts in Chapter 16, and a detail route that shows a single task with the edit form we built in Chapter 12. Along the way we cover route parameters, guards, resolvers, and lazy loading.

## The three moving parts

Angular routing has three concepts you meet everywhere.

**Route definitions** — a list of `{ path, component }` records that tell the router what to render for each URL. You have seen the empty version in `src/app/app.routes.ts`.

**`<router-outlet>`** — a placeholder in a template that says "render the currently-active route's component here." You already had one, briefly, in the CLI-generated `App`; we removed it in Chapter 5.

**Navigation** — the user (or your code) changes the URL, and the router matches it against the route definitions, resolves any guards, and updates whichever `<router-outlet>` is showing the affected component.

## Defining Compass's routes

Edit `src/app/app.routes.ts`:

```ts
import { Routes } from '@angular/router';
import { Home } from './home/home';
import { Stats } from './stats/stats';
import { TaskDetail } from './task-detail/task-detail';

export const routes: Routes = [
  { path: '', component: Home, title: 'Today · Compass' },
  { path: 'stats', component: Stats, title: 'Stats · Compass' },
  { path: 'task/:id', component: TaskDetail, title: 'Task · Compass' },
  { path: '**', redirectTo: '' },
];
```

Four routes:

- `''` is the empty path — the home route, matching `http://localhost:4200/`.
- `'stats'` matches `/stats`.
- `'task/:id'` matches `/task/anything`, capturing the segment after `task/` as `id`.
- `'**'` is the wildcard — anything unmatched redirects to home. Always define this last; the router walks the list top-to-bottom, and a `**` earlier would swallow everything.

The `title` property sets `document.title` when the route activates. It is a small feature that improves how tabs and bookmarks look in a browser.

We need `Home`, `Stats`, and `TaskDetail` components. Create them:

```bash
ng generate component home
ng generate component stats
ng generate component task-detail
```

For now, `Home` is where `TaskList` lives. Move the `<app-task-list>` markup and any orchestration from `App` into `Home`.

`src/app/home/home.ts`:

```ts
import { Component } from '@angular/core';
import { TaskList } from '../task-list/task-list';

@Component({
  selector: 'app-home',
  imports: [TaskList],
  template: `<app-task-list />`,
})
export class Home {}
```

`Stats` is a stub we will flesh out in Chapter 16:

```ts
@Component({
  selector: 'app-stats',
  template: `<h1>Stats</h1><p>Coming soon.</p>`,
})
export class Stats {}
```

`TaskDetail` we look at in a moment.

## `App` becomes a shell

The root component's job is now to hold the `<router-outlet>` and any chrome that surrounds every page — a header, a footer, a sidebar. Rewrite `src/app/app.ts`:

```ts
import { Component } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {}
```

`src/app/app.html`:

```html
<header class="app-header">
  <h1 class="brand">Compass</h1>
  <nav>
    <a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: true }">
      Today
    </a>
    <a routerLink="/stats" routerLinkActive="active">Stats</a>
  </nav>
</header>

<main class="app-main">
  <router-outlet />
</main>
```

`routerLink` renders an `<a>` with the correct `href` and, when clicked, tells the router to navigate — no full page reload. `routerLinkActive` adds a class when the link's route is active. `{ exact: true }` prevents `/` from being "active" every time — otherwise it would be highlighted for `/stats` too, because `/stats` starts with `/`.

Save. Refresh. You should see the header with two nav links. Clicking "Today" and "Stats" switches which view appears below. Notice the URL changes, and the browser back button works.

## Route parameters and `:id`

The `task/:id` route captures a segment. In `TaskDetail`, we need to read that segment.

Modern Angular has an especially nice way: **component input binding** from the router. Turn it on in `app.config.ts`:

```ts
import { provideRouter, withComponentInputBinding } from '@angular/router';

// ...providers:
provideRouter(routes, withComponentInputBinding()),
```

Now any `input()` in a routed component receives matching route parameters as its input:

```ts
import { Component, inject, input, computed } from '@angular/core';
import { TaskStore } from '../task-store';
import { EditTask } from '../edit-task/edit-task';

@Component({
  selector: 'app-task-detail',
  imports: [EditTask],
  templateUrl: './task-detail.html',
})
export class TaskDetail {
  id = input.required<string>();
  private store = inject(TaskStore);
  task = computed(() => this.store.tasks().find(t => t.id === this.id()));
}
```

And the template:

```html
@if (task(); as t) {
  <app-edit-task [task]="t" />
} @else {
  <p>Task not found. <a routerLink="/">Back to today.</a></p>
}
```

`@if (task(); as t)` is a template alias — it binds the truthy value to `t` inside the block. Now `t` is the resolved `Task`, and `EditTask` gets a real task to work with. The `computed` ensures that if the store updates, the detail view updates too.

Reading route params via `input()` is only available with `withComponentInputBinding()`. Without it, you would read them via `ActivatedRoute`:

```ts
private route = inject(ActivatedRoute);
id = toSignal(this.route.paramMap.pipe(map(p => p.get('id') ?? '')), { initialValue: '' });
```

Both work; input binding is cleaner and gets you free type inference on generated links.

## Linking to a task

In `TaskRow`, add a link:

```html
<a [routerLink]="['/task', task().id]" class="detail-link">Details</a>
```

The array form of `routerLink` builds the URL from segments. It handles URL encoding for you. Prefer it over `'/task/' + task().id`.

Notice that `TaskRow` now needs to import `RouterLink` in its `imports` array.

## Query parameters

For state that should be reflected in the URL but is not part of the route match — filters, sorts, search queries — use *query parameters*.

Read them the same way you read route params, using `queryParamMap` on `ActivatedRoute`:

```ts
private route = inject(ActivatedRoute);
filter = toSignal(
  this.route.queryParamMap.pipe(map(p => p.get('tag') ?? 'all')),
  { initialValue: 'all' }
);
```

Write them via the `Router`:

```ts
private router = inject(Router);

setFilter(tag: string): void {
  this.router.navigate([], {
    relativeTo: this.route,
    queryParams: { tag: tag === 'all' ? null : tag },
    queryParamsHandling: 'merge',
  });
}
```

`queryParamsHandling: 'merge'` preserves other query params. Setting a value to `null` removes it.

Query params in the URL have two benefits: users can bookmark and share, and the browser's back button becomes meaningful (each filter change is a history entry, if you want it to be).

## Guards: gating navigation

A guard is a function that decides whether a navigation is allowed. Three main types:

**`canActivate`** — can this user visit this route? Used for authentication.

**`canMatch`** — should this route even be considered for matching? Used to hide routes entirely from users who shouldn't reach them. Better than `canActivate` for auth because the route's code isn't downloaded if `canMatch` returns false.

**`canDeactivate`** — can the user leave this route? Used to warn about unsaved changes.

Here is a `canMatch` for an authenticated area:

```ts
// src/app/auth.guard.ts
import { CanMatchFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { AuthStore } from './auth-store';

export const requireAuth: CanMatchFn = () => {
  const auth = inject(AuthStore);
  const router = inject(Router);
  if (auth.isSignedIn()) return true;
  router.navigateByUrl('/login');
  return false;
};
```

Attach it in `app.routes.ts` — note that the "code isn't downloaded when `canMatch` returns false" benefit only holds for **lazy-loaded routes**, so pair it with `loadComponent`:

```ts
{
  path: 'stats',
  loadComponent: () => import('./stats/stats').then(m => m.Stats),
  canMatch: [requireAuth],
  title: 'Stats · Compass',
},
```

We won't add auth to Compass until Chapter 19 (deployment considers it), but you now know where auth guards go.

## Resolvers: pre-fetching data

Some routes should not render until their data is loaded. A *resolver* is a function that runs before the route activates and blocks the navigation until it completes.

```ts
import { ResolveFn } from '@angular/router';
import { inject } from '@angular/core';
import { TaskStore } from './task-store';
import { Task } from './task';

export const taskResolver: ResolveFn<Task | undefined> = (route) => {
  const store = inject(TaskStore);
  const id = route.paramMap.get('id') ?? '';
  return store.tasks().find(t => t.id === id);
};
```

Attach it:

```ts
{ path: 'task/:id', component: TaskDetail, resolve: { task: taskResolver } },
```

And read the resolved data in the component via `ActivatedRoute.data`:

```ts
task = toSignal(this.route.data.pipe(map(d => d['task'] as Task | undefined)), { initialValue: undefined });
```

Resolvers keep loading spinners out of your component code — but they also delay the first paint. Use them for data you cannot render meaningfully without; otherwise render the shell and let a loading state fill in.

Compass's `TaskDetail` uses the store's signal, not a resolver — the parent store has already loaded tasks, and we can find the task synchronously. Resolvers are more useful when the detail page's data is not already in a store.

## Lazy loading

Every component in `imports` in your route file is included in the initial bundle. On a big app, this bloats the download.

Lazy loading defers a component's load until it is needed:

```ts
{
  path: 'stats',
  loadComponent: () => import('./stats/stats').then(m => m.Stats),
}
```

The router calls the arrow function only when the user navigates to `/stats`, downloads the resulting JavaScript chunk, and renders. There is a fraction-of-a-second delay the first time, which is usually acceptable.

For entire feature areas, `loadChildren` lazily loads a *set* of routes:

```ts
{
  path: 'settings',
  loadChildren: () => import('./settings/settings.routes').then(m => m.settingsRoutes),
}
```

The child file exports its own `Routes` array. Everything under `/settings/*` is downloaded together.

We will convert Compass's `Stats` and `TaskDetail` routes to lazy loading in Chapter 16, once we have measurement to justify it.

## Preloading

Lazy chunks download on demand, which introduces latency on first visit. Preloading downloads them in the background *after* the initial render:

```ts
import { withPreloading, PreloadAllModules } from '@angular/router';

provideRouter(routes, withPreloading(PreloadAllModules)),
```

`PreloadAllModules` is the simple option: download everything lazy after the app has painted. A custom preloader can be smarter (only preload chunks likely to be visited next). For most apps, `PreloadAllModules` is a good default.

## Programmatic navigation

You navigate imperatively with the `Router`:

```ts
private router = inject(Router);

goHome(): void { this.router.navigate(['/']); }
openTask(id: string): void { this.router.navigate(['/task', id]); }
back(): void { window.history.back(); }
```

`navigate` returns a Promise that resolves when navigation completes (or false if it was blocked). `navigateByUrl(url)` takes a string URL.

For most in-template navigation, prefer `[routerLink]` — it renders a real anchor, which is better for accessibility and for open-in-new-tab. Reach for `router.navigate` when navigating from a handler that already ran (after a form save, on a socket event, on a timer).

## `RouterLinkActive` for nav highlighting

`routerLinkActive` adds a CSS class when the link's target is the active route. It can take a list of classes:

```html
<a routerLink="/stats" routerLinkActive="active highlighted">Stats</a>
```

By default, a link is active when the URL *starts with* its target. `{ exact: true }` requires exact match. Use `exact` on the home link (`/`), which otherwise matches every URL.

## `titleStrategy`: dynamic titles

Static `title: '...'` in a route works for pages whose title is known ahead of time. For "Task: X" where X depends on the task, define a `TitleStrategy`:

```ts
import { TitleStrategy, RouterStateSnapshot } from '@angular/router';
import { Title } from '@angular/platform-browser';

@Injectable({ providedIn: 'root' })
export class CompassTitleStrategy extends TitleStrategy {
  private title = inject(Title);
  override updateTitle(state: RouterStateSnapshot): void {
    const t = this.buildTitle(state);
    this.title.setTitle(t ? `${t} · Compass` : 'Compass');
  }
}

// providers:
{ provide: TitleStrategy, useClass: CompassTitleStrategy },
```

Compass's static titles are enough for now; know that the extension point exists.

## What comes next

Chapter 14 promotes `TaskStore` into a general pattern for signal-based state and shows when reaching for a bigger state library (NgRx) is worth it. Chapter 15 covers directives and pipes — the primitives for reusable behavior and formatting that we haven't touched yet. Chapter 16 measures Compass's performance and fixes what needs fixing.

### Exercises

1. Convert the "Stats" and "Task detail" routes to lazy loading. Then run `ng build` and look inside `dist/`. You should see multiple chunk files, one per lazy route.

2. Add a "canDeactivate" guard on the task detail route that prompts the user "You have unsaved changes; leave anyway?" when they try to navigate away from an edit with a dirty form. Hint: the guard function receives the component instance as its first argument.

3. Add a query parameter `filter` to the home route, valid values `all`, `open`, and `done`. Render only the matching tasks. Provide three buttons that update the query param via `router.navigate`, and highlight the active one using `routerLinkActive` on `routerLink` versions of the buttons.
