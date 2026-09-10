# פרק 13. ניתוב: עמודים, פרמטרים, guards, טעינה עצלה

Compass היה מסך יחיד. ליישומים אמיתיים יש כמה — בית, הגדרות, תצוגת פירוט, לפעמים עשרות. ה-*ראוטר* של Angular הוא החלק שהופך URL אחד לעץ קומפוננטות אחד, מעדכן אותו כשהמשתמש מנווט, ומאפשר לחלקים של האפליקציה להגיב לאיזה URL פעיל.

הפרק הזה הופך את Compass לאפליקציה רב-עמודית. נוסיף מסלול בית שמראה את המשימות של היום, מסלול סטטיסטיקות שיארח את התרשימים שלנו בפרק 16, ומסלול פירוט שמראה משימה יחידה עם טופס העריכה שבנינו בפרק 12. תוך כדי כך אנחנו מכסים פרמטרי מסלול, guards, resolvers, וטעינה עצלה.

## שלושת החלקים הנעים

לניתוב ב-Angular יש שלושה מושגים שאתה פוגש בכל מקום.

**הגדרות מסלול** — רשימה של רשומות `{ path, component }` שאומרות לראוטר מה לרנדר עבור כל URL. ראית את הגרסה הריקה ב-`src/app/app.routes.ts`.

**`<router-outlet>`** — placeholder בתבנית שאומר "רנדר כאן את הקומפוננטה של המסלול הפעיל כרגע". כבר היה לך אחד, בקצרה, ב-`App` שנוצר על ידי ה-CLI; הסרנו אותו בפרק 5.

**ניווט** — המשתמש (או הקוד שלך) משנה את ה-URL, והראוטר מתאים אותו להגדרות המסלול, פותר guards כלשהם, ומעדכן את `<router-outlet>` שמראה את הקומפוננטה המושפעת.

## הגדרת המסלולים של Compass

ערוך את `src/app/app.routes.ts`:

```ts
import { Routes } from '@angular/router';
import { Home } from './home/home';
import { Stats } from './stats/stats';
import { TaskDetail } from './task-detail/task-detail';

export const routes: Routes = [
  { path: '', component: Home, title: 'Today · Compass' },
  { path: 'stats', component: Stats, title: 'Stats · Compass' },
  { path: 'task/:id', component: TaskDetail, title: 'Task · Compass' },
  { path: '**', redirectTo: '' },
];
```

ארבעה מסלולים:

- `''` הוא הנתיב הריק — מסלול הבית, התואם `http://localhost:4200/`.
- `'stats'` תואם `/stats`.
- `'task/:id'` תואם `/task/anything`, ולוכד את המקטע אחרי `task/` כ-`id`.
- `'**'` הוא ה-wildcard — כל דבר שלא תואם מפנה חזרה הביתה. תמיד הגדר את זה אחרון; הראוטר צועד ברשימה מלמעלה למטה, ו-`**` קודם היה בולע הכל.

המאפיין `title` מגדיר את `document.title` כשהמסלול מופעל. זו תכונה קטנה שמשפרת איך שטאבים וסימניות נראים בדפדפן.

אנחנו צריכים קומפוננטות `Home`, `Stats`, ו-`TaskDetail`. צור אותן:

```bash
ng generate component home
ng generate component stats
ng generate component task-detail
```

לעת עתה, `Home` הוא איפה ש-`TaskList` חי. העבר את המרקאפ `<app-task-list>` וכל תיאום מ-`App` ל-`Home`.

`src/app/home/home.ts`:

```ts
import { Component } from '@angular/core';
import { TaskList } from '../task-list/task-list';

@Component({
  selector: 'app-home',
  imports: [TaskList],
  template: `<app-task-list />`,
})
export class Home {}
```

`Stats` הוא stub שנעבה בפרק 16:

```ts
@Component({
  selector: 'app-stats',
  template: `<h1>Stats</h1><p>Coming soon.</p>`,
})
export class Stats {}
```

את `TaskDetail` נסתכל עליו בעוד רגע.

## `App` הופך למעטפת

תפקיד הקומפוננטה השורשית עכשיו הוא להחזיק את ה-`<router-outlet>` וכל chrome שסובב כל עמוד — כותרת, footer, סרגל צד. שכתב את `src/app/app.ts`:

```ts
import { Component } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {}
```

`src/app/app.html`:

