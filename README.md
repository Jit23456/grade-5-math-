# Mathematics 5 — BC Curriculum platform

A small web application for the British Columbia Grade 5 Mathematics curriculum.

- An **index page** lists all 19 chapters, grouped by Big Idea strand.
- Each chapter has **its own page** with lessons, worked examples and a self-scoring assessment.
- Teachers sign in to **write chapters and questions by hand**.
- An **AI assistant** drafts lessons, questions, explanations and vocabulary for a teacher to review.
- Every piece of content is **labelled with its origin**: curriculum, teacher written, or AI draft.

The 19 chapters, 77 lessons and 380 questions are seeded from the BC learning
standards on first run. Nothing is missing from the curriculum and nothing outside
it has been added.

Every chapter carries **20 questions**: 14 fill-in-the-blank, 4 multiple choice and
2 multi-select. Most fill-in-the-blank questions come with a **diagram** — a place
value chart, number line, fraction bar, area grid, analog clock, bar graph, spinner
or money layout — and each chapter opens with a diagram of its core idea.

---

## Quick start

```bash
cd app
pip install -r requirements.txt

# Optional: choose the first teacher password yourself.
# Leave it unset and one is generated and printed to the console.
export MATH5_ADMIN_PASSWORD='choose-something-long'

# Required in production so sessions survive a restart.
export MATH5_SECRET_KEY="$(python3 -c 'import secrets;print(secrets.token_hex(32))')"

# Optional: switches the AI assistant on.
export GROQ_API_KEY='gsk_...'   # free key from https://console.groq.com/keys

python3 app.py           # development server on http://127.0.0.1:5000
```

The first run creates `data/math5.sqlite3`, seeds the 19 chapters, and creates a
`teacher` account. Sign in at `/login` and change the password from the dashboard.

### Teacher accounts

Teachers sign themselves up at `/signup` with a mobile number:

1. They give their name, mobile number and a password.
2. A six digit code is texted to that number. Nothing is written to the `users`
   table yet — the pending sign-up waits in `signup_otp`, with the code stored
   hashed, never in the clear.
3. Entering the code creates the account and signs them in.

Afterwards they sign in with **either** their mobile number or the username
generated for them. Numbers are compared in a normalised form, so
`+1 (604) 555-0132` and `+16045550132` are the same person.

A code lasts ten minutes, survives five wrong guesses before it is destroyed, and
can be resent at most five times with a minute between sends. One account per
number.

| Role | Can do |
|---|---|
| teacher | Write and edit chapters and questions, use the AI assistant |
| admin | All of that, plus see every account and remove one |

Everyone who signs up is a plain **teacher**. The seeded `teacher` account is the
**admin**, and can still add accounts by hand and remove anyone — useful for
removing a sign-up that should not have happened. An admin cannot remove their
own account, so the site is never left without one. Removing someone leaves their
chapters and questions in place, still credited to them.

> **Worth knowing before you publish.** A texted code proves someone controls that
> phone, not that they teach at your school. On a public URL, anyone who can
> receive a text can create an account and edit the curriculum. Watch the account
> list, or keep the site private.

### Sending the codes

Set these three and codes are texted through Twilio:

| Variable | Where it comes from |
|---|---|
| `TWILIO_ACCOUNT_SID` | Twilio console |
| `TWILIO_AUTH_TOKEN` | Twilio console |
| `TWILIO_FROM_NUMBER` | a number Twilio has issued you, in `+1...` form |

Leave them unset and sign-up still works for testing: the code is printed to the
server log instead of being sent, and the verify page says so.

---

## Running under a WSGI server

`wsgi.py` exposes the app as `application` and prepares the database on import,
so no separate setup step is needed.

**gunicorn** (recommended)

```bash
cd app
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:application
```

**waitress** (works on Windows)

```bash
waitress-serve --port=8000 --call wsgi:application
```

**uWSGI**

```bash
uwsgi --http :8000 --module wsgi:application --master --processes 4
```

**Apache with mod_wsgi**

```apache
WSGIDaemonProcess math5 python-home=/srv/math5/venv python-path=/srv/math5/app
WSGIProcessGroup math5
WSGIScriptAlias / /srv/math5/app/wsgi.py
Alias /static /srv/math5/app/static
```

**nginx in front of gunicorn**

```nginx
server {
    listen 80;
    server_name maths.example.org;
    location /static/ { alias /srv/math5/app/static/; expires 7d; }
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**systemd unit**

```ini
[Unit]
Description=Mathematics 5 curriculum platform
After=network.target

[Service]
User=www-data
WorkingDirectory=/srv/math5/app
Environment="MATH5_SECRET_KEY=change-me"
Environment="GROQ_API_KEY=gsk_..."
ExecStart=/srv/math5/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Several workers starting at once is safe. Seeding happens inside a
`BEGIN IMMEDIATE` transaction, so exactly one worker seeds and the rest wait,
then find the table already populated.

---

## Opening the project in VS Code

