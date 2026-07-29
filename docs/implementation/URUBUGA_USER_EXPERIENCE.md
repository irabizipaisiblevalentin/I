# Urubuga — How Users Build Websites

Complete user experience design for all skill levels.

---

## 1. Project Creation (CLI)

### Beginner: One command to start

```bash
isoko urubuga tangura indoro.ya
# "tangura" = create, "indoro.ya" = website
# Creates: indoro.ya/ directory with everything
```

### Advanced: Choose your template

```bash
isoko urubuga tangura indoro.ya --ubwoko=indoro
isoko urubuga tangura ububiko.bw.isoko --ubwoko=ububiko
isoko urubuga tangura serivisi --ubwoko=serivisi
isoko urubuga tangura api --ubwoko=api
```

### What gets created:

```
indoro.ya/
├── app.i                    # Main application file
├── ububiko.i                # Database configuration
├── izina.rwanda             # Project manifest (like package.json)
├── icyerekezo/              # Schemas (migrations)
│   └── 001_shtura_abantu.i
├── ibikoresho/              # Models
│   └── umuntu.i
│   └── inkwoko.i
├── ububumwe/                # Controllers
│   └── umuntu.i
│   └── indoro.i
├── imitwaro/                # Views/templates
│   └── ubushyingizi/
│   │   └── umwanya.i.html
│   └── abantu/
│   │   └── urutonde.i.html
│   │   └── ibisobanuro.i.html
│   └── indoro/
│       └── urubuga.i.html
│   └── imigabane/           # Components (partials)
│       └── umutwempangano.i.html
│       └── igice_cy_amakuru.i.html
├── uburambe/                # Assets (CSS, JS, images)
│   └── css/
│   │   └── uburambe.css
│   └── js/
│   │   └── uburambe.js
│   └── amafoto/
│       └── logo.png
├── ibikoresho/              # Config
│   └── ububiko.json         # Database config
│   └── uburambe.json        # Assets config
│   └── umuyobozi.json       # App config
└── test/                    # Tests
    └── test_umuntu.i
```

---

## 2. Configuration

### ububiko.json (Database)

```json
{
  "ububiko": {
    "ubwoko": "sqlite",
  "izina": "indoro_ya.db"
  },
  "uburambe": {
    "urubuga": "/static"
  },
  "umuyobozi": {
    "izina": "indoro.ya",
    "debug": true,
    "ubwiherero": 8000
  }
}
```

### MongoDB-style config (future)

```json
{
  "ububiko": {
    "ubwoko": "postgresql",
    "izina": "indoro_ya",
    "umuyenzi": "localhost",
    "umushyitsi": 5432,
    "ukoresha": "admin",
    "jambo": "secret"
  }
}
```

---

## 3. Main Application File (app.i)

### Beginner: Simple and clean

```python
# app.i — Indoro ya — urubuga wa I

shyiramo urubuga

# Indoro = application instance
indoro = urubuga.Indoro("indoro.ya", debug=yego)

# Umwanya wo gutangira = home page
@indoro.umwanya("/")
def uburuga(request):
    subira indoro.imitwaro("indoro/urubuga.i.html", {
        "izina": "Indoro ya",
        "umumaro": "Urubuga rw'ibikorwa bya elegance"
    })

# Umwanya wo kwinjira = login page
@indoro.umwanya("/kwinjira")
def kwinjira(request):
    subira indoro.imitwaro("ubushyingizi/umwanya.i.html")

# Gutangira = run
indoro.tangira()
```

### Advanced: Full control

```python
# app.i — Full-stack urubuga application

shyiramo urubuga
shyiramo ububiko
shyiramo urubumwe

# Application
indoro = urubuga.Indoro("indoro.ya", debug=yego)

# Database connection
ububiko.uhuguriro("ububiko/ububiko.json")

# Middleware
indoro.shyiramo_middleware(urubuga.amabanga.AmabangaMiddleware())
indoro.shyiramo_middleware(urubuga.urukoko.CORSMiddleware(
    ituma=["https://indoro.ya"]
))
indoro.shyiramo_middleware(urubuga.gukosha.RateLimitMiddleware(
    imibare=100, igihe=60
))

# Route groups
with indoro.igice("/api/v1") as api:
    api.umwanya("/abantu", "GET")(UmuntuController.urutonde)
    api.umwanya("/abantu", "POST")(UmuntuController.shtura)
    api.umwanya("/abantu/{id}", "GET")(UmuntuController.ibisobanuro)
    api.umwanya("/abantu/{id}", "PUT")(UmuntuController.hindura)
    api.umwanya("/abantu/{id}", "DELETE")(UmuntuController.siba)

# Error handlers
@indoro.kubona_gitewe(urubuga.amakosa.NotFoundError)
def not_found(request, inkota):
    subira indoro.imitwaro("amakosa/404.i.html", status=404)

# Background jobs
@indoro.igikorwa(igihe="0 * * * *")  # every hour
def siba_session_zatangiye(request):
    # cleanup expired sessions
    ububiko.Umuntu.hitamwo("session_expire", "<", igihe.ubu()).siba()

# Run
indoro.tangira()
```

