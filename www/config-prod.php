<?php

define("SITETITLE", "bbsengine4 official website");
define("SITEADMINEMAIL", "zoid zechnologies <bbsengine4@projects.zoidtechnologies.com>");

define("STATICSKINURL", "//bbsengine.org/skin/");
/**
 * define the base url for the site. THIS VALUE MUST BE TERMINATED WITH A "/"
 */
define("SITEURL", "http://bbsengine.org/");
define("SITENAME", "bbsenginedotorg");
define("SKINURL", SITEURL . "skin/");
define("SYSTEMDSN", "pgsql://apache@127.0.0.1/zoidweb4");

define("VHOSTDIR", "/srv/www/vhosts/bbsengine.org/");
define("DOCUMENTROOT", VHOSTDIR . "80/html/");

define("SMARTYCOMPILEDTEMPLATESDIR", VHOSTDIR . "templates_c");
define("SMARTYPLUGINSDIR", VHOSTDIR . "smarty/");
define("SMARTYTEMPLATESDIR", DOCUMENTROOT."skin/tmpl/");

// @see http://php.net/strftime
define("DATEFORMAT", "%Y-%b-%d %I:%M %p %Z (%A)");

define("LOGENTRYPREFIX", "bbsenginedotorg");

define("SMARTY3", True);

define("RELEASESDIR", "/srv/repo/");

/**
 * @since 20110817
 */
define("ARCHIVEURL", "/archive/");

/**
 * @since 20140511
 */
define("REPOURL", "//repo.zoidtechnologies.com/");

date_default_timezone_set("America/New_York");

define("SESSIONCOOKIEDOMAIN", ".bbsengine.org");
define("SESSIONCOOKIEEXPIRE", 12*60*60);

define("CURRENTVERSION", "v4/");
//define("HANDBOOKDIR", DOCUMENTROOT . CURRENTVERSION . "handbook/");
define("APIDOCSDIR", DOCUMENTROOT . CURRENTVERSION . "apidocs/");
define("CHANGELOG", DOCUMENTROOT . CURRENTVERSION . "CHANGELOG.txt");
define("README", DOCUMENTROOT . CURRENTVERSION . "README.txt");
define("INSTALL", DOCUMENTROOT . CURRENTVERSION . "INSTALL.txt");
define("RELEASENOTES", DOCUMENTROOT . CURRENTVERSION . "RELEASENOTES.txt");

define("PROJECTURL", "//projects.zoidtechnologies.com/");

define("ENGINEURL", "/");

// @since 20180502 to squash a php notice
define("WWWURL", "//zoidtechnologies.com/");

// define("APIDOCSURI", "");
/**
 * @since 20190223
*/
define("HANDBOOKDIR", DOCUMENTROOT);

?>
