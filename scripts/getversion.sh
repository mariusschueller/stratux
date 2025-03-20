#!/bin/bash
# Get latest tag, suppress errors if no tags exist. Use default "0.0.0" as fallback.
VER=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")

# Remove leading 'v' if present
VER=${VER#v}

# Add -dev suffix if working directory has uncommitted changes
if ! git diff-index --quiet HEAD --; then
    VER="${VER}-dev"
fi

echo "$VER"