---

## 4. Database Models (ibikoresho/)

### umuntu.i (User Model)

```python
# ibikoresho/umuntu.i — Umuntu model

shyiramo ububiko

class Umuntu(ububiko.Ibikoresho):
    """Umuntu — user model for authentication and profiles."""
    _ububiko = "abantu"
    _uzuzanya = ["izina", "email", "jambo"]
    _bihishe = ["jambo"]
    _hindura = {
        "imyaka": "umubumbe",
        "kurangira": "ukuri",
        "itariki_yo_kwiyandikisha": "igihe",
    }
    _imiterere = yego  # auto created_at, updated_at

    # Relationships
    def inkwoko(self):
        """User has one phone."""
        subira self.ifite(Inkwoko)

    def inkono(self):
        """User has many posts."""
        subira self.ifite_birenze(Inkono)

    def uburyo(self):
        """User has many comments."""
        subira self.ifite_birenze(Ikiganiro)

    # Scopes
    def ubusabane_kurangira(self, imibare):
        subira imibare.hitamwo("kurangira", "=", yego)

    def ubusabane_admin(self, imibare):
        subira imibare.hitamwo("ubwoko", "=", "admin")

    # Accessors
    def get_izina_attribute(self, agaciro):
        """Title case name."""
        subira agaciro.title()

    def get_email_attribute(self, agaciro):
        """Lowercase email."""
        subira agaciro.lower()

    # Computed properties
    @property
    def izina_yose(self):
        subira f"{self.izina_rwa} {self.izina_ya_kamere}"
```

### inkwoko.i (Phone Model)

```python
# ibikoresho/inkwoko.i — Inkwoko model (phone)

shyiramo ububiko

class Inkwoko(ububiko.Ibikoresho):
    _ububiko = "inkwoko"
    _uzuzanya = ["numero", "ubwoko"]
    _imiterere = yego

    def umuntu(self):
        """Phone belongs to user."""
        subira self.inyandiko_ya(Umuntu)
```

### inkono.i (Post Model)

```python
# ibikoresho/inkono.i — Inkono model (post)

shyiramo ububiko

class Inkono(ububiko.Ibikoresho):
    _ububiko = "inkono"
    _uzuzanya = ["umutwe", "ubusobanuro", "imimerere", "umuntu_id"]
    _hindura = {
        "imimerere": "ibikubiyemo",
        "itariki_yo_kwandika": "igihe",
    }
    _imiterere = yego

    def umwanditsi(self):
        """Post belongs to user."""
        subira self.inyandiko_ya(Umuntu)

    def ikiganiro(self):
        """Post has many comments."""
        subira self.ifite_birenze(Ikiganiro)

    def ibinyobwa(self):
        """Post has many tags via pivot."""
        subira self.inyandiko_ya_birenze(Igitingo, "inkono_igitingo")

    # Scopes
    def ubusabane_yemerewe(self, imibare):
        subira imibare.hitamwo("imimerere", "=", "yemerewe")

    def ubusabane_igihe(self, imibare, itariki):
        subira imibare.hitamwo("itariki_yo_kwandika", ">=", itariki)
```

---

## 5. Controllers (ububumwe/)

### umuntu.i (User Controller)

