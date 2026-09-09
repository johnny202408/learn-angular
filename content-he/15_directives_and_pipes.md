# פרק 15. דירקטיבות, פייפים, ו-UI לשימוש חוזר

קומפוננטות הן יחידת השימוש החוזר הגדולה ביותר של Angular. פייפים ודירקטיבות הן הקטנות יותר. *פייפ* הוא פונקציה שאתה יכול לקרוא לה בתוך ביטוי תבנית — קטן, טהור, בצורת טרנספורמציה. *דירקטיבה* היא התנהגות שאתה מצמיד לאלמנט קיים בלי לעטוף אותו בקומפוננטה אחרת. שניהם מאפשרים לך לחלץ חזרתיות בלי להציג תגים חדשים או גבולות קומפוננטה חדשים.

הפרק הזה מכסה בניית שניהם. אנחנו מוסיפים פייפ `TimeAgo` שמרנדר "לפני שעתיים" מ-timestamp; דירקטיבת `Autofocus` שממקדת input בעת רנדור; דירקטיבת `LongPress` שפולטת אירוע אחרי החזקה; ובקצרה, קומפוננטת `EmptyState` משותפת שמשתמשת בהזרקת תוכן. עד הסוף, ל-Compass יש ארגז כלים קטן של פרימיטיבי UI לשימוש חוזר שהשאר של הספר (וכל פיצ'ר עתידי) יכול לפנות אליהם.

## פייפים: טרנספורמציה של תבנית בלבד

Compass משתמש כרגע ב-`| date: 'shortDate'` בכמה מקומות. זה פייפ מובנה. Angular מגיעה עם כמה: `date`, `currency`, `percent`, `slice`, `keyvalue`, `json`, `titlecase`, `lowercase`, `uppercase`, `async`. השתמשת ברובם.

פייפים מותאמים אישית הם עבור טרנספורמציות שאתה מוצא את עצמך חוזר עליהן. הכללים של פייפ טוב:

- **טהור.** בהינתן אותם קלטים, תמיד מחזיר את אותו פלט. אין תופעות לוואי. אין מצב גלובלי.
- **מהיר.** פייפים רצים כל זיהוי שינויים. כל דבר יקר צריך memoization או שיעבור ל-`computed`.
- **קטן.** פייפ עם 200 שורות הוא קומפוננטה או שירות בתחפושת.

### בניית `TimeAgo`

Compass מראה `createdAt` בהעברת עכבר, ואנחנו רוצים שהתצוגה תהיה "just now", "5 minutes ago", "2 hours ago", "yesterday", "3 days ago". חומר פייפ מושלם.

צור אותו:

```bash
ng generate pipe time-ago
```

`src/app/time-ago.pipe.ts`:

```ts
import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ name: 'timeAgo' })
export class TimeAgoPipe implements PipeTransform {
  transform(value: string | Date | number | null | undefined): string {
    if (value === null || value === undefined || value === '') return '';
    const date = value instanceof Date ? value : new Date(value);
    if (isNaN(date.getTime())) return '';

    const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
    if (seconds < 45) return 'just now';
    if (seconds < 90) return 'a minute ago';

    const minutes = Math.floor(seconds / 60);
    if (minutes < 45) return `${minutes} minutes ago`;
    if (minutes < 90) return 'an hour ago';

    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} hours ago`;
    if (hours < 42) return 'yesterday';

    const days = Math.floor(hours / 24);
    if (days < 30) return `${days} days ago`;

    const months = Math.floor(days / 30);
    if (months < 12) return `${months} months ago`;
    return `${Math.floor(months / 12)} years ago`;
  }
}
```

שני כללי דרך:

- **טפל בקלט רע בחן.** `null`, `undefined`, מחרוזות לא תקינות — החזר `''` במקום לזרוק. תבניות לא צריכות להתפוצץ כי ערך עדיין לא נטען.
- **קבל איחוד של טיפוסים סבירים.** צרכנים מעבירים צורות שונות; פייפ שמקבל רק טיפוס אחד גורם לטקסים באתרי הקריאה.

השתמש בו בתבנית:

```html
<span title="{{ task.createdAt | date: 'medium' }}">
  Added {{ task.createdAt | timeAgo }}
