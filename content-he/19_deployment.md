# פרק 19. פריסה

Compass מוכן. הוא רץ על המחשב הנייד שלך מול `json-server`. כדי שיהיה לו ערך כלשהו, הוא צריך לחיות איפשהו באינטרנט שבו אתה (ואם תרצה, אחרים) יוכל להגיע אליו. הפרק הזה עובר דרך הבחירות — אירוח סטטי, אירוח Node, containers — ומעלה את Compass לאוויר על אחד מהם.

## שתי הצורות של אפליקציית Angular בהפקה

איזה אירוח שתבחר, אפליקציית Angular בהפקה היא אחת משתי צורות.

**Bundle סטטי.** `ng build` מייצר `dist/compass/browser/` — תיקייה של HTML, JS, ו-CSS. הגשת התיקייה הזאת מכל שרת קבצים סטטי מספיקה. זו הצורה של Compass מרונדר בלקוח או בניית SSG שעברה prerender.

**שרת Node.** עם SSR מופעל, `ng build` גם מייצר `dist/compass/server/` — שרת Node.js. הרצת `node dist/compass/server/server.mjs` מפעילה שרת Express שמרנדר כל בקשה ומגיש את הנכסים שנבנו. הצורה הזאת צריכה אירוח Node.

שאר הפרק הוא: איזה אירוח לאיזו צורה.

## מה Compass צריך מהבקאנד שלו

לפני האירוח של ה-frontend, זכור: Compass מדבר עם בקאנד. `json-server` הוא צעצוע פיתוח; הוא לא משהו להריץ בהפקה. עבור פריסה אמיתית, החלף אותו ב:

- API של REST או GraphQL אמיתי שאתה הבעלים של.
- backend-as-a-service (Firebase, Supabase, PocketBase).
- API serverless (Cloudflare Workers, Vercel Functions, AWS Lambda + API Gateway).

לצד Angular של Compass לא אכפת איזה. כל עוד ה-endpoints ב-`TasksApi` מחזירים את אותה צורה, הכל עובד.

עבור הפרק הזה נניח שבחרת אחד והוא חושף API ב-`https://api.compass.example`. עדכן את הקבוע `BASE_URL` ב-`tasks-api.ts`, או (עדיף) הפוך אותו למשתנה סביבה של זמן-בנייה — ראה את סעיף *תצורת סביבה* למטה.

## אירוח בנייה סטטית של Angular

אם Compass מרונדר בלקוח (ללא SSR), כל אירוח סטטי עובד. המכניקה שונה; העיקרון זהה: העלה את `dist/compass/browser/` והגדר את המארח ליפול חזרה ל-`index.html` עבור מסלולים לא תואמים.

הנקודה האחרונה חשובה. הראוטר בצד הלקוח של Angular מצפה שהדפדפן יטען `index.html` עבור כל URL וייתן ל-Angular להבין את המסלול. אם המארח מחזיר 404 עבור `/stats`, המשתמשים לא יכולים לקשר עמוק. לכל מארח סטטי יש דרך להגדיר את הנפילה הזאת; זה לעתים קרובות נקרא "מצב SPA" או "rewrite ל-index".

שלושה מארחים סטטיים טובים:

**Netlify.** גרור-והשלך את התיקייה ל-app.netlify.com, או דחוף ל-GitHub וחבר את המאגר. Netlify מזהה אוטומטית Angular, מריץ `ng build`, ומגיש את `dist/compass/browser/`. הגדר את הנפילה ב-`netlify.toml`:

```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

**Vercel.** זרימת עבודה דומה. `vercel.json`:

```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

**Cloudflare Pages.** חבר מאגר Git; Cloudflare בונה ומגיש גלובלית ברשת הקצה שלה. נפילה דרך `_redirects`:

```
/*    /index.html   200
```

לכל השלושה יש שכבות חינם נדיבות מספיק עבור פרויקטים אישיים, דומיינים מותאמים אישית, HTTPS, ופריסות שמופעלות על ידי CI. הבחירות קרובות בתכונות; בחר אחד ונסה.

## אירוח Compass SSR

Compass SSR שולח שרת Node. זה מוציא מארחים סטטיים טהורים ודורש אחד מ:

**Vercel, עם ה-runtime של Node.** פלט ה-SSR של Angular עובד מהקופסה על Vercel; פרוס את כל המאגר, ו-Vercel יבנה את bundle ה-SSR ויריץ את השרת על פי דרישה.

**Firebase Hosting + Cloud Functions.** ל-Angular יש שילוב מן המדף; `ng deploy` מ-`@angular/fire` מעלה את נכסי הדפדפן ל-Firebase Hosting ואת bundle השרת כ-Cloud Function.

