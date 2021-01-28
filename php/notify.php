<?php

require_once("config.php");
require_once(SITE.".php");
require_once("bbsengine5.php");

require_once("Pager.php");

class notify
{
  var $dbh = null;

  function buildrecord($key, $notify)
  {
    $data = $notify["data"];

    $val = isset($data[$key]) ? $data[$key] : null;
    if ($val === null)
    {
      logentry("buildrecord.210: ".var_export($key, True)." is null.");
      return null;
    }
    
    logentry("buildrecord.212: key=".var_export($key, True)." data=".var_export($data, True)." val=".var_export($val, True));

    switch ($key)
    {
      case "linkid":
      {
        $record = getlink($val);
        break;
      }
      default:
      {
        logentry("buildrecord.900: unhandled key. key=".var_export($key, True));
        $record = null;
        break;
      }
    }

    if (PEAR::isError($record))
    {
      logentry("buildrecord.100: " . $record->toString());
      $record = null;
    }

    return $record;
  }

  function buildnotifydata($notify)
  {
    $type = $notify["type"];

    $data = $notify["data"];

    $dat = [];

    switch ($type)
    {
      case "link-approved":
      case "link-added":
      {
        $dat["link"] = buildnotifyrecord("linkid", $notify);
        break;
      }
      default:
      {
        logentry("buildnotifydata.900: unhandled type '".var_export($type, True)."'");
        break;
      }
    }

    return $dat;
  }

/*
  // @since 20130520
  function buildnotifyactions($notify)
  {
    logentry("buildnotifyactions.100: getcurrentaction() == ".var_export(getcurrentaction(), True));
//    logentry("buildnotifyactions.150: notify=".var_export($notify, True));

    $type = isset($notify["type"]) ? $notify["type"] : null;
    logentry("buildnotifyactions.120: type=".var_export($type, True));

    $id = isset($notify["id"]) ? $notify["id"] : null;
    
    $data = $notify["data"];

    $actions = [];
    if (getcurrentaction() !== "detail")
    {
      $actions[] = array("href" => ENGINEURL . "notify-detail-{$id}", "title" => "detail", "class" => "fa fa-angle-double-down fa-fw");
    }

    if (accessnotify("delete") === True)
    {
      $actions[] = array("href" => ENGINEURL . "notify-delete-{$id}", "title" => "delete", "class" => "fa fa-remove fa-fw");
    }
    
    return $actions;
  }
*/
  // @since 20130516
  function markread($notifyid)
  {
    $notify = [];
    $notify["read"] = True;
    $notify["dateread"] = "now()";
    $res = $this->dbh->autoExecute("__notify", $notify, MDB2_AUTOQUERY_UPDATE, "id=".$this->dbh->quote($notifyid, "integer"));
    if (PEAR::isError($res))
    {
      logentry("notify.200: " . $res->toString());
      return $res;
    }
    return;
  }

  // @since 20130516
  function delete()
  {
    $notifyid = isset($_REQUEST["notifyid"]) ? intval($_REQUEST["notifyid"]) : null;
    $notify = getnotify($notifyid);
    if (PEAR::isError($notify))
    {
      logentry("notify.300: " . $notify->toString());
      return PEAR::raiseError("Database Error (code: notify.300)");
    }
    if ($notify === null)
    {
      logentry("notify.310: getnotify(".var_export($notifyid, True).") returned null.");
      return PEAR::raiseError("Input Error (code: notify.310)");
    }
    if (accessnotify("delete", $notify) === False)
    {
      logentry("notify.320: delete permission denied. id=".var_export($notifyid, True));
    }
    $confirmed = isset($_REQUEST["confirm"]) ? True : False;
    if ($confirmed === False)
    {
      displaydeleteconfirmation("Are you sure you want to delete this notify?", "/notify-delete-{$notifyid}?confirm", "Yes", getreturntourl(), "No");
      return;
    }
    $res = $this->dbh->autoExecute("__notify", null, MDB2_AUTOQUERY_DELETE, "id=".$this->dbh->quote($notifyid, "integer"));
    if (PEAR::isError($res))
    {
      logentry("notify.330: " . $res->toString());
      return PEAR::raiseError("Database Error (code: notify.330)");
    }
    displayredirectpage("OK. Notify deleted.");
    return;
  }

