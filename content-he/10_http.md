# פרק 10. HTTP: לדבר עם APIs אמיתיים

Compass רץ עד עכשיו לגמרי בזיכרון של הדפדפן. זה מספיק כדי להדגים את האפליקציה, ולא ממש מספיק לשימוש אמיתי. בפרק הזה נציג את שירות `HttpClient` של Angular, נחבר את Compass לבקאנד קטן, ונאפשר להוסיף משימה במכשיר אחד ולראות אותה במכשיר אחר. עד הסוף, המשימות שאתה יוצר ישרדו ריענון של הדפדפן — כי הן חיות בשרת, לא בסיגנל בזיכרון של `TaskStore`.

לפרק יש שני חצאים. החצי הראשון מרים בקאנד מינימלי כדי שיהיה לנו עם מה לדבר. החצי השני מחבר את `HttpClient` ל-`TaskStore` ומכסה interceptors, טיפול בשגיאות, ואת ה-`httpResource` המודרני.

## בקאנד זעיר ל-Compass

אנחנו צריכים שרת. כדי לשמור על הספר עצמאי, נשתמש ב-`json-server` — שרת REST ללא תצורה שקורא קובץ JSON. הוא חושף אוטומטית endpoints של GET/POST/PUT/PATCH/DELETE. בהפקה Compass היה מדבר עם בקאנד אמיתי (Node, Python, Go, כל אחד); הקוד של Angular זהה.

התקן אותו גלובלית:

```bash
npm install --global json-server
```

צור קובץ `compass/db.json` (ברמה העליונה של פרויקט Angular שלך, ליד `package.json`):

```json
{
  "tasks": [
    { "id": "t1", "title": "Buy milk", "done": false, "createdAt": "2026-01-15T09:00:00Z", "dueDate": null, "tags": ["home"] },
    { "id": "t2", "title": "Write chapter 10", "done": true, "createdAt": "2026-01-14T18:30:00Z", "dueDate": "2026-01-16T00:00:00Z", "tags": ["work"] }
  ]
}
```

הרץ אותו במסוף שני:

```bash
json-server --watch db.json --port 3000
```

עכשיו `http://localhost:3000/tasks` מחזיר את מערך המשימות. עשה לו curl, או פתח את ה-URL בדפדפן, כדי לאשר.

`json-server` הוא שרת מזויף, וההתמדה שלו טריוויאלית — הוא כותב שינויים בחזרה ל-`db.json` — אבל ה-API שלו תואם לכל שרת REST JSON שאי פעם תקרא אליו. זו הנקודה.

### הגדרת CORS היא לא הבעיה שלנו

כי אנחנו מריצים את Compass ב-`http://localhost:4200` ואת ה-API ב-`http://localhost:3000`, דפדפנים היו בדרך כלל חוסמים את הבקשות כ-cross-origin. `json-server` מאפשר אותן כברירת מחדל; API אמיתי בהפקה היה שולח כותרות `Access-Control-Allow-Origin`. בבקאנדים העתידיים שלך, זכור זאת: הדפדפן מקפיד על בקשות cross-origin, ותצורה שגויה של CORS היא הסיבה שדברים "פשוט לא עובדים" בתשעים אחוזים מהמקרים כשמחברים frontend חדש ל-backend חדש.

## הפעלת HttpClient ב-Angular

`HttpClient` הוא שירות ה-HTTP המובנה של Angular. הוא מגיע דרך DI, וצריך להיות מוגדר ברמת האפליקציה. ערוך את `src/app/app.config.ts`:

```ts
import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withFetch } from '@angular/common/http';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideHttpClient(withFetch()),
  ],
};
```

`provideHttpClient()` רושם את השירות. `withFetch()` אומר ל-Angular להשתמש ב-API של `fetch` הנייטיבי של הדפדפן מתחת למכסה; המימוש הישן יותר מבוסס XHR עדיין עובד, אבל `fetch` הוא כיוון ההתקדמות ומתחבר טוב יותר עם SSR (פרק 18).

## חוזה ה-API

הגדר מודול קטן שמתאר את ה-URLs ועושה את ה-HTTP הגולמי. צור `src/app/tasks-api.ts`:

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

שלושה פרטים שתפגוש שוב:

