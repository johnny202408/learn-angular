# פרק 11. הבסיס של RxJS

ראית את RxJS פעמיים כבר: `HttpClient` החזיר Observables, וגלגלנו אותם עם `firstValueFrom`. זה מספיק עבור HTTP של בקשה-תגובה, אבל לא לחלקים של Compass שעדיין לפניכם. חיפוש תוך כדי הקלדה, זרמים חיים, עדכוני טפסים מתואמים, ופרמטרי מסלול — כולם הם באופן טבעי זרמים של ערכים לאורך זמן, ו-RxJS היא הספרייה של Angular לזרמים.

הפרק הזה הוא לא סיור מלא ב-RxJS. לספרייה הזאת יש מאה אופרטורים ותת-תרבות משלה. מה שאתה צריך ל-Compass, ולרוב קוד יישום Angular, הוא תת-קבוצה ספציפית: מהו Observable, איך הוא שונה מ-Promise ומסיגנל, תריסר אופרטורים, ונקודות ה-interop בין Observables לסיגנלים. זה מה שהפרק הזה מכסה.

## מהו Observable

**Observable** הוא יצרן של ערכים לאורך זמן. הוא עשוי לייצר אפס ערכים (ואז להשלים), ערך אחד (כמו תגובת HTTP), רצף קבוע (כמו הספרות של פאי), או זרם ללא גבול (כמו אירועי עכבר עד שהחלון נסגר). הוא עשוי להשלים בצורה נורמלית או לצאת מכלל שגיאה. והוא לא עושה כלום עד שמישהו *נרשם* אליו — Observables הם עצלים.

השווה עם שני הדברים שאתה כבר מכיר:

- **Promise** מייצר ערך אחד לכל היותר. ברגע שהוא נוצר, Promise מתחיל לעבוד מיד (הוא להוט) ובסופו של דבר נפתר או נדחה. אי אפשר לבטל אותו ואי אפשר לספק יותר מערך אחד.
- **סיגנל** מחזיק ערך נוכחי בכל עת. קריאה שלו תמיד מחזירה את הערך. כתיבה שלו מודיעה לכל מי שעוקב אחריו.

Observable הוא אף אחד מהם. הוא *תוכנית* לייצור ערכים, מופעלת על ידי הרשמה, יכולה לייצר רבים, וניתנת לביטול.

באופן קונקרטי:

```ts
import { Observable } from 'rxjs';

const numbers = new Observable<number>(subscriber => {
  subscriber.next(1);
  subscriber.next(2);
  subscriber.next(3);
  subscriber.complete();
});

numbers.subscribe({
  next: n => console.log('got', n),
  complete: () => console.log('done'),
});
// מדפיס: got 1, got 2, got 3, done
```

כמעט אף פעם לא תבנה Observables עם `new Observable`. בקוד יישום, הם מגיעים מ*פונקציות יצירה* ומ-APIs של Angular.

## יצירת Observables

הפונקציות שהופכות משהו ל-Observable:

```ts
import { of, from, fromEvent, interval, timer } from 'rxjs';

const three = of(1, 2, 3);                      // פולט 1, 2, 3 ומשלים
const fromArray = from([1, 2, 3]);              // פולט אלמנטים של מערך
const fromPromise = from(fetch('/api/tasks'));  // עוטף Promise

const clicks = fromEvent<MouseEvent>(document, 'click');  // פולט על כל לחיצה
const ticks = interval(1000);                             // פולט 0, 1, 2, ... כל שנייה
const delayed = timer(500);                               // פולט 0 אחרי 500ms ומשלים
```

שניים מאלה — `fromEvent` ו-`interval` — מייצרים זרמים ללא גבול. הירשם אליהם, והם פולטים לנצח, או עד שתבטל את ההרשמה.

Angular נותנת לך Observables לדברים מובנים רבים:

```ts
this.http.get<Task[]>('/api/tasks');            // פליטה אחת, אז השלמה
this.route.params;                              // פולט על כל שינוי param של מסלול
this.route.queryParams;                         // פולט על כל שינוי param של שאילתה
formControl.valueChanges;                       // פולט על כל שינוי של בקרת טופס
```

כל אחד מאלה הוא זרם מוגדר היטב, וכל אחד מזדווג באופן טבעי עם pipeline קטן של אופרטורים כדי לייצר את הערך שאתה באמת רוצה.

