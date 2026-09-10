# Chapter 10. HTTP: talking to real APIs

Compass has been running entirely in the browser's memory. That is enough to demo the app, and not nearly enough for real use. In this chapter we introduce Angular's `HttpClient` service, connect Compass to a small backend, and make it possible to add a task on one device and see it on another. By the end, the tasks you create will survive a browser refresh — because they live on a server, not in `TaskStore`'s in-memory signal.

The chapter has two halves. The first half spins up a minimal backend so we have something to talk to. The second half wires `HttpClient` into `TaskStore` and covers interceptors, error handling, and the modern `httpResource`.

## A tiny backend for Compass

We need a server. To keep this book self-contained, we will use `json-server` — a zero-config REST server that reads a JSON file. It exposes GET/POST/PUT/PATCH/DELETE endpoints automatically. In production Compass would talk to a real backend (Node, Python, Go, whatever); the Angular side of the code is identical.

Install it globally:

```bash
npm install --global json-server
```

Create a file `compass/db.json` (at the top level of your Angular project, next to `package.json`):

```json
{
  "tasks": [
    { "id": "t1", "title": "Buy milk", "done": false, "createdAt": "2026-01-15T09:00:00Z", "dueDate": null, "tags": ["home"] },
    { "id": "t2", "title": "Write chapter 10", "done": true, "createdAt": "2026-01-14T18:30:00Z", "dueDate": "2026-01-16T00:00:00Z", "tags": ["work"] }
  ]
}
```

Run it in a second terminal:

```bash
json-server --watch db.json --port 3000
```

Now `http://localhost:3000/tasks` returns the array of tasks. Curl it, or open the URL in a browser, to confirm.

`json-server` is a fake server, and its persistence is trivial — it writes changes back to `db.json` — but its API matches every JSON REST server you will ever call. That is the point.

### Configuring CORS is not our problem

Because we're running Compass on `http://localhost:4200` and the API on `http://localhost:3000`, browsers would normally block the requests as cross-origin. `json-server` allows them by default; a real production API would send `Access-Control-Allow-Origin` headers. In your own future backends, remember this: the browser is strict about cross-origin requests, and CORS misconfiguration is the reason things "just don't work" ninety percent of the time when hooking a new frontend to a new backend.

## Enabling HttpClient in Angular

`HttpClient` is Angular's built-in HTTP service. It arrives via DI, and it needs to be provided at the app level. Edit `src/app/app.config.ts`:

```ts
import { ApplicationConfig, provideBrowserGlobalErrorListeners, provideZonelessChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withFetch } from '@angular/common/http';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideZonelessChangeDetection(),
    provideRouter(routes),
    provideHttpClient(withFetch()),
  ],
};
```

`provideHttpClient()` registers the service. `withFetch()` tells Angular to use the browser's native `fetch` API under the hood; the default older XHR-based implementation still works, but `fetch` is the direction of travel and integrates better with SSR (Chapter 18).

## The API contract

Define a small module that describes the URLs and does the raw HTTP. Create `src/app/tasks-api.ts`:

```ts
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { Task } from './task';

const BASE_URL = 'http://localhost:3000';

@Injectable({ providedIn: 'root' })
export class TasksApi {
  private http = inject(HttpClient);

  list(): Promise<Task[]> {
    return firstValueFrom(this.http.get<Task[]>(`${BASE_URL}/tasks`));
  }

  create(task: Omit<Task, 'id'>): Promise<Task> {
    return firstValueFrom(this.http.post<Task>(`${BASE_URL}/tasks`, task));
  }

  update(id: string, changes: Partial<Task>): Promise<Task> {
    return firstValueFrom(this.http.patch<Task>(`${BASE_URL}/tasks/${id}`, changes));
  }

  remove(id: string): Promise<void> {
    return firstValueFrom(this.http.delete<void>(`${BASE_URL}/tasks/${id}`));
  }
}
```

Three details you will meet again:

- **Type parameters on the HTTP methods.** `this.http.get<Task[]>(url)` tells the compiler the response body is an array of `Task`. Angular does not validate that the server actually returned that shape; it is a contract you assert. In Chapter 17 we will add tests that check the server's shape matches this assertion.
- **`firstValueFrom` from RxJS.** `HttpClient` methods return *Observables*, not Promises. An Observable is a stream of values over time; `firstValueFrom` awaits the first one and returns a Promise. For request/response HTTP, this is what you want. Chapter 11 unpacks Observables properly.
- **`Omit<Task, 'id'>` and `Partial<Task>`.** These are TypeScript utility types: `Omit<T, 'K'>` is `T` without field `K`; `Partial<T>` is `T` with every field optional. Both are common in API method signatures.