- **פרמטרי טיפוס על מתודות ה-HTTP.** `this.http.get<Task[]>(url)` אומר לקומפיילר שגוף התגובה הוא מערך של `Task`. Angular לא מאמתת שהשרת באמת החזיר את הצורה הזאת; זו טענה שאתה מוסיף. בפרק 17 נוסיף בדיקות שבודקות שהצורה של השרת תואמת לטענה הזאת.
- **`firstValueFrom` מ-RxJS.** מתודות `HttpClient` מחזירות *Observables*, לא Promises. Observable הוא זרם של ערכים לאורך זמן; `firstValueFrom` מחכה לראשון ומחזיר Promise. עבור HTTP של בקשה/תגובה, זה מה שאתה רוצה. פרק 11 פורק Observables כראוי.
- **`Omit<Task, 'id'>` ו-`Partial<Task>`.** אלה הם טיפוסי utility של TypeScript: `Omit<T, 'K'>` הוא `T` בלי השדה `K`; `Partial<T>` הוא `T` עם כל שדה אופציונלי. שניהם נפוצים בחתימות מתודות של API.

## חיווט HTTP לתוך `TaskStore`

עכשיו עדכן את `TaskStore` לשימוש ב-API. החנות עדיין חושפת את אותם סיגנלים ריאקטיביים; היא רק שולפת ומסנכרנת עם השרת.

ערוך את `src/app/task-store.ts`:

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
    // הוספה אופטימית: שים שורה זמנית ב-UI מיד.
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
      // חזרה במקרה של כישלון
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

החנות עכשיו:

- **טוענת אסינכרונית.** ב-`load()`, היא שולפת מהשרת, מעדכנת את הסיגנלים שלה, וחושפת סיגנלי `loading` ו-`error` ל-UI.
- **מחילה שינויים בצורה אופטימית.** `add`, `toggle`, ו-`remove` מעדכנים את ה-UI *לפני* שהשרת מגיב; אם השרת נכשל, החנות חוזרת אחורה. זה מה שגורם לאפליקציות ווב להרגיש snappy.
- **חושפת רק סיגנלים ל-UI.** ה-UI אף פעם לא מחכה למשהו; הוא קורא מצב ריאקטיבי.

## קריאה ל-`load()` בהפעלה

ל-`TaskStore` יש מתודת `load()`, אבל שום דבר לא קורא לה. הוסף קריאה מהקונסטרוקטור של `TaskList`:

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

עדכן את התבנית להראות מצב טעינה ושגיאה:

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

שמור. רענן. אתה אמור לראות הבזק קצר של "Loading…" ואז את שתי המשימות שלך מ-`db.json`. הוסף משימה; פתח את `db.json` בעורך שלך כדי לאשר שהקובץ קיבל רשומה שלישית. העבר משימה; השינוי אמור להתמיד בין ריעננים.

## Interceptors: התנהגות בקשה חוצת-רוחב

נניח שכל בקשה צריכה כותרת `Authorization`, או שכל תגובה צריכה להיות מתועדת, או שכל 401 צריך להפנות לעמוד התחברות. אתה לא רוצה לשים את הקוד הזה בכל מתודה של `TasksApi`. התשובה של Angular היא *interceptors*.

Interceptor הוא פונקציה שרצה על כל בקשת HTTP, יכולה לשנות את הבקשה, ויכולה לשנות את התגובה.

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

רשום אותו ב-`app.config.ts`:

```ts
import { provideHttpClient, withFetch, withInterceptors } from '@angular/common/http';
import { authInterceptor } from './auth-interceptor';

// ...providers:
provideHttpClient(withFetch(), withInterceptors([authInterceptor])),
```

עכשיו כל בקשה שנשלחת על ידי `HttpClient` תופסת את הכותרת, בלי ש-`TasksApi` תצטרך לחשוב על זה.

Interceptors גם הופכים את טיפול השגיאות אחיד. Interceptor שמנתק מ-session ב-401:

```ts
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

נשתמש ב-interceptors יותר בהחלק החמישי; לעת עתה, דע שהם קיימים והם הפטיש הנכון ל"כל בקשה צריכה X".

## `httpResource`: ה-fetch המשולב-סיגנל המודרני

הדפוס של `firstValueFrom(this.http.get(...))` בסדר, אבל Angular מודרנית מציעה משהו יותר נחמד למקרה הנפוץ של "שלוף והחזק את הנתונים האלה". `httpResource<T>` יוצר משאב HTTP מגובה סיגנל שעוקב אחר מצבי טעינה, שגיאה, וערך בשבילך.

```ts
import { httpResource } from '@angular/common/http';

@Injectable({ providedIn: 'root' })
export class TaskStore {
  private baseUrl = 'http://localhost:3000';