</span>
```

כל קומפוננטה שמשתמשת בפייפ בתבנית שלה חייבת לייבא אותו:

```ts
@Component({
  imports: [TimeAgoPipe],
  // ...
})
```

### פייפים עם ארגומנטים

פייפ יכול לקבל ארגומנטים: `{{ value | myPipe: arg1: arg2 }}`. ארגומנטים הופכים לפרמטרים נוספים ל-`transform`:

```ts
@Pipe({ name: 'truncate' })
export class TruncatePipe implements PipeTransform {
  transform(value: string, maxLength: number = 100, ellipsis: string = '…'): string {
    if (!value) return '';
    return value.length <= maxLength ? value : value.slice(0, maxLength - ellipsis.length) + ellipsis;
  }
}
```

השתמש בו: `{{ description | truncate: 80 }}`.

### פייפים וזיהוי שינויים

פייפים נקראים בכל מחזור זיהוי שינויים כברירת מחדל (הם פייפים *טהורים*, ו-Angular שומרת את הפלט שלהם במטמון). Angular קוראת שוב לפייפ רק אם לאחד מהארגומנטים שלו יש התייחסות חדשה. זו הסיבה שאנחנו עושים `[...tasks]` לפני מיון: ההתייחסות החדשה מפעילה הערכה מחדש.

פייפ *לא-טהור* (`@Pipe({ pure: false })`) נקרא בכל זיהוי שינויים בין אם קלטים השתנו ובין אם לא. כמעט תמיד הבחירה הלא נכונה. אם אתה מוצא את עצמך שוקל לא-טהור, שאל למה אתה לא משתמש בסיגנל.

## דירקטיבות attribute: התנהגות על אלמנטים קיימים

דירקטיבת attribute מצמידה התנהגות למה שהיא מוצבת עליו. מקרה השימוש הקלאסי הוא חתיכות קטנות של API אימפרטיבי של דפדפן — focus, tooltip, click-outside, resize observer — שבו עטיפת האלמנט בקומפוננטה אחרת תהיה יותר מדי.

### `Autofocus`

צור:

```bash
ng generate directive autofocus
```

`src/app/autofocus.directive.ts`:

```ts
import { Directive, ElementRef, inject, afterNextRender } from '@angular/core';

@Directive({
  selector: '[appAutofocus]',
})
export class AutofocusDirective {
  private el = inject<ElementRef<HTMLElement>>(ElementRef);

  constructor() {
    afterNextRender(() => this.el.nativeElement.focus());
  }
}
```

השתמש בו בכל תבנית — למשל, על input עריכת המשימה:

```html
<input type="text" formControlName="title" appAutofocus />
```

בכל פעם שהדירקטיבה נוצרת, האלמנט מקבל focus אחרי הרנדור הבא (`afterNextRender` הוא hook מודרני של מחזור חיים שרץ פעם אחת, אחרי ש-DOM התחייב). אין קומפוננטות מעורבות. האלמנט נשאר `<input>` נייטיבי.

שים לב לסלקטור: `[appAutofocus]`. דירקטיבות משתמשות בסלקטורים של attribute, מותאמות בכל מקום שה-attribute מופיע. הקידומת `app` מונעת מהם התנגשות עם attributes קיימים.

### `LongPress`

דירקטיבת `LongPress` שפולטת אירוע אחרי שהמשתמש החזיק את האלמנט למשך סף של זמן.

```ts
import { Directive, ElementRef, inject, output, DestroyRef, input } from '@angular/core';

@Directive({
  selector: '[appLongPress]',
})
export class LongPressDirective {
  threshold = input<number>(500);   // מילישניות
  longPress = output<void>();

