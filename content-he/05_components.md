# פרק 5. קומפוננטות: האטום של אפליקציית Angular

הקמנו את הסדנה; עכשיו נתחיל לבנות. זה הפרק הראשון שבו אתה כותב קוד Angular אמיתי. עד סוף הפרק תמחק את התבנית ההתחלתית של ה-CLI, תחליף אותה בקומפוננטה משלך, ותציג בדפדפן רשימה של משימות מקודדות. זה הישג קטן בפני עצמו, וזה גם הרגע שבו הצורה של אפליקציית Angular מתבררת.

השאר את `ng serve` רץ במסוף אחד, ואת העורך שלך פתוח על תיקיית `compass`. כל בלוק קוד בפרק הזה נועד להיות מוקלד ונצפה.

## מהי קומפוננטה, בשנית

בפרק 1 תיארתי קומפוננטה כ*פיסה עצמאית של המסך*: קצת HTML, קצת CSS, וקצת התנהגות, ארוזים יחד. עכשיו כשיש לך פרויקט בדיסק שלך, אנחנו יכולים להיות יותר קונקרטיים. קומפוננטה היא:

- **מחלקת TypeScript** שמחזיקה את המצב של הקומפוננטה (שדות) ואת ההתנהגות (מתודות).
- **מקושטת ב-`@Component`** — פיסת מטא-דאטה שאומרת ל-Angular "המחלקה הזאת היא קומפוננטה, והנה הסלקטור והתבנית שלה".
- **מקושרת לתבנית**, שהיא HTML מוגדל עם תחביר הקישור של Angular.
- **מקושרת אופציונלית לסגנונות**, scoped כך שלא ידלפו לשאר האפליקציה.
- **בשימוש בתבנית של קומפוננטה אחרת לפי שם**, דרך הסלקטור שלה.

הנקודה האחרונה היא המנגנון שדרכו נוצר *עץ* קומפוננטות. הקומפוננטה השורשית של Compass (`App`) תכלול בסופו של דבר `<app-task-list>` בתבנית שלה. ה-`<app-task-list>` הזה הוא קומפוננטה נוספת שאנחנו עומדים לכתוב. בתוך `<app-task-list>` יהיו מופעים רבים של `<app-task-row>`, אחד למשימה. כל אלמנט שמתחיל ב-`app-` בתבניות שלך הוא קומפוננטה שהגדרת; כל אלמנט שלא (כמו `<div>` או `<button>`) הוא HTML רגיל.

## הדקורטור `@Component`, שדה אחרי שדה

פתח את `src/app/app.ts` (או `app.component.ts`; שם הקובץ תלוי בגרסת ה-CLI, וברירות המחדל של ה-CLI השתנו). הוא נראה בערך כך:

```ts
import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  protected readonly title = signal('compass');
}
```

בואו נצעד דרך שדות ה-`@Component` בזה אחר זה.

**`selector`** הוא שם התג HTML שמייצג את הקומפוננטה הזאת. `'app-root'` פירושו שהקומפוננטה הזאת מופיעה כל מקום ש-`<app-root>` כתוב. סלקטורים הם איך שקומפוננטות מוצאות זו את זו; הם גם איך שהעולם החיצוני (במקרה הזה, `index.html`) יכול להשליט את האפליקציה שלך לתוך דף. הקונבנציה של Angular היא קידומת קצרה ספציפית לאפליקציה (`app-` כאן) ואחריה תפקיד הקומפוננטה. תקרא לקומפוננטות בשמות כמו `<app-task-row>`, `<app-add-task-form>`, `<app-habit-badge>`.

למה הקידומת? כדי למנוע התנגשויות עם אלמנטים אמיתיים של HTML ועם קומפוננטות של צד שלישי. תג כמו `<button>` הוא אלמנט HTML native; תג כמו `<mat-button>` הוא מ-Angular Material; תג כמו `<app-button>` הוא שלך. הקידומת שומרת אותם ישרים.

**`imports`** היא רשימה של קומפוננטות, דירקטיבות, ופייפים אחרים שהתבנית של הקומפוננטה הזאת משתמשת בהם. ב-Angular מודרנית, כל קומפוננטה עצמאית מכריזה על התלויות שלה במפורש. אם התבנית שלך מכילה `<router-outlet>`, אתה חייב לייבא `RouterOutlet`; אם היא מכילה `<app-task-row>`, אתה חייב לייבא `TaskRow`. זה אחד הדברים שמפתיע חדשים ("אני באמת צריך לפרט הכל?") ואחר כך מרוויח את מקומו בשקט ("העברתי את הקומפוננטה הזאת לאפליקציה אחרת והיא עדיין עובדת").

