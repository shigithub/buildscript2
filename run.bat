@ECHO OFF
SET RESULT_PCKG=%1
SET SVN_ORIG_REV_URI=%2
SET SVN_NEW_REV_URI=%3
SET PROJECT_NAME=%4

SET CCD=%CD%
SET SCRIPT_CWD=%~dp0%


IF [%DOTNETFRAMEWORK%] == []  (
ECHO Variable not set: DOTNETFRAMEWORK
exit /b
)

IF [%1] == []  GOTO usage
IF [%1] == [/?]  GOTO usage

ECHO ------------------------------------------------------------
ECHO Resulting package: %RESULT_PCKG%
ECHO Original package revision URI: %SVN_ORIG_REV_URI%
ECHO Result package revision URI: %SVN_NEW_REV_URI%
ECHO Project: %PROJECT_NAME%
ECHO ------------------------------------------------------------

set /p correct=Is above correct (Y/N)? 
IF NOT [%correct%] == [Y] GOTO end


ECHO Cleaning temp directories...
call :clean


ECHO Checking out revision: %SVN_ORIG_REV_URI%
call :checkout %SVN_ORIG_REV_URI% sources\orig
call :buildsolution %CD%\sources\orig\%PROJECT_NAME%\%PROJECT_NAME%.csproj %CD%\build\orig

ECHO Checking out revision: %SVN_NEW_REV_URI%
call :checkout %SVN_NEW_REV_URI% sources\new
call :buildsolution %CD%\sources\new\%PROJECT_NAME%\%PROJECT_NAME%.csproj %CD%\build\new


ECHO Building tree patch...
set DIFF_CMD=%SCRIPT_CWD%diff.py %CCD%\build\orig %CCD%\build\new %CCD%\diff --change-types M
IF NOT [%EXCLUDE_FILE_PATTERN%] == [] set DIFF_CMD=%DIFF_CMD% -x "%EXCLUDE_FILE_PATTERN%"
IF NOT [%INCLUDE_FILE_PATTERN%] == [] set DIFF_CMD=%DIFF_CMD% -i "%INCLUDE_FILE_PATTERN%"
%DIFF_CMD%

ECHO Applying tree patch...
%SCRIPT_CWD%patch.py %CD%\build\orig %CD%\diff %CD%\build\final


ECHO Creating patched archive...
%SCRIPT_CWD%zipper.py zip %RESULT_PCKG% %CD%\build\final

call :clean

ECHO Done.
goto end


:apply_patch
%SVN_DIFF% > %1
svn patch %1 
exit /b

:checkout

set SVN_CMD=svn checkout %1 %2
IF NOT [%SVN_USERNAME%] == []  set SVN_CMD=%SVN_CMD% --username %SVN_USERNAME%
IF NOT [%SVN_PASSWORD%] == [] set SVN_CMD=%SVN_CMD%  --password %SVN_PASSWORD%
%SVN_CMD% > nul

exit /b

:buildsolution
%DOTNETFRAMEWORK%\msbuild  %1 /p:DeployOnBuild=true /p:PublishProfile=%SCRIPT_CWD%buildprofile.pubxml /p:PublishUrlRoot=%2 
exit /b 

:clean
rmdir /S /Q sources > nul 2>nul
rmdir /S /Q build > nul 2>nul
rmdir /S /Q diff > nul 2>nul
exit /b

:usage
ECHO Usage:
ECHO run [result_package] [svn_orig_package_revision_uri] [svn_dest_package_revision_uri]  [project_name]
:end