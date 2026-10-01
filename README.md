# ToDoEnterprise™ 🏢

> _"Every todo deserves an enterprise."_

Undervisningsrepo til **Øvelse 2: Byg din Quality Gate** – kvalitetsgates i praksis.

ToDoEnterprise er en lille (og bevidst letskæv) Flask-API til todo-håndtering, bygget med alle enterprise-dyder: models, repository, service-lag og tynde controllers. App'ens baseline er **100% grøn**: den passer statisk analyse, har 100% testdækning og ingen sikkerhedsfund.

Jeres job er **ikke** at bygge appen. Jeres job er at bygge **sikkerhedsnettet** – og opleve, at gates ikke er en hindring, men et net der fanger jer (og jeres AI-assistent), når noget glipper.

## API'et i 30 sekunder

| Metode | Endpoint | Body / query | Respons |
|---|---|---|---|
| GET | `/health` | – | `{"status": "ok"}` |
| GET | `/todos` | `?status=open` / `in_progress` / `done` (valgfri) | liste af todos |
| POST | `/todos` | `{"title": "..."}` | `201` + oprettet todo |
| PATCH | `/todos/<id>` | `{"status": "..."}` | `200` + opdateret todo |
| DELETE | `/todos/<id>` | – | `204` |

Statusværdier: `open`, `in_progress`, `done`. Data gemmes in-memory (genstart er en feature, ikke en bug).

## Kom i gang lokalt

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements-dev.txt

# Kør API'et (udviklingsserver):
python -m flask --app app run --debug

# Prøv det:
curl http://127.0.0.1:5000/todos
curl -X POST http://127.0.0.1:5000/todos -H "Content-Type: application/json" -d "{\"title\": \"Byg en quality gate\"}"
```

## De tre gates

Alle tre kan køres lokalt (gør det – det er hurtigere end at pushe):

| Gate | Kommando | Krav |
|---|---|---|
| 1. Statisk analyse | `ruff check .` | 0 fejl |
| 2. Unit tests | `pytest --cov=app --cov-fail-under=80` | alle tests grønne **og** mindst 80 % coverage |
| 3. Sikkerhedsscan | `bandit -r app -ll` | 0 fund (medium severity og opefter) |

Alt tooling er open source og kræver ingen eksterne konti eller tjenester.

## Øvelsen (60 min)

### Trin 1 – Konfigurer jeres pipeline (ca. 15 min)

Åbn `.github/workflows/ci.yml`. Scaffolding'en (checkout, Python, dependencies) er på plads, men de **tre gates er TODO-stubber** – hver med et kort hint i kommentaren om, hvilket værktøj der er på tale.

- Udfyld de tre gates med de rigtige kommandoer (brug hintene og tabellen ovenfor).
- Commit og push, og åbn **Actions**-fanen på GitHub.
- I bør nu se en grøn kørsel med tre synlige gate-trin.

### Trin 2 – Generér en feature med jeres AI (ca. 10 min)

Prompt jeres AI-assistent til at tilføje en feature, fx:

> "Tilføj et login-endpoint (POST /login med brugernavn og password) til denne Flask-app."

Commit og push AI'ens kode, **som den er** – I må ikke rette i den først.

### Trin 3 – Se sikkerhedsnettet virke

Kig i Actions-loggen:

- Hvilke gates fejler? Og hvorfor præcis?
- Tip: kør også `bandit -r app -ll` og `pytest --cov=app --cov-fail-under=80` lokalt og sammenlign.

### Trin 4 – Iterér til grønt (resten af tiden)

Ret koden – manuelt eller med nye, mere præcise AI-prompts – indtil **alle gates er grønne igen**. Prøv begge dele og mærk forskellen.

Til sidst: Hvad fangede nettet? Og hvad ville det IKKE have fanget?

## Regler

- Kun open source-værktøj, der kører i GitHub Actions uden eksterne konti.
- Coverage-kravet på 80 % må ikke sænkes. (At fjerne kravet er ikke at bestå gaten 😉)
- Login-funktionen skal virke, når I er færdige – en grøn gate er ikke det samme som korrekt adfærd.

God fornøjelse – og husk: grønne gates betyder ikke fejlfri kode. De betyder kun, at netop disse tre ting er tjekket. Resten er stadig jeres job. 🎓
