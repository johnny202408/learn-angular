# נספח ו'. פתרונות לתרגילים נבחרים

לא לכל תרגיל בספר הזה יש "תשובה נכונה" — הנחיות ההרהור (כמו זו של פרק 1 "תאר את ההבדל בין ספרייה לפריימוורק בלי להשתמש באף אחת מהמילים") הן שלך לחשוב עליהן. אבל לתרגילי הקוד יש פתרונות, והנספח הזה עובר דרך אלה שהכי סביר להכשיל אותך.

סקור את הפתרון רק אחרי שניסית את התרגיל בעצמך. קריאת הפתרון קודם הופכת תרגול קידוד לתרגול קריאה, שאינה אותה מיומנות.

## פרק 2 — TypeScript

**תרגיל 1 (`Habit` interface).**

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

**תרגיל 2 (`unwrap` עם צמצום).**

```ts
function unwrap<T>(r: Result<T>): T {
  if (r.ok) {
    return r.value;    // TypeScript narrows r here
  }
  throw new Error(r.error);
}
```

הטריק: אחרי `if (r.ok)`, TypeScript יודעת ש-`r` הוא ענף ההצלחה ומאפשרת לך לגשת ל-`r.value` בלי טענת המרה.

## פרק 3 — JavaScript מודרני

**תרגיל 1 (שיטות מערך).**

```ts
const nums = [3, 1, 4, 1, 5, 9, 2, 6];
const squares = nums.map(n => n * n);
const sumOfSquares = squares.reduce((s, n) => s + n, 0);
const largest = Math.max(...nums);
const allUnderTen = nums.every(n => n < 10);
```

**תרגיל 2 (`updateTask`).**

```ts
function updateTask(tasks: Task[], id: string, changes: Partial<Task>): Task[] {
  return tasks.map(t => t.id === id ? { ...t, ...changes } : t);
}
```

כל משימה ממופה היא או ההתייחסות המקורית (ללא שינוי) או אובייקט חדש עם השינויים ממוזגים. מערך הקלט לא משתנה.

**תרגיל 3 (Promise chain → async/await).**

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

אם ה-`fetch` הראשון נדחה, ה-`await` זורק, וכל הפונקציה מחזירה Promise שנדחה — בדיוק כמו ששרשרת `.then/.catch` הייתה עושה.

## פרק 6 — קישור נתונים ובקרת זרימה

**תרגיל 1 (כפתור Clear completed).**

```ts
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

**תרגיל 2 (ספירות עם `@let`).**

```html
@let total = tasks.length;
@let done = tasks.filter(t => t.done).length;
@let remaining = total - done;
<p>{{ total }} tasks, {{ done }} done, {{ remaining }} remaining.</p>
```

## פרק 7 — סיגנלים

**תרגיל 1 (ספירת overdue).**

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

**תרגיל 3 (Clear completed עם `update`).**

```ts
clearCompleted() {
  this.tasks.update(current => current.filter(t => !t.done));
}
```

הדבר החשוב: `update` מקבל את המערך הנוכחי ומחזיר מערך *חדש*. אף פעם `this.tasks().push(...)` או `this.tasks().splice(...)` — המוטציות האלה לא מודיעות לסיגנל.

## פרק 8 — הרכבת קומפוננטות

**תרגיל 2 (כפתור delete עם `stopPropagation`).**

```ts
deleted = output<string>();

onDelete(event: MouseEvent) {
  event.stopPropagation();
  this.deleted.emit(this.task().id);
}
```

```html
<button (click)="onDelete($event)" aria-label="Delete task">×</button>
```

`stopPropagation` מונע מהלחיצה לעלות למטפל הלחיצה של אלמנט ההורה.

## פרק 10 — HTTP

**תרגיל 1 (כפתור delete + `store.remove`).**

הרחב את `TaskStore` עם מתודת `remove` מהפרק, הוסף output `deleted` על `TaskRow` (כמו למעלה), אז חבר:

```ts
onDelete(id: string) {
  this.store.remove(id);
}
```

```html
<app-task-row [task]="task" (toggled)="onToggle($event)" (deleted)="onDelete($event)" />
```

## פרק 11 — RxJS

**תרגיל 1 (Load more עם `exhaustMap`).**

```ts
const loadMore = fromEvent<MouseEvent>(button, 'click').pipe(
  exhaustMap(() => http.get<Task[]>(`/api/tasks?page=${page}&size=20`))
);
loadMore.subscribe(next => tasks.update(all => [...all, ...next]));
```

ה-`exhaustMap` מבטיח שאם המשתמש לוחץ בחוזקה, רק הבקשה של הלחיצה הראשונה רצה; לחיצות עוקבות מתעלמות ממנה עד שהיא מסתיימת.

**תרגיל 3 (Observable קר double-fetch).**

הירשם לאותה תוצאת `http.get(...)` פעמיים, צפה בטאב הרשת: שתי בקשות. הוסף `.pipe(shareReplay(1))`, הירשם פעמיים שוב: בקשה אחת, שני המנויים מקבלים את אותה תוצאה.

`shareReplay(1)` לעומת `shareReplay()`: ה-`1` הוא גודל ה-buffer — הוא שומר את הערך האחרון שנפלט ומשמיע אותו מחדש למנויים מאוחרים.

## פרק 12 — טפסים ריאקטיביים

**תרגיל 2 (טופס Add task עם תאריך יעד).**

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

טיפוס ה-`add` של ה-output משתנה מ-`output<string>()` ל-`output<{ title: string; dueDate: string | null }>()`.

**תרגיל 3 (Async validator לכפילות כותרות).**

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

## פרק 13 — ניתוב

**תרגיל 1 (המר את Stats ו-TaskDetail לטעינה עצלה).**

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

**תרגיל 3 (Query param filter).**

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

## פרק 15 — דירקטיבות ופייפים

**תרגיל 2 (`ClickOutside` directive).**

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

שימוש: `<div appClickOutside (clickOutside)="close()">...</div>`.

## פרק 16 — ביצועים

**תרגיל 1 (שבור OnPush על ידי מוטציה).**

```ts
add(title: string) {
  this._tasks().push({ id: crypto.randomUUID(), title, done: false });
  // ללא this._tasks.update — רק מוטציה
}
```

תחת `OnPush`, ה-UI לא מתרענן: ההתייחסות של הסיגנל לא השתנתה, כך שלא מופעלת בדיקה מחדש. התיקון הוא הדפוס שהספר השתמש בו לאורך: `this._tasks.update(current => [...current, newTask])`.

הכלל: **סיגנלים עוקבים אחר זהות התייחסות, לא שוויון עמוק**. תמיד ייצר מערך או אובייקט חדש.

## פרק 17 — בדיקות

**תרגיל 1 (`TaskStore.toggle` מסלול מוצלח + חזרה).**

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
      { id: 't1', title: 'a', done: false } as Task,
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

## מה דילגנו עליו

התרגילים הבאים אין להם תשובה יחידה "נכונה" והם שלך לעבור:

- שלושת תרגילי ההרהור של פרק 1 על פריימוורקים וספריות.
- חקר `ng generate --dry-run` של פרק 4.
- עיצוב קומפוננטת `Panel` של פרק 8.
- תרגילי פרק 14 על החלטות עיצוב מצב.
- תוכנית לימוד של ארבעה שבועות של פרק 20 להמשך.

לעשות את אלה בעל ערך יותר מלקרוא פתרונות להם.
