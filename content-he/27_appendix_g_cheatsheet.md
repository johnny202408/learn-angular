# נספח ז'. דף רפרנס מהיר

הפניה קומפקטית ל-APIs, לתחביר, ולפקודות שתפנה אליהם הכי הרבה. הדפס את זה, הדבק ליד המסך, ובנה מחדש את הזיכרון השרירי שלך מהר יותר.

## סיגנלים

| קריאה | מטרה |
|---|---|
| `signal<T>(initial)` | צור סיגנל לכתיבה. |
| `signal.set(value)` | החלף את הערך. |
| `signal.update(fn)` | חשב את הערך הבא מהנוכחי. |
| `signal.asReadonly()` | חשוף סיגנל בלי הכותב שלו. |
| `computed(() => ...)` | סיגנל נגזר; מחשב מחדש כשתלויות משתנות, ומטמן אחרת. |
| `effect(() => ...)` | תופעת לוואי שרצה מחדש כשתלויות הסיגנל שלה משתנות. |
| `input<T>()` | Input סיגנל אופציונלי. |
| `input.required<T>()` | Input סיגנל נדרש. |
| `output<T>()` | פולט אירועים מבוסס סיגנל; `.emit(payload)` לירי. |
| `model<T>(initial)` | Two-way binding דרך `[(name)]`. |
| `linkedSignal(fn)` | סיגנל לכתיבה שמאפס כשהמקור החישובי שלו משתנה. |
| `viewChild<T>(ref)` | סיגנל שנפתר לאלמנט/קומפוננטה ילד לפי reference בתבנית. |

**כלל:** סיגנלים עוקבים אחר *זהות התייחסות*. לעולם אל תשנה — תמיד ייצר ערך חדש.

## תחביר תבנית

| צורה | דוגמה | משמעות |
|---|---|---|
| אינטרפולציה | `{{ expr }}` | הכנס טקסט |
| קישור property | `[prop]="expr"` | הגדר property של DOM |
| קישור attribute | `[attr.name]="expr"` | הגדר HTML attribute |
| קישור event | `(event)="handler($event)"` | טפל באירוע DOM |
| Two-way binding | `[(name)]="expr"` | Property פנימה, event החוצה |
| קיצור class | `[class.name]="expr"` | העבר class |
| קיצור style | `[style.prop]="expr"` | הגדר סגנון inline |
| Template ref | `#name` | התייחסות לאלמנט באותה תבנית |
| משתנה מקומי | `@let x = expr;` | קשור ביטוי למקומי |

## בקרת זרימה חדשה

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

**טריגרים של `@defer`:** `on viewport`, `on idle`, `on interaction`, `on hover`, `on timer(30s)`, `on immediate`, `when signalExpr()`, בתוספת `prefetch on …` לטעינה ברקע.

## פקודות CLI

| פקודה | מטרה |
|---|---|
| `ng new project` | Scaffold פרויקט חדש |
| `ng serve` | שרת פיתוח עם HMR |
| `ng build` | בנייה פיתוחית |
| `ng build --configuration production` | בנייה להפקה |
| `ng test` | בדיקות יחידה עם Karma + Jasmine |
| `ng generate component task-row` | Scaffold קומפוננטה (`ng g c task-row`) |
| `ng generate service tasks` | Scaffold שירות (`ng g s tasks`) |
| `ng generate pipe time-ago` | Scaffold פייפ |
| `ng generate directive autofocus` | Scaffold דירקטיבה |
| `ng update` | עדכן את Angular וחבילות קשורות |
| `ng add @package` | התקן והגדר חבילה מבוססת schematic |

## הזרקת תלויות

```ts
@Injectable({ providedIn: 'root' })
export class MyService { }

// בשדה מחלקה או קונסטרוקטור:
private svc = inject(MyService);

// Providers ברמת האפליקציה (app.config.ts):
providers: [
  provideRouter(routes),
  provideHttpClient(withFetch()),
  provideZonelessChangeDetection(),
  provideBrowserGlobalErrorListeners(),
]

// ברמת הקומפוננטה:
@Component({ providers: [FeatureState] })

// טוקן ל-non-class:
export const API_URL = new InjectionToken<string>('API_URL');
{ provide: API_URL, useValue: 'https://api.example.com' }

// אופציונלי / self-scope:
inject(Thing, { optional: true })
inject(Thing, { self: true })
```

## אופרטורי RxJS שתשתמש בהם הכי הרבה

