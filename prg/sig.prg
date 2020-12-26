<?php

require_once("config.php");
require_once("zoidweb4.php");
require_once("bbsengine4.php");

require_once("Pager.php");

class sig
{
  var $dbh = null;

  /**
   * @since 20151017
   */
  function getsigcount($labelpath)
  {
    $sql = "select count(id) from engine.sig where path ~ ?";
    $dat = array("{$labelpath}.*{1}");
    $dbh = dbconnect(SYSTEMDSN);
    $res = $dbh->getOne($sql, array("integer"), $dat, array("text"));
    return intval($res);
  }

  function getlinkcount($path)
  {
    $sql = "select count(linkid) from vulcan.map_link_sig where siglabelpath ~ ?";
    $dat = array($path.".*{1}");
    $res = $this->dbh->getOne($sql, array("integer"), $dat, array("text"));
    if (PEAR::isError($res))
    {
      logentry("getlinkcount.100: " . $res->toString());
      return;
    }
    logentry("getlinkcount.110: res=".var_export($res, True));
    return $res;
  }

  function getpostcount($path)
  {
    $sql = "select count(postid) from sophia.map_post_sig where siglabelpath ~ ?";
    $dat = array($path);
    $res = $this->dbh->getOne($sql, array("integer"), $dat, array("text"));
    if (PEAR::isError($res))
    {
      logentry("getpostcount.100: " . $res->toString());
      return;
    }
    logentry("getpostcount.110: res=".var_export($res, True));
    return $res;
  }

  function detail()
  {
    $uri = isset($_REQUEST["uri"]) ? $_REQUEST["uri"] : null;
    logentry("sig.301: uri=".var_export($uri, True));
    $labelpath = buildlabelpath($uri);
    logentry("sig.303: labelpath=".var_export($labelpath, True));
    $sig = getsig($labelpath);
    if (PEAR::isError($sig))
    {
      logentry("sig.300: ".var_export($sig->toString()));
      displayerrorpage("invalid uri (code: sig.300)");
      return;
    }
    if ($sig === null)
    {
      logentry("sig.302: getsigfrompath(".var_export($labelpath, True).") returned null");
      displayerrorpage("invalid uri (code: sig.302)");
      return;
    }
    $sig["totallinks"] = $this->getlinkcount($labelpath);
    $sig["totalposts"] = $this->getpostcount($labelpath);
    $sig["totalsigs"] = $this->getsigcount($labelpath);
    $bare = isset($_REQUEST["bare"]) ? True : False;
    if ($bare === True)
    {
      header('content-type: application/json; charset=utf-8');
      $tmpl = getsmarty();
      $tmpl->assign("sig", $sig);
      $data = $tmpl->fetch("sig-detail.tmpl");
      $encode = encodejson($data);
      $callback = isset($_REQUEST["callback"]) ? $_REQUEST["callback"] : null;
      print "{$callback} ({$encode});";
      return;
    }

    print "not working yet";
    return;
  }

  function edit()
  {
    $currentmemberid = getcurrentmemberid();
    
    $uri = isset($_REQUEST["uri"]) ? $_REQUEST["uri"] : null;
    
    setreturnto(TEOSURL.$uri);

    $labelpath = buildlabelpath($uri);
    $parentlabelpath = buildparentlabelpath($labelpath); // buildlabelpath(dirname($uri));
    $name = basename($uri);

    logentry("sig.209: uri=".var_export($uri, True). " labelpath=".var_export($labelpath, True));

    $sig = getsig($labelpath);
    if (PEAR::isError($sig))
    {
      logentry("sig.210: " . $sig->toString());
      return PEAR::raiseError("Database Error (code: sig.210)");
    }
    
    if ($sig === null)
    {
      logentry("sig.220: labelpath ".var_export($labelpath, True)." not found");
      return PEAR::raiseError("Input Error (code: sig.220)");
    }

    $sig["uri"] = $uri;
    
    if (accesssig("edit", $sig) === False)
    {
      displaypermissiondenied("You do not have permission to edit this sig.");
      return;
    }
    
    $sigid = getsigidfromlabelpath($labelpath);
    $form = getquickform("sig-edit");
    
    $parentpath = buildparentlabelpath($labelpath);

    $defaults = array();
    $defaults["parentlabelpath"] = $parentlabelpath; // $sig["path"];
    $defaults["title"] = $sig["title"];
    $defaults["name"] = $name; // sig["name"];
    $defaults["intro"] = $sig["intro"];

    $form->addDataSource(new HTML_QuickForm2_DataSource_Array($defaults));

    $constants = array();
    $constants["mode"] = "edit";
    $constants["uri"] = $uri;
    $constants["id"] = $sigid;

    $form->addDataSource(new HTML_QuickForm2_DataSource_Array($constants));

    buildsigfieldset($form);
    $form->addElement("submit", "blah", array("value" => "update"));

    $res = handleform($form, array($this, "update"), "edit sig");
    if (PEAR::isError($res))
    {
      logentry("sig.230: " . $res->toString());
      return PEAR::raiseError("error handling form (code: sig.230");
    }
    if ($res === True)
    {
      return;
    }
    
    $renderer = getquickformrenderer();
    $form->render($renderer);
  
    $res = displayform($renderer, "edit sig");
    if (PEAR::isError($res))
    {
      logentry("sig.232: " . $res->toString());
      return PEAR::raiseError("error displaying form (code: sig.232)");
    }
    return;
  }
  