## אופרטורים ו-`pipe`

אופרטור הוא פונקציה שמקבלת Observable ומחזירה Observable חדש. `pipe` מרכיב אופרטורים לשרשרת.

```ts
import { of, map, filter } from 'rxjs';

of(1, 2, 3, 4, 5)
  .pipe(
    filter(n => n % 2 === 0),
    map(n => n * 10)
  )
  .subscribe(n => console.log(n));  // 20, 40
```

יש עשרות אופרטורים. תשתמש אולי בחמישה-עשר מהם באופן קבוע. הנה הרשימה המקוצרת, בערך בסדר של כמה פעמים תפנה אליהם.

**`map(fn)`** מהפך כל פליטה דרך `fn`. אם `fn` מחזיר Promise או Observable, זה *לא* ממתין — לזה, השתמש ב-`switchMap` וחבריו.

**`filter(fn)`** מפיל פליטות ש-`fn` מחזיר עליהן false.

**`tap(fn)`** מריץ את `fn` על כל פליטה עבור תופעות הלוואי שלו, בלי לשנות את הזרם. שימושי לרישום ולדיבוג. `tap({ error })` גם רץ על שגיאות.

**`take(n)`** לוקח את `n` הפליטות הראשונות, אז משלים. `take(1)` נפוץ כשאתה רוצה ש-Observable יתנהג כמו Promise.

**`takeUntil(otherObservable$)`** משלים את זרם המקור כש-`otherObservable$` פולט. ל-Angular יש `takeUntilDestroyed()` מיוחד שקושר את חיי ה-Observable לחיי הקומפוננטה — נשתמש בו למטה.

**`debounceTime(ms)`** מחכה `ms` אחרי הפליטה האחרונה לפני שהוא מעביר אותה. מושלם לחיפוש תוך כדי הקלדה: המשתמש מפסיק, הבקשה יוצאת.

```
source:     --a-b-c------d----|
              debounceTime(200)
                    ↓
output:     -------c------d--|
                    (a and b dropped — c is the last within the 200ms window)
```

**`distinctUntilChanged()`** מדכא ערכים כפולים עוקבים. גם מאוד שימושי לחיפוש: אל תשלוף מחדש אם השאילתה לא באמת השתנתה.

**`switchMap(fn)`** משטח את המקור דרך Observable פנימי, מבטל כל Observable פנימי שנמצא בטיסה כשחדש מגיע. זה האופרטור שגורם לחיפוש תוך כדי הקלדה לעבוד: כל הקלדה מפעילה בקשת HTTP חדשה, והבקשה הקודמת מבוטלת.

```
source:     --a-------b------c---------|
switchMap(x => http.get(x))
inner a:      --A1--A2--X     (cancelled when b arrives)
inner b:            --B1--X   (cancelled when c arrives)
inner c:                  --C1--C2--C3--|
output:     ----A1-A2----B1--------C1--C2--C3--|
```

`X` מסמן איפה זרם פנימי בוטל. רק ה-inner האחרון שורד להשלים.

**`mergeMap(fn)`** משטח, אבל מאפשר לכל Observables הפנימיים לרוץ במקביל. לעתים רחוקות מה שאתה רוצה עבור עבודה מונעת משתמש; שימושי כשאתה רוצה עיבוד מקביל.

**`exhaustMap(fn)`** משטח, אבל מתעלם מפליטות מקור חדשות בזמן ש-Observable פנימי עדיין רץ. האופרטור הנכון לכפתורי "save": אם המשתמש לוחץ פעמיים, אל תירה שתי שמירות.

```
source:     --a---b---c----d---------|
              (b and c ignored — a's inner still running)
inner a:      -----A1--A2--|
inner d:                     -----D1--|
output:     -------A1--A2--------D1--|
```

השווה עם `switchMap` למעלה: `switchMap` מבטל את ה-inner בטיסה ולוקח את אירוע המקור החדש; `exhaustMap` שומר על ה-inner בטיסה ומוריד את אירוע המקור החדש.

**`concatMap(fn)`** משטח, מסדר Observables פנימיים בתור כך שהם רצים אחד אחרי השני. שימושי לכתיבות מסודרות.

**`catchError(fn)`** מיירט שגיאות ואו מחזיר Observable חלופי או זורק שוב. כך אתה מספק ערך ברירת מחדל על קריאת HTTP שנכשלה.

