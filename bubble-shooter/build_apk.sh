#!/bin/bash
# Build script that ensures correct NDK and API versions are used

cd "$(dirname "$0")"

# Force unset any existing environment variables
unset ANDROIDNDK
unset ANDROIDAPI

# Set correct values explicitly
export ANDROIDNDK=/home/aminz/.buildozer/android/platform/android-ndk-r25b
export ANDROIDAPI=35

# Add local bin and buildozer env bin to PATH so Cython can be found
# Also include system paths for git and other tools
export PATH="$HOME/.local/bin:/home/aminz/buildozer_env/bin:/usr/bin:/usr/local/bin:$PATH"

echo "Building APK with:"
echo "  NDK: $ANDROIDNDK"
echo "  API: $ANDROIDAPI"
echo "  PATH includes: $HOME/.local/bin and buildozer_env/bin"
echo ""

# Verify they're set correctly
if [ "$ANDROIDNDK" != "/home/aminz/.buildozer/android/platform/android-ndk-r25b" ]; then
    echo "ERROR: ANDROIDNDK is not set correctly!"
    exit 1
fi

if [ "$ANDROIDAPI" != "35" ]; then
    echo "ERROR: ANDROIDAPI is not set correctly!"
    exit 1
fi

# Verify Cython is accessible
if ! command -v cython &> /dev/null; then
    echo "WARNING: Cython not found in PATH, but continuing anyway..."
    echo "  Buildozer may show a warning but should continue."
fi

# Run buildozer with explicit environment
env ANDROIDNDK=/home/aminz/.buildozer/android/platform/android-ndk-r25b ANDROIDAPI=35 PATH="$HOME/.local/bin:/home/aminz/buildozer_env/bin:/usr/bin:/usr/local/bin:$PATH" /home/aminz/buildozer_env/bin/buildozer android debug