  taskList = httpResource<Task[]>(() => `${this.baseUrl}/tasks`);

  // בקומפוננטה: taskList.value(), taskList.isLoading(), taskList.error()
}
```

`httpResource` מחזיר משאב עם `.value()`, `.isLoading()`, `.error()`, `.reload()`, וכמה אחרים. ה-URL של הבקשה שלו הוא פונקציה; כשכל קריאת סיגנל בתוך הפונקציה משתנה, הוא שולף מחדש. אז `httpResource(() => `${baseUrl}/tasks?tag=${tag()}`)` שולף מחדש בכל פעם ש-`tag` משתנה.

ל-Compass נשמור על ה-`TaskStore` שנעשה ידנית כי הוא גם מטפל במוטציות, אבל לנתונים לקריאה בלבד (סטטיסטיקות, דשבורדים, look-ups), `httpResource` חוסך הרבה קוד. פרק 14 חוזר אליו כשנוסיף את עמוד הסטטיסטיקות.

## שגיאות, timeouts, ניסיונות חוזרים

כל קריאת HTTP יכולה להיכשל. `HttpClient` מדווח על כישלונות כשגיאות על ה-Observable, שהופכות לדחיות על ה-Promise, שהופכות לחריגות שנזרקות ב-`await`. בחנות למעלה תפסנו את אלה והחזרנו את העדכון האופטימי.

לכישלונות חולפים, לוגיקת ניסיון חוזר יכולה לעזור. ל-RxJS יש אופרטור `retry`:

```ts
import { retry } from 'rxjs';

list(): Promise<Task[]> {
  return firstValueFrom(
    this.http.get<Task[]>(`${BASE_URL}/tasks`).pipe(retry({ count: 2, delay: 500 }))
  );
}
```

זה מנסה מחדש את הבקשה עד פעמיים, עם עיכוב של חצי שנייה בין ניסיונות. פרק 11 מכסה אופרטורי RxJS כמו זה כראוי.

ל-timeouts, `HttpContext` ו-interceptors יכולים להגביל משך בקשה, או שאתה יכול לעטוף את הבקשה ב-`Promise.race` עם טיימר. ב-Compass לא נוסיף timeouts ידנית; אם בקשה נתקעת, הדפדפן של המשתמש יגלה את הכישלון בסופו של דבר, והעדכונים האופטימיים שלנו שומרים את ה-UI מגיב.

## מטמון ונתונים מיושנים

`HttpClient` לא שומר במטמון. כל קריאה הולכת לרשת אלא אם שכבת דפדפן או Service Worker תופסת אותה. לרוב נתוני היישום, זה מה שאתה רוצה — אתה לא רוצה נתונים מיושנים שנשמרו במטמון בתוך ה-JavaScript שלך.

`httpResource` שולף מחדש כשסיגנל הבקשה שלו משתנה; הוא גם לא שומר במטמון בין עמודים. אם אתה צריך מטמון (endpoint של הגדרות שאף פעם לא משתנה במהלך session, נניח), פרק 14 מראה דפוס שמשלב `httpResource` עם מטמון מבוסס סיגנל.

## מה בא הלאה

פרק 11 מכסה RxJS — הספרייה מתחת ל-`HttpClient` והדרך ש-Angular מייצגת זרמים שנפרסים לאורך זמן. אז פרק 12 מחליף את ה-input "Add task" שלנו בטפסים ריאקטיביים ראויים, שלמים עם ולידציה ובטיחות טיפוסים.

### תרגילים

1. הוסף כפתור "delete" ל-`TaskRow` שפולט אירוע `deleted`. חבר את `TaskList` לקרוא ל-`store.remove(id)`. וודא שהמחיקה מתמידה בין ריעננים.

2. הפעל כישלון: עצור את `json-server`, ואז לחץ על משימה. מה ה-UI עושה? האם העדכון האופטימי מוחזר? האם הודעת השגיאה מוצגת? ברגע שווידאת, הפעל מחדש את `json-server` ולחץ שוב — הכל אמור להתאושש.

3. שכתב את `TasksApi.list()` לשימוש ב-`httpResource` במקום `http.get` רגיל. איזו חתימה יש למתודה עכשיו? מה `TaskStore` צריך לשנות כדי לצרוך אותה? (אתה יכול להשאיר את `TaskStore` משתמש בגרסת ה-promise אם אתה מעדיף; הפואנטה של התרגיל היא לראות את ההבדל.)
