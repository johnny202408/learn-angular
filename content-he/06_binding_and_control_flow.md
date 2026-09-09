# פרק 6. קישור נתונים ובקרת הזרימה החדשה

תבניות הן איך ש-Angular מתארת ממשק משתמש. הן HTML בתוספת סט קטן של הרחבות: אינטרפולציות להצגת נתונים, קישורים לחיבור נתונים ל-attributes ולאירועים, ותחביר בלוקים לרנדור רשימות ותנאים. הפרק הזה מכסה כל הרחבה שתשתמש בה יומיומית. עד הסוף, Compass יאפשר לך ללחוץ על משימה כדי להעביר אותה בין בוצע ולא בוצע.

שמור על מצב Compass מפרק 5. נוסיף ל-`task-list.ts` ול-`task-list.html` לאורך הפרק.

## אינטרפולציה: הכנסת ערכים לדף

פגשת את `{{ }}` בפרק 5. הוא מעריך ביטוי TypeScript מול השדות של הקומפוננטה ומכניס את התוצאה כטקסט.

```html
<h1>{{ heading }}</h1>
<p>You have {{ tasks.length }} tasks.</p>
<p>Active: {{ tasks.filter(t => !t.done).length }}</p>
```

כל מה שאתה שם בין הסוגריים הכפולים הוא ביטוי, לא הצהרה. משמעות הדבר:

- אתה יכול לקרוא למתודות ולהשתמש באופרטורים: `{{ user.firstName + ' ' + user.lastName }}`.
- אתה לא יכול להקצות, לזרוק, או להשתמש ב-`new`. `{{ x = 5 }}` לא ידור כביטוי תבנית.
- הביטוי חייב להיות *נטול תופעות לוואי*, אחרת Angular תקרא לו מספר פעמים בשנייה והאפליקציה תתנהג לא כשורה.

אינטרפולציה תמיד מייצרת טקסט. כדי להקשר ל-*attributes* או ל-*properties* של אלמנט, תשתמש באחת מצורות הקישור למטה.

## Property binding: `[prop]="expression"`

Property binding מגדיר את ה-*property* של אלמנט HTML (לא את ה-attribute — אלה שונים, עוד על זה בקרוב) לערך של ביטוי.

```html
<img [src]="user.avatarUrl" [alt]="user.name" />
<input [value]="task.title" [disabled]="task.done" />
<a [href]="'/tasks/' + task.id">Details</a>
```

הסוגריים המרובעים משמאל מציינים את ה-property. הגרשיים הכפולים מימין מחזיקים ביטוי TypeScript שמוערך בהקשר של הקומפוננטה.

### Property לעומת attribute

ל-HTML יש גם attributes (מה שאתה כותב במקור) וגם properties (מה שהאובייקט של ה-DOM בעצם מחזיק). לרוב האלמנטים הם מיושרים, אבל לא תמיד. `<input value="hello">` מגדיר את ה-attribute *ההתחלתי*; לאלמנט ה-DOM הרץ יש `.value` property שמשתנה כשהמשתמש מקליד. Property binding כותב ל-property.

במקרים הנדירים שאתה באמת צריך להגדיר attribute (בדרך כלל עבור ARIA), ל-Angular יש תחביר מיוחד:

```html
<button [attr.aria-label]="'Delete task ' + task.title">×</button>
```

`[attr.name]` מגדיר את ה-attribute של HTML בשם `name`. אם Angular אי פעם נותנת לך שגיאה של "no such property" על אלמנט, זה לעתים קרובות התיקון.

### קיצורי class ו-style

שתי צורות מיוחדות של property binding כל כך נפוצות שהן מקבלות תחביר קצר:

```html
<li [class.done]="task.done" [class.overdue]="isOverdue(task)">
<p [style.color]="task.done ? '#999' : 'inherit'">{{ task.title }}</p>
```

`[class.name]` מעביר את ה-class על סמך האמת של הביטוי. `[style.property]` מגדיר את property הסגנון inline. שתי הצורות מקבלות מספר ערכים — אתה יכול להחזיק גם `[class.done]` וגם `[class.overdue]` על אותו אלמנט.

לוגיקה יותר מורכבת של class או style, קשור אובייקט או מערך:

```html
<li [class]="{ done: task.done, overdue: isOverdue(task) }">
<li [class]="cssClasses()">
```

## Event binding: `(event)="handler(...)"`

Event bindings מריצים מתודה של קומפוננטה כשאירוע DOM נורה.

```html
<button (click)="markDone(task)">Done</button>
<input (input)="onSearch($event)" />
<form (submit)="save()">…</form>
```

