# CIPP Fork v2

> Experimenteller Fork von [KelvinTegelaar/CIPP](https://github.com/KelvinTegelaar/CIPP) mit einem komplett neuen FastAPI-Backend als Ersatz fuer die PowerShell Azure Functions.

## Hinweis

Dieses Projekt basiert auf dem grossartigen [CIPP (CyberDrain Improved Partner Portal)](https://github.com/KelvinTegelaar/CIPP) von **Kelvin Tegelaar** und der CIPP-Community. Alle Credits fuer das originale Frontend und die Idee dahinter gehoeren dem urspruenglichen Projekt.

Ich habe diesen Fork **rein aus Lerngruenden und Interesse** erstellt — keine kommerziellen Absichten, kein Unternehmen dahinter. Das einzige Ziel ist es, das Problem mit den langsamen PowerShell-Modul-Downloads beim Backend-Start zu loesen und dabei moderne Technologien zu lernen.

**Was hier anders ist:**
- Backend: FastAPI (Python) statt PowerShell Azure Functions
- Datenbank: PostgreSQL statt Azure Table Storage
- Graph API: Direkte async HTTP Calls statt serielle PS-Cmdlets
- Exchange: Isolierter PS-Runner Container (Module nur einmal beim Build geladen)
- Auth: MSAL OAuth2 mit JWT Sessions statt Azure Static Web Apps

## Original-Projekt

- **CIPP Frontend**: [KelvinTegelaar/CIPP](https://github.com/KelvinTegelaar/CIPP)
- **CIPP Backend (Original)**: [KelvinTegelaar/CIPP-API](https://github.com/KelvinTegelaar/CIPP-API)
- **Dokumentation**: [docs.cipp.app](https://docs.cipp.app)
- **Website**: [cipp.app](https://cipp.app)

## Lizenz

Dieses Projekt steht unter der gleichen [AGPL-3.0 Lizenz](LICENSE.md) wie das Original.
