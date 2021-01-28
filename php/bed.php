<?php

require_once("config.php");
require_once(SITENAME.".php");
require_once("bbsengine5.php");

function updatenotifystatus($ids)
{
  $dbh = dbconnect(SYSTEMDSN);
  $dbh->beginTransaction();
  foreach ($ids as $id)
  {
    $res = $dbh->autoExecute("engine.__notify", ["status" => "delivered"], MDB2_AUTOQUERY_UPDATE, "id=".$dbh->quote($id, "integer"));
    if (PEAR::isError($res))
    {
      logentry("bed.getsentjnotifylist.280: " . $res->toString());
      $dbh->rollback();
      return $res;
    }
  }
  $dbh->commit();
  return;
}

function getsentnotifylist()
{
  $currentmemberid = getcurrentmemberid();
  $sql = "select * from engine.notify where status='sent' and memberid=?";
  $dat = [$currentmemberid];
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("bed.getsentnotifylist.100: " . $dbh->getMessage());
    return $dbh;
  }
  $notifylist = $dbh->getAll($sql, null, $dat, ["integer"]);
  if (PEAR::isError($notifylist))
  {
    logentry("bed.getsentnotifyidlist.100: " . $notifylist->getMessage());
    return $notifylist;
  }

  $currentchecksumlist = isset($_REQUEST["currentchecksumlist"]) ? $_REQUEST["currentchecksumlist"] : [];
  // logentry("bed.getsentnotifylist.400: currentchecksumlist=".var_export($currentchecksumlist, true));

  
  $results = [];
  $ids = [];
  $tmpl = getsmarty();
  foreach ($notifylist as $notify)
  {
    $notify["data"] = decodejson($notify["data"]);
    $notify["actions"] = buildnotifyactions($notify);
    
    if (accessnotify("view", $notify) === true)
    {
      $template = $notify["template"];
      $tmpl->assign("notify", $notify);
      
      $fragment = $tmpl->fetch($template);
      $checksum = crc32($fragment);

      $urgent = toboolean($notify["urgent"]);
      
      $result = [];
      $result["fragment"] = $fragment;
      $result["checksum"] = $checksum;
      $result["urgent"] = $urgent;
      if (in_array($checksum, $currentchecksumlist) === false)
      {
//        logentry("bed.getsentnotifylist.200: notify added");
        $results[] = $result;
        $ids[] = $notify["id"];
      }
    }
  }

  if (count($ids) > 0)
  {
    $res = updatenotifystatus($ids);
    if (PEAR::isError($res))
    {
      logentry("bed.getsentnotifylist.270: " . $res->toString());
      return;
    }
  }
  return $results;
}

function loginlogout()
{
  $tmpl = getsmarty();
  $data = [];
  $data["fragment"] = $tmpl->fetch("topbar-loginlogout.tmpl");
  return $data;
}

function sentnotifycount()
{
  $currentmemberid = getcurrentmemberid();
  $sql = "select sentnotifycount from engine.member where id=?";
  $dat = [$currentmemberid];
  $dbh = dbconnect(SYSTEMDSN);
  $sentnotifycount = $dbh->getOne($sql, ["integer"], $dat, ["integer"]);
  if (PEAR::isError($sentnotifycount))
  {
    logentry("topbar.sentnotifycount.110: " . $res->toString());
  }
  $tmpl = getsmarty();
  $data = [];
  $data["fragment"] = $tmpl->fetch("topbar-notifycount.tmpl");
  return $data;
}

function topbarjoin()
{
  $tmpl = getsmarty();
  $data = [];
  $data["fragment"] = $tmpl->fetch("topbar-join.tmpl");
  return $data;
}

function greetings()
{
  $tmpl = getsmarty();
  $data = [];
  $data["fragment"] = $tmpl->fetch("topbar-greetings.tmpl");
  return $data;
}

function creditcount()
{
  $tmpl = getsmarty();
  $data = [];
  $data["fragment"] = $tmpl->fetch("topbar-credits.tmpl");
  return $data;
}

function topbarupdateinterval()
{
//  logentry("topbarupdateinterval.100: called");
  $data = ["topbarupdateinterval" => 2000];
  return $data;
}

function currentmemberid()
{
  $currentmemberid = getcurrentmemberid();
  $data = ["currentmemberid" => $currentmemberid];
  return $data;
}

function getvar($var)
{
    $res = null;

//    logentry("bed.getvar.100: var=".var_export($var, true));

    switch ($var)
    {
        case "topbar.loginlogout":
        {
          // logentry("engine.topbar.100: calling loginlogout()");
          $res = loginlogout();
          break;
        }
        case "topbar.sentnotifycount":
        {
          $res = sentnotifycount();
          break;
        }
        case "topbar.creditcount":
        {
          $res = creditcount();
          break;
        }
        case "topbar.pointcount":
        {
          $res = pointcount();
          break;
        }
        case "topbar.join":
        {
          $res = topbarjoin();
          break;
        }
        case "topbar.greetings":
        {
          $res = greetings();
          break;
        }
        case "engine.topbarupdateinterval":
        {
          $res = topbarupdateinterval();
//          logentry("bed.340: topbarinterval called, res=".var_export($res, true));
          break;
        }
        case "engine.currentmemberid":
        {
//          logentry("bed.318: currentmemberid");
          $res = currentmemberid();
          break;
        }
        case "engine.sentnotifylist":
        {
          $res = getsentnotifylist();
          break;
        }
        default:
        {
          logentry("bed.320: ".var_export($var, true)." not defined");
          $data = [];
          $data["fragment"] = "<b>undefined var</b>";
          $res = $data;
          break;
        }
    }
    if (PEAR::isError($res))
    {
      logentry("bed.300: " . $res->toString());
      return null;
    }
    return $res;
}

startsession();

// $mode is ignored at the moment
$var = isset($_REQUEST["var"]) ? $_REQUEST["var"] : null;
$res = getvar($var);
//logentry("bed.120: var=".var_export($var, true)." res=".var_export($res, true));
if (PEAR::isError($res))
{
    logentry("engine.bed.100: var=".var_export($var, true)." ". $res->toString());
    $res = ["fragment" => "<b>error</b>"];
//    print encodejson($res);
//    exit(1);
}

$encoded = encodejson($res);
if (isset($_REQUEST["callback"]))
{
//  logentry("bed.prg: callback is set");
  header('Content-type: text/javascript'); // text/plain
//              logentry("bed.php.100: callback exists");
  $output = $_REQUEST["callback"]."({$encoded})";
  print $output;
//              logentry("bed.php.120: output=".var_export($output, true));
}
else
{
  header("Content-type: application/json");
  logentry("bed.php.110: using json (no callback)");
  print $encoded;
}
?>