```python
# ububumwe/umuntu.i — Umuntu controller

shyiramo urubuga
shyiramo ububiko
shyiramo ibikoresho.Umuntu

class UmuntuController:

    @staticmethod
    def urutonde(request):
        """List all users — GET /abantu"""
        abantu = Umuntu.neya("inkwoko").hitamwo(
            request.query("ukurikije", None),
            yego  # searchable
        ).uryaheje("izina").igitero(20).kigeraho()

        subira urubuga.ijwi.json({
            "abantu": [u.kugaragaza() for u in abantu],
            "ibara": Umuntu.ibara()
        })

    @staticmethod
    def shtura(request):
        """Create user — POST /abantu"""
        # Validate
        ishyirwa = urubuga.urwego.Urwego(request.json(), {
            "izina": "umuntu|ibara:2-50",
            "email": "email|birindwa",
            "jambo": "umuntu|ibara:8+",
        })

        niba ishyirwa.ntabwo_bishoboka:
            subira urubuga.ijwi.json({
                "amakosa": ishyirwa.amakosa
            }, status=422)

        # Create
        umuntu = Umuntu.shyiramo(
            izina=request.json("izina"),
            email=request.json("email"),
            jambo=uburambe.kubika_jambo(request.json("jambo"))
        )

        subira urubuga.ijwi.json({
            "umuntu": umuntu.kugaragaza(),
            "ubumessage": "Umuntu yashyizweho neza"
        }, status=201)

    @staticmethod
    def ibisobanuro(request):
        """Get user — GET /abantu/{id}"""
        umuntu = Umuntu.kubona(request.iparamu("id"))

        niba umuntu ndetse None:
            subira urubuga.ijwi.json({
                "amakosa": "Nta muntu wabonetse"
            }, status=404)

        subira urubuga.ijwi.json({
            "umuntu": umuntu.kugaragaza_neza(["inkwoko", "inkono"])
        })

    @staticmethod
    def hindura(request):
        """Update user — PUT /abantu/{id}"""
        umuntu = Umuntu.kubona(request.iparamu("id"))
        niba umuntu ndetse None:
            subira urubuga.ijwi.json({
                "amakosa": "Nta muntu wabonetse"
            }, status=404)

        umuntu.hindura(request.json_kuri=["izina", "email"])
        umuntu.kubika()

        subira urubuga.ijwi.json({
            "umuntu": umuntu.kugaragaza(),
            "ubumessage": "Umuntu yahinduwe neza"
        })

    @staticmethod
    def siba(request):
        """Delete user — DELETE /abantu/{id}"""
        umuntu = Umuntu.kubona(request.iparamu("id"))
        niba umuntu ndetse None:
            subira urubuga.ijwi.json({
                "amakosa": "Nta muntu wabonetse"
            }, status=404)

        umuntu.siba()
        subira urubuga.ijwi.json({
            "ubumessage": "Umuntu yasibwe neza"
        })
```

### indoro.i (Page Controller)

```python
# ububumwe/indoro.i — Indoro controller (pages)

shyiramo urubuga
shyiramo ibikoresho

class IndoroController:

    @staticmethod
    def urubuga(request):
        """Home page — GET /"""
        subira urubuga.imitwaro("indoro/urubuga.i.html", {
            "indoro": "Indoro ya",
            "umumaro": "Urubuga rw'ibikorwa bya elegance",
            "abakoresha": Umuntu.ibara(),
        })

    @staticmethod
    def abantu(request):
        """Users page — GET /abantu"""
        abantu = Umuntu.kubona_buri().uryaheje("created_at", "igirenga").kigeraho()
        subira urubuga.imitwaro("abantu/urutonde.i.html", {
            "abantu": abantu
        })

    @staticmethod
    def umuntu(request):
        """User profile — GET /abantu/{id}"""
        umuntu = Umuntu.kubona(request.iparamu("id"))
        niba umuntu ndetse None:
            subira urubuga.imitwaro("amakosa/404.i.html", status=404)

        subira urubuga.imitwaro("abantu/ibisobanuro.i.html", {
            "umuntu": umuntu,
            "inkono": umuntu.inkono().kigeraho(),
        })
```

---

## 6. Views/Templates (imitwaro/)

### Template Syntax: I-language native

```html
<!-- imitwaro/indoro/urubuga.i.html -->
<!DOCTYPE html>
<html lang="rw">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ indoro }}</title>
    <link rel="stylesheet" href="/static/css/uburambe.css">
</head>
<body>
    <header>
        <h1>{{ indoro }}</h1>
        <nav>
            <a href="/">Urubuga</a>
            <a href="/abantu">Abantu</a>
            <a href="/kwinjira">Kwinjira</a>
        </nav>
    </header>

    <main>
        <h2>{{ umumaro }}</h2>
        <p>Haraho abantu <strong>{{ abakoresha }}</strong> kuri uru rubuga.</p>
    </main>

    <!-- Component inclusion -->
    <%- include("imigabane/umutwempangano.i.html") %>
</body>
</html>
```