  function update($values)
  {
    $path = $values["parentlabelpath"];
    $name = $values["name"];
    $id = intval($values["id"]);

    $uri = $values["uri"];
    $pageprotocol = isset($values["pageprotocol"]) ? $values["pageprotocol"] : "standard";

    $labelpath = normalizelabelpath($path, $name);

    $sig = array();
    $sig["title"] = $values["title"];
    $sig["intro"] = $values["intro"];
    $sig["name"] = $name;
    $sig["path"] =  $labelpath; // path + name
    $sig["lastmodified"] = "now()";
    $sig["lastmodifiedbyid"] = getcurrentmemberid();

    $res = $this->dbh->beginTransaction();
    $res = $this->dbh->autoExecute("engine.__sig", $sig, MDB2_AUTOQUERY_UPDATE, "id=".$this->dbh->quote($id, "integer"));
    if (PEAR::isError($res))
    {
      logentry("sig.300: " . $res->toString());
      $this->dbh->rollback();
      return PEAR::raiseError("Database Error (code: sig.300)");
    }
    $this->dbh->commit();
    displayredirectpage("Folder Updated", TEOSURL.$uri);
    return True;
  }

  function delete()
  {
    $currentmemberid = getcurrentmemberid();
    
    $uri = isset($_REQUEST["uri"]) ? $_REQUEST["uri"] : null;
    if ($uri === null)
    {
      logentry("sig.400: delete() passed null for uri");
      return PEAR::raiseError("Input Error (code: sig.400)");
    }
    
    setreturnto(TEOSURL.$uri."delete");

    $path = buildpath($uri);
    $sig = getsig($path);
    if (PEAR::isError($sig))
    {
      logentry("sig.410: " . $sig->toString());
      return PEAR::raiseError("Database Error (code: sig.410)");
    }
    if ($sig === null)
    {
      logentry("sig.420: getsig(".var_export($path, True).") returned null");
      return PEAR::raiseError("Input Error (code: sig.420)");
    }

    $sig["uri"] = $uri;
    
    if (accesssig("delete", $sig, $currentmemberid) === False)
    {
      logentry("sig.430: permission denied trying to delete ".var_export($path, True));
      displaypermissiondenied("You do not have permission to delete this sig");
      return;
    }
    $confirm = isset($_REQUEST["confirm"]) ? True : False;
    if ($confirm === False)
    {
      $title = $sig["title"];
      displaydeleteconfirmation("Are you sure you want to delete <i>{$title}</i>?", TEOSURL.$uri."delete?confirm", "Yes", TEOSURL.$uri, "No");
      return;
    }

    $res = $this->dbh->autoExecute("sig", null, MDB2_AUTOQUERY_DELETE, "path=".$this->dbh->quote($path, "text"));
    if (PEAR::isError($res))
    {
      logentry("sig.440: ".$res->toString());
      return PEAR::raiseError("Database Error (code: sig.440)");
    }
    displayredirectpage("Sig Deleted", "/");
    return;
  }
  
