@echo off
chcp 936
setlocal

:: 获取脚本当前目录
set "SCRIPT_DIR=%~dp0"

:: 定义Python压缩包路径和下载URL
set "PYTHON_ZIP_URL=https://mirrors.huaweicloud.com/python/3.9.0/python-3.9.0a6-embed-amd64.zip"
set "PYTHON_ZIP_PATH=%SCRIPT_DIR%python-3.9.0a6-embed-amd64.zip"
set "PYTHON_INSTALL_DIR=%SCRIPT_DIR%Python39"

:: 如果安装目录不存在，则创建该目录
if not exist "%PYTHON_INSTALL_DIR%" mkdir "%PYTHON_INSTALL_DIR%"

:: 下载Python压缩包
echo Downloading Python...
powershell -Command "Invoke-WebRequest '%PYTHON_ZIP_URL%' -OutFile '%PYTHON_ZIP_PATH%'"

:: 解压Python压缩包到安装目录
echo Unpacking Python...
powershell -Command "Expand-Archive -LiteralPath '%PYTHON_ZIP_PATH%' -DestinationPath '%PYTHON_INSTALL_DIR%' -Force"
echo Unpack over

:: 下载 get-pip.py
echo Downloading get-pip.py...
powershell -Command "Invoke-WebRequest https://mirrors.aliyun.com/pypi/get-pip.py -OutFile '%PYTHON_INSTALL_DIR%\get-pip.py'"

:: 安装pip
echo Installing pip...
%PYTHON_INSTALL_DIR%\python.exe %PYTHON_INSTALL_DIR%\get-pip.py

:: 使用reg命令永久性地添加Python和pip的路径到系统环境变量，绕过setx的限制
for /f "tokens=2* delims= " %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path') do (
    set "SYSTEM_PATH=%%b"
)

:: 检查Python安装目录是否已经存在于系统PATH中
echo Checking if Python is in PATH...
echo %SYSTEM_PATH% | findstr /C:"%PYTHON_INSTALL_DIR%" > nul
if %ERRORLEVEL% equ 1 (
    echo Python directory is not in PATH. Adding...
    set "NEW_SYSTEM_PATH=%PYTHON_INSTALL_DIR%;%SYSTEM_PATH%"
) else (
    echo Python directory is already in PATH.
)

:: 检查Scripts目录是否已经存在于系统PATH中
echo Checking if Scripts directory is in PATH...
echo %SYSTEM_PATH% | findstr /C:"%PYTHON_INSTALL_DIR%\Scripts" > nul
if %ERRORLEVEL% equ 1 (
    echo Scripts directory is not in PATH. Adding...
    set "NEW_SYSTEM_PATH=%PYTHON_INSTALL_DIR%\Scripts;%NEW_SYSTEM_PATH%"
) else (
    echo Scripts directory is already in PATH.
)

:: 更新系统PATH
if defined NEW_SYSTEM_PATH (
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path /t REG_EXPAND_SZ /d "%NEW_SYSTEM_PATH%" /f
    if %ERRORLEVEL% equ 0 (
        echo Environment variable set successfully。
    ) else (
        echo Setting environment variable failed：%ERRORLEVEL%。
    )
)
:: 检查设置环境变量是否成功
if %ERRORLEVEL% equ 0 (
    echo Environment variable set successfully。
) else (
    echo Setting environment variable failed：%ERRORLEVEL%。
)

:: 删除下载的文件
del "%PYTHON_ZIP_PATH%"
del "%PYTHON_INSTALL_DIR%\get-pip.py"

:: 结束
endlocal
echo Python 3.9.0a6 and pip installed

:: 定义Java压缩包路径和下载URL
set "JAVA_ZIP_URL=https://d6.injdk.cn/openjdk/openjdk/21/openjdk-21.0.2_windows-x64_bin.zip"
set "JAVA_ZIP_PATH=%~dp0openjdk-21.0.2_windows-x64_bin.zip"
:: 这里使用%~dp0来获取当前脚本所在的完整路径
set "JAVA_INSTALL_DIR=%~dp0Java"

:: 如果Java安装目录不存在，则创建该目录
if not exist "%JAVA_INSTALL_DIR%" mkdir "%JAVA_INSTALL_DIR%"

:: 下载Java压缩包
echo Downloading Java...
powershell -Command "Invoke-WebRequest '%JAVA_ZIP_URL%' -OutFile '%JAVA_ZIP_PATH%'"

:: 解压Java压缩包到安装目录
echo Unpacking Java...
powershell -Command "Expand-Archive -LiteralPath '%JAVA_ZIP_PATH%' -DestinationPath '%JAVA_INSTALL_DIR%' -Force"
echo Unpack over


:: 获取当前系统的PATH环境变量
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path') do (
    set "SYSTEM_PATH=%%b"
)

:: 检查Java bin目录是否已经存在于系统PATH中，并且添加绝对路径
echo Checking if Java bin directory is in PATH...
echo %SYSTEM_PATH% | findstr /I /C:"%JAVA_INSTALL_DIR%\bin" > nul
if %ERRORLEVEL% equ 1 (
    echo Java bin directory is not in PATH. Adding...
    :: 添加完整路径到系统的PATH环境变量中
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path /t REG_EXPAND_SZ /d "%JAVA_INSTALL_DIR%\bin;%SYSTEM_PATH%" /f
    if %ERRORLEVEL% equ 0 (
        echo Java environment variable set successfully.
    ) else (
        echo Setting Java environment variable failed: %ERRORLEVEL%.
    )
) else (
    echo Java bin directory is already in PATH.
)
:: 删除下载的文件
del "%JAVA_ZIP_PATH%"

:: 结束
endlocal
echo Python and Java have been installed and configured.

:: 定义MinGit下载URL和本地路径
set "MINGIT_URL=https://mirrors.huaweicloud.com/git-for-windows/v2.24.1.windows.2/MinGit-2.24.1.2-64-bit.zip"
set "MINGIT_ZIP_PATH=%~dp0MinGit-2.24.1.2-64-bit.zip"
set "MINGIT_INSTALL_DIR=%~dp0MinGit"

:: 下载MinGit
echo Downloading MinGit...
powershell -Command "Invoke-WebRequest '%MINGIT_URL%' -OutFile '%MINGIT_ZIP_PATH%'"

:: 解压MinGit
echo Unpacking MinGit...
powershell -Command "Expand-Archive -LiteralPath '%MINGIT_ZIP_PATH%' -DestinationPath '%MINGIT_INSTALL_DIR%' -Force"

:: 清理下载的ZIP文件
del "%MINGIT_ZIP_PATH%"

:: 获取当前系统的PATH环境变量
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path') do (
    set "SYSTEM_PATH=%%b"
)

:: 检查MinGit cmd目录是否已经存在于系统PATH中，并且添加绝对路径
echo Checking if MinGit cmd directory is in PATH...
echo %SYSTEM_PATH% | findstr /I /C:"%MINGIT_INSTALL_DIR%\cmd" > nul
if %ERRORLEVEL% equ 1 (
    echo MinGit cmd directory is not in PATH. Adding...
    :: 添加完整路径到系统的PATH环境变量中
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path /t REG_EXPAND_SZ /d "%MINGIT_INSTALL_DIR%\cmd;%SYSTEM_PATH%" /f
    if %ERRORLEVEL% equ 0 (
        echo MinGit environment variable set successfully.
    ) else (
        echo Setting MinGit environment variable failed: %ERRORLEVEL%.
    )
) else (
    echo MinGit cmd directory is already in PATH.
)

:: 结束
endlocal
echo MinGit has been installed and configured.
pause