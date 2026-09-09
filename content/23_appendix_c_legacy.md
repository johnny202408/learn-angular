# Appendix C. Legacy Angular idioms you'll still meet

This book taught modern Angular: standalone components, signals, the new control flow, `inject()`, and `input()`/`output()` functions. Angular codebases in the wild are older than this book, and many use idioms that were the default when they were written. This appendix maps the old shapes to the new ones so you can read older code without confusion.

Everything in this appendix still works. Angular's compatibility record is excellent. New code should use the modern forms; old code you inherit can be modernized incrementally or left alone.

## NgModules

**Old:**

```ts
@NgModule({
  declarations: [TaskListComponent, TaskRowComponent, TimeAgoPipe],
  imports: [CommonModule, ReactiveFormsModule],
  exports: [TaskListComponent],
})
export class TasksModule {}
```

**Modern:** standalone components each declare their own imports. There is no module. Where you previously registered a group of components together, they now export themselves and consumers import them individually.

If you are inside a codebase built around NgModules, look for:

- `@NgModule` decorators.
- Components without `standalone: true` (or `standalone: false` explicitly).
- `SharedModule` files that re-export common declarations.

Migration path: `ng generate @angular/core:standalone-migration` is a schematic that converts an NgModule-based app to standalone components in one pass. It works well; take a snapshot beforehand.

## Constructor DI vs `inject()`

**Old:**

```ts
export class TaskList {
  constructor(private store: TaskStore, private router: Router) {}
}
```

**Modern:**

```ts
export class TaskList {
  private store = inject(TaskStore);
  private router = inject(Router);
}
```

Both work. `inject()` composes better with signals, factory functions, and outside-of-constructor situations. Constructor DI is fine and is still the default in many code style guides.

If you are converting: don't do them all at once. Convert as you touch a file.

## `@Input()` and `@Output()` decorators

**Old:**

```ts
export class TaskRow {
  @Input() task!: Task;
  @Output() toggled = new EventEmitter<string>();

  onClick() { this.toggled.emit(this.task.id); }
}
```

**Modern:**

```ts
export class TaskRow {
  task = input.required<Task>();
  toggled = output<string>();

  onClick() { this.toggled.emit(this.task().id); }
}
```

The decorator forms still work. Signal inputs (`input()`) give you a reactive value; decorator inputs give you a plain property. Signal outputs (`output()`) and `EventEmitter` are wire-compatible — a parent listens with `(toggled)` either way.

## `*ngIf`, `*ngFor`, `*ngSwitchCase`

**Old:**

```html
<div *ngIf="user; else guest">
  Hello, {{ user.name }}.
</div>
<ng-template #guest>
  <a routerLink="/login">Sign in</a>
</ng-template>

<ul>
  <li *ngFor="let task of tasks; trackBy: trackTask">
    {{ task.title }}
  </li>
</ul>

<div [ngSwitch]="task.status">
  <span *ngSwitchCase="'todo'">To do</span>
  <span *ngSwitchCase="'done'">Done</span>
  <span *ngSwitchDefault>?</span>
</div>
```

**Modern:**

```html
@if (user) {
  <div>Hello, {{ user.name }}.</div>
} @else {
  <a routerLink="/login">Sign in</a>
}

<ul>
  @for (task of tasks; track task.id) {
    <li>{{ task.title }}</li>
  }
</ul>

@switch (task.status) {
  @case ('todo') { <span>To do</span> }
  @case ('done') { <span>Done</span> }
  @default { <span>?</span> }
}
```

The new control flow is cleaner, faster, and doesn't need `CommonModule` in imports. There is a migration schematic: `ng generate @angular/core:control-flow-migration`.

The old forms require `CommonModule` (or the specific directives) in the component's imports; the new forms don't require anything.

## Observables where signals now fit

**Old:**

```ts
export class TaskList implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  tasks: Task[] = [];

  constructor(private store: TaskStore) {}

  ngOnInit() {
    this.store.tasks$
      .pipe(takeUntil(this.destroy$))
      .subscribe(t => this.tasks = t);
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

**Modern:**

```ts
export class TaskList {
  private store = inject(TaskStore);
  tasks = this.store.tasks;   // just a signal read
}
```

Or, if the store still exposes Observables:

```ts
tasks = toSignal(this.store.tasks$, { initialValue: [] });
```

The `destroy$ + takeUntil(destroy$)` pattern is the classic Angular observable-teardown idiom. Modern replacement: `takeUntilDestroyed()`, which reads the current `DestroyRef` from DI and completes automatically.

## `HttpClient` returning Observables

Still the same. Angular's `HttpClient` methods still return Observables. What changed: modern code often unwraps them to Promises via `firstValueFrom`, or feeds them through `toSignal`, or uses the newer `httpResource`. You will still see `.subscribe(v => ...)` in older code; it still works, but pair it with `takeUntilDestroyed`.

## Providers and `forRoot()`

**Old:**

```ts
imports: [RouterModule.forRoot(routes), HttpClientModule]
```

**Modern:**

```ts
providers: [provideRouter(routes), provideHttpClient()]
```

Every Angular feature that used to have a `forRoot()` / `forChild()` module now has a `provide*()` function. The old modules still exist for backward compatibility but new code uses the new forms.

## Template reference variables and `ViewChild`

**Old:**

```ts
@ViewChild('searchInput') searchInput!: ElementRef<HTMLInputElement>;

