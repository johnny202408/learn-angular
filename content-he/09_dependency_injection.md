# פרק 9. הזרקת תלויות, כוח העל של Angular

הגענו לגבול. Compass שומר את המשימות שלו בתוך `TaskList`. פירוש הדבר שהמשימות קיימות רק בזמן ש-`TaskList` על המסך; כשנתחיל להוסיף *עמוד סטטיסטיקות*, *מונה בסרגל צד*, או *ניתוב* בין מסכים, המצב ייעלם בכל ניווט. אנחנו צריכים להעביר את המשימות מהקומפוננטה למשהו שכל האפליקציה תוכל לשתף.

ה"משהו" הזה הוא *שירות*. שירותים ב-Angular הם מחלקות TypeScript רגילות עם מאפיין מיוחד אחד: הן יכולות להיות מוזרקות. קומפוננטה מבקשת שירות, ו-Angular מספקת מופע — אותו מופע לכל מבקש באותו scope — בלי שהקומפוננטה תדע איך השירות נוצר או מי עוד משתמש בו. המנגנון הזה נקרא *הזרקת תלויות* (DI), וזו אחת הסיבות שאפליקציות Angular נשארות ניתנות לתחזוקה בקנה מידה.

הפרק הזה מציג DI, מעצב מחדש את מצב המשימות של Compass לשירות `TaskStore`, ונותן לך את אוצר המילים שאתה צריך לכל פרק עוקב. כל חלק של Angular שתפגוש מכאן והלאה — HTTP, ראוטר, טפסים, בדיקות, guards, resolvers — מגיע לקומפוננטה שלך דרך DI.

## למה "הזרקה"?

דמיין את `TaskList` שצריך לדבר עם שרת. בלי DI, זה היה נראה כך:

```ts
class TaskList {
  taskService = new TaskService(new HttpClient(new HttpBackend(new ...)));
}
```

כל קומפוננטה שמשתמשת ב-`TaskService` הייתה צריכה לבנות את כל השרשרת. גרוע יותר, בבדיקות היית צריך לבנות מחדש את השרשרת עם mocks. זה הופך למוסרבל מהר.

DI הופך את הסידור. הפריימוורק מתחזק רישום (שנקרא *injector*) של שירותים. כשהקומפוננטה שלך אומרת "אני צריכה `TaskService`", Angular מחפשת ברישום, בונה אחד אם נדרש (משתמשת ב-DI שלה עצמה כדי לספק את התלויות של השירות), שומרת אותו במטמון, ומחזירה אותו. הקומפוננטה שלך מקבלת את המוצר המוגמר בלי לדעת מה נכנס אליו.

לזה יש שלוש השלכות שחשובות לנו:

- **קומפוננטות נשארות קטנות.** הן לא בונות את העולם; הן מבקשות מה שהן צריכות.
- **מופעים משותפים כראוי.** כברירת מחדל, שירות שנרשם בשורש יש לו מופע אחד משותף לרוחב כל האפליקציה. שתי קומפוננטות שמבקשות `TaskService` מקבלות את *אותו* `TaskService`, וכל מצב עליו נראה לשתיהן.
- **בדיקות נהיות קלות.** בבדיקות אתה יכול לרשום `TaskService` מזויף לפני יצירת הקומפוננטה; הקומפוננטה לא יודעת ולא אכפת לה.

## יצירת שירות

ל-CLI של Angular יש מייצר:

```bash
ng generate service task-store
```

זה מייצר `src/app/task-store.ts` (או `task-store.service.ts` בגרסאות CLI ישנות יותר) בערך כך:

```ts
import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class TaskStore {}
```

שני מרכיבים:

- **`@Injectable`** הוא דקורטור שמסמן את המחלקה כזמינה ל-DI. הוא גם מאפשר למחלקה לקבל תלויות דרך DI בעצמה.
- **`providedIn: 'root'`** אומר ל-Angular לרשום את השירות ב-injector השורשי — הרמה העליונה של האפליקציה. פירוש הדבר מופע אחד משותף לכל האפליקציה. כל קומפוננטה שמזריקה `TaskStore` מקבלת את אותו מופע.

לרוב השירותים, `providedIn: 'root'` הוא בדיוק מה שאתה רוצה. זו ברירת המחדל המודרנית, זה "tree-shakes" (השירות נופל מה-bundle אם כלום לא משתמש בו), ואין לזה חסרונות לרוב המכריע של המקרים. פנה לחלופות (פרק 13 מכסה וריאנט scoped למסלול) רק כשיש לך סיבה ספציפית.

## העברת המשימות של Compass לתוך `TaskStore`

ערוך את `src/app/task-store.ts`:

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

שלושה דפוסים שכדאי לתת להם שם:

