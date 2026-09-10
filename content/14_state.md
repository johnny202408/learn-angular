# Chapter 14. State beyond one component

`TaskStore` was a good first step. It works because Compass has one kind of data. Real applications have many kinds — tasks, habits, users, settings, drafts, filters, uploads, notifications — and they interact. Once several stores need to share values or react to each other, you need a *pattern*, not one clever service.

This chapter lays out that pattern. We convert Compass's ad-hoc state services into a small, consistent shape. We also cover when to reach for larger libraries — specifically NgRx SignalStore and the classic NgRx (Redux for Angular) — and how to tell.

The chapter is about design, so it has less code and more decisions than the last few. Read it slowly.

## The problem statement

By the end of Compass, we will have at least these pieces of state:

- **Tasks** — an array, loaded from a server, mutated by the user.
- **Habits** — same shape.
- **User** — the currently signed-in user (Chapter 19).
- **UI state** — which task is selected, which filter is active, which panel is open, which theme is chosen.
- **Offline queue** — mutations that failed and need retry when the connection returns.

Some of these are server-backed. Some are purely local. Some are read by two components on screen; some are read by many across the app.

You want the state layer to have consistent shape so someone reading Compass six months from now doesn't have to relearn how each piece works. You also don't want to introduce so much machinery that a tiny piece of state costs fifty lines of ceremony.

## The pattern: a `Store` per concern

The pattern this book uses is simple and scales further than beginners expect. For each domain concern, you have one Injectable class — call it a Store — that owns a small number of private signals, exposes readonly signals for reads, and exposes methods for mutations.

The template is roughly:

```ts
@Injectable({ providedIn: 'root' })
export class SomeStore {
  private readonly _state = signal<State>(initialState);
  readonly state = this._state.asReadonly();

  readonly derivedA = computed(() => /* ... */);
  readonly derivedB = computed(() => /* ... */);

  method1(input): void { this._state.update(s => /* ... */); }
  async method2(input): Promise<void> {
    // possibly async work; optimistic updates; error handling
  }
}
```

That is `TaskStore` from Chapter 10, described generically. Two properties make this scale:

- **One writer per signal.** Only the store's own methods write to `_state`. Callers never bypass. This makes the mutations searchable and testable.
- **Readonly views.** The public `state` is a readonly signal. Consumers cannot mutate it accidentally. `computed` values are already readonly by construction.

Add a `HabitStore` with the same shape. Add a `UserStore`. Compass now has three stores, each about a hundred lines, each following the same template. New readers grok them immediately.

## Local (UI) state vs shared state

Not every piece of state belongs in a Store. Two questions decide.

**Does more than one component read this state?** If no, keep it in the component. Signals inside a component are just as reactive as signals inside a service. Moving them into a service to be "clean" hurts readability without helping anything.

**Does this state need to survive when this component is destroyed?** If no, keep it in the component. A form draft, a modal's local UI, a component-local loading flag — all belong in the component.

The dividing line is usually clear. `TaskList`'s `editingId` in Chapter 12 is component-local — it does not survive the component going away. `TaskStore`'s `tasks` is shared and long-lived. Both are signals; only one is in a service.

## Cross-store interaction

Sometimes one store needs to react to another. When the user signs out, all the task and habit state should clear. When a habit is deleted, the tasks that referenced it should have their tags updated.

The clean pattern for this: use `effect` in the depending store. It reads signals from the store it depends on, and reacts.

```ts
@Injectable({ providedIn: 'root' })
export class TaskStore {
  private userStore = inject(UserStore);

  constructor() {
    effect(() => {
      const user = this.userStore.currentUser();
      if (user === null) {
        this._tasks.set([]);
      }
    });
  }
}
```

Rules:

- **Depend downstream, never in a cycle.** `TaskStore` depending on `UserStore` is fine. `UserStore` depending on `TaskStore` is a bug waiting.
- **Never write to a signal you also read in the same effect.** Angular will refuse to run it and log a warning.
- **Never read one store's signals in a place another store's `computed` reads.** If `HabitStore.streakDays` reads `TaskStore.tasks`, refactor: put the computation where it belongs, or expose a purpose-built projection.

Effects are the sharp end of state management. Used sparingly they solve real problems. Overused they turn the state graph into an unlabeled maze.

## Persistence: `localStorage` and beyond

