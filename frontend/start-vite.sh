#!/bin/bash
export PATH="$HOME/local/node20/bin:$PATH"
cd /Users/apple/Desktop/Hackaton/frontend
exec node node_modules/vite/bin/vite.js --host 0.0.0.0 --port 3000