  function links($labelpath)
  {
    $links = [];
//   $sql = "select id from vulcan.link as l where l.sigs @> array[cast(? as ltree)]";
//    $sql = "select id from vulcan.link as l where l.sigs @> array[".$this->dbh->quote($labelpath, "text")."::ltree]";
//    $sql = "select id from vulcan.link as l where ? = ".$this->dbh->quote($labelpath, "text"). " = any(l.sigs)";
    $sql = "select id from vulcan.link as l where sigs ~ ?";
    if (flag("ADMIN") === False)
    {
      $sql.= " and l.broken='f' and l.approved='t'";
    }
    $sql.= " order by l.dateposted desc";

    $res = $this->dbh->getAll($sql, ["integer"], [$labelpath], ["text"]);
    if (PEAR::isError($res))
    {
      logentry("sig.links.540: " . $res->toString());
      return;
    }

    foreach ($res as $d)
    {
      $id = $d["id"];
      $link = getlinkbyid($id);
      if (PEAR::isError($link))
      {
        logentry("sig.links.101: ". $link->toString());
        continue;
      }
      if ($link === null)
      {
        logentry("sig.links.102: getlinkbyid(".var_export($id, True).") returned null");
        continue;
      }
      if (accesslink("view", $link) === True)
      {
        $links[] = $link;
      }
    }
    return $links;
  }
  
  function sigs($labelpath)
  {
    $currentmemberid = getcurrentmemberid();
    
//    $sql = "select s.id, s.path, s.title, public.teosurl(text(path)) as uri from engine.sig as s where s.path ~ ? order by s.title asc";
    $sql = "select * from engine.sig where sig.path ~ ? order by sig.title asc";
    $dat = "{$labelpath}.*{1}";
    $res = $this->dbh->getAll($sql, null, $dat, ["text"]);
    if (PEAR::isError($res))
    {
      logentry("sig.520: " . $res->toString());
      return PEAR::raiseError("Database Error (code: sig.520)");
    }

    $sigs = [];
    foreach ($res as $rec)
    {
//      logentry("sig.200: rec=".var_export($rec, True));
      if (accesssig("view", $rec, $currentmemberid) === False || strpos("top.eros", $rec["path"]) === 0)
      {
        continue;
      }
      $rec["actions"] = buildsigactions($rec);
      $sigs[] = $rec;
    }

/*
    $sql = "select s.id, s.path, s.title, public.teosurl(text(path)) as uri from engine.sig as s where s.path ~ ? order by s.title asc";
    $dat = "{$path}.*{1}";
    $res = $this->dbh->getAll($sql, null, $dat, array("text"));
    if (PEAR::isError($res))
    {
      logentry("sig.520: " . $res->toString());
      return PEAR::raiseError("Database Error (code: sig.520)");
    }

    $sigs = [];
    foreach ($res as $rec)
    {
//      logentry("sig.200: rec=".var_export($rec, True));
      if (accesssig("view", $rec, $currentmemberid) === False || strpos("top.eros", $rec["path"]) === 0)
      {
        continue;
      }
      $rec["actions"] = buildsigactions($rec);
      $sigs[] = $rec;
    }
*/    
    return $sigs;
  }

  function posts($labelpath)
  {
    $currentmemberid = getcurrentmemberid();

    $sql = "select id from sophia.post as p, sophia.map_post_sig as m where p.id = m.postid and m.siglabelpath ~ ? and p.parentid is null";
    $dat = array($labelpath);
    $res = $this->dbh->getAll($sql, array("integer"), $dat, array("text"));
    $posts = array();
    foreach ($res as $rec)
    {
      $id = $rec["id"];
      $post = getpost($id);
      if (accesspost("view", $post, $currentmemberid) === False)
      {
        continue;
      }
      $post["id"] = $id;
      $posts[] = $post;
    }
    return $posts;
  }

