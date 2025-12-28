# Quick Start Guide - Python Version

## 🚀 Getting Started

### Step 1: Install Python

Make sure you have Python 3.8+ installed:
```bash
python --version
```

### Step 2: Install Kivy

**On Windows:**
```bash
python -m pip install --upgrade pip wheel setuptools
python -m pip install docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew
python -m pip install kivy
```

**On Linux/Mac:**
```bash
pip install kivy
```

Or use requirements.txt:
```bash
pip install -r requirements.txt
```

### Step 3: Run the Game

```bash
python main.py
```

You should see a window with the bubble shooter game!

## 🎮 How to Play

1. **Touch/Drag** on screen to aim
2. **Release** to shoot bubble
3. Match bubbles to pop them!

## 📱 Building for Android

### Option 1: Using Buildozer (Recommended)

1. **Install Buildozer:**
```bash
pip install buildozer
```

2. **Initialize (first time only):**
```bash
buildozer init
```

3. **Build APK:**
```bash
buildozer android debug
```

4. **Install on device:**
```bash
adb install bin/*.apk
```

### Option 2: Using Python-for-Android

More complex but more control. See Kivy documentation.

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'kivy'"

**Solution:**
```bash
pip install kivy
```

### "kivy installation failed"

**Try:**
- Update pip: `python -m pip install --upgrade pip`
- Install dependencies first (see Step 2)
- Check Python version (need 3.8+)

### "Game window doesn't open"

**Check:**
- Look for errors in terminal
- Try: `python main.py` and read error messages
- Make sure Kivy is installed correctly

## 📝 Next Steps

1. ✅ Run `python main.py` to test
2. ✅ Play the game on desktop
3. ✅ Customize colors/mechanics in `game.py`
4. ✅ Build for Android when ready

---

**That's it! Much simpler than Unity setup!** 🎉

