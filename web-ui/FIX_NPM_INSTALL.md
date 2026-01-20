# Fix npm install EPERM Error

If you encounter the `EPERM` error where npm tries to create a directory at `C:\`, follow these steps:

## Solution 1: Clear npm cache and retry

```powershell
cd C:\Users\Space\web-ui
npm cache clean --force
npm install
```

## Solution 2: Delete node_modules and package-lock.json (if exists) and reinstall

```powershell
cd C:\Users\Space\web-ui
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue
npm cache clean --force
npm install
```

## Solution 3: Use yarn instead (alternative package manager)

```powershell
cd C:\Users\Space\web-ui
npm install -g yarn
yarn install
```

## Solution 4: Check npm configuration

Check if there's a global .npmrc file causing issues:

```powershell
npm config get prefix
npm config get cache
```

If these point to `C:\`, reset them:

```powershell
npm config set prefix "${APPDATA}\npm"
npm config set cache "${APPDATA}\npm-cache"
```

## Solution 5: Run as Administrator (if not already)

Close PowerShell and reopen as Administrator, then:

```powershell
cd C:\Users\Space\web-ui
npm cache clean --force
npm install
```