  function amznitems($sigpath)
  {
    $sql = "select attributes->>'asin' as asin from agora.amznitem where sigs ~ ?";
//    $sql = "select engine.node.* from engine.node, engine.map_node_sig where engine.node.id = engine.map_node_sig.nodeid and engine.map_node_sig.sigpath=?";
    $dat = [$sigpath];
    $res = $this->dbh->getAll($sql, null, $dat, ["text"]);
    if (PEAR::isError($res))
    {
      logentry("teos.sig.amznitems.100: " . $res->toString());
    }

//    logentry("amznitems.100: sigpath=".var_export($sigpath, true)); // . " res=".var_export($res, true));

    $amznitems = [];
    foreach ($res as $rec)
    {
      $asin = $rec["asin"];
      $foo = getamznitem($asin);
      if (PEAR::isError($foo))
      {
        logentry("teos.amznitems.100: " . $foo->toString());
        break;
      }
      $amznitem = buildamznitem($foo);
      if (accessamznitem("view", $amznitem) === false)
      {
        continue;
      }
      $amznitem["comments"] = [];
      $amznitems[] = $amznitem;
    }
    return $amznitems;
  }

  function browse()
  {
    $uri = isset($_REQUEST["uri"]) ? $_REQUEST["uri"] : null;
    $normalizeduri = normalizeuri($uri);
    $labelpath = buildlabelpath($normalizeduri);
    logentry("browse.100: uri=".var_export($uri, True). " labelpath=".var_export($labelpath, True));
    setreturnto(getcurrenturi());

    if ($labelpath === "top")
    {
      setcurrentpage("index");
    }
    else
    {
      setcurrentpage($labelpath);
    }

    if (strpos($labelpath, "top.eros") === 0 && flag("EROS") === False)
    {
      displaypermissiondenied();
      return;
    }

    if ($uri != $normalizeduri)
    {
      logentry("sig.browse.150: adding trailing slash!");
      displayredirectpage("OK", TEOSURL.$normalizeduri, 0);
      return;
    }

    setcurrentaction("browse");

    $currentsig = getsig($labelpath);
    if ($currentsig === null)
    {
      displayerrorpage("sig not found", 404);
      return;
    }

    $currentsig["uri"] = $uri;

    $currentmemberid = getcurrentmemberid();
    
    $actions = [];
    $actions["edit"] = accesssig("edit", $currentsig);
    $actions["add"] = accesssig("add", $currentsig);
    $actions["delete"] = accesssig("delete", $currentsig);
    $currentsig["actions"] = $actions;
    
    $sigs = $this->sigs($labelpath);
    $data["sigs"] = $sigs;

    $links = $this->links($labelpath);
    $data["links"] = $links;

    $posts = $this->posts($labelpath);
    $data["posts"] = $posts;

    $amznitems = $this->amznitems($labelpath);
    $data["amznitems"] = $amznitems;

    setreturnto(getcurrenturi());

    $breadcrumbs = buildbreadcrumbs($labelpath);
//    logentry("teos.sig.200: breadcrumbs=".var_export($breadcrumbs, True));
    
    $sidebar = [];
    if (accesssig("addlink", $currentsig) === True)
    {
      $sidebar[] = array("name" => "addlink", "url" => TEOSURL."{$uri}add-link", "desc" => "add a link to this sig", "title" => "add link");
    }
    if (accesssig("addpost", $currentsig) === True)
    {
      $sidebar[] = array("name" => "addpost", "url" => TEOSURL."{$uri}add-post", "desc" => "add a post to this sig", "title" => "add post");
    }
    if (accesssig("add", $currentsig) === True)
    {
      $sidebar[] = array("name" => "addsig", "url" => TEOSURL."{$uri}add-sig", "desc" => "add a subsig to this sig", "title" => "add sig");
    }
    if (accesssig("edit", $currentsig) === True)
    {
      $sidebar[] = array("name" => "editsig", "url" => TEOSURL."{$uri}edit-sig", "desc" => "edit sig", "title" => "edit sig");
    }
    
    $titles = [];
    
    foreach ($breadcrumbs as $foo)
    {
      $titles[] = $foo["title"];
    }
//    logentry("teos.100: bar=".var_export($bar, True)." titles=".var_export($titles, True));

    $title = "teos - browse - ". implode(" - ", $titles);
    $page = getpage($title);

//    logentry("teos.101: currentsig=".var_export($currentsig, True));

    $data = [];
    $data["currentsig"] = $currentsig;
    $data["sigs"] = $sigs;
    $data["breadcrumbs"] = $breadcrumbs;
    $data["posts"] = $posts;
    $data["links"] = $links;
    $data["pagetemplate"] = "sig.tmpl";
    $data["sidebar"] = $sidebar;
    $data["amznitems"] = $amznitems;
//    $data["usingamznapi"] = false;
    return displaypage($page, $data);
  }

