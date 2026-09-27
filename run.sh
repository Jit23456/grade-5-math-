#!/usr/bin/env bash
# Start the platform under gunicorn. Edit the exports, then: ./run.sh
set -eu
cd "$(dirname "$0")"

# Sign session cookies with a fixed value so teachers stay signed in across restarts.
: "${MATH5_SECRET_KEY:?Set MATH5_SECRET_KEY first, e.g. export MATH5_SECRET_KEY=\$(python3 -c 'import secrets;print(secrets.token_hex(32))')}"

# Switch the AI assistant on by exporting GROQ_API_KEY before running this.
export GROQ_MODEL="${GROQ_MODEL:-openai/gpt-oss-120b}"
PORT="${PORT:-8000}"
WORKERS="${WORKERS:-4}"

if [ -z "${GROQ_API_KEY:-}" ]; then
  echo "note: GROQ_API_KEY is not set, so the AI assistant will be switched off."
fi

exec gunicorn -w "$WORKERS" -b "0.0.0.0:$PORT" --access-logfile - wsgi:application
