<?php

require_once("config.prg");
//require_once("beetlejuice.prg");
require_once("bbsengine5.prg");

class topbar
{
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

  function notifycount()
  {
//    logentry("topbar.900: notifycount()");
    $currentmember = getcurrentmember();
    if (PEAR::isError($currentmember))
    {
      logentry("topbar.notifycount.110: " . $res->toString());
    }
    $tmpl = getsmarty();
    $data = [];
    $data["fragment"] = $tmpl->fetch("topbar-notifycount.tmpl");
    return $data;
  }

  function authenticated()
  {
    $tmpl = getsmarty();
    $data = [];
    $data["fragment"] = $tmpl->fetch("topbar-authenticated.tmpl");
    return $data;
  }
  
  function join()
  {
    $tmpl = getsmarty();
    $data = [];
    $data["fragment"] = $tmpl->fetch("topbar-join.tmpl");
    return $data;
  }

  function loginlogout()
  {
    $tmpl = getsmarty();
    $data = [];
    $data["fragment"] = $tmpl->fetch("topbar-loginlogout.tmpl");
    return $data;
  }

  function main()
  {
    startsession();
    
    $res = null;
      
    $mode = isset($_REQUEST["mode"]) ? $_REQUEST["mode"] : "content";
    // logentry("topbar.120: mode=".var_export($mode, True));
    switch ($mode)
    {
/*
      case "authenticated":
      {
        $res = $this->authenticated();
        break;
      }
*/
      case "loginlogout":
      {
        // logentry("engine.topbar.100: calling loginlogout()");
        $res = $this->loginlogout();
        break;
      }
      
      case "notifycount":
      {
        $res = $this->notifycount();
        break;
      }
      case "creditcount":
      {
        $res = $this->creditcount();
        break;
      }
      case "join":
      {
        $res = $this->join();
        break;
      }
      case "greetings":
      {
        $res = $this->greetings();
        break;
      }
      
      // @FIX: add 'default' case which handles the error
      default:
      {
        $res["fragment"] = "unknown mode {$mode}";
        break;
      }
    }
//    logentry("engine.topbar.110: res=".var_export($res, True));
    $encoded = encodejson($res);
    if (isset($_REQUEST["callback"]))
    {
      print $_REQUEST["callback"]."({$encoded})";
    }
    else
    {
      print $encoded;
    }
    return;
  }
};

$a = new topbar();
$b = $a->main();
if (PEAR::isError($b))
{
    logentry("topbar.999: " . $b->toString());
    displayerrorpage($b->getMessage());
    exit;
}

?>
