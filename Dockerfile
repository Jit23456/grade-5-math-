FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8000
EXPOSE 8000
# Pass MATH5_SECRET_KEY and (optionally) GROQ_API_KEY at run time:
#   docker run -p 8000:8000 -e MATH5_SECRET_KEY=... -e GROQ_API_KEY=... -v $PWD/data:/app/data math5
#
# PORT and WEB_CONCURRENCY are read at start-up: a host that assigns its own port
# (Render, Fly, Cloud Run, Koyeb) is followed without editing this file, and a small
# free instance can be held to fewer workers. `exec` keeps gunicorn as PID 1 so it
# still receives stop signals. An AI request can take most of a minute, so each
# worker runs a few threads (one slow request does not hold up the site) and the
# timeout is well above gunicorn's default of 30 seconds.
CMD ["sh", "-c", "exec gunicorn -w ${WEB_CONCURRENCY:-2} --threads 4 --timeout 180 -b 0.0.0.0:${PORT:-8000} --access-logfile - wsgi:application"]