  function add()
  {
    if (accesssig("add") === False)
    {
      logentry("sig.25: permission denied. op=add memberid=".var_export($currentmemberid, True)." labelpath=".var_export($labelpath, True));
      displaypermissiondenied("You do not have permission to add sigs here. (code: sig.25)");
      return;
    }

    setcurrentpage("sig");
    setcurrentaction("add");

    $uri = isset($_REQUEST["uri"]) ? $_REQUEST["uri"] : null;
    $labelpath = buildlabelpath($uri);
    
    $currentmemberid = getcurrentmemberid();
    
    setreturnto(TEOSURL.$uri);
    
    logentry("sig.49: labelpath=".var_export($labelpath, True));

    $form = getquickform("teos-add");
    buildsigfieldset($form);
    $form->addElement("submit", "addsig", array("value" => "add"));

    $defaults = array();
    $defaults["parentlabelpath"] = $labelpath;

    $form->addDataSource(new HTML_QuickForm2_DataSource_Array($defaults));

    $const = array();
    $const["mode"] = "add";
    $const["memberid"] = getcurrentmemberid();
    $form->addDataSource(new HTML_QuickForm2_DataSource_Array($const));

    $renderer = getquickformrenderer();
    $form->render($renderer);
    $res = handleform($form, array($this, "insert"), "add sig");
    if (PEAR::isError($res))
    {
      logentry("sig.300: ". $res->toString());
      return PEAR::raiseError("unable to handle form. (code: sig.300)");
    }
    if ($res === True)
    {
      logentry("sig.302: handleform(...) returned true");
      return;
    }
    $res = displayform($renderer, "add sig");
    return;
  }

  function insert($values)
  {
    $title = $values["title"];
    $labelpath = $values["parentlabelpath"];    
    $name = !empty($values["name"]) ? $values["name"] : buildlabel($title);

    logentry("sig.22: name=".var_export($name, True)." title=".var_export($title, True)." labelpath=".var_export($labelpath, True));

    $currentmemberid = getcurrentmemberid();
    
    $sig = array();
    $sig["path"] = normalizelabelpath($labelpath, $name);
    $sig["title"] = $title;
    $sig["intro"] = $values["intro"];
    $sig["name"] = $name;
    $sig["postedbyid"] = $currentmemberid;
    $sig["dateposted"] = "now()";
    $sig["lastmodified"] = "now()";
    $sig["lastmodifiedbyid"] = $currentmemberid;
    
    $res = $this->dbh->autoExecute("engine.__sig", $sig, MDB2_AUTOQUERY_INSERT);
    if (PEAR::isError($res))
    {
      logentry("sig.28: " . $res->toString());
      return PEAR::raiseError("Error Inserting Folder (code: sig.28)");
    }
    
    displayredirectpage("SIG added", TEOSURL.$siguri);
    return True;
  }
  
  function main()
  {
    startsession();

    setcurrentsite("teos");
    setcurrentpage("index");
        
    $this->dbh = dbconnect(SYSTEMDSN);
    if (PEAR::isError($this->dbh))
    {
      logentry("sig.90: ".$this->dbh->toString());
      return PEAR::raiseError("Database Connect Error (code: sig.90)");
    }
    
    clearpageprotocol();
    
    $mode = isset($_REQUEST["mode"]) ? $_REQUEST["mode"] : null;
    logentry("sig.500: mode=".var_export($mode, True));
    switch($mode)
    {
      case "browse":
      {
        $r = $this->browse();
        break;
      }
      case "add":
      {
        $r = $this->add();
        break;
      }
      case "edit":
      {
        $r = $this->edit();
        break;
      }
      case "delete":
      {
        $r = $this->delete();
        break;
      }
      case "detail":
      {
        $r = $this->detail();
        break;
      }
      default:
      {
        $r = $this->browse();
        break;
      }
    }
    return $r;
  }
};

$a = new sig();
$b = $a->main();
if (PEAR::isError($b))
{
  logentry("sig.100: " . $b->toString());
  displayerrorpage($b->getMessage());
}
?>
