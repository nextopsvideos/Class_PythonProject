#!/bin/bash
set -e
# Use virtualenv python if available, otherwise fallback to system python3/python
if [ -n "${VIRTUAL_ENV-}" ]; then
	export PATH="$VIRTUAL_ENV/bin:$PATH"
	PYTHON="$VIRTUAL_ENV/bin/python"
else
	# Try to locate Oryx-created virtualenv 'antenv' in common locations
	VENV_CANDIDATE=""
	if [ -d "/home/site/wwwroot/antenv" ]; then
		VENV_CANDIDATE="/home/site/wwwroot/antenv"
	else
		for p in /tmp/*/antenv /tmp/antenv ./antenv; do
			[ -d "$p" ] || continue
			VENV_CANDIDATE="$p"
			break
		done
	fi

	if [ -n "$VENV_CANDIDATE" ]; then
		export PATH="$VENV_CANDIDATE/bin:$PATH"
		PYTHON="$VENV_CANDIDATE/bin/python"
	else
		PYTHON=$(command -v python3 || command -v python)
	fi
fi
	echo "Selected python: $PYTHON"
	"$PYTHON" --version || true
	if command -v ldd >/dev/null 2>&1; then
		echo "ldd output (filtering for libpython):"
		ldd "$PYTHON" 2>/dev/null | grep libpython || true
	fi

"$PYTHON" -m pip install --upgrade pip
"$PYTHON" -m pip install psycopg[binary]==3.2.3
"$PYTHON" -m pip install -e src

echo "Running seed_data with 30s timeout..."
timeout 30 "$PYTHON" src/fastapi_app/seed_data.py || {
  EXIT_CODE=$?
  if [ $EXIT_CODE -eq 124 ]; then
    echo "WARNING: seed_data.py timed out (database may be unreachable). Continuing startup..."
  else
    echo "WARNING: seed_data.py exited with code $EXIT_CODE. Continuing startup..."
  fi
}

echo "Starting gunicorn..."
"$PYTHON" -m gunicorn fastapi_app:app -c src/gunicorn.conf.py