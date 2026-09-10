# Appendix G. Cheat sheet

A compact reference for the APIs, syntax, and commands you'll reach for most often. Print this, tape it next to your monitor, and rebuild your muscle memory faster.

## Signals

| Call | Purpose |
|---|---|
| `signal<T>(initial)` | Create a writable signal. |
| `signal.set(value)` | Replace the value. |
| `signal.update(fn)` | Compute the next value from the current. |
| `signal.asReadonly()` | Expose a signal without its writer. |
| `computed(() => ...)` | Derived signal; recomputes when dependencies change, caches otherwise. |
| `effect(() => ...)` | Side effect that re-runs when its signal dependencies change. Registered in a DI context. |
| `input<T>()` | Optional signal input (default `undefined` unless provided). |
| `input.required<T>()` | Required signal input; template compiler enforces. |
| `output<T>()` | Signal-based event emitter; `.emit(payload)` to fire. |
| `model<T>(initial)` | Two-way binding via `[(name)]`; read + set. |
| `linkedSignal(fn)` | Writable signal that resets when its computed source changes. |
| `viewChild<T>(ref)` | Signal that resolves to a child element/component by template reference. |
| `contentChild<T>(ref)` | Signal that resolves to a projected child. |

**Rule:** signals track *reference identity*. Never mutate — always produce a new value.

## Template syntax

| Form | Example | Meaning |
|---|---|---|
| Interpolation | `{{ expr }}` | Insert text |
| Property binding | `[prop]="expr"` | Set DOM property |
| Attribute binding | `[attr.name]="expr"` | Set HTML attribute |
| Event binding | `(event)="handler($event)"` | Handle DOM event |
| Two-way binding | `[(name)]="expr"` | Property in, event out |
| Class shortcut | `[class.name]="expr"` | Toggle class |
| Style shortcut | `[style.prop]="expr"` | Set inline style |
| Template ref | `#name` | Reference the element in the same template |
| Local variable | `@let x = expr;` | Bind expression to a local |

## New control flow

```
@if (cond) { … } @else if (c2) { … } @else { … }

@for (item of items; track item.id; let i = $index) {
  …
} @empty {
  …
}

@switch (value) {
  @case ('a') { … }
  @case ('b') { … }
  @default { … }
}

@defer (on viewport) {
  <heavy-component />
} @placeholder { <div>…</div> }
  @loading (after 100ms; minimum 300ms) { <spinner /> }
  @error { <error-view /> }
```

**`@defer` triggers:** `on viewport`, `on idle`, `on interaction`, `on hover`, `on timer(30s)`, `on immediate`, `when signalExpr()`, plus `prefetch on …` for background loading.

## CLI commands

| Command | Purpose |
|---|---|
| `ng new project` | Scaffold a new project |
| `ng serve` | Dev server with HMR |
| `ng serve --open` | Same, and open browser |
| `ng build` | Development build |
| `ng build --configuration production` | Production build |
| `ng test` | Karma + Jasmine unit tests |
| `ng lint` | Lint (if configured) |
| `ng generate component task-row` | Scaffold a component (`ng g c task-row`) |
| `ng generate service tasks` | Scaffold a service (`ng g s tasks`) |
| `ng generate pipe time-ago` | Scaffold a pipe |
| `ng generate directive autofocus` | Scaffold a directive |
| `ng update` | Update Angular and related packages |
| `ng add @package` | Install and configure a schematic-based package |

## Dependency injection

```ts
@Injectable({ providedIn: 'root' })
export class MyService { }

// In a class field or constructor:
private svc = inject(MyService);

// App-level providers (app.config.ts):
providers: [
  provideRouter(routes),
  provideHttpClient(withFetch()),
  provideZonelessChangeDetection(),
  provideBrowserGlobalErrorListeners(),
]

// Component-level:
@Component({ providers: [FeatureState] })

// Token for non-class:
export const API_URL = new InjectionToken<string>('API_URL');
{ provide: API_URL, useValue: 'https://api.example.com' }

// Optional / self-scope:
inject(Thing, { optional: true })
inject(Thing, { self: true })
```

## RxJS operators you'll use most

