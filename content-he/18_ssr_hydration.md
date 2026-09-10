# פרק 18. רינדור בצד השרת ו-hydration

Compass, כפי שהוא עומד, הוא יישום *מרונדר לקוח*. כשמשתמש מבקר לראשונה, הדפדפן מוריד shell HTML כמעט ריק, מוריד bundle של JavaScript, ורק אז Angular מתאתחלת ומרנדרת את הדף. משתמשים ברשתות מהירות רואים את זה כהבזק קצר של כלום לפני שהאפליקציה מופיעה. משתמשים ברשתות איטיות רואים את זה כמסך ריק ארוך. crawlers של מנוע חיפוש עשויים לראות את זה כדף ריק ולא לאנדקס כלום.

רינדור בצד השרת (SSR) מתקן את שניהם. השרת מריץ את אפליקציית Angular שלך, מייצר את ה-HTML המרונדר במלואו עבור ה-URL המבוקש, ושולח את זה חזרה לדפדפן. המשתמש רואה תוכן מיד. Angular אז מתאתחל בלקוח ו*מבצע hydration* לדף — מצמיד מטפלי אירועים ל-DOM הקיים במקום לרנדר אותו מחדש מאפס.

הפרק הזה הופך את Compass לאפליקציית SSR. זה אחד הפרקים הקצרים ביותר בספר כי Angular עשתה את רוב העבודה. `ng add @angular/ssr` מוריד אותך 80% מהדרך.

## SSR, רינדור לקוח, וייצור סטטי

שלושה מצבים, והשמות משתנים לרוחב האקוסיסטמים:

- **רינדור בצד הלקוח (CSR)**: השרת שולח shell; הדפדפן מוריד JS ומרנדר. פשוט; צביעה ראשונה איטית.
- **רינדור בצד השרת (SSR)**: השרת מרנדר כל בקשה. צביעה ראשונה מהירה; השרת עושה עבודה לכל בקשה.
- **ייצור אתר סטטי (SSG) / prerendering**: השרת מרנדר כל מסלול פעם אחת, בזמן בנייה, ומגיש את ה-HTML הסטטי. צביעה ראשונה מהירה והשרת עושה אפס עבודה לכל בקשה — אבל כל URL חייב להיות ידוע בזמן בנייה.

Angular תומכת בכל השלושה. אתה בוחר לכל מסלול: חלק מ-prerender (עמודי השיווק), חלק SSR (עמודים מותאמים אישית שצריכים נתוני session), חלק CSR (כלים אינטראקטיביים כבדים שלא נהנים מרינדור שרת).

עבור Compass, השילוב ההגיוני הוא:

- דף הבית: CSR (מותאם אישית, ללא צורך ב-SEO).
- דף שיווק / נחיתה (אם היה לנו): SSG.
- פירוט משימה: SSR כשה-URL משותף באופן פומבי; אחרת CSR בסדר.

נפעיל SSR גלובלית בפרק הזה ונאפשר לתצורה לכל מסלול לעקוב.

## הוספת SSR ל-Compass

הרץ:

```bash
ng add @angular/ssr
```

ה-schematic עושה כמה דברים:

1. מוסיף `@angular/ssr` ו-Express כתלויות.
2. יוצר `server.ts` בשורש הפרויקט — שרת Express שמרנדר את Angular עבור כל בקשה.
3. מוסיף target `server` build ל-`angular.json` וסקריפט `serve-ssr`.
4. משנה את `main.ts` לקבל bootstraps גם של דפדפן וגם של שרת.
5. מוסיף `app.config.server.ts` עבור providers רק לשרת.
6. מפעיל hydration דרך `provideClientHydration()` ב-`app.config.ts`.

אחרי שהוא מסתיים:

```bash
npm run start:ssr        # שרת פיתוח עם SSR
npm run build            # בונה גם bundles של דפדפן וגם של שרת
npm run serve:ssr:compass  # מריץ את השרת שנבנה
```

פתח `http://localhost:4000` (פורט ברירת המחדל של SSR). צפה במקור של הדף (לחיצה ימנית → View Source). תראה את רשימת המשימות המרונדרת במלואה ב-HTML — לא רק `<app-root>` ריק. רענן ובדוק את טאב הרשת; התגובה הראשונה מגיעה כבר מאוכלסת.

## Hydration: התאמת הלקוח לשרת

ברגע ש-Angular מתאתחלת בלקוח, היא צריכה *לבצע hydration* ל-DOM הקיים במקום לזרוק אותו ולרנדר מחדש. `provideClientHydration()` (הוסף על ידי ה-schematic) מטפל בזה. הוא מתאים את הצמתים שרונדרו בשרת עם עץ הקומפוננטות המרונדר בלקוח, מצמיד מאזיני אירועים, ומשמר כל מצב DOM (כמו ערך של input) שכבר היה שם.

