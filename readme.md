runWithCfg [result_package] [svn_orig_package_revision_uri] [svn_dest_package_revision_uri] [project_name]

* [result_package] - path to result ZIP package e.g. c:\project_1_1_repack.zip
* [svn_original_package_revision_uri] - svn original revision locator e.g. https://repo.com/svn/project/trunk@2 
* [svn_dest_package_revision_uri] - svn destination revision locator e.g. https://repo.com/svn/project/trunk@2 
* [project_name] - project folder name (the convention is that .csproj file has exactly the same name as project folder in solution)


runWithCfg calls run eventually and allows to set additional variables like:
* SVN_USERNAME
* SVN_PASSWORD
* DOTNETFRAMEWORK - a path to .NET framework distribution
* EXCLUDE_FILE_PATTERN - a list of filename patterns for files to be excluded while actioning diff operation e.g. *.config,*.asmx
* INCLUDE_FILE_PATTERN - a list of filename pattern for files to be included while actioning diff operation, takes precedence over EXCLUDE one

Example:
runWithCfg fina.zip https://subversion.assembla.com/svn/autobuild_ps/trunk@2 https://subversion.assembla.com/svn/autobuild_ps/trunk@6 ExMvc1
