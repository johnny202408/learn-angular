# Chapter 9. Dependency injection, Angular's superpower

We have hit a limit. Compass keeps its tasks inside `TaskList`. That means the tasks exist only while `TaskList` is on screen; when we start adding a *stats page*, a *sidebar count*, or *routing* between screens, the state will disappear on every navigation. We need to move the tasks out of the component and into something the whole app can share.

That "something" is a *service*. Services in Angular are ordinary TypeScript classes with one special property: they can be injected. A component asks for a service, and Angular provides an instance — the same instance to every asker in the same scope — without the component knowing how the service was created or who else uses it. This mechanism is called *dependency injection* (DI), and it is one of the reasons Angular apps stay maintainable at scale.

This chapter introduces DI, refactors Compass's task state into a `TaskStore` service, and gives you the vocabulary you need for every subsequent chapter. Every part of Angular you meet from now on — HTTP, router, forms, tests, guards, resolvers — arrives at your component through DI.

## Why "injection"?

Imagine `TaskList` needing to talk to a server. Without DI, it would look like:

```ts
class TaskList {
  taskService = new TaskService(new HttpClient(new HttpBackend(new ...)));
}
```

Every component that uses `TaskService` would have to construct the whole chain. Worse, in tests you would have to reconstruct the chain with mocks. It gets baroque fast.

