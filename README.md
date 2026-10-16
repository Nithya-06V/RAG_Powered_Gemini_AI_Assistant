# Gemini Desk

A local Flask chatbot with Gemini responses, persistent conversation history, and a real retrieval-augmented generation (RAG) pipeline. Documents are parsed, split into overlapping chunks, embedded with Google's Gemini embedding model, stored in Chroma, and retrieved by semantic similarity before document-grounded questions are sent to Gemini.

## Project layout

```text
app.py                    Flask routes and application factory
config.py                 Environment-based configuration
database.py               SQLite schema and demo account initialization
document_processor.py     PDF, DOCX, CSV, TXT, and Markdown extraction/chunking
gemini_service.py         Official Google Gen AI SDK calls
rag_pipeline.py           Gemini embeddings and persistent Chroma search
init_db.py                Optional explicit SQLite initialization
requirements.txt          Python dependencies
.env.example              Safe environment-variable template
templates/                Login, dashboard, chat, documents, settings
static/css/style.css      Responsive UI styles
static/js/                Chat, document, and settings interactions
instance/                 Local SQLite database (created at runtime)
uploads/                  Private original uploads (created at runtime)
vector_store/             Persistent Chroma vectors (created at runtime)
tests/                    Focused application tests
```

SQLite is the supported local database and is created automatically. MySQL is not enabled in this starter project, so MySQL Workbench is not required. This keeps setup independent of a database server while preserving a clear path to add MySQL later.

## Windows and VS Code setup

Open the project folder (`E:\rag model`) in VS Code, then run these commands in a PowerShell terminal:

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks virtual-environment activation, allow it for the current terminal only, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

In `.env`, replace `FLASK_SECRET_KEY` with a long random value. Set `DEMO_USERNAME` and `DEMO_PASSWORD` before the first database initialization if you want different local demo credentials. The default `admin` / `admin123` is for local demonstration only; passwords are stored as hashes. Never use the defaults or Flask's development server for a public deployment.

## Gemini API key

1. Create an API key in [Google AI Studio](https://aistudio.google.com/apikey).
2. Start the app using the commands below and sign in.
3. Open **Settings**, enter the key, and choose **Test key** or **Save key**. Saving writes it to the local `.env`; it is not stored in SQLite, browser storage, page source, or API responses. The input clears after saving.

You can also set `GEMINI_API_KEY` directly in `.env`. The default text model is `gemini-3.5-flash-lite` and the embedding model is `gemini-embedding-001`; change `GEMINI_MODEL` or `GEMINI_EMBEDDING_MODEL` in `.env` if your API project uses different supported models. Restart Flask after editing `.env` by hand. Without a key, login, dashboard, chat history, and document management still load; AI answers and indexing show a clear setup message.

## Initialize and run

With `.venv` active:

```powershell
python init_db.py
python app.py
```

Open **http://127.0.0.1:5000**. The Flask app also initializes the SQLite schema automatically on startup. Sign in with `admin` / `admin123` unless changed before the first initialization.

To run the focused tests:

```powershell
python -m unittest discover -s tests -v
```

## Try the app

Upload a PDF, DOCX, CSV, TXT, or Markdown file from **RAG documents**. The original file stays under the private, Git-ignored `uploads/` folder so it can be re-indexed. Chunks and embeddings are stored in the Git-ignored `vector_store/`. Uploading requires a working Gemini API key because embedding generation uses Gemini.

Example questions:

- General AI: `What are three ways to make a Python script easier to maintain?`
- Document retrieval: `According to my uploaded policy, how long can a user retain a record?`
- Python code: `Write a complete Python program that reads a CSV and prints each column's missing-value count. Explain how to run it in VS Code.`
- Debugging: paste a traceback and ask what caused it and how to fix it.

When relevant chunks are found, the response includes source filename and page or chunk references. If no chunks are relevant, the assistant does not claim that it used retrieval. Generated code is displayed as text and is never executed by the app.

## Data and security notes

- `instance/`, `uploads/`, `vector_store/`, `.env`, and Python caches are excluded from Git.
- Login is session-based; chats and documents are scoped to the signed-in user's database ID. State-changing forms and JSON requests use CSRF protection.
- The demo account is seeded on first database creation. Change demo credentials before that first run; changing `.env` afterward does not rewrite an existing password hash.
- The local Settings form can save the key to `.env`. Keep the file private and never commit it. Use HTTPS, a strong secret, managed identity/secrets, production-grade password management, and a production WSGI server before deployment.
- Upload limit is 16 MB. Scanned PDFs without an embedded text layer may need OCR before upload.

## Troubleshooting

- **`py` is not recognized:** install Python 3 from python.org and enable the Windows Python Launcher, then reopen VS Code.
- **Activation is blocked:** use the current-terminal `Set-ExecutionPolicy` command above; it does not change the machine-wide policy.
- **Gemini says the key is invalid:** create a key in AI Studio, confirm the corresponding project/API access, and save it again in Settings.
- **Quota or model errors:** check the Google AI project quota and update `GEMINI_MODEL` or `GEMINI_EMBEDDING_MODEL` in `.env` to a model available to that project.
- **Network errors:** check internet access, proxy/firewall settings, and retry the key test.
- **Embedding or upload errors:** confirm a key is saved, the file is under 16 MB and readable, and the upload format is supported. Re-index from the document list after fixing configuration.
- **No document answer:** verify the document status is `ready`; PDFs need selectable text. Ask a focused question using wording found in the file.
- **SQLite errors:** stop Flask, verify the project directory is writable, then inspect `instance/app.db`. The database is local and can be backed up before repair.
- **Can't install a package:** activate `.venv`, upgrade pip, and retry `python -m pip install -r requirements.txt`. Chroma and pandas can take longer than small Flask packages to install.