| אופרטור | מתי |
|---|---|
| `map(fn)` | הפוך כל פליטה. |
| `filter(fn)` | הפל לא תואמים. |
| `tap(fn)` | תופעת לוואי, אין שינוי. |
| `take(n)` | n פליטות ראשונות. |
| `debounceTime(ms)` | חכה ms אחרי הפליטה האחרונה. |
| `distinctUntilChanged()` | הפל כפילויות עוקבות. |
| `switchMap(fn)` | בטל את ה-inner בטיסה על מקור חדש. |
| `mergeMap(fn)` | זרמים פנימיים מקבילים. |
| `exhaustMap(fn)` | התעלם ממקור חדש בזמן שה-inner רץ. |
| `concatMap(fn)` | תור inners בסדר. |
| `catchError(fn)` | טפל בשגיאות; החזר Observable חלופי. |
| `retry({ count, delay })` | הירשם מחדש על שגיאה. |
| `combineLatest([a$, b$])` | האחרון של כל אחד על כל פליטה. |
| `startWith(v)` | הוסף ערך בתחילה. |
| `takeUntilDestroyed()` | השלם כשהקומפוננטה מושמדת. |
| `shareReplay(n)` | שתף ריצה אחת, השמע מחדש למנויים מאוחרים. |

**Interop:**
- `toSignal(obs$, { initialValue })` — Observable → סיגנל.
- `toObservable(sig)` — סיגנל → Observable.

## טפסים ריאקטיביים

```ts
private fb = inject(FormBuilder);

form = this.fb.nonNullable.group({
  title: ['', [Validators.required, Validators.minLength(2)]],
  dueDate: [null as string | null],
  tags: this.fb.array<FormControl<string>>([]),
});

form.value                    // ערך מוקלד
form.valid / form.invalid     // תקינות
form.controls.title.errors    // שגיאות ולידציה
form.controls.title.touched   // האם הפוקוס אבד עדיין
form.controls.title.valueChanges  // Observable<string>
form.reset()                  // אפס לערכים התחלתיים
```

Validators נפוצים: `required`, `email`, `min(n)`, `max(n)`, `minLength(n)`, `maxLength(n)`, `pattern(regex)`, `requiredTrue`.

Custom validator: `(control: AbstractControl) => ValidationErrors | null`.

## Router

```ts
{ path: 'task/:id', component: TaskDetail, title: 'Task' }
{ path: 'stats', loadComponent: () => import('./stats').then(m => m.Stats) }
{ path: '**', redirectTo: '' }
```

**ב-`app.config.ts`:** `provideRouter(routes, withComponentInputBinding(), withPreloading(PreloadAllModules))`.

**תבניות:** `<router-outlet />`, `[routerLink]="['/task', id]"`, `routerLinkActive="active"`, `[routerLinkActiveOptions]="{exact: true}"`.

**Guards:** `CanActivateFn`, `CanMatchFn`, `CanDeactivateFn`, `ResolveFn<T>`.

**תוכניתי:** `inject(Router).navigate([...])`, `.navigateByUrl(url)`, `.events` Observable.

## קודי שגיאה נפוצים של Angular

| קוד | משמעות |
|---|---|
| `NG0100` | ExpressionChangedAfterItHasBeenCheckedError — ערך השתנה במהלך זיהוי שינויים. |
| `NG0200` | DI מעגלית. שני שירותים מזריקים זה את זה. |
| `NG0201` | אין provider — הוסף `providedIn: 'root'` או `providers: [...]`. |
| `NG0950` | חסר Input נדרש מתבנית ההורה. |
| `NG05104` | לא נמצא אלמנט שורש — בדוק `<app-root>` ב-`index.html`. |

## דפוסים נפוצים

**עדכון אופטימי עם חזרה:**
```ts
async action(id) {
  const previous = this._items();
  this._items.update(all => /* changed */);
  try { await this.api.update(id); }
  catch { this._items.set(previous); this._error.set('...'); }
}
```

**סיגנל מתמיד:**
```ts
const s = signal(JSON.parse(localStorage.getItem(key) ?? 'null') ?? initial);
effect(() => localStorage.setItem(key, JSON.stringify(s())));
```

**Route param כ-input:**
```ts
// ב-app.config.ts:
provideRouter(routes, withComponentInputBinding())
// בקומפוננטה מנותבת:
id = input.required<string>();
```

**חיפוש תוך כדי הקלדה:**
```ts
input$.pipe(
  debounceTime(200),
  distinctUntilChanged(),
  switchMap(q => http.get(`/api?q=${q}`))
).subscribe(...);
```

**בדיקת חנות עם spy:**
```ts
apiSpy = jasmine.createSpyObj<Api>('Api', ['list', 'create']);
TestBed.configureTestingModule({
  providers: [{ provide: Api, useValue: apiSpy }]
});
apiSpy.list.and.resolveTo([...]);
```

## שלד קומפוננטה עצמאית

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

זה Angular בעמוד אחד.
