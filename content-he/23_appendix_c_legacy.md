# נספח ג'. אידיומים ישנים של Angular שתפגוש עדיין

הספר הזה לימד Angular מודרנית: קומפוננטות עצמאיות, סיגנלים, זרימת השליטה החדשה, `inject()`, ופונקציות `input()`/`output()`. קודי Angular בטבע ישנים יותר מהספר הזה, ורבים משתמשים באידיומים שהיו ברירת המחדל כשהם נכתבו. הנספח הזה ממפה את הצורות הישנות לחדשות כך שתוכל לקרוא קוד ישן יותר בלי בלבול.

הכל בנספח הזה עדיין עובד. שיא התאימות של Angular מצוין. קוד חדש צריך להשתמש בצורות המודרניות; קוד ישן שאתה יורש יכול להיות מודרן בהדרגה או להישאר לבד.

## NgModules

**ישן:**

```ts
@NgModule({
  declarations: [TaskListComponent, TaskRowComponent, TimeAgoPipe],
  imports: [CommonModule, ReactiveFormsModule],
  exports: [TaskListComponent],
})
export class TasksModule {}
```

**מודרני:** קומפוננטות עצמאיות כל אחת מכריזה על הייבואים שלה. אין מודול. איפה שרשמת קודם קבוצת קומפוננטות יחד, הן עכשיו מייצאות את עצמן וצרכנים מייבאים אותן בנפרד.

אם אתה בתוך קוד שנבנה סביב NgModules, חפש:

- דקורטורי `@NgModule`.
- קומפוננטות בלי `standalone: true` (או `standalone: false` במפורש).
- קבצי `SharedModule` שמייצאים מחדש declarations נפוצות.

מסלול הגירה: `ng generate @angular/core:standalone-migration` הוא schematic שממיר אפליקציה מבוססת NgModule לקומפוננטות עצמאיות במעבר אחד. הוא עובד היטב; קח snapshot לפני.

## DI של קונסטרוקטור לעומת `inject()`

**ישן:**

```ts
export class TaskList {
  constructor(private store: TaskStore, private router: Router) {}
}
```

**מודרני:**

```ts
export class TaskList {
  private store = inject(TaskStore);
  private router = inject(Router);
}
```

שניהם עובדים. `inject()` מתחבר טוב יותר עם סיגנלים, פונקציות factory, ומצבים מחוץ לקונסטרוקטור. DI של קונסטרוקטור בסדר ועדיין ברירת המחדל במדריכי סגנון קוד רבים.

אם אתה ממיר: אל תעשה את כולם בבת אחת. המר כשאתה נוגע בקובץ.

## דקורטורים `@Input()` ו-`@Output()`

**ישן:**

```ts
export class TaskRow {
  @Input() task!: Task;
  @Output() toggled = new EventEmitter<string>();

  onClick() { this.toggled.emit(this.task.id); }
}
```

**מודרני:**

```ts
export class TaskRow {
  task = input.required<Task>();
  toggled = output<string>();

  onClick() { this.toggled.emit(this.task().id); }
}
```

צורות הדקורטור עדיין עובדות. Signal inputs (`input()`) נותנים לך ערך ריאקטיבי; decorator inputs נותנים לך property רגיל. Signal outputs (`output()`) ו-`EventEmitter` תואמים על החוט — הורה מקשיב עם `(toggled)` בכל מקרה.

## `*ngIf`, `*ngFor`, `*ngSwitchCase`

**ישן:**

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

**מודרני:**

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

בקרת הזרימה החדשה נקייה יותר, מהירה יותר, ולא צריכה את `CommonModule` ב-imports. יש schematic להגירה: `ng generate @angular/core:control-flow-migration`.

הצורות הישנות דורשות את `CommonModule` (או את הדירקטיבות הספציפיות) ב-imports של הקומפוננטה; החדשות לא דורשות כלום.

## Observables איפה שסיגנלים עכשיו מתאימים

