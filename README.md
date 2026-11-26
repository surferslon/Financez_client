# Financez client

Tiny web app that only stores new entries. The main Financez app picks them up (and removes them here)
when its main page is loaded.

## Deploy
1. `cp .env.example .env` and fill in the values.
2. `docker compose up -d --build`
3. Put an HTTPS reverse proxy in front of `127.0.0.1:8000`. The login cookie is only sent over HTTPS.
4. In the `.env` of Financez set:

       CLIENT_URL=https://your-client.example.com
       CLIENT_SYNC_TOKEN=<same as SYNC_TOKEN>

5. Log in to Financez and open its main page: this sends your user, accounts and currencies to the client.
6. Log in to the client with the same username and password.

Financez sends password **hashes** to the client, so it only talks to `https://` (or localhost) addresses.
Every Financez user who opens the main page gets a login on the client, with separate entries.
A changed password takes effect on the client the next time that user opens the Financez main page.

## Logs
Logins, new entries and every sync request are logged to stderr (`docker compose logs -f client`).
Financez logs its side of the sync to its console under `entries.services`.

## Layout
    app/
      __init__.py     wires the layers together
      config.py       configuration from the environment
      presentation/   HTTP only: web interface, sync API, templates, static files
      services/       use cases
      repositories/   SQLite, the only place with SQL
      domain/         entry model and validation rules
    tests/

Dependencies point downwards: presentation -> services -> repositories. All of them may use the domain.
Services and repositories do not know about Flask.

## Test
    pip install -r requirements.txt
    python -m unittest

## Sync API
All requests need `Authorization: Bearer <SYNC_TOKEN>`.

| Request | Body | Purpose |
|---|---|---|
| `PUT /api/users/<username>` | `{"password_hash": "pbkdf2_sha256$...", "accounts": [{id, name, group, depth}], "currencies": [{id, name, selected}]}` | create or update a user |
| `GET /api/users/<username>/entries` | | pending entries of the user |
| `POST /api/users/<username>/entries/delete` | `{"ids": [...]}` | remove imported entries |