### Template features:

```html
<!-- Variable interpolation -->
<h1>{{ izina }}</h1>

<!-- Conditionals -->
<niba kurangira == yego>
    <span class="badge">Yemejwe</span>
<cyangwa>
    <span class="badge">Bidatumijwe</span>
<iherezo>

<!-- Loops -->
<kuri umuntu muri abantu>
    <div class="card">
        <h3>{{ umuntu.izina }}</h3>
        <p>{{ umuntu.email }}</p>
    </div>
<iherezo>

<!-- Partials/Components -->
<%- include("imigabane/umutwempangano.i.html") %>

<!-- Raw HTML -->
<% rawhtml %>
<div>{{{ raw_html_content }}}</div>
<% endrawhtml %>

<!-- Form helpers -->
<form method="POST" action="/abantu">
    <input type="text" name="izina" value="{{ old('izina') }}">
    <%- errors.izina %>
    <button type="submit">Ongeraho</button>
</form>
```

---

## 7. Authentication (kwemeza)

### Built-in auth routes

```python
# app.i — with authentication

shyiramo urubuga
shyiramo urubuga.kwemeza

indoro = urubuga.Indoro("indoro.ya")

# Enable authentication with one line
urubuga.kwemeza.tangura(indoro, {
    "umubiko": "abantu",
    "inyandiko": ["izina", "email", "jambo"],
    "inyandiko_yo_kwemeza": ["email", "jambo"],
    "inyandiko_yo_gufungura": ["izina", "email"],
})

# This automatically creates:
# GET  /kwinjira          — Login page
# POST /kwinjira          — Login handler
# GET  /kwiyandikisha     — Register page
# POST /kwiyandikisha     — Register handler
# POST /gufunga           — Logout handler
# GET  /profile           — Profile page
# PUT  /profile           — Profile update

# Protected routes
@indoro.umwanya("/dashboard")
@urubuga.kwemeza.rihwaho  # requires login
def dashboard(request):
    subira urubuga.imitwaro("dashboard.i.html", {
        "umuntu": request.umuntu  # current user
    })

# Admin-only routes
@indoro.umwanya("/admin")
@urubuga.kwemeza.admin  # requires admin role
def admin(request):
    subira urubuga.imitwaro("admin.i.html")
```

### User registration form:

```html
<!-- imitwaro/ubushyingizi/kwiyandikisha.i.html -->
<form method="POST" action="/kwiyandikisha">
    <%- amabanga_csrf() %>

    <div class="urubuga">
        <label for="izina">Izina ry'ukoresha</label>
        <input type="text" id="izina" name="izina"
               value="{{ old('izina') }}" required>
        <%- errors.izina %>
    </div>

    <div class="urubuga">
        <label for="email">Email</label>
        <input type="email" id="email" name="email"
               value="{{ old('email') }}" required>
        <%- errors.email %>
    </div>

    <div class="urubuga">
        <label for="jambo">Ijambo ry'ibanga</label>
        <input type="password" id="jambo" name="jambo" required>
        <%- errors.jambo %>
    </div>

    <button type="submit" class="bwomeka">Iyandikishe</button>
</form>
```

---

## 8. Forms & Validation (urwego)

### Server-side validation

```python
# Validation in controller
@staticmethod
def shtura(request):
    ishyirwa = urubuga.urwego.Urwego(request.json(), {
        "izina": "umuntu|ibara:2-50",
        "email": "email|birindwa",
        "jambo": "umuntu|ibara:8+",
        "imyaka": "umubumbe|ibiri:18-120",
        "ahantu": "umuntu|gisanzwe:Kigali",
    })

    niba ishyirwa.ntabwo_bishoboka:
        subira urubuga.ijwi.json({
            "amakosa": ishyirwa.amakosa
        }, status=422)
```

### Form request classes (advanced)

```python
# urwego/ishyirwa_umuntu.i

shyiramo urubuga

class IshyirwaUmuntu(urubuga.UrwegoRwIshyirwa):
    """Validate user creation request."""

    def imibare_yo_guhindura(self):
        subira {
            "izina": "umuntu|ibara:2-50",
            "email": "email|birindwa",
            "jambo": "umuntu|ibara:8+|ntabwo_birambuye:yego",
            "imyaka": "umubumbe|ibiri:18-120",
        }

    def ubusobanuro(self):
        subira {
            "izina": "Izina ry'ukoresha",
            "email": "Aderesi ya email",
            "jambo": "Ijambo ry'ibanga",
            "imyaka": "Imyaka",
        }
```