## Wiring HTTP into `TaskStore`

Now update `TaskStore` to use the API. The store still exposes the same reactive signals; it just fetches and syncs to the server.

Edit `src/app/task-store.ts`:

```ts
import { Injectable, signal, computed, inject } from '@angular/core';
import { Task } from './task';
import { TasksApi } from './tasks-api';

@Injectable({ providedIn: 'root' })
export class TaskStore {
  private api = inject(TasksApi);
  private readonly _tasks = signal<Task[]>([]);
  private readonly _loading = signal(false);
  private readonly _error = signal<string | null>(null);

  readonly tasks = this._tasks.asReadonly();
  readonly loading = this._loading.asReadonly();
  readonly error = this._error.asReadonly();
  readonly remaining = computed(() => this._tasks().filter(t => !t.done).length);

  async load(): Promise<void> {
    this._loading.set(true);
    this._error.set(null);
    try {
      const tasks = await this.api.list();
      this._tasks.set(tasks);
    } catch (err) {
      this._error.set('Could not load tasks. Try again in a moment.');
    } finally {
      this._loading.set(false);
    }
  }

  async add(title: string): Promise<void> {
    const draft: Omit<Task, 'id'> = {
      title,
      done: false,
      createdAt: new Date().toISOString(),
      dueDate: null,
      tags: [],
    };
    // Optimistic add: put a temporary row in the UI immediately.
    const tempId = `temp-${crypto.randomUUID()}`;
    const optimistic: Task = { ...draft, id: tempId };
    this._tasks.update(current => [...current, optimistic]);
    try {
      const saved = await this.api.create(draft);
      this._tasks.update(current =>
        current.map(t => (t.id === tempId ? saved : t))
      );
    } catch {
      this._tasks.update(current => current.filter(t => t.id !== tempId));
      this._error.set('Could not save the new task.');
    }
  }

  async toggle(id: string): Promise<void> {
    const current = this._tasks().find(t => t.id === id);
    if (!current) return;
    const next: Task = { ...current, done: !current.done };
    this._tasks.update(all => all.map(t => (t.id === id ? next : t)));
    try {
      await this.api.update(id, { done: next.done });
    } catch {
      // Revert on failure
      this._tasks.update(all => all.map(t => (t.id === id ? current : t)));
      this._error.set('Could not save that change.');
    }
  }

  async remove(id: string): Promise<void> {
    const previous = this._tasks();
    this._tasks.update(all => all.filter(t => t.id !== id));
    try {
      await this.api.remove(id);
    } catch {
      this._tasks.set(previous);
      this._error.set('Could not delete the task.');
    }
  }
}
```

The store now:

- **Loads asynchronously.** On `load()`, it fetches from the server, updates its signals, and exposes `loading` and `error` signals for the UI.
- **Applies changes optimistically.** `add`, `toggle`, and `remove` update the UI *before* the server responds; if the server fails, the store reverts. This is what makes web apps feel snappy.
- **Exposes only signals to the UI.** The UI never awaits anything; it reads reactive state.

## Calling `load()` on startup

`TaskStore` has a `load()` method, but nothing calls it. Add a call from `TaskList`'s constructor:

```ts
export class TaskList {
  private store = inject(TaskStore);
  tasks = this.store.tasks;
  remaining = this.store.remaining;
  loading = this.store.loading;
  error = this.store.error;

  constructor() {
    this.store.load();
  }

  onAdd(title: string): void { this.store.add(title); }
  onToggle(id: string): void { this.store.toggle(id); }
}
```

Update the template to show loading and error state:

```html
<h1>Tasks — {{ remaining() }} left</h1>

@if (loading()) {
  <p class="status">Loading…</p>
}
@if (error()) {
  <p class="status error">{{ error() }}</p>
}

<app-add-task-form (add)="onAdd($event)" />

<ul class="task-list">
  @for (task of tasks(); track task.id) {
    <app-task-row [task]="task" (toggled)="onToggle($event)" />
  } @empty {
    <li class="empty">Nothing to do. Nice.</li>
  }
</ul>
```

Save. Refresh. You should see a brief "Loading…" flash and then your two tasks from `db.json`. Add a task; open `db.json` in your editor to confirm the file got a third entry. Toggle a task; the change should persist across refreshes.

## Interceptors: cross-cutting request behavior