ngAfterViewInit() {
  this.searchInput.nativeElement.focus();
}
```

**Modern:**

```ts
searchInput = viewChild<ElementRef<HTMLInputElement>>('searchInput');

constructor() {
  afterNextRender(() => this.searchInput()?.nativeElement.focus());
}
```

The signal-based `viewChild()` gives you a reactive reference. `afterNextRender` replaces `ngAfterViewInit` for the common "run after DOM has rendered" case.

## `ChangeDetectorRef.detectChanges()` / `markForCheck()`

**Old:** components on `ChangeDetectionStrategy.OnPush` sometimes call `this.cdr.markForCheck()` after mutating state to tell Angular to re-check them.

**Modern:** signals notify Angular automatically. If you have moved to signals, you should not need `markForCheck()`. If you find yourself reaching for `ChangeDetectorRef`, you are probably managing state outside the reactive system.

## `Renderer2`

Still current. `Renderer2` is Angular's platform-agnostic way to manipulate the DOM (safe for SSR). Use it when you would otherwise reach for `nativeElement.style.foo = ...`; it works on the server, too.

## `ngClass` and `ngStyle`

**Old:**

```html
<li [ngClass]="{ done: task.done, overdue: isOverdue(task) }">
<span [ngStyle]="{ color: task.done ? '#999' : 'inherit' }">
```

**Modern:**

```html
<li [class]="{ done: task.done, overdue: isOverdue(task) }">
<span [style]="{ color: task.done ? '#999' : 'inherit' }">
```

Or the compact shortcuts we covered in Chapter 6:

```html
<li [class.done]="task.done" [class.overdue]="isOverdue(task)">
<span [style.color]="task.done ? '#999' : 'inherit'">
```

`[ngClass]` and `[ngStyle]` still work; they require `CommonModule`. The plain `[class]` and `[style]` bindings do not.

## Router: `RouterModule` vs `provideRouter`

**Old:**

```ts
@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
```

**Modern:**

```ts
providers: [provideRouter(routes)]
```

In templates, `RouterOutlet`, `RouterLink`, and `RouterLinkActive` are still directives you import per component in standalone mode.

## Forms: `FormsModule` vs `ReactiveFormsModule`

Both still exist. Older codebases sometimes import both to allow either style; newer codebases pick one. This book uses `ReactiveFormsModule` exclusively.

## Lifecycle hooks

The classic hooks — `ngOnInit`, `ngOnDestroy`, `ngOnChanges`, `ngAfterViewInit`, `ngAfterContentInit`, `ngDoCheck` — all still work. Modern Angular's guidance is:

- Prefer `effect` over `ngOnInit` for "react to inputs."
- Prefer `DestroyRef.onDestroy` (via `inject`) or `takeUntilDestroyed()` over `ngOnDestroy`.
- Prefer `afterNextRender` / `afterRender` over `ngAfterViewInit`.

The old hooks are not deprecated; they are just less needed. When you inherit code that uses them, don't rewrite for the sake of it.

## `ngOnChanges` and `SimpleChanges`

**Old:**

```ts
export class TaskRow implements OnChanges {
  @Input() task!: Task;

  ngOnChanges(changes: SimpleChanges) {
    if (changes['task']) {
      this.recompute();
    }
  }
}
```

**Modern:**

```ts
export class TaskRow {
  task = input.required<Task>();

  computed = computed(() => this.recompute(this.task()));
}
```

`ngOnChanges` used to be how you reacted to input changes. Signal inputs make `computed` and `effect` the more natural replacements.

## `EventEmitter`

Still current; `output()` returns an `OutputEmitterRef` which behaves like an `EventEmitter` for the parent's listener. Older code writing `new EventEmitter<T>()` still works. New code prefers `output<T>()`.

## Interceptors: class-based vs function-based

**Old:**

```ts
@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // ...
  }
}

// registered with HTTP_INTERCEPTORS:
{ provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }
```

**Modern:**

```ts
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  // ...
  return next(req);
};

// registered with withInterceptors:
provideHttpClient(withInterceptors([authInterceptor]))
```

Both work.

## Rule of thumb for reading legacy code

Old code was written when it was current. It solves the same problems modern Angular solves, in the shapes that were available then. Angular's team has consistently made *new* shapes without breaking *old* ones. That means:

- Read the old shape. It is not wrong, just older.
- Understand what it does.
- Convert only if you have a reason: you are already editing the file, or you are pulling it into a modernized area of the codebase.
- Never rewrite a whole file just because it uses `@Input()` instead of `input()`. That change costs a code review round without adding value.

The Angular team publishes migration schematics for each major shift (`ng update` applies them). If a large migration is worth doing, they usually made a tool for it.
