@echo off
echo ================================================
echo  Adding Windows Firewall Exception for Node.js
echo ================================================
echo.
echo This script will allow Node.js to accept incoming connections.
echo Please run this file as Administrator!
echo.
pause

netsh advfirewall firewall add rule name="Node.js (Vite Dev Server)" dir=in action=allow program="C:\Program Files\nodejs\node.exe" enable=yes
netsh advfirewall firewall add rule name="Node.js (Vite Dev Server)" dir=out action=allow program="C:\Program Files\nodejs\node.exe" enable=yes

echo.
echo ✅ Firewall rules added successfully!
echo.
echo Now you can access localhost:3001 in your browser.
echo.
pause
