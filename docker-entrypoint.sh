#!/bin/bash
set -e

# Reinstall frontend deps if node_modules is empty (wiped by volume mount)
for component in audio pipeline rttm; do
    dir="/app/gryannote/$component/frontend"
    if [ -d "$dir" ] && [ ! -d "$dir/node_modules/@gradio" ]; then
        echo "Installing npm dependencies for $component..."
        cd "$dir" && npm install --prefer-offline 2>/dev/null
    fi
done

cd /app/gryannote/audio
exec "$@"