**`retry({ count, delay })`** נרשם מחדש על שגיאה. השתמשנו בו בפרק 10.

**`combineLatest([a$, b$])`** לוקח מספר Observables ופולט מערך של הערכים האחרונים שלהם בכל פעם שאחד מהם פולט. שילוב של route params ו-query params של Angular הוא שימוש נפוץ.

**`startWith(value)`** מוסיף ערך לתחילת הזרם, כך שמנויים מקבלים פליטה מיידית.

כלל הלמידה: אל תנסה לשנן את כולם. למד map, filter, tap, take, debounceTime, distinctUntilChanged, ו-switchMap. חפש את השאר כשבעיה מזמינה אותם.

## דוגמה עובדת: חיפוש תוך כדי הקלדה

נניח ש-Compass מקבל תיבת חיפוש. המשתמש מקליד "buy m", ו-Compass שולף `/tasks?q=buy%20m`. אם המשתמש עדיין מקליד כשתגובה מגיעה, התגובה צריכה להיזרק — השאילתה מיושנת.

```ts
import { fromEvent } from 'rxjs';
import { debounceTime, distinctUntilChanged, filter, map, switchMap } from 'rxjs';

const input = document.querySelector('input')!;

fromEvent<Event>(input, 'input').pipe(
  map(e => (e.target as HTMLInputElement).value.trim()),
  debounceTime(200),
  distinctUntilChanged(),
  filter(q => q.length >= 2),
  switchMap(q => http.get<Task[]>(`/api/tasks?q=${encodeURIComponent(q)}`)),
).subscribe(results => {
  render(results);
});
```

קרא את זה מלמעלה למטה:

1. כל אירוע input, קבל את הערך המנוקה.
2. חכה 200ms אחרי ההקלדה האחרונה.
3. המשך רק אם השאילתה השתנתה.
4. המשך רק אם יש לפחות שני תווים.
5. ירה את בקשת ה-HTTP. אם הקלדה חדשה מגיעה בזמן שהבקשה הזאת בטיסה, בטל אותה והתחל חדשה.

ה-pipeline של שש השורות הזה מחליף את מה שאחרת היה טיימר מנוהל ידנית, מעקב אחר בקשה בטיסה, ref של debounce, והשוואה לשינוי. זה מה ש-RxJS נועד לו.

## סיגנלים ו-Observables: interop

רוב מצב Compass חי בסיגנלים. רוב ה-APIs המובנים של Angular פולטים Observables. ה-interop הוא שתי פונקציות:

**`toSignal(observable, options)`** הופך Observable לסיגנל.

```ts
import { toSignal } from '@angular/core/rxjs-interop';

class TaskList {
  private route = inject(ActivatedRoute);
  filter = toSignal(this.route.queryParamMap.pipe(
    map(params => params.get('tag') ?? 'all')
  ), { initialValue: 'all' });
}
```

עכשיו `filter` הוא סיגנל שאתה יכול לקרוא בתבנית כ-`filter()`, והוא מתעדכן בכל פעם ש-query params של המסלול משתנים. `toSignal` גם מנקה את ההרשמה כשהקומפוננטה מושמדת.

**`toObservable(signal)`** הופך סיגנל ל-Observable.

```ts
import { toObservable } from '@angular/core/rxjs-interop';

class TaskStore {
  filter = signal('all');
  filter$ = toObservable(this.filter);

  filteredTasks$ = this.filter$.pipe(
    switchMap(f => this.api.list(f))
  );
}
```

`toObservable` פולט בכל פעם שהסיגנל משתנה, והפליטה היא הערך החדש של הסיגנל. בשילוב עם אופרטורים, זה מאפשר לך לבנות pipelines של "שליפה מונעת סיגנל" בלי לעזוב את המרחב הריאקטיבי.

## הרשמה בטוחה

כל הרשמה היא משאב. אם הקומפוננטה שלך נרשמת ואף פעם לא מבטלת הרשמה, ה-callback ממשיך לרוץ אחרי שהקומפוננטה עוזבת את המסך — דליפה. Angular נותנת לך שלוש אפשרויות טובות ואחת רעה.

**הטוב ביותר (בדרך כלל): הפייפ `async`.** קשור Observable ישירות בתבנית, ו-Angular נרשמת ומבטלת הרשמה בשבילך.