Compass's tasks are backed by HTTP, but UI state — filters, theme, sidebar open/closed, drafts — is nicer to persist across sessions without a round trip. `localStorage` is the standard tool.

A tiny persistence utility:

```ts
export function persistedSignal<T>(key: string, initial: T): WritableSignal<T> {
  const raw = localStorage.getItem(key);
  let start: T = initial;
  if (raw !== null) {
    try { start = JSON.parse(raw); } catch { /* ignore */ }
  }
  const s = signal<T>(start);
  effect(() => {
    localStorage.setItem(key, JSON.stringify(s()));
  });
  return s;
}
```

Use it inside a store's constructor (or as a class-field with `runInInjectionContext` if you're clever):

```ts
@Injectable({ providedIn: 'root' })
export class UIState {
  filter = persistedSignal<'all' | 'open' | 'done'>('compass:filter', 'all');
  theme = persistedSignal<'light' | 'dark' | 'system'>('compass:theme', 'system');
}
```

Now the filter and theme survive refresh, with no additional wiring. Just remember: `localStorage` is synchronous and blocks the main thread. Do not store megabytes. Keep it for small UI state; keep server-backed data on the server.

## Offline queue: a state pattern with real teeth

An offline queue is a good case study for a nontrivial store.

The idea: when the user makes a mutation (add a task, toggle done), Compass tries to send it to the server. If the network is down or the server returns 5xx, the mutation is queued locally with a timestamp and retried later — when the browser is online again, or after a delay.

Sketch of the store:

```ts
type PendingMutation =
  | { kind: 'add'; task: Omit<Task, 'id'>; localId: string }
  | { kind: 'toggle'; taskId: string; done: boolean }
  | { kind: 'remove'; taskId: string };

@Injectable({ providedIn: 'root' })
export class MutationQueue {
  private api = inject(TasksApi);
  private queue = persistedSignal<PendingMutation[]>('compass:queue', []);

  readonly pendingCount = computed(() => this.queue().length);
  readonly online = signal(navigator.onLine);

  constructor() {
    window.addEventListener('online', () => this.online.set(true));
    window.addEventListener('offline', () => this.online.set(false));
    effect(() => {
      if (this.online() && this.queue().length > 0) {
        this.drain();
      }
    });
  }

  enqueue(m: PendingMutation): void {
    this.queue.update(q => [...q, m]);
  }

  private async drain(): Promise<void> { /* ... */ }
}
```

The full drain implementation is longer than we need in this chapter (it has to handle ordering, partial failure, and reconciliation with server IDs). The key point is that the queue is *just another store*. It has private signals, exposes readonly views, exposes methods, uses effect for reactivity. It looks like every other store in Compass.

When you reach for something bigger — NgRx SignalStore or classic NgRx — this is usually the kind of code that motivates the switch. Not "we have more than one signal" but "we have coordinated state updates and cross-cutting behaviors."

## NgRx SignalStore

`@ngrx/signals` is a lightweight library that codifies the pattern above and adds features like *entity management* (indexed arrays with fast lookups by id), *effect helpers*, and *reactive extensions*. If you find yourself writing a lot of `store.tasks().find(t => t.id === x)`, or building indexed lookups by hand, SignalStore's `withEntities` is worth a look.

A sketch:

```ts
import { signalStore, withState, withMethods } from '@ngrx/signals';
import { withEntities } from '@ngrx/signals/entities';
import { inject } from '@angular/core';

export const TaskStore = signalStore(
  { providedIn: 'root' },
  withEntities<Task>(),
  withState({ loading: false, error: null as string | null }),
  withMethods((store) => {
    const api = inject(TasksApi);
    return {
      async load() { /* ... */ },
      async add(title: string) { /* ... */ },
      // ...
    };
  }),
);
```

(Note that `withEntities` lives in `@ngrx/signals/entities`, not the main `@ngrx/signals` package. And `inject()` is called inside the `withMethods` factory body — not as a default parameter — because factories run in an injection context.)

SignalStore is opinionated and modestly sized. You do not need it for Compass; hand-rolled stores work fine. When you find that all your stores use similar entity-indexing code, SignalStore is the natural place to reach.

## When to reach for classic NgRx (Redux)

Classic NgRx — actions, reducers, effects, selectors — is a much larger commitment. It brings:

- **Time-travel debugging.** Every state change is an action; you can step through them in DevTools.
- **Serializable state.** State is plain data, always. This makes it easy to save, replay, or ship over the network.
- **Predictable mutations.** A reducer is a pure function; the only way to change state is to dispatch an action.

It also brings:

- **Ceremony.** Every mutation becomes an action, a reducer case, an effect, a selector. A one-line change to state can touch five files.
- **A learning cliff.** New team members spend a week getting oriented.

Reach for classic NgRx when you have all of these:

- A team of five or more engineers who will touch state code daily.
- State mutations that need audit trails, undo/redo, or replay.
- Complex asynchronous flows that benefit from being described as pipelines of actions.

Do not reach for it because "the app is getting big." Bigness alone is not the criterion; complexity of the state graph is. Compass, even fully-featured, does not need it. A large customer-support platform probably does.

## Selectors, projections, and joins

When two stores need to combine their state, the answer is a *selector* — a `computed` that pulls from both.

```ts
@Injectable({ providedIn: 'root' })
export class TodayDashboard {
  private tasks = inject(TaskStore);
  private habits = inject(HabitStore);

  todayCount = computed(() =>
    this.tasks.tasks().filter(t => !t.done && this.isToday(t.dueDate)).length +
    this.habits.habits().filter(h => !this.doneToday(h)).length
  );

  private isToday(d: string | null) { /* ... */ return false; }
  private doneToday(h: Habit) { /* ... */ return false; }
}
```

`TodayDashboard` is a *view store*: a store built on top of two others, providing a projected view. This composition pattern replaces most of the need for a global state container. Each store owns its concern; a view store combines what it needs.

## Testing stores

Because stores are Injectables, they test with the same DI mechanics as components. Chapter 17 has the full story; the preview:

```ts
describe('TaskStore', () => {
  let store: TaskStore;
  let apiSpy: jasmine.SpyObj<TasksApi>;

  beforeEach(() => {
    apiSpy = jasmine.createSpyObj('TasksApi', ['list', 'create']);
    TestBed.configureTestingModule({
      providers: [{ provide: TasksApi, useValue: apiSpy }],
    });
    store = TestBed.inject(TaskStore);
  });

  it('exposes tasks after load', async () => {
    apiSpy.list.and.resolveTo([{ id: 't1', title: 'a', done: false, /* ... */ }]);
    await store.load();
    expect(store.tasks().length).toBe(1);
  });
});
```

The store is Injectable, so `TestBed.inject` gets a fresh instance. Its dependency, `TasksApi`, is provided as a spy. The test drives the store's public API and asserts on its exposed signals.

## What you should avoid

A few state-shaped anti-patterns catch beginners.

- **Reading from and writing to the same signal in one `computed`.** Computed values are for pure derivations. If you find yourself wanting to write, use an effect (and think hard about whether you have a state-graph cycle).
- **Making everything an observable.** Older Angular code centered on `BehaviorSubject` as the state primitive. Signals are the right primitive now. Keep observables for genuine streams (HTTP, DOM events, WebSockets).
- **Storing derived state.** If A is `B + C`, don't store A. Store B and C; derive A with `computed`. Then A cannot drift out of sync.
- **Deep object graphs.** Signals track references, not deep values. Big nested trees are hard to update immutably. Prefer flat, normalized state; use entity maps (`Record<Id, Entity>`) rather than nested arrays.

## What comes next

Chapter 15 turns to directives and pipes — the reusable UI primitives that let you package behavior (auto-focus, long-press, tooltip) and formatting (relative time, currency, truncation) without wrapping everything in components. Chapter 16 profiles Compass and adds `@defer`, `OnPush`, and image optimization to make it fast on a phone.

### Exercises

1. Add a `SelectionStore` that tracks which tasks are currently selected (say, for bulk actions). It should expose `selected: Signal<Set<string>>`, `isSelected(id)`, `toggle(id)`, `clear()`, and a `count = computed(...)`. Keep it small.

2. Wire the `MutationQueue` sketch above into `TaskStore`. When the network is offline, enqueue mutations; when it comes back, drain them in order. Test by killing `json-server` mid-session and reading the queue's `pendingCount` signal.

3. Refactor Compass's `UIState` (filter, theme, sidebar) to use `persistedSignal`. Then open two browser tabs on Compass and see whether changes in one propagate to the other (they won't by default — `storage` events would, and that is a small extension to `persistedSignal`).