הסוגריים משמאל מציינים את האירוע (כל אירוע DOM: `click`, `input`, `focus`, `keydown`, כל דבר). הצד הימני הוא *הצהרה* — זה המקום היחיד בתבנית שאתה יכול לקרוא למתודה לתופעת הלוואי שלה. `$event` בתוך ההצהרה מתייחס לאובייקט האירוע (אותו אובייקט שהיית מקבל ב-listener JavaScript רגיל).

בואו נשתמש בזה ב-Compass. פתח את `task-list.ts` והוסף מתודה:

```ts
export class TaskList {
  tasks: Task[] = [ /* ... */ ];

  toggle(task: Task): void {
    task.done = !task.done;
  }
}
```

וב-`task-list.html`, חבר את הלחיצה:

```html
<li class="task" [class.done]="task.done" (click)="toggle(task)">
  <span class="title">{{ task.title }}</span>
  @if (task.dueDate) {
    <span class="due">due {{ task.dueDate | date: 'shortDate' }}</span>
  }
</li>
```

שמור. בדפדפן, לחץ על כל משימה. היא אמורה לעבור בין בוצע ולא בוצע, עם הקו החוצה מופיע ונעלם.

שני דברים ששווה לציין:

- מטפל הלחיצה משנה את `task.done` במקום. זה עובד, אבל זה עובד *רק* כי זיהוי השינויים מבוסס zone של Angular בודק מחדש תבניות אחרי כל אירוע DOM. זה שביר: סיגנלים (פרק 7) יגרמו לאותו קוד להיות יותר מפורש ויותר מתנהג היטב.
- כל ה-`<li>` עכשיו לחיץ. זה בסדר לעת עתה אבל פרקטיקת נגישות רעה — יישום ראוי היה משתמש ב-`<button>` או מוסיף טיפול במקלדת. נתקן את זה כשנחזור לנגישות.

## Two-way binding: `[(model)]="value"`

Two-way binding הוא התחביר של Angular לדפוס הנפוץ של "לקשר property פנימה *ולהאזין* לשינויים שיוצאים". השימוש הקנוני הוא inputs של טפסים:

```html
<input [(ngModel)]="task.title" />
```

בקריאה מימין לשמאל, הסוגריים בתוך הסוגריים המרובעים הם המזמון של "בננה בקופסה". התחביר מתרחב ל-property binding על `ngModel` ו-event binding על `ngModelChange`:

```html
<!-- שווה ערך לזה למעלה -->
<input [ngModel]="task.title" (ngModelChange)="task.title = $event" />
```

`ngModel` הוא יישום ספציפי אחד של דפוס ה-two-way. Two-way binding מבוסס סיגנלים, שנשתמש בו ב-Compass, משתמש ב-*model input* — מושג שנפגוש בפרק 8. לעת עתה, דע רק ש-`[(x)]` הוא התחביר של Angular ל-two-way binding, ושהסמנטיקה שלו היא תמיד "property פנימה, event החוצה". אין קסם — זו לא ספריית קישור נתונים — רק חבילה תחבירית.

## בקרת הזרימה החדשה

תבניות צריכות לקבל החלטות ("הראה את זה אם המשתמש מחובר") ולחזור ("רנדר שורה אחת לכל משימה"). התחביר המודרני של Angular לאלה נקרא *בקרת הזרימה החדשה*: `@if`, `@for`, `@switch`, `@empty`, ו-`@let`. הם מחליפים סט ישן יותר של *דירקטיבות מבניות* — `*ngIf`, `*ngFor`, `*ngSwitchCase` — שאתה עדיין תראה בקוד קיים. שניהם עובדים; התחביר החדש הוא ברירת המחדל המומלצת בכל פרויקט שנוצר אחרי אמצע 2024.

### `@if` ו-`@else`

```html
@if (user.loggedIn) {
  <p>Welcome back, {{ user.name }}.</p>
} @else if (user.pending) {
  <p>Confirming your email…</p>
} @else {
  <a routerLink="/login">Sign in</a>
}
```

סוגריים נדרשים סביב הענפים. אתה יכול לקנן חופשית. אין דו-משמעות לגבי איפה ענף מסתיים.

### `@for` ו-`track`

```html
@for (task of tasks; track task.id) {
  <li>{{ task.title }}</li>
}
```

הפסקה `track` נדרשת. היא אומרת ל-Angular איך לזהות כל פריט לרוחב רנדורים. כשהמערך משתנה — אתה מוסיף משימה, מסיר אחת, מסדר מחדש — Angular משתמש ב-`track` כדי להחליט אילו צמתים קיימים של DOM מתאימים לאילו פריטים במערך החדש. `track` נכון פירושו ש-Angular משתמש שוב בצמתי DOM (מהיר); `track` שגוי פירושו ש-Angular יוצר מחדש כל צומת בכל פעם (איטי).