כללי הדרך:

- **השרת והלקוח חייבים לייצר את אותו HTML.** תוכן אקראי (`Math.random()`, `new Date()`) יהיה שונה, ו-hydration יזהיר על אי-ההתאמה. עטוף תוכן לא-דטרמיניסטי ב-`@if (isBrowser())` (ראה למטה) כך שהוא ירנדר רק בלקוח.
- **מניפולציה של DOM לפני ש-hydration מסתיים היא מסוכנת.** אל תושיט יד ל-`document` מקונסטרוקטור קומפוננטה אלא אם אתה יודע מה אתה עושה.
- **ספריות צד שלישי שמתמרנות את ה-DOM ישירות (תוספי jQuery, חלק מספריות תרשימים) לא עובדות טוב עם hydration.** טען אותן בתוך `afterNextRender`, או דחה אותן לגמרי.

## זיהוי הפלטפורמה

חלק מהקוד צריך לרוץ רק בדפדפן. Angular נותנת לך `isPlatformBrowser`:

```ts
import { inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

@Injectable({ providedIn: 'root' })
export class SomeService {
  private isBrowser = isPlatformBrowser(inject(PLATFORM_ID));

  loadPreference(): string {
    if (this.isBrowser) {
      return localStorage.getItem('pref') ?? 'default';
    }
    return 'default';
  }
}
```

בשרת, `PLATFORM_ID` הוא `'server'`; בלקוח, `'browser'`. זה מאפשר לך להימנע מקריאה ל-APIs של דפדפן בשרת, שהיו זורקים כי `window`, `document`, ו-`localStorage` לא קיימים שם.

עבור קומפוננטות: `afterNextRender` נורה רק בלקוח. השתמש בו כדי להריץ אתחול ספציפי לדפדפן:

```ts
constructor() {
  afterNextRender(() => {
    // רץ בלקוח, פעם אחת, אחרי הרנדור הראשון.
    window.scrollTo(0, 0);
  });
}
```

## Transfer state: אל תשלוף מחדש מה שהשרת כבר היה לו

כשהשרת מרנדר את דף הבית של Compass, הוא שולף משימות מה-API. כשהלקוח אז מבצע hydration, הוא היה שולף מחדש — את אותם נתונים — מאותו API, מבזבז מסע הלוך ושוב.

ל-Angular יש *transfer state* כדי לפתור את זה. עטוף HTTP עם `withHttpTransferCacheOptions` ב-`app.config.ts`:

```ts
import { provideHttpClient, withFetch, withInterceptors, withHttpTransferCacheOptions } from '@angular/common/http';

providers: [
  provideHttpClient(
    withFetch(),
    withInterceptors([authInterceptor]),
    withHttpTransferCacheOptions({
      includeHeaders: [],
      includePostRequests: false,
    }),
  ),
],
```

Angular מסדרת את התגובה של כל GET של HTTP לתוך ה-HTML הראשוני (בתוך תג `<script>`). בלקוח, `HttpClient` בודק את המטמון הזה לפני שהוא פוגע ברשת — בקשה תואמת מחזירה את התגובה השמורה מיד.

אתה יכול גם להעביר מצב שרירותי דרך `TransferState`:

```ts
import { makeStateKey, TransferState } from '@angular/core';

const TASKS_KEY = makeStateKey<Task[]>('tasks');

// בשרת:
const transferState = inject(TransferState);
transferState.set(TASKS_KEY, tasks);

// בלקוח:
const initial = transferState.get(TASKS_KEY, []);
```

Compass יקלוט transfer state אוטומטית עבור קריאות ה-`HttpClient` שלו, בלי צנרת נוספת.

## Prerendering של מסלולים ספציפיים

עבור מסלולים שהתוכן שלהם לא תלוי במשתמש, prerender בזמן בנייה. הוסף אותם ל-`app.routes.server.ts` (שנוצר על ידי ה-schematic של SSR):

```ts
import { RenderMode, ServerRoute } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  { path: '', renderMode: RenderMode.Prerender },
  { path: 'stats', renderMode: RenderMode.Server },
  { path: 'task/:id', renderMode: RenderMode.Server },
];
```

`Prerender` רץ בזמן בנייה; `Server` רץ לכל בקשה; `Client` משבית SSR עבור המסלול הזה.

עבור מקטעים דינמיים כמו `task/:id`, ספק פונקציית `getPrerenderParams` שמחזירה את ה-ids לבצע prerender בזמן בנייה:

```ts
{
  path: 'task/:id',
  renderMode: RenderMode.Prerender,
  getPrerenderParams: async () => {
    const tasks = await fetchAllPublicTasks();
    return tasks.map(t => ({ id: t.id }));
  },
}
```

פירוט המשימה של Compass הוא ספציפי למשתמש, כך ש-prerender לא עוזר; `RenderMode.Server` (SSR לכל בקשה) היא הבחירה הנכונה אם אנחנו רוצים שהדף יהיה ניתן לשיתוף, או `RenderMode.Client` (רק לקוח) אם לא.

## בדיקת SSR מקומית

`npm run build && npm run serve:ssr:compass` מריץ את בניית ההפקה מול שרת Node מקומי. פתח אותו, צפה במקור, אשר שהתוכן קיים.

לדיבוג קוד שרת בלבד, `console.log` בקומפוננטה או שירות יופיע במסוף (שרת), לא בדפדפן (לקוח). אם אתה לא רואה כלום, זכור את הפיצול.

## מטא-דאטה של SEO

דפים מרונדרים בשרת מאפשרים למנועי חיפוש לראות את התוכן שלך — אבל הם גם צריכים מטא-דאטה. השירותים `Title` ו-`Meta` של Angular מגדירים את תגי `<title>` ו-`<meta>`:

```ts
import { Title, Meta } from '@angular/platform-browser';

constructor() {
  const title = inject(Title);
  const meta = inject(Meta);
  title.setTitle('Compass — plan your day');
  meta.updateTag({ name: 'description', content: 'A calm daily planner.' });
  meta.updateTag({ property: 'og:image', content: 'https://compass.example/og.png' });
}
```

עבור מטא-דאטה לכל דף, הנע את אלה מנתוני מסלול או resolvers. ה-`TitleStrategy` שהצגנו בפרק 13 היא הדרך השיטתית.

## מתי SSR שווה את זה

לא כל אפליקציית Angular נהנית מ-SSR.

**SSR משתלם כש:**

- המשתמשים שלך לעתים קרובות מבקרים ברשתות איטיות.
- מנועי חיפוש צריכים לאנדקס את התוכן.
- שיתוף חברתי (Open Graph, Twitter cards) חשוב.
- לאפליקציה שלך יש JS משמעותי מעבר למה שיש על החלק הנראה של הצביעה הראשונה.

**SSR לא שווה את זה כש:**

- האפליקציה מאחורי אימות ולעולם לא מאונדקסת.
- התוכן הכבד הוא שנוצר על ידי משתמשים אחרי הטעינה הראשונה (צ'אט, עורך, דשבורד).
- כל דף דורש התאמה אישית שהשרת לא יכול לחשב בזול.
- היית צריך לשכפל לוגיקה משמעותית בצד השרת.

Compass נהנה בעדינות מ-SSR — האפליקציה קטנה, ומשתמשים בדרך כלל שומרים אותו במועדפים וטוענים אותו מהמטמון אחרי הביקור הראשון. אם היית בונה אתר שיווקי פומבי, SSR היה קרוב יותר להיות חיוני.

## מה בא הלאה

פרק 19 פורס את Compass לאינטרנט. אירוח סטטי עבור Compass המרונדר בלקוח, אירוח Node עבור וריאנט ה-SSR, ו-CI כדי לגרום לפריסה להיות בטוחה. פרק 20 מוסר לך את המפה למה ללמוד הבא.

### תרגילים

1. הפעל SSR ב-Compass, בנה אותו, והגש אותו. צפה במקור בדף הבית. השווה את גודל תגובת ה-HTML הראשונית עכשיו לעומת לפני SSR (טאב רשת, מסנן "Doc", הסתכל על "Size"). האם היה שינוי משמעותי?

2. הוסף `provideClientHydration()` אם הוא לא שם; אז שבור hydration בכוונה על ידי הוספת `<span>{{ Math.random() }}</span>` לתבנית של קומפוננטה. פתח את הקונסולה; אתה אמור לראות אזהרת אי-התאמה של hydration. תקן את זה על ידי העברת הקריאה האקראית מאחורי `afterNextRender`.

3. הוסף תגי title ו-description מטא למסלול פירוט המשימה, כך שכש-URL של משימה משותף ל-Slack או לאפליקציית העברת הודעות, הוא נפרס עם תצוגה מקדימה שימושית. בדוק עם ה-Sharing Debugger של Facebook או Twitter Card Validator ב-URL הפרוס שלך (פרק 19 מביא אותך למצב פרוס).