```html
<p>{{ user$ | async }}</p>
```

**השני הכי טוב: `toSignal`.** לצרכנים של Observable שאינם בתבנית. Angular קורעת את ההרשמה בהשמדת הקומפוננטה.

**שלישי: `takeUntilDestroyed()`.** להרשמות מפורשות בהקשר קומפוננטה.

```ts
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

class TaskList {
  constructor() {
    this.route.params.pipe(takeUntilDestroyed()).subscribe(params => {
      // ...
    });
  }
}
```

`takeUntilDestroyed()` קורא את ה-DestroyRef הנוכחי (מ-DI) ומשלים את ה-Observable כשהקומפוננטה מושמדת. לא נדרש `ngOnDestroy` מפורש.

**רע: `.subscribe()` חשוף בלי איזה קריעה שהיא.** זו הדליפה. אם ה-linter שלך הגון, הוא יצעק עליך.

## Cold לעומת hot, בקצרה

Observable הוא *cold* אם כל מנוי מקבל ריצה משלו של היצרן, ו-*hot* אם כל המנויים חולקים ריצה אחת.

`http.get()` הוא cold: כל הרשמה יורה בקשה חדשה. `fromEvent(document, 'click')` הוא hot: כל המנויים מקבלים את אותם אירועי לחיצה.

לעתים רחוקות תצטרך לחשוב על זה במפורש. איפה שזה חשוב: אם אתה `subscribe` לתוצאת `http.get` פעמיים, אתה יורה שתי בקשות. השתמש ב-`shareReplay(1)` כדי לחלוק בקשה אחת בין מנויים רבים, או המר לסיגנל.

## מתי לא להשתמש ב-RxJS

RxJS חזק. הוא גם מנוצל יתר על המידה. סימנים שהוגזמת:

- לקומפוננטות שלך יש חמש קריאות `pipe` מקוננות כדי לחשב משהו שסיגנל `computed` היה מבטא בשורה אחת.
- יש לך שדה `Subject` על שירות שנמצא בשימוש כמכל עם מצב. השתמש בסיגנל.
- אתה `.subscribe()` למשהו ומגדיר שדה עם התוצאה. השתמש ב-`toSignal`.
- אתה מבצע debounce על סיגנל דרך `toObservable` ו-`debounceTime`. בסדר — אבל בדוק אם `linkedSignal` או effect קטן אינם ברורים יותר למקרה שלך.

כלל האצבע מפרק 7 עומד: סיגנלים למצב, RxJS לזרמים. כשאתה מוצא את עצמך משתמש ב-RxJS למצב, הגר; כשאתה מוצא את עצמך משתמש בסיגנלים לזרמים, שאל למה.

## מה בא הלאה

פרק 12 מסיים את החלק השלישי עם טפסים ריאקטיביים. ל-Compass יש כרגע input "Add task" שנעשה ידנית. בפרק 12 אנחנו מחליפים אותו ב-`FormGroup`, מוסיפים ולידציה, ובונים דיאלוג עריכה למשימות עם תאריכי יעד ותגיות. אחרי פרק 12, ל-Compass יש בקאנד אמיתי, טפסים אמיתיים, והתנהגות ריאקטיבית אמיתית — כל מה שאפליקציה קטנה צריכה לפני שהיא גדלה למספר עמודים, שזו העבודה של החלק הרביעי.

### תרגילים

1. כתוב pipeline של Observable שלוקח לחיצות על כפתור "load more" וכל לחיצה מוסיפה את העמוד הבא של משימות. השתמש ב-`exhaustMap` כך שמספר לחיצות מהירות לא ייורו מספר בקשות. וודא על ידי לחיצה מהירה.

2. המר את ה-pipeline של חיפוש-תוך-כדי-הקלדה בפרק הזה לקומפוננטת Compass. צור `SearchBox` עם input, חבר את ה-pipeline בקונסטרוקטור שלו, ופלט output `results`. השתמש ב-`takeUntilDestroyed` על ההרשמה.

3. `HttpClient` מחזיר Observables קרים — כל subscribe יורה מחדש את הבקשה. הוכח זאת: הירשם לאותו Observable של `http.get(...)` פעמיים ובדוק את ה-network tab. אחר כך הוסף `shareReplay(1)` ואשר שהוא יורה פעם אחת. למה `shareReplay(1)` ולא `shareReplay()`?