```html
<header class="app-header">
  <h1 class="brand">Compass</h1>
  <nav>
    <a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: true }">
      Today
    </a>
    <a routerLink="/stats" routerLinkActive="active">Stats</a>
  </nav>
</header>

<main class="app-main">
  <router-outlet />
</main>
```

`routerLink` מרנדר `<a>` עם ה-`href` הנכון, וכשלוחצים עליו, אומר לראוטר לנווט — בלי טעינה מלאה של דף. `routerLinkActive` מוסיף class כשמסלול הקישור פעיל. `{ exact: true }` מונע מ-`/` להיות "פעיל" בכל פעם — אחרת הוא היה מודגש גם עבור `/stats`, כי `/stats` מתחיל ב-`/`.

שמור. רענן. אתה אמור לראות את הכותרת עם שני קישורי nav. לחיצה על "Today" ו-"Stats" מחליפה איזו תצוגה מופיעה מתחת. שים לב שה-URL משתנה, וכפתור "back" של הדפדפן עובד.

## פרמטרי מסלול ו-`:id`

המסלול `task/:id` לוכד מקטע. ב-`TaskDetail`, אנחנו צריכים לקרוא את המקטע הזה.

ל-Angular מודרנית יש דרך יפה במיוחד: **קישור input של קומפוננטה** מהראוטר. הפעל אותו ב-`app.config.ts`:

```ts
import { provideRouter, withComponentInputBinding } from '@angular/router';

// ...providers:
provideRouter(routes, withComponentInputBinding()),
```

עכשיו כל `input()` בקומפוננטה מנותבת מקבל פרמטרי מסלול תואמים כ-input שלו:

```ts
import { Component, inject, input, computed } from '@angular/core';
import { TaskStore } from '../task-store';
import { EditTask } from '../edit-task/edit-task';

@Component({
  selector: 'app-task-detail',
  imports: [EditTask],
  templateUrl: './task-detail.html',
})
export class TaskDetail {
  id = input.required<string>();
  private store = inject(TaskStore);
  task = computed(() => this.store.tasks().find(t => t.id === this.id()));
}
```

והתבנית:

```html
@if (task(); as t) {
  <app-edit-task [task]="t" />
} @else {
  <p>Task not found. <a routerLink="/">Back to today.</a></p>
}
```

`@if (task(); as t)` הוא alias של תבנית — הוא קושר את הערך האמיתי ל-`t` בתוך הבלוק. עכשיו `t` הוא ה-`Task` שנפתר, ו-`EditTask` מקבל משימה אמיתית לעבוד איתה. ה-`computed` מבטיח שאם החנות מתעדכנת, תצוגת הפירוט מתעדכנת גם.

קריאת פרמטרי מסלול דרך `input()` זמינה רק עם `withComponentInputBinding()`. בלעדיו, היית קורא אותם דרך `ActivatedRoute`:

```ts
private route = inject(ActivatedRoute);
id = toSignal(this.route.paramMap.pipe(map(p => p.get('id') ?? '')), { initialValue: '' });
```

שניהם עובדים; קישור input נקי יותר ונותן לך הסקת טיפוסים חינם על קישורים שנוצרו.

## קישור למשימה

ב-`TaskRow`, הוסף קישור:

```html
<a [routerLink]="['/task', task().id]" class="detail-link">Details</a>
```

צורת המערך של `routerLink` בונה את ה-URL ממקטעים. היא מטפלת בקידוד URL בשבילך. העדף אותה על פני `'/task/' + task().id`.

שים לב ש-`TaskRow` צריך עכשיו לייבא `RouterLink` ב-`imports` שלו.

## Query parameters

עבור מצב שצריך להשתקף ב-URL אבל אינו חלק מהתאמת המסלול — מסננים, מיונים, שאילתות חיפוש — השתמש ב-*query parameters*.

קרא אותם באותה דרך שאתה קורא פרמטרי מסלול, באמצעות `queryParamMap` על `ActivatedRoute`:

```ts
private route = inject(ActivatedRoute);
filter = toSignal(
  this.route.queryParamMap.pipe(map(p => p.get('tag') ?? 'all')),
  { initialValue: 'all' }
);
```

כתוב אותם דרך ה-`Router`:

```ts
private router = inject(Router);

setFilter(tag: string): void {
  this.router.navigate([], {
    relativeTo: this.route,
    queryParams: { tag: tag === 'all' ? null : tag },
    queryParamsHandling: 'merge',
  });
}
```

`queryParamsHandling: 'merge'` שומר על query params אחרים. הגדרת ערך ל-`null` מסירה אותו.