**`templateUrl`** מצביע על קובץ ה-HTML שהקומפוננטה הזאת מרנדרת. לחלופין אתה יכול להשתמש ב-**`template`**, שמקבל מחרוזת inline:

```ts
@Component({
  selector: 'app-hello',
  template: `<h1>Hello.</h1>`,
})
export class Hello {}
```

תבניות inline נוחות לקומפוננטות זעירות (מתחת לכ-10 שורות). כל דבר גדול יותר שייך לקובץ נפרד. הספר משתמש בשניהם, ומעדיף קבצים נפרדים לקומפוננטות אמיתיות ו-inline לשורות בודדות.

**`styleUrl`** (או `styles`, או `styleUrls`) מצביע על ה-CSS ה-scoped של הקומפוננטה. הכל בקובץ חל רק בתוך מופעים של הקומפוננטה הזאת — class בשם `.title` כאן לא יתנגש עם class בשם `.title` במקום אחר באפליקציה. זה נעשה דרך *view encapsulation*, ש-Angular מיישמת על ידי הוספת attribute ייחודי לכל אלמנט שהקומפוננטה מרנדרת ושכתוב ה-CSS שלך לכוון ל-attribute הזה. אתה לא צריך לחשוב על המנגנון; אתה רק צריך לדעת ש-CSS שאתה כותב בקומפוננטה נשאר בתוך הקומפוננטה.

## בניית הקומפוננטה האמיתית הראשונה של Compass

בואו נחליף את התחלת ה-CLI במשהו שאנחנו הבעלים שלו. נבנה קומפוננטה `TaskList` שמראה רשימה מקודדת של משימות. בפרקים מאוחרים נחליף את הנתונים המקודדים בסיגנלים, אז בשירות, אז ב-HTTP.

מתיקיית `compass` שלך:

```bash
ng generate component task-list
```

זה יוצר `src/app/task-list/` שמכיל:

```
task-list/
├── task-list.ts        (או task-list.component.ts)
├── task-list.html
├── task-list.css
└── task-list.spec.ts
```

פתח את `task-list.ts`:

```ts
import { Component } from '@angular/core';

@Component({
  selector: 'app-task-list',
  imports: [],
  templateUrl: './task-list.html',
  styleUrl: './task-list.css',
})
export class TaskList {}
```

נתן לקומפוננטה הזאת *טיפוס* למשימות ורשימה מקודדת. קודם, בואו נשים את הטיפוס בקובץ משלו כדי שנוכל לשתף אותו מאוחר יותר. יצור `src/app/task.ts`:

```ts
export interface Task {
  id: string;
  title: string;
  done: boolean;
  createdAt: string;
  dueDate: string | null;
  tags: string[];
}
```

עכשיו ערוך את `task-list.ts`:

```ts
import { Component } from '@angular/core';
import { Task } from '../task';

@Component({
  selector: 'app-task-list',
  imports: [],
  templateUrl: './task-list.html',
  styleUrl: './task-list.css',
})
export class TaskList {
  tasks: Task[] = [
    {
      id: 't1',
      title: 'Buy milk',
      done: false,
      createdAt: '2026-01-15T09:00:00Z',
      dueDate: null,
      tags: ['home'],
    },
    {
      id: 't2',
      title: 'Write chapter 5',
      done: true,
      createdAt: '2026-01-14T18:30:00Z',
      dueDate: '2026-01-16T00:00:00Z',
      tags: ['work'],
    },
    {
      id: 't3',
      title: 'Call the plumber',
      done: false,
      createdAt: '2026-01-15T11:00:00Z',
      dueDate: '2026-01-18T00:00:00Z',
      tags: ['home', 'urgent'],
    },
  ];
}
```

עכשיו ערוך את `task-list.html` כדי להציג אותם. פרק 6 מכסה את התחביר לעומק; לעת עתה, העתק אותו וצפה:

```html
<h1>Tasks</h1>
<ul class="task-list">
  @for (task of tasks; track task.id) {
    <li class="task" [class.done]="task.done">
      <span class="title">{{ task.title }}</span>
      @if (task.dueDate) {
        <span class="due">due {{ task.dueDate | date: 'shortDate' }}</span>
      }
    </li>
  } @empty {
    <li class="empty">Nothing to do. Nice.</li>
  }
</ul>
```

