# Projekt-Regeln (AGENTS.md)

## Planungs- & Implementierungs-Workflow

1. **Keine Direkt-Implementierung ohne Plan:** Code-Änderungen oder Implementierungen dürfen NIEMALS gestartet werden, bevor der Benutzer den erstellten Implementierungsplan (`implementation_plan.md`) gelesen und explizit freigegeben hat.
2. **Immer Implementierungsplan & Tasks erstellen:** Für jede Aufgabe/Anfrage muss zuerst ein detaillierter Implementierungsplan bzw. entsprechende Tasks erstellt werden.
---
name: clean-architecture-developer
description: Implementiert Features nach Clean Architecture Prinzipien mit Fokus auf Single Responsibility, Dependency Injection und Testbarkeit. Aktiviert bei neuen Feature-Implementierungen oder Refactoring-Aufgaben.
---

# Clean Architecture Developer Skill

## Überblick

Dieser Skill implementiert Code nach strengen Clean Architecture Prinzipien. Er stellt sicher, dass jede Komponente klar definierte Verantwortungen hat, Abhängigkeiten explizit verwaltet werden und der Code isoliert testbar bleibt.

## Wann verwenden

- Bei der Implementierung neuer Features
- Beim Refactoring bestehender Codebasis
- Bei der Erstellung neuer Klassen oder Module
- Wenn Code zu komplex oder unübersichtlich wird
- Bei der Überarbeitung von God-Klassen

## Implementierungsregeln

### 1. Single Responsibility Principle (SRP)

**Prüfung:**
- Hat die Klasse nur eine technische Verantwortung?
- Vermischt sie Business-Logik mit Infrastruktur-Code?
- Kann ich klar benennen, was diese Klasse tut?

**Umsetzung:**
- Erstelle separate Komponenten für:
  - Speicherung (Store)
  - HTTP-Kommunikation (Client)
  - Browser-Interaktion (Launcher)
  - Konfiguration (Config)
  - Logging (Logger)

### 2. Orchestratoren klein halten

**Checkliste:**
- Klasse maximal 60–80 Zeilen
- Methoden maximal 15–20 Zeilen
- Nur Koordination, keine technische Implementierung

**Muster:**
```python
class FeatureManager:
    def __init__(self, service, store, logger):
        self._service = service
        self._store = store
        self._logger = logger

    def execute(self, data):
        self._logger.info("Starte Ausführung")
        result = self._service.process(data)
        self._store.save(result)
        return result
```

### 3. Keine direkten externen Abhängigkeiten

**Vorher (FALSCH):**
```python
class Service:
    def __init__(self):
        self.client = requests.Client()  # Direkte Erzeugung
        self.browser = webbrowser        # Direkter Zugriff
```

**Nachher (RICHTIG):**
```python
class Service:
    def __init__(self, http_client, browser_launcher):
        self._http_client = http_client
        self._browser = browser_launcher
```

### 4. Dependency Injection

**Injiziere alle externen Abhängigkeiten:**
- HTTP Clients
- Dateisystem-Operationen
- Datenbankverbindungen
- Browser
- APIs
- Zeitquellen
- Konfiguration

**Ziel:** Unit Tests ohne echte Infrastruktur

### 5. Keine globalen Zustände

**Verboten:**
- Globale Variablen für Status
- Klassenvariablen für Laufzeitdaten
- Singletons ohne triftigen Grund

**Erlaubt:**
- Instanzvariablen
- Events/Queues
- Futures
- Rückgabewerte

### 6. Datenmodelle statt Dictionaries

**Vorher (FALSCH):**
```python
user["name"] = "Max"
user["email"] = "max@example.com"
```

**Nachher (RICHTIG):**
```python
@dataclass
class User:
    name: str
    email: str
```

### 7. Konfiguration extern halten

**Verboten:**
```python
class Service:
    def __init__(self):
        load_env()               # NEIN!
        self.config = Config()   # NEIN!
```

**Erlaubt:**
```python
# App-Start
env = load_env()
config = AppConfig(env)
service = Service(config)
```

### 8. Konstanten zentralisieren

**Betroffene Elemente:**
- URLs
- Dateipfade
- API-Endpunkte
- Timeouts
- Magische Zahlen

**Umsetzung:**
```python
class ApiEndpoints:
    TOKEN = "https://api.example.com/token"
    USER = "https://api.example.com/user"
```

### 9. Logging und Ausgabe trennen

**Regeln:**
- Libraries/Services → Nur Logging
- CLI/UI → Entscheidet über Benutzerausgaben
- Keine Mischung von `print()` und `logger`

### 10. Kleine Methoden bevorzugen

**Ein guter Workflow:**
```python
def authenticate(self):
    url = self._build_url()
    code = self._wait_for_callback(url)
    token = self._exchange_token(code)
    self._save_token(token)
    return token
```