```bash
unzip math5-platform.zip
code math5-platform
```

VS Code will offer the recommended extensions on first open: Python, debugpy,
Jinja HTML (so the templates get proper highlighting) and an SQLite viewer.

Set up the environment once:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Pick the interpreter with **Ctrl/Cmd + Shift + P → Python: Select Interpreter**
and choose the `.venv` one.

Then press **F5**. Three run configurations are included:

| Configuration | What it does |
|---|---|
| Run the site (development) | Flask's own server on <http://127.0.0.1:5000>, with breakpoints |
| Run with the AI assistant on | The same, passing your shell's `GROQ_API_KEY` through |
| Run under gunicorn (as in production) | Four workers on port 8000, matching the deployed setup |

The first two create a `teacher` account with the password `teacher1234`, which is
fine locally and must never be used on a public server.

Useful places to start reading:

| File | What is in it |
|---|---|
| `app.py` | Every route, the database schema, and the AI assistant calls |
| `templates/index.html` | The chapter index |
| `templates/chapter.html` | A chapter page and the browser-side quiz marking |
| `templates/assistant.html` | The AI assistant screen |
| `static/style.css` | All the styling, with the palette in `:root` at the top |
| `data/seed.json` | The 19 chapters, 77 lessons and 380 questions, with their diagrams |
| `scripts/viz.py` | The inline-SVG diagram generators (number lines, grids, clocks, charts) |
| `scripts/gen_questions.py` | Rebuilds the fill-in-the-blank questions and diagrams into `seed.json` |
| `scripts/reseed.py` | Reloads `seed.json` into an existing database, keeping teacher accounts |

Breakpoints work normally in `app.py`. To inspect the database, open
`data/math5.sqlite3` with the SQLite extension.

Copy `.env.example` to `.env` if you prefer keeping secrets in a file. `.env` is
already in `.gitignore`.

---

## Environment variables

| Variable | Default | What it does |
|---|---|---|
| `MATH5_SECRET_KEY` | random each start | Signs session cookies. **Set this in production**, or everyone is signed out on every restart. |
| `MATH5_DB` | `app/data/math5.sqlite3` | Database file path. |
| `MATH5_ADMIN_PASSWORD` | generated and printed | Password for the first `teacher` account. Only read on first run. |
| `GROQ_API_KEY` | unset | Switches the AI assistant on. Without it the assistant explains that it is off and everything else works. |
| `GROQ_MODEL` | `openai/gpt-oss-120b` | Model the assistant calls. |
| `GROQ_API_URL` | `https://api.groq.com/openai/v1/chat/completions` | Override to route through a gateway or proxy. |
| `TWILIO_ACCOUNT_SID` | unset | Texts the sign-up code. Without all three, the code goes to the server log instead. |
| `TWILIO_AUTH_TOKEN` | unset | Twilio auth token. |
| `TWILIO_FROM_NUMBER` | unset | The Twilio number the code is sent from. |
| `PORT` | `5000` | Development server port only. |

---

## The AI assistant

At `/teacher/assistant`. Choose what you need, describe the topic, and the
assistant returns a draft. Five kinds of help:

| Kind | Returns |
|---|---|
| Lesson | A `### Lesson n.n` block with a worked example and a "Watch out" note, in the same shape as the seeded chapters |
| Questions | Multiple choice, multi-select and fill-in-the-blank questions with answer keys and explanations |
| Explanation | A short explanation for a teacher to read aloud |
| Vocabulary | Six to eight terms with plain-language meanings |
| Rewrite | Your own text rewritten in simpler language, with the mathematics unchanged |

Nothing is saved until you read the draft and press save. Saved content is tagged
`ai`, and the chapter page shows an "AI draft" label beside it.

**Check the mathematics.** Language models get arithmetic wrong sometimes. Work
through every calculation and every answer key before putting a draft in front of
a class. The assistant is a drafting tool, not an authority.

Malformed output is handled rather than trusted: question JSON is parsed
defensively, entries with missing options or unknown types are dropped, and a
multiple-choice question that comes back with several correct answers is
reclassified as multi-select.

Requests are logged to the `ai_log` table (who, what kind, whether it worked)
and the last eight appear on the dashboard. Prompts and responses are not stored.

---

## Content origin labels

| Label | Meaning |
|---|---|
| **Curriculum** | Seeded from the BC learning standards |
| **Teacher written** | Written by hand in the editor |
| **AI draft** | Generated by the assistant and saved by a teacher |

Editing a curriculum chapter or question by hand relabels it as teacher written,
so a reader can see it no longer matches the seeded text.

---

## Writing a chapter

From the dashboard, **Add chapter**. Only the number and title are required.

The lessons field takes Markdown:

```markdown
### Lesson 4.1 - A short title

A sentence or two stating the concept plainly.

​```
A worked example, laid out step by step
   4.62 to the nearest tenth
   hundredths digit is 2 -> round down
   answer: 4.6
​```

| A table | if it helps |
|---|---|
| row | row |

> **Watch out.** The most common student error, and how to avoid it.
```

