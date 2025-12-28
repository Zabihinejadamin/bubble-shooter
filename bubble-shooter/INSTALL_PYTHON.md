# Python Installation Guide

## ✅ Step-by-Step Setup

### Step 1: Check Python Installation

Open terminal/command prompt and check:
```bash
python --version
```

You need **Python 3.8 or higher**.

**If Python is not installed:**
- Download from: https://www.python.org/downloads/
- **Important:** Check "Add Python to PATH" during installation!

### Step 2: Install Kivy

#### Windows:

```bash
python -m pip install --upgrade pip wheel setuptools
python -m pip install docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew
python -m pip install kivy
```

#### Mac:

```bash
pip3 install kivy
```

#### Linux:

```bash
sudo apt-get install python3-pip
pip3 install kivy
```

### Step 3: Verify Installation

Test if Kivy works:
```bash
python -c "import kivy; print(kivy.__version__)"
```

Should print the Kivy version number.

### Step 4: Run the Game

```bash
python main.py
```

A window should open with the bubble shooter game!

## 🐛 Common Issues

### "python: command not found"

**Solution:**
- Windows: Try `py` instead of `python`
- Mac/Linux: Make sure Python is in PATH

### "pip: command not found"

**Solution:**
- Windows: Use `python -m pip` instead of `pip`
- Mac/Linux: Try `pip3` instead of `pip`

### "kivy installation failed"

**Solution:**
1. Update pip: `python -m pip install --upgrade pip`
2. Install dependencies first (see Step 2)
3. Check Python version: `python --version`

### "ModuleNotFoundError: No module named 'kivy'"

**Solution:**
- Make sure Kivy installed successfully
- Try: `python -m pip install kivy --upgrade`
- Check you're using the same Python where Kivy is installed

## ✅ Success Checklist

- [ ] Python 3.8+ installed
- [ ] Kivy installed successfully
- [ ] Can run `python main.py`
- [ ] Game window opens
- [ ] Can see bubbles on screen

---

**Once Python and Kivy are installed, just run `python main.py`!**