| Operator | When |
|---|---|
| `map(fn)` | Transform each emission. |
| `filter(fn)` | Drop non-matching. |
| `tap(fn)` | Side effect, no change. |
| `take(n)` | First n emissions. |
| `debounceTime(ms)` | Wait ms after last emission (search boxes). |
| `distinctUntilChanged()` | Drop consecutive duplicates. |
| `switchMap(fn)` | Cancel in-flight inner on new source (search-as-you-type). |
| `mergeMap(fn)` | Concurrent inner streams (parallel processing). |
| `exhaustMap(fn)` | Ignore new source while inner runs (save buttons). |
| `concatMap(fn)` | Queue inners in order. |
| `catchError(fn)` | Handle errors; return fallback Observable. |
| `retry({ count, delay })` | Re-subscribe on error. |
| `combineLatest([a$, b$])` | Latest of each on any emission. |
| `startWith(v)` | Prepend a value. |
| `takeUntilDestroyed()` | Complete when component destroys (Angular). |
| `shareReplay(n)` | Share one execution, replay to late subscribers. |

**Interop:**
- `toSignal(obs$, { initialValue })` — Observable → signal.
- `toObservable(sig)` — signal → Observable.

## Reactive forms

```ts
private fb = inject(FormBuilder);

form = this.fb.nonNullable.group({
  title: ['', [Validators.required, Validators.minLength(2)]],
  dueDate: [null as string | null],
  tags: this.fb.array<FormControl<string>>([]),
});

form.value                    // typed value
form.valid / form.invalid     // validity
form.controls.title.errors    // validation errors
form.controls.title.touched   // has focus been lost yet
form.controls.title.valueChanges  // Observable<string>
form.reset()                  // reset to initial values
```

Common validators: `required`, `email`, `min(n)`, `max(n)`, `minLength(n)`, `maxLength(n)`, `pattern(regex)`, `requiredTrue`.

Custom validator: `(control: AbstractControl) => ValidationErrors | null`.

## Router

```ts
{ path: 'task/:id', component: TaskDetail, title: 'Task' }
{ path: 'stats', loadComponent: () => import('./stats').then(m => m.Stats) }
{ path: '**', redirectTo: '' }
```

**In `app.config.ts`:** `provideRouter(routes, withComponentInputBinding(), withPreloading(PreloadAllModules))`.

**Templates:** `<router-outlet />`, `[routerLink]="['/task', id]"`, `routerLinkActive="active"`, `[routerLinkActiveOptions]="{exact: true}"`.

**Guards:** `CanActivateFn`, `CanMatchFn`, `CanDeactivateFn`, `ResolveFn<T>`.

**Programmatic:** `inject(Router).navigate([...])`, `.navigateByUrl(url)`, `.events` Observable.

## Common Angular error codes

| Code | Meaning |
|---|---|
| `NG0100` | ExpressionChangedAfterItHasBeenCheckedError — value changed during change detection. |
| `NG0200` | Circular DI. Two services inject each other. |
| `NG0201` | No provider — add `providedIn: 'root'` or `providers: [...]`. |
| `NG0950` | Required input missing from parent template. |
| `NG05104` | Root element not found — check `<app-root>` in `index.html`. |

## Common patterns

**Optimistic update with revert:**
```ts
async action(id) {
  const previous = this._items();
  this._items.update(all => /* changed */);
  try { await this.api.update(id); }
  catch { this._items.set(previous); this._error.set('...'); }
}
```

**Persisted signal:**
```ts
const s = signal(JSON.parse(localStorage.getItem(key) ?? 'null') ?? initial);
effect(() => localStorage.setItem(key, JSON.stringify(s())));
```

**Route param as input:**
```ts
// In app.config.ts:
provideRouter(routes, withComponentInputBinding())
// In routed component:
id = input.required<string>();
```

**Search-as-you-type:**
```ts
input$.pipe(
  debounceTime(200),
  distinctUntilChanged(),
  switchMap(q => http.get(`/api?q=${q}`))
).subscribe(...);
```

**Testing store with spy:**
```ts
apiSpy = jasmine.createSpyObj<Api>('Api', ['list', 'create']);
TestBed.configureTestingModule({
  providers: [{ provide: Api, useValue: apiSpy }]
});
apiSpy.list.and.resolveTo([...]);
```

## Standalone component skeleton

```ts
import { Component, ChangeDetectionStrategy, input, output, inject } from '@angular/core';

@Component({
  selector: 'app-thing',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [/* other components, directives, pipes */],
  template: `…`,
  styles: `…`,
})
export class Thing {
  data = input.required<T>();
  changed = output<U>();
  private service = inject(SomeService);

  computedThing = computed(() => …);

  onChange(value: U) { this.changed.emit(value); }
}
```

That's Angular in one page.