  function notificationcount()
  {
    $currentmemberid = getcurrentmemberid();
    
    $total = gettotalnotifications($currentmemberid);
    if (PEAR::isError($total))
    {
      logentry("notify.400: " . $total->toString());
      print encodejson("ERROR (notify.400)");
      return;
    }
    $unread = gettotalunreadnotifications($currentmemberid);
    if (PEAR::isError($unread))
    {
      logentry("notify.402: " . $unread->toString());
      print encodejson("ERROR (notify.402)");
      return;
    }
    $tmpl = getsmarty();
    $tmpl->assign("total", $total);
    $tmpl->assign("unread", $unread);
    print encodejson($tmpl->fetch("notify-count.tmpl"));
    return;
  }

  function undisplayed()
  {
    $currentmemberid = getcurrentmemberid();
    $displaylist = isset($_REQUEST["displaylist"]) ? $_REQUEST["displaylist"] : NULL;

    if (count($displaylist) > 0)
    {
      $where = join(", ", $displaylist);
    }
    else
    {
      $where = "";
    }
    $sql = "select id from engine.notify where displayed='f' and memberid=?";
    if (strlen($where) > 0) 
    {
      $sql .=" and id not in ({$where})";
    }
    $sql .=" order by datecreated desc limit 1";

//    logentry("notify.490: sql=".var_export($sql, True));

    $dat = array($currentmemberid);
    $res = $this->dbh->getAll($sql, null, $dat);
    if (PEAR::isError($res))
    {
      print encodejson([]); // "ERROR (poll.24)");
      logentry("notify.500: " . $res->toString());
      return;
    }

//    logentry("notify.502: res=".var_export($res, True));
    
    $notifications = [];
    if (count($res) > 0)
    {
      $tmpl = getsmarty();
      foreach ($res as $rec)
      {
        $notifyid = $rec["id"];
        $notify = getnotify($notifyid);
        if (PEAR::isError($notify))
        {
          logentry("notify.600: ".$notify->toString());
          return;
        }

        $template = $notify["template"];

        $actions = buildnotifyactions($notify);
        $notify["actions"] = $actions;
        
        $notify["sticky"] = True;

        $type = $notify["type"];

/*
        $dat = buildnotifydata($type, $notify);
        if (PEAR::isError($dat))
        {
          logentry("notify.800: " . $dat->toString());
          print encodejson("null");
          return;
        }
        $notify["data"] = $dat;
*/        
        $tmpl->assign("notify", $notify);
        $tmpl->assign("mode", "popup");
        $notify["html"] = $tmpl->fetch($template);
//        logentry("notify.526: notify.html=".var_export($notify["html"], True));
        $notifications[] = $notify;

        $notify = [];
        $notify["displayed"] = True;
        $notify["datedisplayed"] = "now()";
        $res = $this->dbh->autoExecute("engine.__notify", $notify, MDB2_AUTOQUERY_UPDATE, "id=".$this->dbh->quote($notifyid, "integer"));
        if (PEAR::isError($res))
        {
          logentry("notify.528: " . $res->toString());
        }
        $this->dbh->commit();
//        logentry("notify.530: trace");
      }
    }
    header("Content-Type: application/json; charset=utf-8");

    $encoded = encodejson($notifications);
    if (isset($_GET["callback"]))
    {
//      logentry("notify.535: using callback");
      print $_GET["callback"]."({$encoded})";
    }
    else
    {
      print $encoded;
    }
  }
  
