# Learn Angular by Building Compass

## A project-driven path from your first line of TypeScript to a deployed Angular app

---

*First edition, 2026*

*Prepared for personal use.*

---

## Preface

If you have never built a web application before, this book is written for you. It assumes you can read English, use a computer, and are willing to type things into an editor and see what happens. It does not assume you know what a framework is, what TypeScript is, or why anyone would voluntarily use something called *dependency injection*. By the last chapter, all of those words will feel like tools you reach for, not jargon you tolerate.

The book is built around a single application called **Compass** — a personal task tracker. In Chapter 4 you will type `ng new compass` and see an empty starter appear on your screen. Every chapter after that adds one real capability to Compass. By the end you will have written a real app: it will let you manage a real task list backed by a real HTTP server, edit tasks with reactive forms, navigate between screens, render fast on a phone, and run in a browser on the public internet — with the tests and CI pipeline that a real app deserves.

Compass is deliberately not a full-featured productivity suite. Authentication, offline sync, drag-and-drop, and habit-tracking are excellent *next* projects — the tools you'll have by Chapter 20 are exactly the ones you'd reach for to build them, and Appendix D points at where to go next. But the book's promise is to teach Angular, not to ship every feature a real task app might have.

Learning by building has two advantages that reading-first books tend to give up. The first is that every concept lands somewhere. When you meet a new idea — say, an *interceptor* — you do not just read a definition; you write one, watch it change the behavior of your app, and then break it on purpose to see what happens. The second is that you end with something. Compass is small enough to hold in your head and rich enough to show a friend. It is also yours: nothing in this book is a puzzle whose answer is hidden at the back.

### How the book is organized

The book has five parts and a set of appendices.

**Part I — Foundations.** Four chapters that get you from zero to a running Angular project. You will meet TypeScript, the modern JavaScript features Angular actually uses, and the Angular CLI. You will not touch a component here; the goal is to have a workshop before you pick up a hammer.

**Part II — Components and templates.** The core mechanics: what a component is, how templates and data binding work, and how *signals* — Angular's modern reactive primitive — let you describe changing state without ceremony. By the end of Part II, Compass will look and feel like a real app.

**Part III — Services and the outside world.** Applications don't live in a single component. This part covers dependency injection, HTTP, RxJS, and forms — the four things you need to talk to servers, gather user input, and share behavior across your app without copying and pasting.

**Part IV — Building a real app.** Routing, state that outlives a single screen, custom directives and pipes, and performance. This is where Compass grows from "one page that works" into "several pages that stay fast."

**Part V — Production.** Testing, server-side rendering, deployment, and the ecosystem you are joining. When you finish Part V you will have a Compass instance on the internet, and you will know what to search for next.

**Appendices.** A machine setup guide (A), a debugging checklist (B), a short tour of older Angular idioms you will encounter in existing codebases (C), a curated list of resources for continuing your Angular education (D), an accessibility guide that retrofits the a11y considerations the main text keeps deferring (E), solutions to the code exercises (F), and a one-page cheat sheet for signals, template syntax, RxJS, and error codes (G). Read them when you need them; they are reference material, not sequential.

### How to read this book

Read it at the keyboard. Every chapter has code you should type — not paste. The typing itself does work: it slows you down enough to see what changed and forces you to notice syntax that a copy would gloss over. When a chapter ends with an *Exercises* section, do them before starting the next chapter. They are not optional in the sense that the next chapter assumes you did them; they are optional in the sense that if you skip them, you will lose the muscle memory the book is trying to build.

Callouts appear throughout:

> **Note.** A useful aside — deeper context, a related concept, or a piece of history.

> **Watch out.** A common mistake or a subtle behavior that will save you an afternoon later.

> **Try it.** A one-minute experiment to change some code and see the result. Do these; they are cheap.

### What you need

- A laptop or desktop computer running macOS, Windows, or Linux.
- About 5 GB of free disk space (mostly for `node_modules`, which we will meet in Chapter 4).
- A stable internet connection while working through Parts I and V; the rest of the book works offline.
- Roughly 30 to 50 hours across however many sittings suit you. Some readers finish in two weekends; some spread it over three months. The book does not care.

You do not need any prior experience with Angular, React, Vue, or any other framework. You do not need to know TypeScript; Chapter 2 teaches enough of it. You do not need to know how servers work; when we need a server in Part III, we spin one up together in a few lines of code.

### A word on Angular versions

Angular ships a new major version roughly every six months, but the *ideas* in this book — components, signals, dependency injection, routing, forms — have been stable and central for years and will remain so. The specific syntax targets Angular 18 and later, which is the first version where the modern control flow (`@if`, `@for`, `@switch`), signals, and standalone components are the recommended defaults. If you are reading this and Angular is on version 22 by then, most of the code will still run untouched; anything that changes will be a rename, not a rethink.

Turn the page. Chapter 1 is a short one — no code, just a map of where we are and where we are going.
