#!/bin/bash
# Build script that builds both APK (debug) and AAB (release bundle)
# Ensures correct NDK and API versions are used

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

echo "=========================================="
echo "Building Android packages with:"
echo "  NDK: $ANDROIDNDK"
echo "  API: $ANDROIDAPI"
echo "  PATH includes: $HOME/.local/bin, buildozer_env/bin, /usr/bin, /usr/local/bin"
echo "=========================================="
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

BUILDOZER_CMD="/home/aminz/buildozer_env/bin/buildozer"
BUILD_ENV="ANDROIDNDK=/home/aminz/.buildozer/android/platform/android-ndk-r25b ANDROIDAPI=35 PATH=\"$HOME/.local/bin:/home/aminz/buildozer_env/bin:/usr/bin:/usr/local/bin:\$PATH\""

# Build APK (debug version)
echo "=========================================="
echo "Step 1: Building APK (debug)..."
echo "=========================================="
env $BUILD_ENV $BUILDOZER_CMD android debug
APK_EXIT_CODE=$?

if [ $APK_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ APK build completed successfully!"
    echo "   Output: bin/elementbubblearena-0.1-arm64-v8a-debug.apk"
    echo ""
else
    echo ""
    echo "❌ APK build failed with exit code $APK_EXIT_CODE"
    echo ""
fi

# Build AAB (release bundle)
echo "=========================================="
echo "Step 2: Building AAB (release bundle)..."
echo "=========================================="
echo "Note: AAB requires signing keys. If not configured, build may fail."
echo ""

env $BUILD_ENV $BUILDOZER_CMD android release
AAB_EXIT_CODE=$?

if [ $AAB_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ AAB build completed successfully!"
    echo "   Output: bin/elementbubblearena-0.1-arm64-v8a-release-unsigned.aab"
    echo "   (or signed AAB if signing keys are configured)"
    echo ""
else
    echo ""
    echo "⚠️  AAB build completed with exit code $AAB_EXIT_CODE"
    echo "   This may be due to missing signing keys."
    echo "   To create signed AAB for Google Play, configure signing in buildozer.spec"
    echo ""
fi

# Summary
echo "=========================================="
echo "Build Summary:"
echo "=========================================="
if [ $APK_EXIT_CODE -eq 0 ]; then
    echo "✅ APK: SUCCESS"
else
    echo "❌ APK: FAILED"
fi

if [ $AAB_EXIT_CODE -eq 0 ]; then
    echo "✅ AAB: SUCCESS"
else
    echo "⚠️  AAB: See notes above (may need signing configuration)"
fi

echo ""
echo "Check bin/ directory for output files"
echo "=========================================="