**Container בכל cloud.** בנה תמונת Docker קטנה, פרוס אותה ל-Fly.io, Railway, Render, App Platform של DigitalOcean, AWS ECS, Google Cloud Run, או כל שווה ערך. זה הגמיש ביותר; זה גם הכי הרבה עבודה.

הנה Dockerfile מינימלי שעובד עבור SSR של Angular:

```Dockerfile
FROM node:20-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-slim AS runtime
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
COPY package*.json ./
EXPOSE 4000
CMD ["node", "dist/compass/server/server.mjs"]
```

בנה והרץ מקומית:

```bash
docker build -t compass .
docker run -p 4000:4000 compass
```

דחוף את התמונה לרישום ופרוס במארח שבחרת.

## תצורת סביבה

`BASE_URL` של Compass לא צריך להיות מקודד. פרויקטי Angular מטפלים בזה עם קבצי סביבה.

צור `src/environments/environment.ts`:

```ts
export const environment = {
  production: false,
  apiBaseUrl: 'http://localhost:3000',
};
```

ו-`src/environments/environment.prod.ts`:

```ts
export const environment = {
  production: true,
  apiBaseUrl: 'https://api.compass.example',
};
```

הגדר את `angular.json` להחליף את הקובץ בזמן בנייה. במערך `configurations.production.fileReplacements` (שבדרך כלל כבר שם):

```json
"fileReplacements": [
  {
    "replace": "src/environments/environment.ts",
    "with": "src/environments/environment.prod.ts"
  }
]
```

יבא והשתמש:

```ts
import { environment } from '../environments/environment';
// ...
const BASE_URL = environment.apiBaseUrl;
```

`ng build --configuration production` מחליף לערכי prod. `ng serve` משתמש בערכי dev.

עבור סודות — מפתחות API, tokens — אל תבדוק אותם לתוך קבצי סביבה. כל דבר ש-Angular שולחת לדפדפן הוא פומבי. שים סודות בבקאנד, חשוף רק את הערכים הבטוחים ל-frontend.

## HTTPS, CORS, ו-cookies

ברגע ש-Compass נמצא בדומיין וה-backend שלו בדומיין אחר, שלוש תצורות הופכות ל-load-bearing.

**HTTPS בכל מקום.** כל מארח טוב מספק אותו אוטומטית. אל תפרוס דרך HTTP; דפדפנים חוסמים או מנמיכים יותר מדי APIs (service workers, geolocation, cookies) דרך HTTP.

**CORS.** ה-backend חייב לשלוח `Access-Control-Allow-Origin: https://compass.example` (או המקורות הספציפיים שמותרים). אם Compass מבצע בקשות עם cookies, `Access-Control-Allow-Credentials: true` וה-origin לא יכול להיות `*`.

**Cookies.** אם auth משתמש ב-cookies, הם חייבים להיות `Secure` (HTTPS בלבד), `HttpOnly` (לא-נגישים ל-JS), ו-`SameSite=Lax` או `Strict`. Cookies בין אתרים (`SameSite=None`) דורשים סיבה טובה וטיפול נוסף.

כל אחד מאלה נשך צוות פעם אחת ולימד אותם לקח לצמיתות. הגדר אותם נכון בפעם הראשונה.

## פריסה רציפה

הגדר CI כך שדחיפות ל-`main` פורסות את Compass. לכל מארח יש תבנית.

GitHub Actions ל-Netlify:

```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run test -- --watch=false --browsers=ChromeHeadlessNoSandbox
      - run: npx playwright test
      - run: npm run build
      - uses: nwtgck/actions-netlify@v3
        with:
          publish-dir: 'dist/compass/browser'
          production-deploy: true
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

דחוף commit; כמה דקות מאוחר יותר, ההפקה מעודכנת.

## סביבות תצוגה מקדימה

באופן אידיאלי, כל pull request מקבל URL תצוגה מקדימה משלו. Netlify, Vercel, ו-Cloudflare Pages עושים את זה אוטומטית עבור מאגרי Git מחוברים. סוקרים פותחים את קישור התצוגה המקדימה, לוחצים מסביב, ומגיבים על התנהגות אמיתית במקום לנסות לדמיין אותה מ-diff.

אם המארח שלך לא עושה את זה בצורה נייטיבית, GitHub Actions יכול לבנות ולדחוף ל-S3 bucket לפי סניף או ערוץ Firebase. ההגדרה היא אחר צהריים אחד ומשתלמת לנצח.

## דומיינים מותאמים אישית

כל מארח שהזכרנו תומך בדומיינים מותאמים אישית. המכניקה:

1. קנה דומיין מרשם (Namecheap, Cloudflare Registrar, וכן הלאה).
2. במארח, הוסף את הדומיין.
3. ברשם, הוסף את רשומות ה-DNS שהמארח מספק (בדרך כלל CNAME או שני A records).
4. חכה כמה דקות עבור התפשטות DNS.
5. אישור HTTPS מוקצה אוטומטית דרך Let's Encrypt.

הצבע את `compass.yourname.dev` ל-Netlify; חמש דקות מאוחר יותר, `https://compass.yourname.dev` מגיש את Compass.