Tables, fenced code blocks and `> **Watch out.**` blockquotes all render with
the same styling as the seeded chapters. Learning goals, vocabulary and summary
points are one per line; vocabulary uses `Term | meaning`.

Unpublished chapters are hidden from the index and return 404 to visitors, while
signed-in teachers can still open them to keep working.

---

## Questions

Three types:

- **Multiple choice** — two to six options, exactly one correct.
- **Multi-select** — two or more correct; a student must find all of them for the mark.
- **Fill in the blank** — the student types an answer. List every form they might
  reasonably type, one per line. Spaces, commas and dollar signs are ignored when
  marking, so `3800000`, `3 800 000` and `3,800,000` all match.

Each question carries an explanation shown after the student checks their answer,
plus an optional skill tag and a difficulty. Marking happens in the browser; no
attempt data is sent to the server or stored.

---

## Routes

| Route | Who | What |
|---|---|---|
| `/` | anyone | Chapter index and standards checklist |
| `/chapter/<n>` | anyone | One chapter, with its assessment |
| `/api/course.json` | anyone | The whole course as JSON |
| `/healthz` | anyone | Status, chapter count, whether the AI is configured |
| `/login`, `/logout` | anyone | Teacher sign in, by mobile number or username |
| `/signup` | anyone | Teacher sign up, sends the code |
| `/signup/verify` | anyone | Enter the code, creates the account |
| `/teacher` | teacher | Dashboard |
| `/teacher/chapter/new`, `/teacher/chapter/<n>/edit` | teacher | Chapter editor |
| `/teacher/chapter/<n>/questions` | teacher | Question list |
| `/teacher/chapter/<n>/question/new` | teacher | Question editor |
| `/teacher/assistant` | teacher | AI assistant |
| `/api/ai/generate`, `/api/ai/accept` | teacher | Assistant endpoints |
| `/teacher/password` | teacher | Change your own password |
| `/teacher/users/new` | **admin** | Create a teacher account |
| `/teacher/users/<id>/delete` | **admin** | Remove a teacher account |

---

## Notes before going live

- Set `MATH5_SECRET_KEY` to a fixed value.
- Serve over HTTPS. Session cookies carry the teacher sign-in.
- Change the generated `teacher` password from the dashboard.
- Back up `data/math5.sqlite3`. It holds every chapter, question and account.
- **Upgrading a database that already holds the old seed:** the `visual` column is
  added automatically on startup, but the seeded questions are only written when the
  chapters table is empty. To pull new `seed.json` content into an existing database,
  run `python scripts/reseed.py` once. It replaces only the rows still tagged
  `curriculum`, so teacher-written chapters, edits and accounts are left alone.
- SQLite suits a school or a small district comfortably. For many concurrent
  writers, move to PostgreSQL by replacing the queries in `app.py`; they are
  plain parameterised SQL with no ORM in the way.
- The AI assistant is teacher-only and is never reachable by students.

---

## Curriculum coverage

Source: BC Ministry of Education, Mathematics 5 Core —
<https://curriculum.gov.bc.ca/curriculum/mathematics/5/core>

| Ch | Content standard | Strand |
|---|---|---|
| 1 | number concepts to 1 000 000 | Number |
| 2 | decimals to thousandths | Number |
| 3 | equivalent fractions | Number |
| 4 | whole-number, fraction, and decimal benchmarks | Number |
| 5 | addition and subtraction of whole numbers to 1 000 000 | Computational Fluency |
| 6 | multiplication and division to three digits, including division with remainders | Computational Fluency |
| 7 | addition and subtraction of decimals to thousandths | Computational Fluency |
| 8 | addition and subtraction facts to 20 (extending computational fluency) | Computational Fluency |
| 9 | multiplication and division facts to 100 (emerging computational fluency) | Computational Fluency |
| 10 | rules for increasing and decreasing patterns with words, numbers, symbols, and variables | Patterning |
| 11 | one-step equations with variables | Patterning |
| 12 | area measurement of squares and rectangles | Geometry and Measurement |
| 13 | relationships between area and perimeter | Geometry and Measurement |
| 14 | duration, using measurement of time | Geometry and Measurement |
| 15 | classification of prisms and pyramids | Geometry and Measurement |
| 16 | single transformations | Geometry and Measurement |
| 17 | one-to-one correspondence and many-to-one correspondence, using double bar graphs | Data and Probability |
| 18 | probability experiments, single events or outcomes | Data and Probability |
| 19 | financial literacy — monetary calculations, including making change with amounts to 1000 dollars and developing simple financial plans | Number |

Chapter elaborations include the First Peoples connections named in the
curriculum: Tsimshian and Tlingit counting systems, traditional dwellings,
weaving and cedar basket designs, and traditional measuring techniques. These are
referenced where the curriculum names them and are treated lightly on purpose.
Developing that content properly should involve local Elders and knowledge
keepers, as the curriculum itself advises.