Track לפי מזהה יציב — id של מסד נתונים, מחרוזת ייחודית — כשיש לך אחד. Track לפי אינדקס (`track $index`) רק כמוצא אחרון, ורק כשפריטים ממש חליפיים.

לבלוק `@for` יש משתני הקשר שימושיים אחרים:

```html
@for (task of tasks; track task.id; let i = $index; let first = $first; let last = $last) {
  <li>
    #{{ i + 1 }}: {{ task.title }}
    @if (first) { <span>(first)</span> }
    @if (last) { <span>(last)</span> }
  </li>
}
```

זמינים: `$index`, `$first`, `$last`, `$even`, `$odd`, `$count`.

ובאופן חשוב, בלוק `@empty`:

```html
@for (task of tasks; track task.id) {
  <li>{{ task.title }}</li>
} @empty {
  <li>Nothing to do.</li>
}
```

`@empty` מרנדר כשהמערך ריק. זה מחליף אידיום שהיית כותב עם `@if (tasks.length === 0)` נפרד — יותר נקי, ומאפשר ל-Angular לייעל את המקרה הריק.

### `@switch`, `@case`, `@default`

לשיגור רב-ענפי על ערך יחיד:

```html
@switch (task.status) {
  @case ('todo') { <span class="badge todo">To do</span> }
  @case ('doing') { <span class="badge doing">In progress</span> }
  @case ('done') { <span class="badge done">Done</span> }
  @default { <span class="badge">?</span> }
}
```

אתה יכול לקנן `@switch` בתוך `@for`, `@if` בתוך `@switch`, וכן הלאה. אין הגבלות.

### `@let`

`@let` קושר משתנה מקומי בתוך תבנית כדי שתוכל להשתמש שוב בחישוב:

```html
@let activeCount = tasks.filter(t => !t.done).length;
@let hasActive = activeCount > 0;

@if (hasActive) {
  <p>{{ activeCount }} tasks remaining.</p>
} @else {
  <p>All done for today.</p>
}
```

שני דברים לדעת: קשרי `@let` הם scoped לבלוק שמסביב; והביטוי מוערך מחדש כשה-inputs משתנים, כך שהקישור נשאר טרי.

## פייפים: הפוך במקום

כבר השתמשת בפייפ: `{{ task.dueDate | date: 'shortDate' }}`. *פייפ* הוא פונקציה שאתה יכול להחיל בתוך ביטוי תבנית, באמצעות `|`. תפקידו הוא עיצוב חד-כיווני וללא תופעות לוואי.

פייפים מובנים ששווים לדעת:

```html
{{ task.title | uppercase }}
{{ task.title | lowercase }}
{{ task.title | titlecase }}
{{ task.createdAt | date: 'medium' }}
{{ percentage | percent: '1.0-2' }}
{{ price | currency: 'USD' }}
{{ someObject | json }}       <!-- נהדר לדיבוג -->
{{ items | slice: 0 : 5 }}
```

פייפים יכולים להשתרשר:

```html
{{ task.title | slice: 0 : 40 | titlecase }}
```

תכתוב פייפים משלך בפרק 15. עד אז, המובנים מכסים את רוב הצרכים.

## קישורי attribute שתצטרך

מעבר ל-`class` ו-`style`, כמה קישורי attribute מגיעים לעתים קרובות:

```html
<button [disabled]="loading">Save</button>
<input [placeholder]="hint" [autofocus]="isNew" />
<a [href]="url" [target]="external ? '_blank' : '_self'">Link</a>
<img [src]="avatarUrl" [width]="size" [height]="size" [alt]="user.name" />
```

לרוב ה-attributes של HTML יש property מתאים, ו-Angular חכם מספיק כדי לקשור ל-property. כשלא (המקרה של aria-* למעלה), השתמש ב-`[attr.name]`.

## הכל יחד: input "הוסף משימה"

בואו נוסיף טופס קטן שמוסיף משימה לרשימה. ערוך את `task-list.ts`:

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
  tasks: Task[] = [ /* ... שלושת המשימות ההתחלתיות מפרק 5 ... */ ];

  draft = '';

  toggle(task: Task): void {
    task.done = !task.done;
  }

  add(): void {
    const title = this.draft.trim();
    if (title === '') return;
    this.tasks = [
      ...this.tasks,
      {
        id: crypto.randomUUID(),
        title,
        done: false,
        createdAt: new Date().toISOString(),
        dueDate: null,
        tags: [],
      },
    ];
    this.draft = '';
  }
}
```

שני פרטים שכדאי לתת להם שם:

- `this.tasks = [...this.tasks, newTask]` יוצר *מערך חדש* במקום לשנות את הישן. ב-Angular מבוסס-סיגנלים (פרק 7), הדפוס הזה נדרש; כאן הוא אופציונלי אבל הרגל טוב לבנות.
- `crypto.randomUUID()` הוא מובנה של דפדפן שמייצר id טרי. באפליקציות אמיתיות ה-id מגיע לעתים קרובות מהשרת; לעת עתה זה מספיק.

וב-`task-list.html`, הוסף טופס בראש:

```html
<h1>Tasks</h1>

