<?php

print "<h1>2021-03-16: porting bbsengine.org to bbsengine5 and php 7.2</h1>";
exit;
//phpinfo();
//exit;

/**
 * handles display of the index page
 *
 * @package bbsengine4
 */

/**
 * application config file 
 */
require_once("config.php");
require_once("bbsenginedotorg.php");
require_once("bbsengine4.php");

/**
 * handle display of index page.
 *
 * @package bbsenginedotorg
 */
class index
{
  var $dbh = null;
  
  function _latestrelease()
  {
    $sql = "select releaseid from repo.latestrelease where projectname='bbsengine4'";
    $res = $this->dbh->getOne($sql);
    logentry("index.99: res=".var_export($res, True));
    if (PEAR::isError($res))
    {
      logentry("index.100: " . $res->toString());
    }
    $release = array();
    $files = array();
    if ($res !== null)
    {
      $sql = "select * from repo.file as f where f.releaseid=? and f.hidden='f' order by f.filepath";
      $dat = array($res);
      $res = $this->dbh->getAll($sql, null, $dat, array("integer"));
      if (PEAR::isError($res))
      {
        logentry("index.22: " . $res->toString());
        return PEAR::raiseError("Database Error (code: index.22)");
      }

      foreach ($res as $rec)
      {
        $file = $rec;
        $file["name"] = basename($rec["filepath"]);
        
        $files[] = $file;
      }
      
      $release["files"] = $files;
    }
    
    return $release;
  }

  function docsort($a, $b)
  {
    if ($a["updatedepoch"] === $b["updatedepoch"])
    {
      return 0;
    }
    if ($a["updatedepoch"] > $b["updatedepoch"])
    {
      return -1;
    }
    return 1;
  }

  function main()
  {
    startsession();
    
    $this->dbh = dbconnect(SYSTEMDSN);
    if (PEAR::isError($this->dbh))
    {
      logentry("index.10: " . $this->dbh->toString());
      return PEAR::raiseError("Database Error (code: index.10)");
    }

    setcurrentsite("bbsenginedotorg");
    setcurrentpage("index");
    setreturnto(getcurrenturi());
    
    $page = getpage("bbsengine4 - simple and elegant application framework in php and python");
//    $page->addBodyContent(fetchpageheader());
 //    $page->addStyleSheet(SKINURL . "css/index.css");
    $tmpl = getsmarty();
    if (PEAR::isError($tmpl))
    {
      logentry("index.20: " . $tmpl->toString());
      return PEAR::raiseError("Database Error (code: index.20)");
    }
    
//    logentry("index.50: calling _latestrelease()");
    $latestrelease = $this->_latestrelease();
//    logentry("index.51: called _latestrelease()");
    
    $docs = [];
    $docs[] = ["title" => "handbook", "url" => "/current/handbook/", "updatedepoch" => filemtime(HANDBOOKDIR)];
    $docs[] = ["title" => "API documentation", "url" => "/current/apidocs/", "updatedepoch" => filemtime(APIDOCSDIR)];
    $docs[] = ["title" => "changelog", "url" => "/current/CHANGELOG", "updatedepoch" => filemtime(CHANGELOG)];
    $docs[] = ["title" => "readme", "url" => "/current/README.md", "updatedepoch" => filemtime(README)];
    $docs[] = ["title" => "install", "url" => "/current/INSTALL.md", "updatedepoch" => filemtime(INSTALL)];
    $docs[] = ["title" => "releasenotes", "url" => "/current/RELEASENOTES.md", "updatedepoch" => filemtime(RELEASENOTES)];
    
    usort($docs, [$this, "docsort"]);
//    $tmpl->assign("release", $release);
//    $tmpl->assign("docs", $docs);
//    $page->addBodyContent($tmpl->fetch("index.tmpl"));
//    $page->addBodyContent(fetchpagefooter());
//    $options = [];
//    $options["pagedata"]["body"] = $tmpl->fetch("index.tmpl");

//    logentry("index.php");
    $data = [];
    $data["latestrelease"] = $latestrelease;
    $data["docs"] = $docs;
    $data["pagetemplate"] = "index.tmpl";

    $res = displaypage($page, $data);
    
    $this->dbh->disconnect();
    return $res;
  }
}

$i = new index();
$r = $i->main();
if (PEAR::isError($r))
{
  logentry("index.100: " . $r->toString());
  displayerrorpage($r->getMessage());
}

?>