---

## 9. Real-time Features (amahera)

### WebSocket

```python
# app.i — real-time features

shyiramo urubuga
shyiramo urubuga.amahera

indoro = urubuga.Indoro("indoro.ya")

# WebSocket manager
amahera = urubuga.amahera.Amahera(indoro)

@amahera.kwinjira("ijwi")
def on_message(indwi, data):
    """Broadcast message to all connected clients."""
    amahera.yashyira("ijwi", data)

@amahera.kwinjira("uburyo")
def on_join(indwi, data):
    """Join a room."""
    indwi.kwinjira_icyumba(data["icyumba"])

@amahera.gufunga("ijwi")
def on_leave(indwi):
    """Handle disconnect."""
    pass
```

### Server-Sent Events

```python
# Real-time notifications
@indoro.umwanya("/amakuru")
def amakuru_bose(request):
    """SSE endpoint for notifications."""
    def generate():
        while True:
            # Send notification
            yield f"data: {json.dumps({'ubumessage': 'amakuru maze'})}\n\n"

    subira urubuga.amahera.SSE(generate())
```

---

## 10. File Uploads (amadosiye)

```python
# File upload handler
@indoro.umwanya("/kubika_amafoto", "POST")
@urubuga.kwemeza.rihwaho
def kubika_amafoto(request):
    """Upload profile photo."""
    ifoto = request.ifoto("ifoto")

    # Validate
    niba ifoto.ubwoko not in ["image/jpeg", "image/png", "image/webp"]:
        subira urubuga.ijwi.json({
            "amakosa": "Ubwoko bw'ifoto bushobora kuba JPEG, PNG cyangwa WebP"
        }, status=422)

    niba ifoto.uburengero > 5 * 1024 * 1024:  # 5MB
        subira urubuga.ijwi.json({
            "amakosa": "Ifoto ntigomba kuba nini kuruta 5MB"
        }, status=422)

    # Store
    indenga = urubuga.amadosiye.kubika(
        ifoto,
        ahantu="public/amafoto",
        izina=None  # auto-generate name
    )

    # Update user
    request.umuntu.ifoto = indenga
    request.umuntu.kubika()

    subira urubuga.ijwi.json({
        "indenga": indenga,
        "ubumessage": "Ifoto yashyizweho neza"
    })
```

---

## 11. API Development (API)

### REST API with resource controllers

```python
# RESTful routes
from urubuga import ijwi

@indoro.igice("/api/v1")
def api_v1(api):
    # Auto-generates full CRUD
    api.inkono("/abantu", UmuntuResource)
    api.inkono("/inkono", InkonoResource)
    api.inkono("/amakuru", AmakuruResource)

# Resource controller
class UmuntuResource(urubuga.Resource):
    """Full REST resource for users."""

    def index(self, request):
        """GET /api/v1/abantu"""
        abantu = Umuntu.kigeraho()
        subira ijwipaginate(abantu)

    def store(self, request):
        """POST /api/v1/abantu"""
        umuntu = Umuntu.shyiramo(**request.validated)
        subira ijwi(umuntu.kugaragaza(), status=201)

    def show(self, request, id):
        """GET /api/v1/abantu/{id}"""
        umuntu = Umuntu.kubona(id)
        subira ijwi(umuntu.kugaragaza_neza())

    def update(self, request, id):
        """PUT /api/v1/abantu/{id}"""
        umuntu = Umuntu.kubona(id)
        umuntu.hindura(**request.validated)
        umuntu.kubika()
        subira ijwi(umuntu.kugaragaza())

    def destroy(self, request, id):
        """DELETE /api/v1/abantu/{id}"""
        Umuntu.kubona(id).siba()
        subira ijwi(None, status=204)
```

---

## 12. Background Jobs (imirimo)