  constructor() {
    const el = inject<ElementRef<HTMLElement>>(ElementRef).nativeElement;
    const destroyRef = inject(DestroyRef);

    let timeout: number | undefined;

    const start = () => {
      timeout = window.setTimeout(() => this.longPress.emit(), this.threshold());
    };
    const cancel = () => {
      if (timeout) window.clearTimeout(timeout);
    };

    el.addEventListener('mousedown', start);
    el.addEventListener('touchstart', start);
    el.addEventListener('mouseup', cancel);
    el.addEventListener('mouseleave', cancel);
    el.addEventListener('touchend', cancel);

    destroyRef.onDestroy(() => {
      el.removeEventListener('mousedown', start);
      // ...אחרים...
      cancel();
    });
  }
}
```

השתמש בה:

```html
<div appLongPress [threshold]="800" (longPress)="onLongPress()">
  Hold me
</div>
```

לדירקטיבות יכולים להיות inputs ו-outputs בדיוק כמו לקומפוננטות. כל המכניקה הריאקטיבית עובדת אותו הדבר. מה שחסר הוא התבנית — לדירקטיבה אין תצוגה משלה; היא מרחיבה אלמנט מארח.

`DestroyRef` הוא מנגנון ה-tear-down מבוסס DI של Angular. הזרקתו וקריאה ל-`onDestroy` נקייה יותר ממתודת `ngOnDestroy`. הוא גם מתחבר עם `takeUntilDestroyed` מתחת למכסה.

## דירקטיבות מבניות — לרוב, אל תעשה

דירקטיבות מבניות הן אלה שמקבלות קידומת `*` (`*ngIf`, `*ngFor`, `*ngSwitchCase`). הן מוסיפות או מסירות אלמנטים מה-DOM. מכיוון שהזרימה החדשה של השליטה (`@if`, `@for`, `@switch`) מכסה כל מקרה אמיתי, כמעט לעולם לא תכתוב דירקטיבה מבנית משלך ב-Angular מודרנית.

המקום היחיד שבו הן עדיין מופיעות הוא כשאתה רוצה להוסיף API בצורת תבנית — קח פיסת תוכן תבנית ותרנדר אותה תחת תנאי כלשהו או עם העשרה כלשהי. אם אתה מוצא את עצמך זקוק לזה, חפש את התיעוד על `TemplateRef` ו-`ViewContainerRef`. עבור ספר של קוד יישום, אנחנו יכולים להשאיר את זה שם.

## `HostBinding` ו-`HostListener`, או המקבילות המודרניות שלהן

דפוס ישן יותר להתנהגות דירקטיבה השתמש בדקורטורים:

```ts
@HostBinding('class.active') isActive = false;
@HostListener('click') onClick() { this.isActive = !this.isActive; }
```

Angular מודרנית משתמשת ב-`host` בבלוק המטא-דאטה:

```ts
@Directive({
  selector: '[appToggleActive]',
  host: {
    '[class.active]': 'isActive',
    '(click)': 'onClick()',
  },
})
export class ToggleActiveDirective {
  isActive = false;
  onClick() { this.isActive = !this.isActive; }
}
```

שתי הצורות שוות; בלוק `host` מועדף להולך והתקדם. בדירקטיבות קטנות, הגישה האימפרטיבית שהשתמשנו בה עבור `LongPress` (הוספת מאזיני אירועים ישירות על האלמנט בקונסטרוקטור) גם בסדר ולפעמים ברורה יותר.

## קומפוננטות עם הזרקת תוכן: `EmptyState`

חלק מ-UI לשימוש חוזר הוא קומפוננטה עם חריצים. ל-Compass יש כמה מקומות שצריכים "מצב ריק" — הודעה ידידותית כשלרשימה אין פריטים. במקום לחזור על המרקאפ, חלץ קומפוננטה.

```ts
@Component({
  selector: 'app-empty-state',
  template: `
    <div class="empty-state">
      <div class="icon"><ng-content select="[icon]"></ng-content></div>
      <h3>{{ title() }}</h3>
      <p class="body"><ng-content></ng-content></p>
      <div class="actions"><ng-content select="[actions]"></ng-content></div>
    </div>
  `,
  styles: `
    .empty-state { padding: 40px; text-align: center; color: #666; }
    .icon { font-size: 3rem; margin-bottom: 12px; }
    h3 { margin: 0 0 6px; font-size: 1.2rem; }
    .body { margin: 0 0 16px; }
  `,
})
export class EmptyState {
  title = input.required<string>();
}
```

שימוש ב-`TaskList`:

```html
@if (tasks().length === 0) {
  <app-empty-state title="Nothing to do today.">
    <span icon>🌤</span>
    Enjoy some free time, or add something below.
    <button actions (click)="focusInput()">Add a task</button>
  </app-empty-state>
}
```

שלושה חריצים בשמות (`icon`, ברירת מחדל, `actions`), כולם אופציונליים, מלואים על ידי המזמין. הזרקת תוכן היא מה שמאפשר לקומפוננטות של מערכת עיצוב להישאר דקלרטיביות — המזמין מרכיב מרקאפ, ה-container מעצב.

## מתי לפנות למה

רשימת בדיקה עבור "קומפוננטה, דירקטיבה, או פייפ".

**פייפ** — יש לך ערך; אתה רוצה ערך בצורה אחרת בתבנית. אין התנהגות, אין שינויי DOM, אין מצב.

**דירקטיבה** — אתה רוצה להצמיד התנהגות לאלמנט שכבר יש לו תפקיד. Focus, drag-and-drop, intersection observer, tooltip trigger. אפס או שינויי DOM מינימליים.

**קומפוננטה** — הדבר לשימוש חוזר הוא פיסה של מרקאפ עם זהות ויזואלית משלה, או יש לה מצב, או צריכה להזרים תוכן.

לקבל את זה נכון חוסך הרבה קוד. עטיפת `<div>` ב-`<app-tooltip-host>` כשדירקטיבת `[appTooltip]` הייתה מספיקה מכפילה את האלמנטים ב-DOM. פייפ של חישוב כשסיגנל `computed` בבעלות קומפוננטה היה מספיק מפצל את הלוגיקה לרוחב הקוד.

## שלוש הקידומות: `app-`, `app`, `app-`

קונבנציה:

- קומפוננטות: `<app-thing>` (תג kebab-case עם קידומת).
- דירקטיבות: `[appThing]` (attribute camelCase עם קידומת).
- פייפים: `{{ x | appThing }}` (קצר, camelCase).

צוות Angular מעדיף שדירקטיבות *לא* ישתמשו בקידומת עבור סלקטור ה-attribute שלהן כשהדירקטיבה היא גנרית (כמו `ngIf`). לדירקטיבות של קוד יישום שאתה כותב בעצמך, הקידומת שומרת על הדברים חד-משמעיים.

## מה בא הלאה

פרק 16 מודד את הביצועים של Compass ומחיל את הכלים שחשובים. זיהוי שינויים `OnPush`, בלוקי `@defer` עבור חלקים שלא צריכים להיטען מיד, אופטימיזציה של תמונות, וניתוח bundle. עד סוף פרק 16, Compass ירגיש snappy בטלפון בטווח בינוני.

### תרגילים

1. בנה פייפ `Currency` שמעצב `number` כ-USD לשתי ספרות עשרוניות עם פסיקים ("1,234.56"). אז הסר אותו והשתמש בפייפ המובנה `currency`. השווה — כמה פייפים מובנים אתה לא צריך לכתוב?

2. בנה דירקטיבת `ClickOutside` שפולטת כשהמשתמש לוחץ מחוץ לאלמנט שהיא מוצמדת אליו. השתמש בה כדי לסגור קומפוננטת תפריט dropdown. רמז: הקשב ל-`document.click`; בדוק אם ה-target הוא צאצא של `el.nativeElement`.

3. המר את "שורת המשימה" של Compass מקומפוננטה לדירקטיבה על `<li>` — `<li appTaskRow [task]="task" (toggled)="onToggle($event)">`. מה אתה יכול לשמור? מה חייב לזוז? בסוף, החלט אם הקומפוננטה או הדירקטיבה היא הצורה הטובה יותר וחזור אחורה על מה שמפסיד.