Suppose every request needs an `Authorization` header, or every response needs to be logged, or every 401 needs to redirect to a login page. You do not want to put that code in every method of `TasksApi`. Angular's answer is *interceptors*.

An interceptor is a function that runs on every HTTP request, can modify the request, and can modify the response.

```ts
// src/app/auth-interceptor.ts
import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('compass:token');
  if (token) {
    req = req.clone({ setHeaders: { Authorization: `Bearer ${token}` } });
  }
  return next(req);
};
```

Register it in `app.config.ts`:

```ts
import { provideHttpClient, withFetch, withInterceptors } from '@angular/common/http';
import { authInterceptor } from './auth-interceptor';

// ...providers:
provideHttpClient(withFetch(), withInterceptors([authInterceptor])),
```

Now every request sent by `HttpClient` picks up the header, without `TasksApi` having to think about it.

Interceptors also make error handling uniform. A `logout on 401` interceptor:

```ts
import { HttpInterceptorFn } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';

export const authGuardInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    catchError(err => {
      if (err.status === 401) {
        localStorage.removeItem('compass:token');
        window.location.href = '/login';
      }
      return throwError(() => err);
    })
  );
};
```

We will use interceptors more in Part V; for now, know they exist and are the right hammer for "every request needs X."

## `httpResource`: the modern signal-integrated fetch

The `firstValueFrom(this.http.get(...))` pattern is fine, but modern Angular offers something nicer for the common case of "fetch and hold this data." `httpResource<T>` creates a signal-backed HTTP resource that tracks loading, error, and value state for you.

```ts
import { httpResource } from '@angular/common/http';

@Injectable({ providedIn: 'root' })
export class TaskStore {
  private baseUrl = 'http://localhost:3000';

  taskList = httpResource<Task[]>(() => `${this.baseUrl}/tasks`);

  // In a component: taskList.value(), taskList.isLoading(), taskList.error()
}
```

`httpResource` returns a resource with `.value()`, `.isLoading()`, `.error()`, `.reload()`, and a few more. Its request URL is a function; when any signal read inside the function changes, it re-fetches. So `httpResource(() => `${baseUrl}/tasks?tag=${tag()}`)` re-fetches whenever `tag` changes.

For Compass we will keep our hand-rolled `TaskStore` because it also handles mutations, but for read-only data (statistics, dashboards, look-ups), `httpResource` cuts a lot of code. Chapter 14 revisits it when we add the stats page.

## Errors, timeouts, retries

Every HTTP call can fail. `HttpClient` reports failures as errors on the Observable, which become rejections on the Promise, which become thrown exceptions on `await`. In the store above we caught those and revert the optimistic update.

For transient failures, retry logic can help. RxJS has a `retry` operator:

```ts
import { retry } from 'rxjs';

list(): Promise<Task[]> {
  return firstValueFrom(
    this.http.get<Task[]>(`${BASE_URL}/tasks`).pipe(retry({ count: 2, delay: 500 }))
  );
}
```

This retries the request up to twice, with a half-second delay between attempts. Chapter 11 covers RxJS operators like this properly.

For timeouts, `HttpContext` and interceptors can cap request durations, or you can wrap the request in `Promise.race` with a timer. In Compass we will not add timeouts by hand; if a request hangs, the user's browser will surface the failure eventually, and our optimistic updates keep the UI responsive.

## Cache and stale data

`HttpClient` does not cache. Every call goes to the network unless a browser or Service Worker layer catches it. For most application data, this is what you want — you do not want stale data cached inside your JavaScript.

`httpResource` re-fetches when its request signal changes; it does not cache across pages either. If you need caching (a settings endpoint that never changes during a session, say), Chapter 14 shows a pattern that combines `httpResource` with a signal-based cache.

## What comes next

Chapter 11 covers RxJS — the library beneath `HttpClient` and the way Angular represents streams that unfold over time. Then Chapter 12 replaces our hand-rolled "Add task" input with proper reactive forms, complete with validation and type safety.

### Exercises

1. Add a "delete" button to `TaskRow` that emits a `deleted` event. Wire `TaskList` to call `store.remove(id)`. Verify that the deletion persists across refreshes.

2. Trigger a failure: stop `json-server`, then click a task. What does the UI do? Is the optimistic update reverted? Is the error message shown? Once you have verified, restart `json-server` and click again — everything should recover.

3. Rewrite `TasksApi.list()` to use `httpResource` instead of a plain `http.get`. What signature does the method have now? What does `TaskStore` need to change to consume it? (You can leave `TaskStore` using the promise-based version if you prefer; the point of the exercise is to see the difference.)
