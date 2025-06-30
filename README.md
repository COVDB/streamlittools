# Gereedschappenbeheer (Offline)

Deze Streamlit-app laat je een geëxporteerde SharePoint-lijst (Excel of CSV) uploaden en een PDF genereren met een overzicht van gereedschappen.

## Bestanden

- `app.py`: de main Streamlit-app.
- `requirements.txt`: Python dependencies.
- `.gitignore`: bestanden die niet in Git moeten.
- `.streamlit/secrets.toml.example`: voorbeeld voor je secrets-configuratie.

## Installatie

```bash
git clone https://github.com/gebruikersnaam/repo.git
cd repo
pip install -r requirements.txt
```

## Gebruik

1. Maak een bestand `.streamlit/secrets.toml` gebaseerd op het voorbeeld:
   ```toml
   # secrets.toml
   # Voor nu niet nodig, maar later voor Azure of andere API keys
   ```
2. Start de app:
   ```bash
   streamlit run app.py
   ```
3. Upload je geëxporteerde SharePoint-list (Excel of CSV).
4. Download de gegenereerde PDF.