ותן לו קצת עיצוב scoped ב-`task-list.css`:

```css
:host {
  display: block;
  max-width: 480px;
  margin: 2em auto;
  font-family: system-ui, sans-serif;
}

h1 {
  font-size: 1.4rem;
  margin: 0 0 1em 0;
}

.task-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.task {
  padding: 12px 14px;
  border-bottom: 1px solid #eee;
  display: flex;
  gap: 12px;
  align-items: center;
}

.task.done .title {
  text-decoration: line-through;
  color: #999;
}

.due {
  margin-left: auto;
  font-size: 0.85rem;
  color: #666;
}

.empty {
  padding: 20px;
  text-align: center;
  color: #999;
  font-style: italic;
}
```

## שימוש בקומפוננטה

שני שינויים נוספים ונוכל לראות אותה בדפדפן.

ראשית, אמור לקומפוננטה השורשית לרנדר `<app-task-list>`. ערוך את `src/app/app.ts`:

```ts
import { Component } from '@angular/core';
import { TaskList } from './task-list/task-list';

@Component({
  selector: 'app-root',
  imports: [TaskList],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {}
```

שני שינויים חשובים: הסרנו את ייבוא `RouterOutlet` (נחזיר אותו בפרק 13), והוספנו את `TaskList` ל-`imports`. כל קומפוננטה שמופיעה בתבנית של הקומפוננטה הזאת חייבת להיות מיובאת.

שנית, ערוך את `src/app/app.html`. מחק את מה שה-CLI שם שם והחלף ב:

```html
<app-task-list></app-task-list>
```

שמור. תסתכל על טאב הדפדפן שלך. אמורה להיות לך כותרת "Tasks" ושלושה פריטים — אחד עם קו חוצה (המושלם) ושניים עם תאריכי יעד.

בדיוק כתבת את הקומפוננטה הראשונה של Angular ורכבת אותה באפליקציה. קח דקה להעריך את זה.

## מה `:host` עושה

בטח שמת לב לפסאודו-קלאס `:host` ב-`task-list.css`. כך גיליון הסגנונות של קומפוננטה מתייחס לאלמנט השורשי של הקומפוננטה עצמה — `<app-task-list>` עצמו, מבחוץ. בתוך קובץ ה-CSS, `:host` הוא ה-wrapper; כל מה שבתוך התבנית של הקומפוננטה הוא תוכן צאצא של `:host`.

ההבחנה חשובה כי Angular מרנדרת כל קומפוננטה לתוך אלמנט משלה. כש-Angular רואה `<app-task-list>` בתבנית של `App`, היא לא מחליפה את התג במרקאפ של רשימת המשימות; היא *מכניסה* את המרקאפ בתוך התג. זה משמר את הגבול של האנקפסולציה ונותן לך מקום לתלות סגנונות כמו `display: block` או `margin` על הקומפוננטה בכללותה.

## מחזור חיים של קומפוננטה, בפסקה אחת

כל קומפוננטה עוברת כמה רגעים בחיים שלה: היא *נבנית* (המחלקה מקבלת מופע), אז *מאותחלת* (Angular חיברה את ה-inputs שלה), ובסופו של דבר *מושמדת* (הקומפוננטה מוסרת מה-DOM, וצריכה לנקות subscriptions). Angular מספקת *hooks* של מחזור חיים — מתודות שאתה יכול להגדיר עם שמות ספציפיים — עבור הרגעים האלה: `ngOnInit`, `ngOnDestroy`, וכמה אחרים. בקוד Angular ישן יותר, אלה היו בכל מקום.

ב-Angular מודרנית, רוב הסיבות שהיית פונה ל-hook של מחזור חיים משורתות טוב יותר על ידי פרימיטיבים אחרים — סיגנלים, `computed`, `effect`, וריאקטיביות מבוססת DI. השימושים הכשרים שנשארים צרים: לעשות הקמה חד-פעמית שצריכה לראות inputs (נדיר — `computed` בדרך כלל טוב יותר), או ניקוי משאבים חיצוניים שלא מנוהלים על ידי Angular (נדיר — `takeUntilDestroyed` בדרך כלל טוב יותר). נפגוש את ה-hooks כראוי כשנצטרך אותם; אל תלך לחפש אותם.

