# Flutter Installation Guide for BlindStick App

## Quick Installation Steps

### Windows Installation

#### Step 1: Download Flutter SDK
1. Go to https://docs.flutter.dev/get-started/install/windows
2. Download "Flutter SDK" (latest stable version)
3. Extract to: `C:\src\flutter` (or any location without spaces)

#### Step 2: Add Flutter to PATH
1. Open System Properties → Environment Variables
2. Under "User variables", find "Path"
3. Click "Edit" → "New"
4. Add: `C:\src\flutter\bin`
5. Click "OK" to save

#### Step 3: Verify Installation
Open new PowerShell window:
```powershell
flutter --version
```

You should see Flutter version information.

#### Step 4: Run Flutter Doctor
```powershell
flutter doctor
```

This checks your setup and shows what's needed.

### Android Setup (for running on Android phone)

#### Step 1: Install Android Studio
1. Download from: https://developer.android.com/studio
2. Install with default settings

#### Step 2: Install Android SDK
In Android Studio:
1. Tools → SDK Manager
2. Install: Android SDK Platform (API 31+)
3. Install: Android SDK Build-Tools

#### Step 3: Enable USB Debugging on Phone
1. Settings → About Phone
2. Tap "Build Number" 7 times
3. Go back → Developer Options
4. Enable "USB Debugging"

#### Step 4: Connect Phone
1. Connect phone via USB
2. Accept USB debugging prompt on phone
3. Run: `flutter devices`

### iOS Setup (for running on iPhone - requires Mac)

#### Step 1: Install Xcode (Mac only)
1. App Store → Install Xcode
2. Open Xcode, accept license

#### Step 2: Install CocoaPods
```bash
sudo gem install cocoapods
```

#### Step 3: Connect iPhone
1. Trust computer on iPhone
2. Run: `flutter devices`

---

## Running the BlindStick App

### After Flutter Installation:

```powershell
# Navigate to app directory
cd C:\Users\Tashu\OneDrive\Desktop\BlindStick\mobile_app

# Get dependencies
flutter pub get

# Check connected devices
flutter devices

# Run on device
flutter run
```

### Building APK (to install without USB)

```powershell
# Build release APK
flutter build apk --release

# APK location:
# build/app/outputs/flutter-apk/app-release.apk
```

Transfer APK to phone and install.

---

## Alternative: Use Pre-built APK (Easiest!)

If you just want to test the app quickly:

### Option A: Ask for Pre-built APK
I can help you understand how to build it manually, or you can:
1. Find someone with Flutter installed
2. Build once using instructions above
3. Share APK file

### Option B: Use Android Emulator (for testing without phone)

```powershell
# In Android Studio:
1. Tools → Device Manager
2. Create Virtual Device
3. Download system image
4. Start emulator
5. Run: flutter run
```

---

## Troubleshooting

### "flutter command not found"
- Restart terminal after adding to PATH
- Verify: `echo $env:Path` (should include flutter/bin)

### "No devices found"
Android:
- Enable USB debugging
- Try different USB cable/port
- Install USB drivers (Windows)

iOS:
- Trust computer on iPhone
- Make sure iTunes is installed (Windows)

### "Pub get failed"
- Check internet connection
- Delete `pubspec.lock` and try again
- Run: `flutter clean` then `flutter pub get`

### Build errors
- Run: `flutter clean`
- Run: `flutter pub get`
- Run: `flutter doctor` (fix any issues)

---

## Minimum Requirements

### Android
- Android 8.0 (API 26) or higher
- 2GB RAM minimum
- ARM processor recommended

### iOS  
- iOS 12.0 or higher
- iPhone 5s or newer

### Development PC
- Windows 10/11 (64-bit)
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space

---

## Next Steps After Installation

1. ✅ Install Flutter SDK
2. ✅ Run `flutter doctor`
3. ✅ Connect device/emulator
4. ✅ Navigate to mobile_app folder
5. ✅ Run `flutter pub get`
6. ✅ Run `flutter run`

For detailed setup guide, visit: https://docs.flutter.dev/get-started/install

---

**Quick Test Command:**
```powershell
cd C:\Users\Tashu\OneDrive\Desktop\BlindStick\mobile_app
flutter pub get
flutter run
```
