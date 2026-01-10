# Build Instructions for Desktop Application

## Prerequisites

### For Building Executable
- Python 3.8+
- PyInstaller: `pip install pyinstaller`

### For Creating Installer
- Inno Setup 6+ (download from https://jrsoftware.org/isdl.php)
- Windows OS (for creating .exe installer)

## Building Standalone Executable

### Option 1: Automated Build Script
```bash
cd build
python build_gui.py
```

### Option 2: Manual PyInstaller
```bash
cd C:\Users\Space
pyinstaller --name="TrashRouteGenerator" --windowed --onefile gui/trash_route_gui.py
```

The executable will be created at: `dist/TrashRouteGenerator.exe`

## Creating Windows Installer

### Step 1: Build Executable
First, build the standalone executable (see above).

### Step 2: Create Installer with Inno Setup
1. Open Inno Setup Compiler
2. Open `build/create_installer.iss`
3. Click "Build" → "Compile" (or press F9)
4. The installer will be created at: `dist/TrashRouteGenerator-Setup.exe`

### Step 3: Test Installation
1. Run `TrashRouteGenerator-Setup.exe` on a clean Windows machine
2. Install the application
3. Verify desktop shortcut and Start Menu entry
4. Test the application runs correctly

## Distribution Files

After building, you'll have:

- `dist/TrashRouteGenerator.exe` - Standalone executable (portable)
- `dist/TrashRouteGenerator-Setup.exe` - Windows installer (recommended)

## Customization

### Adding Application Icon
1. Create or obtain an `.ico` file
2. Update `gui.spec`:
   ```python
   icon='path/to/icon.ico',
   ```
3. Rebuild

### Changing Installer Settings
Edit `build/create_installer.iss`:
- `AppVersion` - Update version number
- `AppPublisher` - Change publisher name
- `LicenseFile` - Add license file path (optional)

## Troubleshooting

**Problem**: PyInstaller fails with "ModuleNotFoundError"
- **Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

**Problem**: Executable is very large (>100MB)
- **Solution**: This is normal. PyInstaller bundles Python + all dependencies. Use UPX compression if needed.

**Problem**: Inno Setup not found
- **Solution**: Download and install from https://jrsoftware.org/isdl.php

**Problem**: Executable doesn't run on other Windows machines
- **Solution**: Test on clean Windows 10/11 VM. May need to include Visual C++ redistributables.

## Testing Checklist

- [ ] Executable runs on development machine
- [ ] Executable runs on clean Windows 10 machine
- [ ] Installer installs correctly
- [ ] Desktop shortcut works
- [ ] Start Menu entry works
- [ ] Uninstaller works
- [ ] GUI opens and functions correctly
- [ ] Route generation works end-to-end
- [ ] Output files are created correctly