DI inverts the arrangement. The framework maintains a registry (called an *injector*) of services. When your component says "I need a `TaskService`," Angular looks in the registry, constructs one if needed (using its own DI to satisfy the service's dependencies), caches it, and hands it back. Your component gets the finished product without knowing what went into it.

This has three consequences that matter to us:

- **Components stay small.** They don't build the world; they ask for what they need.
- **Instances are shared appropriately.** By default, a service registered at the root has one instance shared across the entire app. Two components asking for `TaskService` receive the *same* `TaskService`, and any state on it is visible to both.
- **Tests get easy.** In tests you can register a fake `TaskService` before creating the component; the component doesn't know or care.

## Creating a service

The Angular CLI has a generator:

```bash
ng generate service task-store
```

That produces `src/app/task-store.ts` (or `task-store.service.ts` in older CLI versions) roughly like:

```ts
import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class TaskStore {}
```

Two ingredients:

- **`@Injectable`** is a decorator that marks the class as available for DI. It also lets the class receive dependencies via DI itself.
- **`providedIn: 'root'`** tells Angular to register the service at the root injector — the top level of the app. That means one shared instance for the entire application. Every component that injects `TaskStore` gets the same instance.

For most services, `providedIn: 'root'` is exactly what you want. It is the modern default, it "tree-shakes" (the service is dropped from the bundle if nothing uses it), and it has no downsides for the vast majority of cases. Reach for the alternatives (Chapter 13 covers a route-scoped variant) only when you have a specific reason.

## Moving Compass's tasks into `TaskStore`

Edit `src/app/task-store.ts`:

```ts
import { Injectable, signal, computed } from '@angular/core';
import { Task } from './task';

@Injectable({ providedIn: 'root' })
export class TaskStore {
  private readonly _tasks = signal<Task[]>([
    { id: 't1', title: 'Buy milk', done: false, createdAt: '2026-01-15T09:00:00Z', dueDate: null, tags: ['home'] },
    { id: 't2', title: 'Write chapter 9', done: true, createdAt: '2026-01-14T18:30:00Z', dueDate: '2026-01-16T00:00:00Z', tags: ['work'] },
    { id: 't3', title: 'Call the plumber', done: false, createdAt: '2026-01-15T11:00:00Z', dueDate: '2026-01-18T00:00:00Z', tags: ['home', 'urgent'] },
  ]);

  readonly tasks = this._tasks.asReadonly();
  readonly remaining = computed(() => this._tasks().filter(t => !t.done).length);
  readonly done = computed(() => this._tasks().filter(t => t.done).length);

  add(title: string): void {
    this._tasks.update(current => [
      ...current,
      {
        id: crypto.randomUUID(),
        title,
        done: false,
        createdAt: new Date().toISOString(),
        dueDate: null,
        tags: [],
      },
    ]);
  }

  toggle(id: string): void {
    this._tasks.update(current =>
      current.map(t => (t.id === id ? { ...t, done: !t.done } : t))
    );
  }

  remove(id: string): void {
    this._tasks.update(current => current.filter(t => t.id !== id));
  }

  clearCompleted(): void {
    this._tasks.update(current => current.filter(t => !t.done));
  }
}
```

Three patterns worth naming:

- **Private writable signal, public readonly view.** `_tasks` is private and mutable; `tasks` is the public, readonly signal that consumers see. This prevents callers from doing `this.store.tasks.set(...)` and bypassing the API.
- **Behavior over data.** The service exposes methods that describe *intent* — add, toggle, remove, clearCompleted. Consumers do not know how tasks are stored, only what they can do with them.
- **Computed derived state.** `remaining` and `done` live here, not in components. Any component can read them; when tasks change, all readers update.

## Injecting the service into a component

Two forms of injection work in modern Angular. The `inject()` function is the newer, preferred form; constructor injection is the older, still-supported form. We use `inject()` throughout the book.

Edit `src/app/task-list/task-list.ts`:

```ts
import { Component, inject } from '@angular/core';
import { TaskStore } from '../task-store';
import { TaskRow } from '../task-row/task-row';
import { AddTaskForm } from '../add-task-form/add-task-form';

@Component({
  selector: 'app-task-list',
  imports: [TaskRow, AddTaskForm],
  templateUrl: './task-list.html',
  styleUrl: './task-list.css',
})
export class TaskList {
  private store = inject(TaskStore);

  tasks = this.store.tasks;
  remaining = this.store.remaining;

  onAdd(title: string): void {
    this.store.add(title);
  }

  onToggle(id: string): void {
    this.store.toggle(id);
  }
}
```

The component is now essentially a translator between the DOM and the service. All of its state and logic have moved to `TaskStore`. If we want the same data in a different component — a sidebar showing `remaining`, say — we just inject `TaskStore` there too and read `store.remaining`. Nothing to plumb through the tree.

The template does not need to change; `tasks` and `remaining` are still signals with the same interface.

Save. The app behaves identically. The tasks now live outside the component, and other components could share them if they existed.

## The `inject()` function

`inject(Class)` returns an instance of `Class` from the current injector. You can call it:

- In a component's field initializer or constructor (as above).
- In a service's field initializer or constructor.
- Inside functions called from those contexts, transitively.

You cannot call `inject()` from a random function that isn't in a DI context. Angular throws a runtime error. If you need to inject outside a natural context, wrap the call in `runInInjectionContext(injector, () => { ... })`, but this is rare in application code — you will encounter it maybe once a year.

`inject()` also has generic forms for optionality and multi-token cases:

```ts
private optionalThing = inject(TokenClass, { optional: true });  // may be null
private allOfThem = inject(TokenClass, { self: true });          // only this injector, not parents
```

We will not need these for a while. Plain `inject(Something)` covers 95% of uses.

## Providers: how services get into the injector

`providedIn: 'root'` is one way to register a service. There are others, and you will meet them one at a time.

### App-level providers via `provideX(...)`

Some services are configured with data; you cannot just register them with a decorator. Angular's convention is a `provide<Feature>(config)` function you place in `providers` in `app.config.ts`:

```ts
export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(),
    provideAnimations(),
  ],
};
```

`provideRouter`, `provideHttpClient`, and their friends are how Angular's opt-in features arrive in your app. Each function returns a set of provider records; Angular reads them at bootstrap.

### Component-level providers

A component can register a service scoped to itself and its children:

```ts
@Component({
  selector: 'app-editor',
  providers: [EditorState],
})
export class Editor { }
```

Now every `EditorState` reference *inside* `Editor` (in `Editor` itself and any child component) resolves to the same instance; a `EditorState` reference *outside* `Editor` resolves to a different instance (or fails if there is no root provider).

This is useful for state that is local to a screen: a wizard's step state, a modal's form draft, a page's filter selections. We will use it in Chapter 13.

### Value and factory providers

Sometimes what you want to inject is not a class, but a value or a function's return. Angular has syntax for these too:

```ts
providers: [
  { provide: 'API_BASE_URL', useValue: 'https://api.compass.example' },
  { provide: TaskLoader, useFactory: () => new TaskLoader(navigator.onLine) },
]
```

An `InjectionToken<T>` is the type-safe way to identify a non-class provider:

```ts
import { InjectionToken } from '@angular/core';

export const API_BASE_URL = new InjectionToken<string>('API_BASE_URL');

// providers:
{ provide: API_BASE_URL, useValue: 'https://api.compass.example' }

// injection:
private apiUrl = inject(API_BASE_URL);
```

You will see `InjectionToken` in Angular's own code and in libraries. In application code, plain classes with `providedIn: 'root'` cover most needs.

## Hierarchical injectors

Angular's injectors form a tree that follows the component tree. When you `inject(X)` in a component, Angular walks *up* from that component's injector looking for a provider for `X`. It uses the first one it finds.

That is why component-level `providers: [EditorState]` gives every descendant a shared instance, while the same code in a sibling component's `providers` array gives that sibling a different instance. The lookup finds the nearest provider.

You will rarely think about this explicitly. It matters when:

- You have a service you want scoped to a specific feature area (a wizard, a modal), not the whole app.
- You need to override a service in tests (Chapter 17).
- You want two instances of the same service class for two different purposes.

For everything else, `providedIn: 'root'` and forget about it.

## Circular dependencies

Two services that inject each other create a cycle. Angular refuses to construct them and throws at runtime. If you hit this, it usually means the services have a design problem: they should be merged, or one should hold the other but not vice versa, or the shared state should be extracted into a third service they both depend on.

There is a workaround — inject `Injector` and look up lazily — but you should not need it. When you feel the pull toward it, take that as a signal to redesign.

## Testing benefits, previewed

Because everything a component uses comes in through DI, tests can *replace* those dependencies:

```ts
TestBed.configureTestingModule({
  providers: [
    { provide: TaskStore, useValue: fakeStore },
  ],
});
```

The component's `inject(TaskStore)` now returns `fakeStore`. No monkey-patching, no imports to redirect. Chapter 17 unpacks this in detail; for now, know that the reason your Compass tests will be easy later is because you designed it around DI now.

## What comes next

Chapter 10 hooks `TaskStore` up to a real HTTP backend. We will introduce Angular's `HttpClient`, write functions to fetch, create, update, and delete tasks, and wire them into the store. By the end of Chapter 10, refreshing the browser will preserve your tasks — because they live on a server, not in memory.

### Exercises

1. Create a second component `TaskCountBadge` that shows just the remaining count as a small pill. Inject `TaskStore` inside it and render `{{ store.remaining() }}`. Place it near the heading in `TaskList`. Notice that no data flows through props — the two components share state via the service.

2. Add a `HabitStore` service scaffolded the same way as `TaskStore`. It should hold a signal of habits (make up an `interface Habit`), expose read-only `habits`, and provide `add`, `remove`, and `check`. Don't wire it into any component yet; just make sure it compiles.

3. Register `TaskStore` at the component level instead of `providedIn: 'root'`. What breaks? Reset it, and think about why: what property of shared state depends on where the service is registered?