  function summary()
  {
    if (flag("AUTHENTICATED") === False)
    {
      displaypermissiondenied();
      return;
    }

    $memberid = getcurrentmemberid();
    if ($memberid === null)
    {
      logentry("notify.600: id is null");
      return PEAR::raiseError("Input Error (code: notify.600)");
    }

    $totalnotifications = gettotalnotifications($memberid);
    if (PEAR::isError($totalnotifications))
    {
      logentry("notify.602: " . $totalnotifications->toString());
      $totalnotifications = 0;
    }

    setcurrentaction("summary");
    
    $params = [];
    $params["mode"] = "Sliding";
    $params["perPage"] = 50;
    $params["delta"] = 3;
    $params["totalItems"] = $totalnotifications;
    $params["curPageSpanPre"] = "[ ";
    $params["curPageSpanPost"] = " ]";
    $params["path"] = "/";
    $params["fileName"] = "show-notifications-{$memberid}-%d";
    $params["append"] = False;
        
    $sql = "select id from engine.notify where memberid=".$this->dbh->quote($memberid, "integer")." order by status, datecreated desc";
    $pagerinfo = buildpagerinfo($sql, $params);

    $currentpage = isset($_REQUEST["pageID"]) ? $_REQUEST["pageID"] : 1;
    if ($currentpage > 1)
    {
        setcurrentpage("notify-summary-{$currentpage}");
    }
    else
    {
        setcurrentpage("notify-summary");
    }

    $data = $pagerinfo["data"];
    foreach ($data as $notify)
    {
      if (accessnotify("view", $notify) === true)
      {
        $items[] = $notify;
      }
    }
    
    setcurrentpage("notify");
    setcurrentaction("summary");
    setreturnto(getcurrenturi());
    // more here
    return;
  }
  
  function detail()
  {
    $notifyid = isset($_REQUEST["notifyid"]) ? intval($_REQUEST["notifyid"]) : null;
    $notify = getnotify($notifyid);
    if (PEAR::isError($notify))
    {
      logentry("notify.200: ". $notify->toString());
      return PEAR::raiseError("Database Error (code: notify.200)");
    }
    if ($notify === null)
    {
      logentry("notify.202: getnotify(".var_export($notifyid, True).") returned null");
      return PEAR::raiseError("Input Error (code: notify.202)");
    }

    if (accessnotify("detail", $notify) === False)
    {
      logentry("notify.203: permission denied for notify detail #{$notifyid}");
      displaypermissiondenied();
      return;
    }

    setcurrentaction("detail");

    $notify["actions"] = buildnotifyactions($notify);
    logentry("notify.204: notify.actions=".var_export($notify["actions"], True));
    
    $template = $notify["detailtemplate"];
    
    if ($template == "")
    {
      displayerrorpage("This notification does not have any details");
      return;
    }
    
    logentry("notify.240: currenturi=".var_export(getcurrenturi(), True));
    setreturnto(getcurrenturi());
    
    $type = $notify["type"];
    
    $data = $notify["data"];

    $res = $this->markread($notifyid);
    if (PEAR::isError($res))
    {
      logentry("notify.220: " . $res->toString());
      return $res;
    }
    
    setcurrentaction("detail");

    $data = [];
    $data["notify"] = $notify;
    $data["mode"] = "detail";
    $data["pagetemplate"] = $template;
    
    displaypage($data);
    return;
  }
  
  function main()
  {
    startsession();
    
    $this->dbh = dbconnect(SYSTEMDSN);
    if (PEAR::isError($this->dbh))
    {
      displayerrorpage("Database Error (code: notify.10)");
      logentry("notify.10: " . $this->dbh->toString());
      return;
    }

    $res = null;
    
    $mode = isset($_REQUEST["mode"]) ? $_REQUEST["mode"] : null;
    switch ($mode)
    {
      case "summary":
      {
        $res = $this->summary();
        break;
      }
      case "undisplayed":
      {
        $res = $this->undisplayed();
        break;
      }
/*
      case "count":
      {
        $res = $this->getnotifycount();
        break;
      }
*/
      case "detail":
      {
        $res = $this->detail();
        break;
      }
      case "delete":
      {
        $res = $this->delete();
        break;
      }
    }
    $this->dbh->disconnect();
    return $res;
  }
};

$a = new notify();
$b = $a->main();
if (PEAR::isError($b))
{
  displayerrorpage($b->getMessage());
  logentry("notify.100: " . $b->toString());
  exit;
}

?>