```python
# mirimo/herekana_email.i

shyiramo urubuga
shyiramo urubuga.mirimo

class HerekanaEmail(urubuga.mirimo.Igikorwa):
    """Send welcome email after registration."""

    def __init__(self, umuntu_id):
        self.umuntu_id = umuntu_id

    def gutegurwa(self):
        """Retry on failure."""
        subira self.gukosha_5()

    def gutegurwa(self, igihe):
        """Delay before execution."""
        subira self.gutegeka(60)  # 60 seconds

    def kwinjira(self):
        """Execute the job."""
        umuntu = Umuntu.kubona(self.umuntu_id)
        urubuga.amakuru.yohereza(
            kuri=umuntu.email,
            umutwe="Murakaza neza!",
            ubusobanuro=f"Muraho {umuntu.izina}, murakaza neza kuri indoro.ya"
        )

# Dispatch job
urubuga.mirimo.tegura(HerekanaEmail(umuntu.id))

# Or chain jobs
urubuga.mirimo.tegura(
    HerekanaEmail(umuntu.id)
    .himbira(HerekanaAmakuru(umuntu.id))
    .himbira(HerekanaAmabanga(umuntu.id))
)
```

---

## 13. Testing (imenyanya)

```python
# test/test_umuntu.i

shyiramo urubuga.menyanya
shyiramo ibikoresho.Umuntu

class TestUmuntu(menyanya.Umenyanya):

    def test_kubika_umuntu(self):
        """Test creating a user."""
        umuntu = Umuntu.shyiramo(
            izina="Jean",
            email="jean@example.com",
            jambo="password123"
        )
        self.imenya(umuntu.id)
        self.imenya(umuntu.izina, "Jean")

    def test_kubona_umuntu(self):
        """Test finding a user."""
        Umuntu.shyiramo(izina="Alice", email="a@b.com")
        umuntu = Umuntu.kubona(1)
        self.imenya(umuntu.izina, "Alice")

    def test_siba_umuntu(self):
        """Test deleting a user."""
        umuntu = Umuntu.shyiramo(izina="Bob", email="b@b.com")
        umuntu.siba()
        self.ikibazo(Umuntu.kubona(umuntu.id) is None)
```

```bash
# Run tests
isoko urubuga test
# or
isoko urubuga test --imenyanya=TestUmuntu
```

---

## 14. Development Server

```bash
# Start dev server with hot reload
isoko urubuga dev

# Output:
# Murakaza neza kuri indoro.ya!
# Indoro iri gutangira kuri http://localhost:8000
# Debug mode: yego
# Ububiko: indoro_ya.db
# Hot reload: yego
```

---

## 15. Build & Deploy

```bash
# Build for production
isoko urubuga kubaka

# Analyze project
isoko urubuga isuzumisha

# Health check
isoko urubuga dokotere
```

---

## Complete Example: Building a Blog

```bash
# 1. Create project
isoko urubuga tangura blog.ya --ubwoko=indoro

# 2. Create model
isoko urubuga model Inkono
# Creates: ibikoresho/inkono.i with template

# 3. Create migration
isoko urubuga guhindura shtura_inkono
# Creates: icyerekezo/001_shtura_inkono.i

# 4. Run migration
isoko urubuga guhindura kwinjira

# 5. Create controller
isoko urubuga ububumwe Inkono
# Creates: ububumwe/inkono.i with CRUD

# 6. Create views
isoko urubuga imitwaro inkono
# Creates: imitwaro/inkono/ with list, show, create, edit

# 7. Start development
isoko urubuga dev

# 8. Open browser → http://localhost:8000/inkono
```

### The blog.i app file:

```python
# app.i — Blog ya

shyiramo urubuga

indoro = urubuga.Indoro("blog.ya", debug=yego)

# Home page
@indoro.umwanya("/")
def urubuga(request):
    inkono = Inkono.neya("umwanditsi").ubusabane_yemerewe().kigeraho()
    subira urubuga.imitwaro("urubuga.i.html", {"inkono": inkono})

# Blog posts
@indoro.umwanya("/inkono")
def urutonde(request):
    inkono = Inkono.uryaheje("created_at", "igirenga").igitero(10).kigeraho()
    subira urubuga.imitwaro("inkono/urutonde.i.html", {"inkono": inkono})

@indoro.umwanya("/inkono/{slug}")
def ibisobanuro(request):
    inkono = Inkono.hitamwo("slug", "=", request.iparamu("slug")).kona()
    subira urubuga.imitwaro("inkono/ibisobanuro.i.html", {"inkono": inkono})

# Enable auth
urubuga.kwemeza.tangura(indoro)

indoro.tangira()
```