## Analytics ודיווח שגיאות

ברגע ש-Compass פומבי, אתה רוצה לדעת מתי הוא נשבר.

**דיווח שגיאות**: Sentry, Rollbar, Bugsnag, LogRocket. לכל אחד יש SDK של Angular; אתה מאתחל אותו ב-`main.ts` ומגדיר טיפול שגיאות גלובלי על ידי אספקת `ErrorHandler`:

```ts
providers: [
  { provide: ErrorHandler, useClass: SentryErrorHandler },
],
```

**Analytics**: Plausible, Fathom, או Google Analytics. טען תג script, או השתמש ב-SDK שלהם. לראוטר של Angular יש `Router.events` Observable שפולט על כל ניווט; הירשם ורשום את ה-URL אם אתה רוצה מעקב עמוד יחיד.

שניהם אופציונליים; שניהם בדרך כלל שווה להקים לפני שאתה מספר למישהו על האפליקציה שלך.

## ניטור ביצועים

ניטור משתמש אמיתי (RUM) עוקב אחרי איך האפליקציה מתפקדת עבור משתמשים ממשיים, על המכשירים הממשיים שלהם. Web Vitals — LCP, FID, CLS — הם מדדים סטנדרטיים שאתה יכול למדוד עם `web-vitals` (הספרייה):

```ts
import { onCLS, onFID, onLCP } from 'web-vitals';

onCLS(metric => sendToAnalytics(metric));
onFID(metric => sendToAnalytics(metric));
onLCP(metric => sendToAnalytics(metric));
```

כל מארח מספק RUM משלו אם אתה מעדיף לא לגלגל משלך.

## חזרה אחורה ו-staging

כל פריסה יכולה להשתבש. שתי רשתות ביטחון שאתה רוצה מוקדם:

**חזרה אחורה בלחיצה אחת.** כל המארחים שרשמנו מאפשרים לך להחזיר לפריסה קודמת. תרגל את השימוש בזה לפני שאתה צריך את זה.

**סביבת staging.** פריסה נפרדת (compass-staging.example) שמשקפת הפקה אבל עם backend של בדיקה. פרוס ל-staging קודם, וודא, קדם להפקה. זה ההבדל בין פריסה בערב שישי לאירוע בערב שישי.

## אחרי הפריסה: לשמור על Angular מעודכן

Angular משחררת גרסה ראשית כל שישה חודשים. `ng update` מטפל ברוב ההגירות:

```bash
ng update @angular/cli @angular/core
```

הוא מריץ schematics של הגירה שמתאימים את הקוד שלך אוטומטית עבור APIs ששמם שונה. לפעמים עבודה ידנית נדרשת; פלט העדכון אומר לך מה.

הישאר גרסה או שתיים מאחורי העדכני אם אתה מעריך יציבות; הישאר על העדכני אם אתה רוצה תכונות חדשות. אל תיפול יותר משלוש גרסאות מאחור — מסלול השדרוג הופך כואב.

## מה בא הלאה

פרק 20 הוא הפרק האחרון. הוא ממפה את האקוסיסטם של Angular מעבר למה ש-Compass נזקק לו — Material, Nx, NgRx, Universal, הרחבות ראוטר — ומצביע לך על מה לקרוא, לצפות, ולנסות הבא.

### תרגילים

1. פרוס את Compass (גרסה מרונדרת בלקוח) ל-Netlify, Vercel, או Cloudflare Pages. כלול את נפילת ה-SPA כך ש-`/stats` לא יגרום ל-404. שתף את ה-URL עם חבר ואשר שהוא נטען דרך נתוני הטלפון שלו.

2. הפעל SSR (לפי פרק 18), בנה את bundle ה-SSR, ופרוס למארח שתומך ב-Node (Vercel, Fly.io, או Cloud Run). וודא עם `curl -sS https://your-url/task/t1 | grep -c task-detail` שהתגובה מכילה HTML מרונדר.

3. הקם GitHub Actions להריץ בדיקות, לבנות, ולפרוס על כל דחיפה ל-`main`. שבור בדיקה אחת בכוונה; וודא שהפריסה מדולגת. תקן את הבדיקה; צפה בה מצליחה.
