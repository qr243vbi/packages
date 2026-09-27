let version = find("v(.+)", gh("GSConnect/gnome-shell-extension-gsconnect"), 1);
rpm.version(version);