- **סיגנל פרטי לכתיבה, תצוגת readonly ציבורית.** `_tasks` הוא פרטי וניתן לשינוי; `tasks` הוא הסיגנל הציבורי, לקריאה בלבד שצרכנים רואים. זה מונע ממקוראים לעשות `this.store.tasks.set(...)` ולעקוף את ה-API.
- **התנהגות על פני נתונים.** השירות חושף מתודות שמתארות *כוונה* — add, toggle, remove, clearCompleted. צרכנים לא יודעים איך משימות מאוחסנות, רק מה הם יכולים לעשות איתן.
- **מצב נגזר computed.** `remaining` ו-`done` חיים כאן, לא בקומפוננטות. כל קומפוננטה יכולה לקרוא אותם; כשמשימות משתנות, כל הקוראים מתעדכנים.

## הזרקת השירות לקומפוננטה

שתי צורות של הזרקה עובדות ב-Angular מודרנית. הפונקציה `inject()` היא הצורה החדשה יותר, המועדפת; הזרקת קונסטרוקטור היא הצורה הישנה יותר, שעדיין נתמכת. אנחנו משתמשים ב-`inject()` לרוחב הספר.

ערוך את `src/app/task-list/task-list.ts`:

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

הקומפוננטה עכשיו בעצם מתרגמת בין ה-DOM לבין השירות. כל המצב והלוגיקה שלה עברו ל-`TaskStore`. אם נרצה את אותם הנתונים בקומפוננטה אחרת — סרגל צד שמראה `remaining`, נגיד — אנחנו פשוט מזריקים `TaskStore` גם שם וקוראים `store.remaining`. אין מה לחבר דרך העץ.

התבנית לא צריכה להשתנות; `tasks` ו-`remaining` הם עדיין סיגנלים עם אותו ממשק.

שמור. האפליקציה מתנהגת באופן זהה. המשימות עכשיו חיות מחוץ לקומפוננטה, וקומפוננטות אחרות היו יכולות לשתף אותן אילו היו קיימות.

## הפונקציה `inject()`

`inject(Class)` מחזירה מופע של `Class` מה-injector הנוכחי. אתה יכול לקרוא לה:

- באתחול שדה או בקונסטרוקטור של קומפוננטה (כמו למעלה).
- באתחול שדה או בקונסטרוקטור של שירות.
- בתוך פונקציות שנקראות מההקשרים האלה, בטרנזיטיביות.

אתה לא יכול לקרוא ל-`inject()` מפונקציה אקראית שלא בהקשר DI. Angular זורקת שגיאת זמן ריצה. אם אתה צריך להזריק מחוץ להקשר טבעי, עטוף את הקריאה ב-`runInInjectionContext(injector, () => { ... })`, אבל זה נדיר בקוד יישום — תיתקל בזה אולי פעם בשנה.

ל-`inject()` יש גם צורות גנריות לאופציונליות ולמקרים של multi-token:

```ts
private optionalThing = inject(TokenClass, { optional: true });  // עשוי להיות null
private allOfThem = inject(TokenClass, { self: true });          // רק ה-injector הזה, לא הורים
```

לא נצטרך את אלה זמן מה. `inject(Something)` רגיל מכסה 95% מהשימושים.

## Providers: איך שירותים נכנסים ל-injector

`providedIn: 'root'` היא דרך אחת לרשום שירות. יש אחרות, ותפגוש אותן אחת אחת.

### Providers ברמת האפליקציה דרך `provideX(...)`

חלק מהשירותים מוגדרים עם נתונים; אתה לא יכול פשוט לרשום אותם עם דקורטור. הקונבנציה של Angular היא פונקציית `provide<Feature>(config)` שאתה מציב ב-`providers` ב-`app.config.ts`:

```ts
export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(),
    provideAnimations(),
  ],
};
```

`provideRouter`, `provideHttpClient`, וחבריהם הם איך שהפיצ'רים ה-opt-in של Angular מגיעים לאפליקציה שלך. כל פונקציה מחזירה סט של רישומי provider; Angular קוראת אותם ב-bootstrap.

### Providers ברמת הקומפוננטה

קומפוננטה יכולה לרשום שירות scoped לעצמה ולילדיה:

```ts
@Component({
  selector: 'app-editor',
  providers: [EditorState],
})
export class Editor { }
```

עכשיו כל התייחסות ל-`EditorState` *בתוך* `Editor` (ב-`Editor` עצמו ובכל קומפוננטת ילד) פותרת לאותו מופע; התייחסות ל-`EditorState` *מחוץ* ל-`Editor` פותרת למופע אחר (או נכשלת אם אין provider שורשי).

זה שימושי למצב שהוא מקומי למסך: מצב שלב של אשף, טיוטת טופס של מודאל, בחירות מסנן של עמוד. נשתמש בזה בפרק 13.

### Providers של ערכים ו-factory

לפעמים מה שאתה רוצה להזריק הוא לא מחלקה, אלא ערך או תוצאת פונקציה. ל-Angular יש תחביר גם לאלה:

```ts
providers: [
  { provide: 'API_BASE_URL', useValue: 'https://api.compass.example' },
  { provide: TaskLoader, useFactory: () => new TaskLoader(navigator.onLine) },
]
```

`InjectionToken<T>` היא הדרך הבטוחה מבחינת טיפוסים לזהות provider שאינו מחלקה:

```ts
import { InjectionToken } from '@angular/core';

export const API_BASE_URL = new InjectionToken<string>('API_BASE_URL');

// providers:
{ provide: API_BASE_URL, useValue: 'https://api.compass.example' }

// הזרקה:
private apiUrl = inject(API_BASE_URL);
```

תראה `InjectionToken` בקוד של Angular עצמה ובספריות. בקוד יישום, מחלקות רגילות עם `providedIn: 'root'` מכסות את רוב הצרכים.

## Injectors היררכיים

ה-injectors של Angular מרכיבים עץ שעוקב אחר עץ הקומפוננטות. כשאתה `inject(X)` בקומפוננטה, Angular הולכת *למעלה* מה-injector של הקומפוננטה הזאת ומחפשת provider ל-`X`. היא משתמשת בראשון שהיא מוצאת.

זו הסיבה ש-`providers: [EditorState]` ברמת הקומפוננטה נותן לכל צאצא מופע משותף, בעוד שאותו קוד במערך `providers` של קומפוננטה אחות נותן לאחות מופע שונה. החיפוש מוצא את ה-provider הקרוב ביותר.

לעתים רחוקות תחשוב על זה במפורש. זה חשוב כש:

- יש לך שירות שאתה רוצה scoped לאזור פיצ'ר ספציפי (אשף, מודאל), לא לכל האפליקציה.
- אתה צריך לעקוף שירות בבדיקות (פרק 17).
- אתה רוצה שני מופעים של אותה מחלקת שירות לשתי מטרות שונות.

לכל השאר, `providedIn: 'root'` ושכח מזה.

## תלויות מעגליות

שני שירותים שמזריקים זה את זה יוצרים מעגל. Angular מסרבת לבנות אותם וזורקת בזמן ריצה. אם אתה נתקל בזה, זה בדרך כלל אומר שיש לשירותים בעיית עיצוב: הם צריכים להתמזג, או שאחד צריך להחזיק את השני אבל לא להיפך, או שהמצב המשותף צריך להיות מחולץ לשירות שלישי ששניהם תלויים בו.

יש מעקף — הזרקת `Injector` וחיפוש עצל — אבל אתה לא צריך אותו. כשאתה מרגיש את המשיכה אליו, קח את זה כסימן לעצב מחדש.

## תועלת בבדיקות, בתצוגה מקדימה

כי הכל שקומפוננטה משתמשת בו נכנס דרך DI, בדיקות יכולות *להחליף* את התלויות האלה:

```ts
TestBed.configureTestingModule({
  providers: [
    { provide: TaskStore, useValue: fakeStore },
  ],
});
```

ה-`inject(TaskStore)` של הקומפוננטה עכשיו מחזיר `fakeStore`. אין monkey-patching, אין ייבואים להסיט. פרק 17 פורק את זה בפירוט; לעת עתה, דע שהסיבה שבדיקות Compass שלך יהיו קלות מאוחר יותר היא כי עיצבת אותו סביב DI עכשיו.

## מה בא הלאה

פרק 10 מחבר את `TaskStore` לבקאנד HTTP אמיתי. נציג את `HttpClient` של Angular, נכתוב פונקציות לשלוף, ליצור, לעדכן, ולמחוק משימות, ונחבר אותן לחנות. עד סוף פרק 10, ריענון הדפדפן ישמור את המשימות שלך — כי הן חיות בשרת, לא בזיכרון.

### תרגילים

1. צור קומפוננטה שנייה `TaskCountBadge` שמראה רק את הספירה הנותרת כגלולה קטנה. הזרק את `TaskStore` בתוכה ורנדר `{{ store.remaining() }}`. הצב אותה ליד הכותרת ב-`TaskList`. שים לב ששום נתונים לא זורמים דרך props — שתי הקומפוננטות חולקות מצב דרך השירות.

2. הוסף שירות `HabitStore` שנבנה באותה דרך כמו `TaskStore`. הוא צריך להחזיק סיגנל של הרגלים (המצא `interface Habit`), לחשוף `habits` לקריאה בלבד, ולספק `add`, `remove`, ו-`check`. אל תחבר אותו עדיין לאף קומפוננטה; רק תוודא שהוא מדור.

3. רשום את `TaskStore` ברמת הקומפוננטה במקום `providedIn: 'root'`. מה נשבר? החזר את זה, וחשוב למה: איזה מאפיין של מצב משותף תלוי איפה השירות רשום?
