#!/bin/sh
# Run a Lumbung hook script with the first Python 3.8+ that actually works here.
# Linux often has only python3; Windows (Git Bash) often has only python or py, and its python3 may be
# the Microsoft Store stub, so each candidate is tried before use. Hook input stays on stdin.
# Never fails: a missing Python must not break a session.
script="$1"
for py in python3 python "py -3"; do
  if $py -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" </dev/null >/dev/null 2>&1; then
    exec $py "$script"
  fi
done
exit 0
