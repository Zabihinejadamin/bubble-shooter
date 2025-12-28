# Element Bubble Arena - Python/Kivy Version

A bubble shooter game built with Python and Kivy, designed for Android mobile devices.

## 🎮 Game Features

- **Element-Based Bubbles**: Fire, Water, Earth, Air
- **Touch Controls**: Aim and shoot by touching the screen
- **Color Matching**: Match 3+ bubbles of the same element
- **Physics-Based**: Realistic bubble movement and collision
- **Cross-Platform**: Works on desktop (for testing) and Android

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Install Kivy:**
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install kivy
```

2. **Run the game:**
```bash
python main.py
```

## 📱 Building for Android

### Using Buildozer

1. **Install Buildozer:**
```bash
pip install buildozer
```

2. **Initialize buildozer:**
```bash
buildozer init
```

3. **Edit `buildozer.spec`** to configure your app

4. **Build APK:**
```bash
buildozer android debug
```

5. **Install on device:**
```bash
adb install bin/*.apk
```

## 🎯 How to Play

1. **Touch and drag** to aim
2. **Release** to shoot bubble
3. **Match 3+ bubbles** of the same element to pop them
4. **Clear all bubbles** to win!

## 📁 Project Structure

```
.
├── main.py              # Application entry point
├── game.py              # Main game logic
├── requirements.txt     # Python dependencies
├── buildozer.spec      # Build configuration (after buildozer init)
└── README.md           # This file
```

## 🛠️ Development

### Testing on Desktop

Run directly:
```bash
python main.py
```

### Testing on Android

1. Connect Android device via USB
2. Enable USB debugging
3. Build and install using Buildozer (see above)

## 📝 Code Structure

- `main.py`: Creates the Kivy app and sets up the game window
- `game.py`: Contains all game logic:
  - `Bubble`: Represents a single bubble
  - `BubbleShooterGame`: Main game widget with all game mechanics

## 🎨 Element System

- **Fire** (Orange/Red): Classic bubble
- **Water** (Blue): Classic bubble
- **Earth** (Brown): Classic bubble
- **Air** (Light Blue): Classic bubble

*Element interactions can be added later*

## 🔧 Customization

Edit `game.py` to customize:
- Bubble colors
- Grid size
- Bubble speed
- Game mechanics

## 📚 Resources

- [Kivy Documentation](https://kivy.org/doc/stable/)
- [Buildozer Documentation](https://buildozer.readthedocs.io/)

## 🆘 Troubleshooting

### Kivy Installation Issues

On Windows, you might need:
```bash
python -m pip install --upgrade pip wheel setuptools
python -m pip install docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew
python -m pip install kivy
```

### Buildozer Issues

Make sure you have:
- Android SDK installed
- Android NDK installed
- Python-for-Android set up

---

**Enjoy building your bubble shooter game!** 🎉