### 11. Fehler explizit behandeln

**Verboten:**
```python
try:
    response = self._http_client.get(url)
except Exception:  # Zu allgemein
    self._logger.error("Fehler aufgetreten")
```

**Erlaubt:**
```python
try:
    response = self._http_client.get(url)
except HTTPError as e:
    self._logger.error(f"HTTP-Fehler: {e}")
    raise
except TimeoutError as e:
    self._logger.warning(f"Timeout beim Request: {e}")
    raise
except JSONDecodeError as e:
    self._logger.error(f"Ungültige Antwort: {e}")
    raise
except OSError as e:
    self._logger.error(f"Systemfehler: {e}")
    raise
```

### 12. Infrastruktur kapseln

**Jede Infrastruktur erhält eigene Klasse:**

```python
class TokenStore:
    def load(self): ...
    def save(self, token): ...
    def clear(self): ...
    def exists(self): ...

class ApiClient:
    def get(self, url): ...
    def post(self, url, data): ...

class BrowserLauncher:
    def open(self, url): ...
```

**Gegen Interfaces injizieren, nicht gegen konkrete Klassen:**

Damit Implementierungen austauschbar bleiben (z. B. echter `ApiClient` vs. `FakeApiClient` in Tests), sollten Abhängigkeiten wo möglich gegen ein Interface/Protocol typisiert werden statt gegen eine konkrete Klasse:

```python
from typing import Protocol

class HttpClient(Protocol):
    def get(self, url: str) -> dict: ...
    def post(self, url: str, data: dict) -> dict: ...

class Service:
    def __init__(self, http_client: HttpClient):
        self._http_client = http_client
```

### 13. Testbarkeit als Designziel

**Checkliste:**
- Keine versteckten Abhängigkeiten
- Keine direkten Systemzugriffe
- Keine globalen Zustände
- Keine Seiteneffekte im Konstruktor

### 14. Dateistruktur nach Verantwortlichkeiten

**Struktur:**
```
feature/
├── feature_manager.py    # Orchestrierung
├── feature_service.py    # Business-Logik
├── feature_store.py      # Persistierung
├── feature_model.py      # Datenmodelle
├── feature_config.py     # Konfiguration
├── feature_adapter.py    # Externe Integration
└── tests/
    ├── test_feature_manager.py
    ├── test_feature_service.py
    └── fakes.py           # Fake-/Stub-Implementierungen für Tests
```

### 15. Neue Features vertikal schneiden

**Vorgehen:**
1. Neue Verantwortung identifizieren
2. Neue Klasse erstellen
3. Bestehende Klasse orchestriert nur

### 16. Änderungen zuerst analysieren

**Analyse-Schritte:**
1. Bestehende Verantwortlichkeiten prüfen
2. Neue Klasse benötigt?
3. Bestehende Klasse überlastet?
4. Abhängigkeiten identifizieren
5. Erst dann implementieren

### 17. Clean Architecture Priorität

**Schichten (von innen nach außen):**
1. Domain-Logik
2. Use Cases / Services
3. Interfaces / Abstraktionen
4. Infrastruktur
5. UI / CLI

**Regel:** Abhängigkeiten zeigen immer nach innen

### 18. Ziel jeder Implementierung

**Nach jedem Feature:**
- Weniger Kopplung
- Kleinere Klassen
- Kleinere Methoden
- Bessere Testbarkeit
- Klare Verantwortlichkeiten
- Austauschbare Infrastruktur
- Keine versteckten Seiteneffekte

## Implementierungsablauf

1. **Anforderungsanalyse**
   - Feature verstehen
   - Verantwortlichkeiten identifizieren
   - Abhängigkeiten erkennen

2. **Design**
   - Datenmodelle definieren
   - Schnittstellen entwerfen
   - Komponentenstruktur festlegen

3. **Implementierung**
   - Von innen nach außen entwickeln
   - Tests parallel schreiben
   - Dependency Injection anwenden

4. **Überprüfung**
   - Regeln anwenden
   - Code-Reviews durchführen
   - Testabdeckung prüfen

## Häufige Fehler vermeiden

- Keine God-Klassen erstellen
- Keine versteckten Abhängigkeiten
- Keine fest codierten Pfade/URLs
- Keine globalen Variablen
- Keine unstrukturierten Daten (Dictionaries)
- Keine Vermischung von Verantwortlichkeiten
- Keine leeren oder zu allgemeinen `except`-Blöcke

## Kommandos

- `analyze` – Prüfe bestehenden Code auf Regelverletzungen
- `design` – Erstelle Architekturplan für neues Feature
- `implement` – Implementiere Feature nach Clean Architecture
- `refactor` – Refactoriere bestehenden Code
- `review` – Führe Code-Review durch