ל-query params ב-URL יש שני יתרונות: משתמשים יכולים לשמור במועדפים ולשתף, וכפתור ה-back של הדפדפן הופך משמעותי (כל שינוי מסנן הוא רשומה בהיסטוריה, אם אתה רוצה שהוא יהיה כזה).

## Guards: שערי ניווט

Guard הוא פונקציה שמחליטה אם ניווט מותר. שלושה סוגים עיקריים:

**`canActivate`** — האם המשתמש הזה יכול לבקר במסלול הזה? נמצא בשימוש לאימות.

**`canMatch`** — האם המסלול הזה בכלל צריך להיחשב להתאמה? נמצא בשימוש כדי להסתיר מסלולים לגמרי ממשתמשים שלא צריכים להגיע אליהם. טוב יותר מ-`canActivate` לאימות כי הקוד של המסלול אינו נטען אם `canMatch` מחזיר false.

**`canDeactivate`** — האם המשתמש יכול לצאת מהמסלול הזה? נמצא בשימוש כדי להזהיר על שינויים לא שמורים.

הנה `canMatch` לאזור מאומת:

```ts
// src/app/auth.guard.ts
import { CanMatchFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { AuthStore } from './auth-store';

export const requireAuth: CanMatchFn = () => {
  const auth = inject(AuthStore);
  const router = inject(Router);
  if (auth.isSignedIn()) return true;
  router.navigateByUrl('/login');
  return false;
};
```

צרף אותו ב-`app.routes.ts`:

```ts
{ path: 'stats', component: Stats, canMatch: [requireAuth], title: 'Stats · Compass' },
```

לא נוסיף auth ל-Compass עד פרק 19 (פריסה שוקלת את זה), אבל עכשיו אתה יודע איפה auth guards נכנסים.

## Resolvers: שליפה מקדימה של נתונים

חלק מהמסלולים לא צריכים לרנדר עד שהנתונים שלהם נטענו. *Resolver* הוא פונקציה שרצה לפני שהמסלול מופעל וחוסמת את הניווט עד שהוא מסתיים.

```ts
export const taskResolver: ResolveFn<Task | undefined> = (route) => {
  const store = inject(TaskStore);
  const id = route.paramMap.get('id') ?? '';
  return store.loadOne(id);
};
```

צרף אותו:

```ts
{ path: 'task/:id', component: TaskDetail, resolve: { task: taskResolver } },
```

וקרא את הנתונים שנפתרו בקומפוננטה דרך `ActivatedRoute.data`:

```ts
task = toSignal(this.route.data.pipe(map(d => d['task'] as Task | undefined)), { initialValue: undefined });
```

Resolvers שומרים spinners של טעינה מחוץ לקוד הקומפוננטה שלך — אבל הם גם דוחים את הצביעה הראשונה. השתמש בהם עבור נתונים שאתה לא יכול לרנדר בצורה משמעותית בלעדיהם; אחרת רנדר את המעטפת ותן למצב טעינה למלא.

`TaskDetail` של Compass משתמש בסיגנל של החנות, לא ב-resolver — החנות ההורית כבר טענה משימות, ואנחנו יכולים למצוא את המשימה סינכרונית. Resolvers שימושיים יותר כשהנתונים של דף הפירוט אינם כבר בחנות.

## טעינה עצלה

כל קומפוננטה ב-`imports` בקובץ המסלולים שלך נכללת ב-bundle הראשוני. באפליקציה גדולה, זה מנפח את ההורדה.

טעינה עצלה דוחה את טעינת הקומפוננטה עד שהיא נדרשת:

```ts
{
  path: 'stats',
  loadComponent: () => import('./stats/stats').then(m => m.Stats),
}
```

הראוטר קורא לפונקציית החץ רק כשהמשתמש מנווט ל-`/stats`, מוריד את חתיכת ה-JavaScript שנוצרה, ומרנדר. יש עיכוב של שבריר שנייה בפעם הראשונה, שהוא בדרך כלל מקובל.

עבור אזורי פיצ'ר שלמים, `loadChildren` טוען עצל *סט* של מסלולים:

```ts
{
  path: 'settings',
  loadChildren: () => import('./settings/settings.routes').then(m => m.settingsRoutes),
}
```

קובץ הילד מייצא מערך `Routes` משלו. כל דבר מתחת ל-`/settings/*` מורד יחד.

נמיר את המסלולים `Stats` ו-`TaskDetail` של Compass לטעינה עצלה בפרק 16, ברגע שיש לנו מדידה שמצדיקה זאת.