## ידידותי לסיגנלים כברירת מחדל

שים לב שבפרק הזה, `tasks` הוא שדה רגיל על המחלקה — `tasks: Task[] = [...]`. זה עובד: התבנית קוראת אותו ומרנדרת. אבל הוא לא *ריאקטיבי*. אם תוסיף מאוחר יותר כפתור שדוחף משימה חדשה לרשימה, Angular תרנדר מחדש את הרשימה (בזכות זיהוי שינויים מבוסס zone, שהוא המנגנון הקלאסי); אבל ההתנהגות הזאת בדרך החוצה. Angular מודרנית זזה לעבר סיגנלים כפרימיטיב הריאקטיבי, ו-Compass יעשה את המעבר הזה החל מפרק 7.

לעת עתה, שדות רגילים מספיקים. פרק 6 מבלה את זמנו על תחביר התבנית (`@for`, `@if`, `{{ }}`); פרק 7 משכתב את `tasks` כסיגנל. הדפוס של הספר הוא: להציג את הגרסה הרגילה, להרגיש את הגירוד, ללמוד את הגרסה הריאקטיבית, לנשום לרווחה.

## תבניות inline לעומת חיצוניות

שני סגנונות, שניהם בסדר:

```ts
// חיצוני (ברירת מחדל מ-`ng generate`)
@Component({
  selector: 'app-task-list',
  templateUrl: './task-list.html',
  styleUrl: './task-list.css',
})

// Inline
@Component({
  selector: 'app-empty-state',
  template: `
    <div class="empty">
      <p>{{ message }}</p>
    </div>
  `,
  styles: `
    .empty { padding: 20px; text-align: center; }
  `,
})
```

כללי אצבע: תבניות של עד כ-10 שורות של מרקאפ בסדר inline; כל דבר גדול יותר קל יותר לקרוא בקובץ נפרד. אם התבנית ה-inline שלך מתחילה להכיל `@for` ומספר ענפי `@if`, העבר אותה לקובץ `.html` — העורך שלך יודה לך (סימון תחביר, השלמה אוטומטית, הזחה כולם משתפרים).

## View encapsulation, בקצרה

לכל קומפוננטה יש מצב `ViewEncapsulation`. ברירת המחדל היא `Emulated`, שזה מה שתיארנו למעלה — Angular מגבילה את ה-CSS שלך לקומפוננטה על ידי הוספת attributes. `None` משבית את ההגבלה (ה-CSS שלך הופך גלובלי — בדרך כלל לא מה שאתה רוצה). `ShadowDom` משתמש ב-API האמיתי של Shadow DOM של הדפדפן להגבלה, שהוא חזק יותר אבל מגיע עם מוזרויות סביב עיצוב, פונטים, וספריות צד שלישי.

תמיד תשאיר את האנקפסולציה על ברירת המחדל. הפעם היחידה שתשנה אותה היא אם היית בונה ספריית קומפוננטות וצריך את הבידוד החזק ביותר האפשרי.

## מה בא הלאה

פרק 6 מכסה את כל מה שקרה עכשיו בתבנית. ראית `{{ }}`, `[class.done]`, `@for`, `@if`, `@empty`, ו-`| date: 'shortDate'`. בפרק 6 נסתכל על כל אחד מהם כראוי, יחד עם property bindings, event bindings, ו-two-way bindings. עד סוף פרק 6, Compass יגיב ללחיצות — תוכל להעביר משימות בין בוצע ולא בוצע.

### תרגילים

1. הוסף משימה רביעית למערך המקודד — אחת שהיא `done: true` ויש לה `dueDate` בעבר. שמור וודא שהיא מרנדרת עם הקו החוצה ותאריך הפיגור שלה. אל תשתמש בשום תכונת Angular מלבד אלה שהפרק הזה כיסה.

2. שנה את ה-`selector` ב-`task-list.ts` מ-`'app-task-list'` ל-`'compass-task-list'`. שמור ורענן את הדפדפן. מה נשבר? תקן את זה. שים לב שסלקטורים הם חוזה קטן בין שני קבצים (הקומפוננטה והמשתמש בה).

3. הרץ `ng generate component habit-badge`. קרא את ארבעת הקבצים שה-CLI מייצר. אילו מהם הם מידע חדש אחרי הפרק הזה? אילו הם boilerplate שאתה יכול עכשיו לכתוב מהזיכרון?