<form (submit)="add(); $event.preventDefault()">
  <input
    type="text"
    placeholder="What needs doing?"
    [value]="draft"
    (input)="draft = $any($event.target).value" />
  <button type="submit" [disabled]="draft.trim() === ''">Add</button>
</form>

<ul class="task-list">
  @for (task of tasks; track task.id) {
    <li class="task" [class.done]="task.done" (click)="toggle(task)">
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

שמור. הקלד שם של משימה. לחץ על Add או תלחץ Enter. היא מופיעה בסוף הרשימה, מנוקה מה-input, והכפתור מושבת מחדש עד שתקליד שוב.

שני דברים לשים לב לגבי הטופס:

- `(submit)="add(); $event.preventDefault()"` מטפל בהגשת הטופס ועוצר את הדפדפן מטעינה מחדש של הדף. `$event.preventDefault()` היא אותה קריאה שהיית כותב ב-JavaScript רגיל.
- `(input)="draft = $any($event.target).value"` הוא two-way binding *ידני*. הוא קורא את ה-`value` של ה-input בכל הקלדה ומעתיק אותו ל-`draft`. בפרק 12 נחליף את זה בטפסים ריאקטיביים ראויים, ובפרק 8 תפגוש את `model()` — גרסה טובה עוד יותר. לעת עתה, נעשה את זה ידנית.

ה-`$any(...)` הוא מעקף: ל-`$event.target` יש טיפוס `EventTarget | null`, שלא יודע על property `.value`. `$any` אומר לבודק התבנית "סמוך עליי, אל תתלונן". במתודת קומפוננטה עם handler מוקלד כראוי, נשתמש בהמרת TypeScript ממשית; בביטוי תבנית, `$any` הוא פתח המילוט.

## מה אתה לא צריך לעשות בתבניות

תבניות צריכות להיות תיאורים דקלרטיביים של מה לרנדר בהינתן נתונים כלשהם. יש כמה דברים ש*עובדים* בתבניות אבל אתה לא צריך לעשות:

- **ביטויים ארוכים.** כל דבר יותר מורכב מ-ternary קטן או קריאת מתודה שייך למחלקת הקומפוננטה. תבניות מלאות בשרשראות `?:` וקריאות מתודה מקוננות הופכות לחפצים לקריאה בלבד.
- **קריאות מתודה שעושות עבודה אמיתית.** כל קישור מוערך מספר פעמים ככל שהאפליקציה רצה. אם תבנית אומרת `{{ expensiveComputation(item) }}`, הקריאה הזאת קורה בכל זיהוי שינויים. השתמש בסיגנל computed (פרק 7) או העבר את העבודה למחלקה.
- **שינויים.** שום ביטוי תבנית לא צריך לשנות מצב. הצהרות של אירועים (`(click)="..."`) יכולות, אבל אינטרפולציות וקישורי property חייבים להיות קריאות טהורות.

עקיבה אחר הכללים האלה גורמת לתבניות להיות מהירות, צפויות, וניתנות לדיבוג. שבור אותם, ותבלה שעות אחר צהריים תוהה למה משהו מרנדר מחדש ארבעים פעם בשנייה.

## מה בא הלאה

פרק 7 מציג סיגנלים — פרימיטיב המצב הריאקטיבי המודרני של Angular. נשכתב את שדה `tasks` של Compass כסיגנל, והאפליקציה תתנהג אותו הדבר אבל מסיבות אחרות לגמרי. מתחת למכסה נעבור מ"Angular בודקת הכל אחרי כל אירוע" ל"Angular מעדכנת בדיוק את החלקים של המסך שהסיגנלים שלהם השתנו".

### תרגילים

1. הוסף כפתור "Clear completed" מעל הרשימה שמסיר כל משימה שבוצעה. חבר אותו עם event binding; אל תשנה את המערך, ייצר חדש עם `filter`. הכפתור צריך להיות מושבת כשאין מה לנקות.

2. הצג ספירה מתחת לרשימה: "3 tasks, 1 done, 2 remaining." השתמש ב-`@let` כדי לחשב את הספירות פעם אחת, ובאינטרפולציה כדי להציג אותן.

3. ה-`<li>` הלחיץ הוא נגישות רעה. העבר את מטפל הלחיצה לאלמנט `<button>` פנימי, והשתמש ב-CSS כדי לגרום לכפתור להתאים ויזואלית לשורה. בונוס: הוסף קישור `(keydown.enter)` לכפתור כדי שלחיצה על Enter גם תעביר.