**ישן:**

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

**מודרני:**

```ts
export class TaskList {
  private store = inject(TaskStore);
  tasks = this.store.tasks;   // רק קריאה של סיגנל
}
```

או, אם החנות עדיין חושפת Observables:

```ts
tasks = toSignal(this.store.tasks$, { initialValue: [] });
```

הדפוס `destroy$ + takeUntil(destroy$)` הוא האידיום הקלאסי של קריעת observable של Angular. החלפה מודרנית: `takeUntilDestroyed()`, שקורא את ה-`DestroyRef` הנוכחי מ-DI ומשלים אוטומטית.

## `HttpClient` מחזיר Observables

עדיין אותו הדבר. מתודות ה-`HttpClient` של Angular עדיין מחזירות Observables. מה שהשתנה: קוד מודרני לעתים קרובות עוטף אותם ל-Promises דרך `firstValueFrom`, או מזין אותם דרך `toSignal`, או משתמש ב-`httpResource` החדש יותר. עדיין תראה `.subscribe(v => ...)` בקוד ישן יותר; זה עדיין עובד, אבל שלב אותו עם `takeUntilDestroyed`.

## Providers ו-`forRoot()`

**ישן:**

```ts
imports: [RouterModule.forRoot(routes), HttpClientModule]
```

**מודרני:**

```ts
providers: [provideRouter(routes), provideHttpClient()]
```

לכל תכונה של Angular שהייתה לה `forRoot()` / `forChild()` מודול יש עכשיו פונקציית `provide*()`. המודולים הישנים עדיין קיימים לתאימות לאחור אבל קוד חדש משתמש בצורות החדשות.

## משתני תבנית ו-`ViewChild`

**ישן:**

```ts
@ViewChild('searchInput') searchInput!: ElementRef<HTMLInputElement>;

ngAfterViewInit() {
  this.searchInput.nativeElement.focus();
}
```

**מודרני:**

```ts
searchInput = viewChild<ElementRef<HTMLInputElement>>('searchInput');

constructor() {
  afterNextRender(() => this.searchInput()?.nativeElement.focus());
}
```

`viewChild()` מבוסס סיגנל נותן לך התייחסות ריאקטיבית. `afterNextRender` מחליף את `ngAfterViewInit` עבור המקרה הנפוץ של "רץ אחרי ש-DOM רונדר".

## `ChangeDetectorRef.detectChanges()` / `markForCheck()`

**ישן:** קומפוננטות ב-`ChangeDetectionStrategy.OnPush` לפעמים קוראות ל-`this.cdr.markForCheck()` אחרי שינוי מצב כדי לומר ל-Angular לבדוק אותן שוב.

**מודרני:** סיגנלים מודיעים ל-Angular אוטומטית. אם עברת לסיגנלים, לא אמור להיות צורך ב-`markForCheck()`. אם אתה מוצא את עצמך פונה ל-`ChangeDetectorRef`, כנראה אתה מנהל מצב מחוץ למערכת הריאקטיבית.

## `Renderer2`

עדיין עדכני. `Renderer2` הוא הדרך של Angular לא-תלוי-פלטפורמה למנפולציה של DOM (בטוח ל-SSR). השתמש בו כשהיית פונה אחרת ל-`nativeElement.style.foo = ...`; הוא עובד גם בשרת.

## `ngClass` ו-`ngStyle`

**ישן:**

```html
<li [ngClass]="{ done: task.done, overdue: isOverdue(task) }">
<span [ngStyle]="{ color: task.done ? '#999' : 'inherit' }">
```

**מודרני:**

```html
<li [class]="{ done: task.done, overdue: isOverdue(task) }">
<span [style]="{ color: task.done ? '#999' : 'inherit' }">
```

או הקיצורים הקומפקטיים שכיסינו בפרק 6:

```html
<li [class.done]="task.done" [class.overdue]="isOverdue(task)">
<span [style.color]="task.done ? '#999' : 'inherit'">
```

