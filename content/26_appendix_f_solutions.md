# Appendix F. Solutions to selected exercises

Not every exercise in this book has a "right answer" — the reflection prompts (like Chapter 1's "describe the difference between a library and a framework without using either word") are yours to think through. But the code exercises do have solutions, and this appendix walks through the ones most likely to trip you up.

Skim the solution only after you've attempted the exercise yourself. Reading the solution first turns coding practice into reading practice, which is not the same skill.

## Chapter 2 — TypeScript

**Exercise 1 (`Habit` interface).**

```ts
interface Habit {
  id: string;
  name: string;
  frequency: 'daily' | 'weekly' | 'custom';
  color?: string;
  readonly createdAt: string;
}

function describe(habit: Habit): string {
  return `${habit.name} (${habit.frequency})`;
}
```

**Exercise 2 (`unwrap` with narrowing).**

```ts
function unwrap<T>(r: Result<T>): T {
  if (r.ok) {
    return r.value;    // TypeScript narrows r to { ok: true; value: T } here
  }
  throw new Error(r.error);
}
```

The trick: after `if (r.ok)`, TypeScript knows `r` is the success branch and lets you access `r.value` without a cast.

## Chapter 3 — Modern JavaScript

**Exercise 1 (array methods).**

```ts
const nums = [3, 1, 4, 1, 5, 9, 2, 6];
const squares = nums.map(n => n * n);              // (a)
const sumOfSquares = squares.reduce((s, n) => s + n, 0);  // (b)
const largest = Math.max(...nums);                 // (c)
const allUnderTen = nums.every(n => n < 10);       // (d)
```

**Exercise 2 (`updateTask`).**

```ts
function updateTask(tasks: Task[], id: string, changes: Partial<Task>): Task[] {
  return tasks.map(t => t.id === id ? { ...t, ...changes } : t);
}
```

Each mapped task is either the original reference (untouched) or a new object with the changes merged in. The input array is not mutated.

**Exercise 3 (Promise chain → async/await).**

```ts
async function loadWithAuth(): Promise<Task[]> {
  const sessionRes = await fetch('/api/session');
  const session = await sessionRes.json();
  const tasksRes = await fetch('/api/tasks', {
    headers: { Authorization: session.token },
  });
  return tasksRes.json();
}
```

If the first `fetch` rejects, the `await` throws, and the whole function returns a rejected Promise — exactly like the `.then/.catch` chain would.

## Chapter 6 — Data binding and control flow

**Exercise 1 (Clear completed button).**

```ts
// In TaskList
hasCompleted = () => this.tasks.some(t => t.done);

clearCompleted() {
  this.tasks = this.tasks.filter(t => !t.done);
}
```

```html
<button (click)="clearCompleted()" [disabled]="!hasCompleted()">
  Clear completed
</button>
```

**Exercise 2 (Counts with `@let`).**

```html
@let total = tasks.length;
@let done = tasks.filter(t => t.done).length;
@let remaining = total - done;
<p>{{ total }} tasks, {{ done }} done, {{ remaining }} remaining.</p>
```

## Chapter 7 — Signals

**Exercise 1 (overdue count).**

```ts
overdueCount = computed(() =>
  this.tasks().filter(t =>
    !t.done && t.dueDate !== null && new Date(t.dueDate) < new Date()
  ).length
);
```

```html
@if (overdueCount() > 0) {
  <p class="overdue-warning">{{ overdueCount() }} overdue</p>
}
```

**Exercise 3 (Clear completed with `update`).**

```ts
clearCompleted() {
  this.tasks.update(current => current.filter(t => !t.done));
}
```

The important thing: `update` receives the current array and returns a *new* array. Never `this.tasks().push(...)` or `this.tasks().splice(...)` — those mutations don't notify the signal.

## Chapter 8 — Composing components

**Exercise 2 (Delete button with `stopPropagation`).**

```ts
// In TaskRow
deleted = output<string>();

onDelete(event: MouseEvent) {
  event.stopPropagation();
  this.deleted.emit(this.task().id);
}
```

```html
<button (click)="onDelete($event)" aria-label="Delete task">×</button>
```

`stopPropagation` prevents the click from bubbling to the parent element's click handler.

## Chapter 10 — HTTP

**Exercise 1 (Delete button + `store.remove`).**

Extend `TaskStore` with the `remove` method from the chapter, add a `deleted` output on `TaskRow` (as above), then wire it up:

```ts
// In TaskList
onDelete(id: string) {
  this.store.remove(id);
}
```

```html
<app-task-row [task]="task" (toggled)="onToggle($event)" (deleted)="onDelete($event)" />
```

Refresh the browser to verify the deletion persists.

## Chapter 11 — RxJS

**Exercise 1 (Load more with `exhaustMap`).**

```ts
const loadMore = fromEvent<MouseEvent>(button, 'click').pipe(
  exhaustMap(() => http.get<Task[]>(`/api/tasks?page=${page}&size=20`))
);
loadMore.subscribe(next => tasks.update(all => [...all, ...next]));
```

The `exhaustMap` guarantees that if the user rage-clicks, only the first click's request runs; subsequent clicks are ignored until it completes.

**Exercise 3 (Cold Observable double-fetch).**

Subscribe to the same `http.get(...)` result twice, watch the Network tab: two requests. Add `.pipe(shareReplay(1))`, subscribe twice again: one request, both subscribers receive the same result.

`shareReplay(1)` vs `shareReplay()`: the `1` is the buffer size — it stores the last emitted value and replays it to late subscribers. Without the `1`, late subscribers get nothing.

## Chapter 12 — Reactive forms

**Exercise 2 (Add task form with due date).**

```ts
form = this.fb.nonNullable.group({
  title: ['', [Validators.required, Validators.minLength(2)]],
  dueDate: [null as string | null],
});

submit(): void {
  if (this.form.invalid) return;
  const raw = this.form.getRawValue();
  this.add.emit({ title: raw.title.trim(), dueDate: raw.dueDate });
  this.form.reset();
}
```

The `add` output type changes from `output<string>()` to `output<{ title: string; dueDate: string | null }>()`. `TaskStore.add` needs a matching signature update.

**Exercise 3 (Async duplicate-title validator).**

```ts
duplicateTitleValidator(store: TaskStore): AsyncValidatorFn {
  return (control) => {
    const title = (control.value ?? '').trim().toLowerCase();
    if (!title) return of(null);
    const taken = store.tasks().some(t => t.title.trim().toLowerCase() === title);
    return of(taken ? { duplicate: true } : null);
  };
}
```

Not really async since it reads a signal, but it fits the `AsyncValidatorFn` shape. To debounce, wrap in `timer(300).pipe(switchMap(...))`.

## Chapter 13 — Routing

**Exercise 1 (Convert Stats and TaskDetail to lazy).**

```ts
export const routes: Routes = [
  { path: '', component: Home, title: 'Today · Compass' },
  {
    path: 'stats',
    loadComponent: () => import('./stats/stats').then(m => m.Stats),
    title: 'Stats · Compass',
  },
  {
    path: 'task/:id',
    loadComponent: () => import('./task-detail/task-detail').then(m => m.TaskDetail),
    title: 'Task · Compass',
  },
  { path: '**', redirectTo: '' },
];
```

After `ng build`, look inside `dist/compass/browser/chunk-*.js` — one chunk per lazy route.

**Exercise 3 (Query param filter with `router.navigate`).**

```ts
setFilter(f: 'all' | 'open' | 'done') {
  this.router.navigate([], {
    relativeTo: this.route,
    queryParams: { filter: f === 'all' ? null : f },
    queryParamsHandling: 'merge',
  });
}

filter = toSignal(
  this.route.queryParamMap.pipe(map(p => (p.get('filter') ?? 'all') as 'all' | 'open' | 'done')),
  { initialValue: 'all' as const }
);

filteredTasks = computed(() => {
  const tasks = this.store.tasks();
  switch (this.filter()) {
    case 'open': return tasks.filter(t => !t.done);
    case 'done': return tasks.filter(t => t.done);
    default: return tasks;
  }
});
```

## Chapter 15 — Directives and pipes

**Exercise 2 (`ClickOutside` directive).**

```ts
@Directive({ selector: '[appClickOutside]' })
export class ClickOutsideDirective {
  clickOutside = output<void>();
  private el = inject<ElementRef<HTMLElement>>(ElementRef);
  private destroyRef = inject(DestroyRef);

  constructor() {
    const onClick = (event: MouseEvent) => {
      if (!this.el.nativeElement.contains(event.target as Node)) {
        this.clickOutside.emit();
      }
    };
    document.addEventListener('click', onClick);
    this.destroyRef.onDestroy(() => document.removeEventListener('click', onClick));
  }
}
```

Use: `<div appClickOutside (clickOutside)="close()">...</div>`.

## Chapter 16 — Performance

**Exercise 1 (Break OnPush by mutating).**

```ts
// In TaskStore
add(title: string) {
  this._tasks().push({ id: crypto.randomUUID(), title, done: false, /* ... */ });
  // no this._tasks.update — mutation only
}
```

Under `OnPush`, the UI doesn't refresh: the signal's reference didn't change, so no re-check is triggered. The fix is the pattern the book has used throughout: `this._tasks.update(current => [...current, newTask])`.

The rule: **signals track reference identity, not deep equality**. Always produce a new array or object.

## Chapter 17 — Testing

**Exercise 1 (`TaskStore.toggle` happy path + revert).**

```ts
describe('TaskStore.toggle', () => {
  let store: TaskStore;
  let apiSpy: jasmine.SpyObj<TasksApi>;

  beforeEach(() => {
    apiSpy = jasmine.createSpyObj<TasksApi>('TasksApi', ['list', 'update']);
    TestBed.configureTestingModule({
      providers: [{ provide: TasksApi, useValue: apiSpy }],
    });
    store = TestBed.inject(TaskStore);
    store['_tasks'].set([
      { id: 't1', title: 'a', done: false, /* ... */ } as Task,
    ]);
  });

  it('applies the toggle and calls the API on success', async () => {
    apiSpy.update.and.resolveTo({} as Task);
    await store.toggle('t1');
    expect(store.tasks()[0].done).toBe(true);
    expect(apiSpy.update).toHaveBeenCalledOnceWith('t1', { done: true });
  });

  it('reverts on API failure', async () => {
    apiSpy.update.and.rejectWith(new Error('boom'));
    await store.toggle('t1');
    expect(store.tasks()[0].done).toBe(false);
    expect(store.error()).toContain('Could not save');
  });
});
```

## Chapter 19 — Deployment

**Exercise 3 (CI that skips deploy on test failure).**

The default GitHub Actions job (from the chapter's YAML) runs steps sequentially and stops on the first failure. To confirm: change one test to fail, push, watch the Actions tab — the deploy step won't run because the test step exited non-zero.

## What we skipped

The following exercises don't have a single "right answer" and are yours to work through:

- Chapter 1's three reflection exercises about frameworks and libraries.
- Chapter 4's `ng generate --dry-run` exploration.
- Chapter 8's `Panel` component design.
- Chapter 14's exercises about state design decisions.
- Chapter 20's four-week study plan follow-through.

Doing those is more valuable than reading solutions to them.