## Preloading

Chunks עצלים מורידים על פי דרישה, מה שמכניס latency לביקור ראשון. Preloading מוריד אותם ברקע *אחרי* הרנדור הראשוני:

```ts
import { withPreloading, PreloadAllModules } from '@angular/router';

provideRouter(routes, withPreloading(PreloadAllModules)),
```

`PreloadAllModules` היא האפשרות הפשוטה: הורד את כל העצלים אחרי שהאפליקציה צבעה. preloader מותאם אישית יכול להיות חכם יותר (רק לטעון מראש chunks שסביר שייבקרו בהם הבא). לרוב האפליקציות, `PreloadAllModules` היא ברירת מחדל טובה.

## ניווט תוכניתי

אתה מנווט בצורה אימפרטיבית עם ה-`Router`:

```ts
private router = inject(Router);

goHome(): void { this.router.navigate(['/']); }
openTask(id: string): void { this.router.navigate(['/task', id]); }
back(): void { window.history.back(); }
```

`navigate` מחזיר Promise שנפתר כשהניווט מסתיים (או false אם הוא נחסם). `navigateByUrl(url)` מקבל string URL.

לרוב הניווט בתבנית, העדף `[routerLink]` — הוא מרנדר עוגן אמיתי, שטוב יותר לנגישות ולפתיחה בטאב חדש. פנה ל-`router.navigate` כשמנווטים מ-handler שכבר רץ (אחרי שמירת טופס, על אירוע socket, על טיימר).

## `RouterLinkActive` לסימון nav

`routerLinkActive` מוסיף CSS class כשהיעד של הקישור הוא המסלול הפעיל. הוא יכול לקחת רשימת classes:

```html
<a routerLink="/stats" routerLinkActive="active highlighted">Stats</a>
```

כברירת מחדל, קישור פעיל כשה-URL *מתחיל ב*-target שלו. `{ exact: true }` דורש התאמה מדויקת. השתמש ב-exact על קישור הבית (`/`), שאחרת מתאים לכל URL.

## `titleStrategy`: כותרות דינמיות

`title: '...'` סטטי במסלול עובד עבור עמודים שהכותרת שלהם ידועה מראש. עבור "Task: X" שבו X תלוי במשימה, הגדר `TitleStrategy`:

```ts
import { TitleStrategy, RouterStateSnapshot } from '@angular/router';
import { Title } from '@angular/platform-browser';

@Injectable({ providedIn: 'root' })
export class CompassTitleStrategy extends TitleStrategy {
  private title = inject(Title);
  override updateTitle(state: RouterStateSnapshot): void {
    const t = this.buildTitle(state);
    this.title.setTitle(t ? `${t} · Compass` : 'Compass');
  }
}

// providers:
{ provide: TitleStrategy, useClass: CompassTitleStrategy },
```

הכותרות הסטטיות של Compass מספיקות לעת עתה; דע שנקודת ההרחבה קיימת.

## מה בא הלאה

פרק 14 מקדם את `TaskStore` לדפוס כללי למצב מבוסס סיגנלים ומראה מתי לפנות לספריית מצב גדולה יותר (NgRx) שווה. פרק 15 מכסה דירקטיבות ופייפים — הפרימיטיבים להתנהגות ולעיצוב לשימוש חוזר שעדיין לא נגענו בהם. פרק 16 מודד את הביצועים של Compass ומתקן את מה שצריך תיקון.

### תרגילים

1. המר את המסלולים "Stats" ו-"Task detail" לטעינה עצלה. אז הרץ `ng build` ותסתכל בתוך `dist/`. אתה אמור לראות מספר קבצי chunk, אחד לכל מסלול עצל.

2. הוסף guard "canDeactivate" על מסלול פירוט המשימה שמבקש מהמשתמש "יש לך שינויים לא שמורים; לצאת בכל זאת?" כשהוא מנסה לנווט מחוץ לעריכה עם טופס מלוכלך. רמז: פונקציית ה-guard מקבלת את מופע הקומפוננטה כארגומנט הראשון שלה.

3. הוסף query parameter `filter` למסלול הבית, ערכים תקפים `all`, `open`, ו-`done`. רנדר רק את המשימות התואמות. ספק שלושה כפתורים שמעדכנים את ה-query param דרך `router.navigate`, והדגש את הפעיל באמצעות `routerLinkActive` על גרסאות `routerLink` של הכפתורים.