`[ngClass]` ו-`[ngStyle]` עדיין עובדים; הם דורשים `CommonModule`. הקישורים הפשוטים `[class]` ו-`[style]` לא.

## ראוטר: `RouterModule` לעומת `provideRouter`

**ישן:**

```ts
@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
```

**מודרני:**

```ts
providers: [provideRouter(routes)]
```

בתבניות, `RouterOutlet`, `RouterLink`, ו-`RouterLinkActive` הן עדיין דירקטיבות שאתה מייבא לכל קומפוננטה במצב standalone.

## טפסים: `FormsModule` לעומת `ReactiveFormsModule`

שניהם עדיין קיימים. קודים ישנים יותר לפעמים מייבאים את שניהם כדי לאפשר כל סגנון; קודים חדשים יותר בוחרים אחד. הספר הזה משתמש ב-`ReactiveFormsModule` באופן בלעדי.

## Hooks של מחזור חיים

ה-hooks הקלאסיים — `ngOnInit`, `ngOnDestroy`, `ngOnChanges`, `ngAfterViewInit`, `ngAfterContentInit`, `ngDoCheck` — כולם עדיין עובדים. ההנחיה המודרנית של Angular היא:

- העדף `effect` על `ngOnInit` עבור "הגב ל-inputs".
- העדף `DestroyRef.onDestroy` (דרך `inject`) או `takeUntilDestroyed()` על `ngOnDestroy`.
- העדף `afterNextRender` / `afterRender` על `ngAfterViewInit`.

ה-hooks הישנים לא הוצאו משימוש; הם פשוט פחות נחוצים. כשאתה יורש קוד שמשתמש בהם, אל תשכתב לשם השכתוב.

## `ngOnChanges` ו-`SimpleChanges`

**ישן:**

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

**מודרני:**

```ts
export class TaskRow {
  task = input.required<Task>();

  computed = computed(() => this.recompute(this.task()));
}
```

`ngOnChanges` הייתה הדרך להגיב לשינויי input. Signal inputs הופכים את `computed` ו-`effect` לחלופות טבעיות יותר.

## `EventEmitter`

עדיין עדכני; `output()` מחזירה `OutputEmitterRef` שמתנהג כמו `EventEmitter` עבור ה-listener של ההורה. קוד ישן יותר שכותב `new EventEmitter<T>()` עדיין עובד. קוד חדש מעדיף `output<T>()`.

## Interceptors: מבוססי מחלקה לעומת מבוססי פונקציה

**ישן:**

```ts
@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // ...
  }
}

// רשום עם HTTP_INTERCEPTORS:
{ provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }
```

**מודרני:**

```ts
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  // ...
  return next(req);
};

// רשום עם withInterceptors:
provideHttpClient(withInterceptors([authInterceptor]))
```

שניהם עובדים.

## כלל אצבע לקריאת קוד ישן

קוד ישן נכתב כשהוא היה עדכני. הוא פותר את אותן הבעיות ש-Angular מודרנית פותרת, בצורות שהיו זמינות אז. צוות Angular עשה באופן עקבי צורות *חדשות* בלי לשבור את ה*ישנות*. זה אומר:

- קרא את הצורה הישנה. היא לא שגויה, פשוט ישנה יותר.
- הבן מה היא עושה.
- המר רק אם יש לך סיבה: אתה כבר עורך את הקובץ, או שאתה מושך אותו לאזור מודרן של הקוד.
- לעולם אל תשכתב קובץ שלם רק כי הוא משתמש ב-`@Input()` במקום ב-`input()`. השינוי הזה עולה סבב סקירת קוד בלי להוסיף ערך.

צוות Angular מפרסם schematics של הגירה עבור כל שינוי גדול (`ng update` מיישם אותם). אם הגירה גדולה שווה עשייה, בדרך כלל הם עשו כלי לזה.
