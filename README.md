# My Flask App

Dieses Projekt ist eine einfache Flask-Anwendung, die es Benutzern ermöglicht, Daten über ein Eingabefeld einzugeben und diese in einer SQLite-Datenbank zu speichern. Die gespeicherten Werte werden am Ende der Seite angezeigt.

## Projektstruktur

```
my-flask-app
├── app.py               # Einstiegspunkt der Anwendung
├── templates
│   └── index.html      # HTML-Template für die Webseite
├── static
│   └── style.css       # CSS-Stile für die Webseite
├── database.db         # SQLite-Datenbank
├── requirements.txt     # Abhängigkeiten für das Projekt
└── README.md           # Dokumentation des Projekts
```

## Installation

1. Klone das Repository oder lade die Dateien herunter.
2. Stelle sicher, dass Python und pip installiert sind.
3. Installiere die benötigten Abhängigkeiten mit folgendem Befehl:

```
pip install -r requirements.txt
```

## Ausführung

Um die Anwendung zu starten, führe den folgenden Befehl aus:

```
python app.py
```

Öffne dann deinen Webbrowser und gehe zu `http://127.0.0.1:5000`, um die Anwendung zu nutzen.

## Nutzung

- Gib einen Wert in das Eingabefeld ein und klicke auf "Speichern".
- Die gespeicherten Werte werden am Ende der Seite angezeigt.