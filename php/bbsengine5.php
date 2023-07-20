<?php

/**
 * This file is part of bbsengine5
 * @copyright (C) 2002-2023 zoidtechnologies.com. All Rights Reserved.
 *
 * @package bbsengine5
 */

/**
 * pull in {@link http://pear.php.net/html_quickform pear::html_quickform}
 *
 */
require_once("HTML/QuickForm2.php");
require_once("HTML/QuickForm2/Renderer.php");
require_once("HTML/QuickForm2/Element/Captcha/Image.php");
require_once("InputEmail.php");

/**
 * @since 20160419
 */
require_once("Log.php");

/**
 * pull in smarty class
 */
require_once("Smarty.class.php");

/**
 * pull in {@link http://pear.php.net/mdb2 PEAR::MDB2} database abstraction module
 */
require_once("MDB2.php");

require_once("Pager.php");

// require_once("HTML/Page2.php");

/**
 * returns a configured PEAR::HTML_QuickForm2 instance.
 *
 * the 'tracksubmit' param defaults to true because I cannot think of a reason not to use it that way but it should be a knob.
 *
 * there is a recursive filter automagically added that calls 'trim'.
 *
 * @param string $name name of the form which should be unique to the app
 * @param string $method "post" or "get" defaults to "post"
 * @param string $attributes attributes for the <form> tag i.e. action 
 * @param boolean $tracksubmit defines whether or not to add a hidden field that tracks if the form has been submitted.
 * @return a configured html_quickform2 instance
 *
 * @since 20130209
 */
function getquickform($id, $method="post", $attributes=[], $tracksubmit=true)
{
  $form = new HTML_QuickForm2($id, $method, $attributes, $tracksubmit);
  $form->setAttribute("enctype", "multipart/form-data");
  $form->addHidden("mode")->setValue("NEEDINFO");
  $form->addHidden("id")->setValue("NEEDINFO");
  $form->addHidden("memberid")->setValue("NEEDINFO");
//  $form->addHidden("pageprotocol")->setValue("standard");
  $form->addRecursiveFilter("trim");
//  $form->addRecursiveFilter("strip_tags");

  return $form;
}

/**
 * @since 20140902
 *
 * function which returns a configured Array renderer for use by quickform2
 * @param $options array optional dictionary containing renderer options
 * @return QF2 Array renderer
 */
function getquickformrenderer($options=null)
{
 $_options = array(
  "group_errors" => true, 
  "group_hiddens" => true, 
  "required_note" => "<span class='requiredstar'>*</span> denotes required fields."
 );
 
 if (is_array($options))
 {
  $_options = array_merge($_options, $options);
 }

 $renderer = HTML_QuickForm2_Renderer::factory("array")->setOption($_options);
 return $renderer;
}

/**
 * return a smarty3 template object, configured for the website
 * @param dictionary options an array of options: templatedir, pluginsdir, compiledir, compileid
 * @since 20140710
 */
function _getsmarty($options=null)
{
//    logentry("_getsmarty.100: options=".var_export($options, true));
    
    $s = new Smarty();

    $currentcart = [];
    $currentcart["items"] = [];
    $currentcart["itemcount"] = 0;
    
    $s->assign("currentcart", $currentcart); // getcurrentcart());

    if (is_array($options))
    {
      if (array_key_exists("templatedir", $options) === true)
      {
        $s->setTemplateDir($options["templatedir"]);
      }
      if (array_key_exists("pluginsdir", $options) === true)
      {
        $s->addPluginsDir($options["pluginsdir"]);
      }
      if (array_key_exists("compiledir", $options) === true)
      {
        $s->compile_dir = $options["compiledir"];
      }
      if (array_key_exists("compileid", $options) === true)
      {
        $s->compile_id = $options["compileid"];
      }
      if (array_key_exists("vars", $options) === true)
      {
        foreach ($options["vars"] as $k => $v)
        {
          $s->assign($k, $v);
        }
      }
    }
    
    $currentmemberid = getcurrentmemberid();
    
    if ($currentmemberid > 0)
    {
      $currentmember = getcurrentmember();
      if (PEAR::isError($currentmember))
      {
        logentry("getsmarty.10: " . $currentmember->toString());
        return PEAR::raiseError($currentmember);
      }
    }
    else
    {
      $currentmember = [];
      $currentmember["id"] = null;
    }
    $flags = getflags($currentmemberid);
    if (PEAR::isError($flags))
    {
      logentry("getsmarty.42: " . $flags->toString());
      return PEAR::raiseError($flags);
    }

    $currentmember["flags"] = $flags;

    $s->assign("currentpage", getcurrentpage());
    $s->assign("currentmemberid", $currentmemberid);
    $s->assign("currentmember", $currentmember);
    $s->assign("currentaction", getcurrentaction());
    $s->assign("currentsite", getcurrentsite());
    $s->assign("currenturi", getcurrenturi());
    $s->assign("currentpath", getcurrentpath());
    $s->assign("currentsig", getcurrentsig());
    $s->assign("sitevars", getsitevars());

//    logentry("getsmarty.43: currentsite=".var_export(getcurrentsite(), true));

    
//    logentry("getsmarty.44: gettemplatedir=".var_export($s->getTemplateDir(), true));
    return $s;
}

/**
 * define getsmarty() in case an upper layer did not define it
 * @since 20140710
 */
if (function_exists("getsmarty") === false)
{
  function getsmarty($options=null)
  {
    $options = [];
    $options["pluginsdir"] = SMARTYPLUGINSDIR;
    $options["templatedir"] = SMARTYTEMPLATESDIR;
    $options["compiledir"] = SMARTYCOMPILEDTEMPLATESDIR;
    $options["compileid"] = LOGENTRYPREFIX;
    return _getsmarty($options);
  }
}

/**
 * display a redirect page template with message and optional url
 * 
 * @param string $message
 * @param string $url
 * @access public
 */
function displayredirectpage($message, $url = null, $delay = 0)
{
  // if we were not given a url to redirect to, get the last one that was
  // set and use that.
  $url = ($url === null) ? getreturntourl() : $url;
  $title = getreturntotitle();
  
  if ($delay === 0)
  {
    header("Location: {$url}");
    return;
  }
  $data = [];
  $data["pagetemplate"] = "redirectpage.tmpl";
  $data["url"] = $url;
  $data["delay"] = $delay;
  $data["message"] = $message;

  logentry("bbsengine5.displayredirectpage.100: delay=".var_export($delay, true));

  return displaypage($data);
}

/**
 * display an error page template with message
 * 
 * @param string $message
 * @param integer $errorcode http error code (i.e. 500, 404)
 * @access public
 * @since 20120608
 */
function displayerrorpage($message, $statuscode=418, $title="error", $template="errorpage.tmpl", $data=[])
{
  logentry("displayerrorpage.100: message=".var_export($message, true)." statuscode=".var_export($statuscode, true));
  
  header("HTTP/1.0 {$statuscode} {$title}", true, $statuscode);
  $data["statuscode"] = $statuscode;
  $data["message"] = $message;
  $data["title"] = $title;
  $data["pagetemplate"] = $template;
  displaypage($data);
  return;
}

/**
 * returns footer.tmpl as a string with optional mantra
 * 
 * @param array $options dictionary of options
 * @since 20110105
 * @access private
 */
/*
function _fetchpagefooter($options=null)
{
  $tmpl = getsmarty();
  return $tmpl->fetch("pagefooter.tmpl");
}

if (!function_exists("fetchpagefooter"))
{
  function fetchpagefooter()
  {
    return _fetchpagefooter();
  }
}
*/
/**
 * put $message into a log at the given priority
 *
 * @since 20080105
 * @param string
 * @param enum
 */
function logentry($message, $priority=LOG_INFO)
{
  
  if (defined("LOGENTRYPREFIX") === false)
  {
    define("LOGENTRYPREFIX", "define-logentryprefix");
  }
  
  $logger = Log::factory("syslog", "", LOGENTRYPREFIX, [], PEAR_LOG_DEBUG);
//  $logger->log("bbsengine5.logentry.100: _SERVER=".var_export($_SERVER, true), $priority);
  $ip = $_SERVER["REMOTE_ADDR"];
  
  $logger->log($message, $priority);
  return;
}

/**
 * set the 'returnto' session variable used by redirectpage()
 *
 * @param string $url
 * @param string $title
 * @return old value
 *
 */
function setreturnto($url=null, $title=null)
{
  $old = getreturntourl();
  $url = ($url === null) ? $old : $url;
//  $parsedurl = parse_url($url);
//  $normalizedurl = http_build_url($parsedurl, $parsedurl);
  $returnto = ["url" => $url, "title" => $title];

  $_SESSION["returnto"] = $returnto;
    
//  logentry("setreturnto: url='{$url}'  title='{$title}'");

  return $old;
}
               
/**
 * get the 'returnto' session var which contains 'url' and 'title', falling back to SITEURL and SITETITLE from config
 *
 * @since 20150722
 * @return array with two keys 'url' and 'title'
*/
function getreturnto()
{
 return isset($_SESSION["returnto"]) ? $_SESSION["returnto"] : array("url" => SITEURL, "title" => SITETITLE);
}
                 
/**
 * returns the returntourl as a string if it has been set, else uses SITEURL define
 *
 */
function getreturntourl()
{
  $url = isset($_SESSION["returnto"]["url"]) ? $_SESSION["returnto"]["url"] : SITEURL;
  
  if (isset($url) && !empty($url) && !is_null($url))
  {
    return $url;
  }
  else
  {
    return SITEURL;
  }
}
                   
function getreturntotitle()
{
  return isset($_SESSION["returnto"]["title"]) ? $_SESSION["returnto"]["title"] : SITETITLE;
}
                     
/**
 * only strip slashes from a string if get_magic_quotes_gpc() returns true
 *
 * this function was ripped from {@link http://pear.php.net/services_amazon/ PEAR::Services_Amazon}.
 *
 * @param string
 * @return string with slashes stripped if get_magic_quotes_gpc returns true
 * 
 */
function safestripslashes($value)
{
  return get_magic_quotes_gpc() ? stripslashes($value) : $value;
}

/**
 * display the permission denied template
 *
 * @access public
 * @since 20121008
 */
function displaypermissiondenied($message="permission denied", $title="permission denied")
{
  logentry("displaypermissiondenied.100: message=".var_export($message, true));
  
  $message = empty($message) ? "permission has been denied. sorry it didn't work out" : $message;
  $res = displayerrorpage($message, 401, $title);
  return $res;
}

/**
 * @since 20110722
 * @deprecated
 */
function permission($name, $memberid=0)
{
  logentry("used deprecated function permission(). use flag() instead.");
  return flag($name, $memberid);
}

/**
 * permission checking function
 * 
 * permissions "PUBLIC" and "AUTHENTICATED" are built-in and checked for
 * specially before any database connection is made. other permissions are
 * in uppercase and must be listed in the flag table. if the member being
 * checked does not have a value set for a particular flag, the default
 * value will be returned.
 *
 * @param string $name 
 * @param integer $memberid
 * @return boolean
 * @since 20080324
 */ 
function flag($name, $memberid=0)
{
  if ($memberid == 0)
  {
    $memberid = getcurrentmemberid();
  }
	
  $name = strtoupper($name);
    
  if ($name == "PUBLIC")
  {
    return true;
  }

  if ($memberid == 0 || is_null($memberid))
  {
    return false;
  }
	
  if ($name == "AUTHENTICATED")
  {
    return true;
  }
    
  $res = getflag($name, $memberid);
  if (PEAR::isError($res))
  {
    logentry("permission: ERROR: " . $res->toString());
    return PEAR::raiseError($res);
  }
  
  if (is_null($res))
  {
    return $res;
  }
  
  if ($res == true)
  {
    return true;
  }
  
  return false;
}

/**
 *
 * connect to a DSN using the MDB2 "singleton" static method, configures the
 * object (quote_identifier set to true, fetchmode set to
 * MDB2_FETCHMODE_ASSOC, and loading the "Extended" module), and returns a
 * reference to it.
 *
 * @param string dsn
 * @return object|error
 */
function dbconnect($dsn)
{
  logentry("dbconnect.100: dsn=".var_export($dsn, true));
  $dbh = MDB2::singleton($dsn);
  if (PEAR::isError($dbh))
  {
    logentry("dbconnect.10: " . $dbh->toString(), LOG_ERROR);
    return $dbh;
  }
  
  $res = $dbh->setFetchMode(MDB2_FETCHMODE_ASSOC);
  if (PEAR::isError($res))
  {
    logentry("dbconnect.12: " . $res->toString(), LOG_NOTICE);
    return $res;
  }
  
  $res = $dbh->loadModule("Extended");
  if (PEAR::isError($res))
  {
    logentry("dbconnect.14: " . $res->toString(), LOG_NOTICE);
    return $res;
  }

  return $dbh;
}

/**
 * return the "current member id" for the session
 *
 * @param string key optional key to use when accessing $_SESSION, defaults to "currentmemberid"
 *
 * @return int
 */
function getcurrentmemberid()
{
  $res = isset($_SESSION["currentmemberid"]) ? intval($_SESSION["currentmemberid"]) : null;
  return $res;
}

/**
 * set the "current member id" for the session
 * 
 * @param integer
 * @return int previous value
 */
function setcurrentmemberid($id)
{
  logentry("setcurrentmemberid.10: id=".var_export($id, true));

  $old = getcurrentmemberid();
  $_SESSION["currentmemberid"] = intval($id);
  return $old;
}

/**
 * returns data for a given member id.
 *
 * @param text $username
 * @return array|PEAR::Error
 * @access public
 * @since 19990102
 */
function getmember($username)
{
  logentry("getmember.110: username=" . $username);

  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("getmember.100: " . $dbh->toString());
    return $dbh;
  }

  $sql = "select * from engine.member where username=? limit 1";
  $dat = array($username);
  $res = $dbh->getRow($sql, null, $dat, array("text"));
  if (PEAR::isError($res))
  {
    logentry("getmember.120: " . $res->toString());
  }
  return $res;
}

function getmemberbyid($id)
{
//  logentry("getmemberbyid.110: id=" . $id);

  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("bbsengine5.getmember.100: " . $dbh->toString());
    return $dbh;
  }

  $sql = "select * from engine.member where id=? limit 1";
  $dat = array($id);
  $res = $dbh->getRow($sql, null, $dat, array("integer"));
  if (PEAR::isError($res))
  {
    logentry("getmember.120: " . $res->toString());
  }
  return $res;
}

function getcurrentmember()
{
  $currentmemberid = getcurrentmemberid();
  return getmemberbyid($currentmemberid);
}

/**
 * an html_quickfom rule which returns true if the given email address is in the database.
 *
 * @param string
 * @param integer
 * @todo is this a duplicate?
 * @see emailaddresscallback()
 *
 */
function emailaddressformrule($value, $id=0)
{
  if (empty($value))
  {
    return false;
  }

  if (emailaddresscallback($value) === false)
  {
    return true;
  }
  else
  {
    return false;
  }
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("bbsengine2.emailaddressformrule: " . $dbh->toString());
    return false;
  }

  $sql = "select id from member where emailaddress=?";
  $dat = array($value);
  $res = $dbh->getOne($sql, "integer", $dat, array("text"));
  if (PEAR::isError($res))
  {
    logentry("bbsengine2.emailaddressformrule: " . $res->toString());
    return false;
  }

  $id = intval($res);
  if ($id > 0)
  {
    return false;
  }

  return true;
}

function datestamp($stamp, $format=null)
{
  if (is_string($format) && !is_null($format) && !empty($format))
  {
    $res = strftime($format, $stamp);
  }
  else
  {
    $res = strftime(DATEFORMAT, $stamp);
  }
//  logentry("datestamp: {$stamp} = {$res}");
  return $res;
}

/**
 * add a flag to the system
 *
 * @since 20121029
 */
function addflag($name, $description, $defaultvalue)
{
  $flag = [];
  $flag["name"] = $name;
  $flag["description"] = $description;
  $flag["defaultvalue"] = $defaultvalue;
  
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("addflag.8: " . $dbh->toString());
    return $dbh;
  }
  $res = $dbh->autoExecute("flag", $flag, MDB2_AUTOQUERY_INSERT);
  if (PEAR::isError($res))
  {
    logentry("addflag.10: " . $res->toString());
    return $res;
  }
  return;
}

/**
 * function to clear a flag, resetting it to the default value for the given user.
 *
 * @since 20121029
 */
function clearflag($name, $memberid=null)
{
  if ($memberid === null)
  {
    $memberid = getcurrentmemberid();
  }
  logentry("clearflag.14: clearing {$name} for memberid {$memberid}");
  
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("clearflag.10: " . $dbh->toString());
    return $dbh;
  }

  $res = $dbh->autoExecute("map_member_flag", null, MDB2_AUTOQUERY_DELETE, "name=".$dbh->quote($name, "text")." and memberid=".$dbh->quote($memberid, "integer"));
  if (PEAR::isError($res))
  {
    logentry("clearflag.12: " . $res->toString());
    return $res;
  }
  return;
}
/**
 * set a flag on the given memberid to the given value
 * 
 * @since 20120409
 * @param string
 * @param boolean
 * @param integer
 */
function setflag($flag, $value, $id=null)
{
  logentry("setflag: id=".var_export($id, true)." flag=".var_export($flag, true)." value=".var_export($value, true));

  if ($id === null)
  {
    $id = getcurrentmemberid();
  }

  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    return $dbh;
  }

//  $sql = "delete from map_member_flag where memberid=" . $dbh->quote($id, "integer") . " and flagname=" . $dbh->quote($flag, "text");
//  $res = $dbh->execute($sql);
  $where = array("memberid=" . $dbh->quote($id, "integer"), "name=" . $dbh->quote($flag, "text"));
  $res = $dbh->autoExecute("engine.map_member_flag", null, MDB2_AUTOQUERY_DELETE, $where);
  if (PEAR::isError($res))
  {
    logentry("setflag.10: " . $res->toString());
    return $res;
  }
  
  $mmf = [];
  $mmf["name"] = $flag;
  $mmf["memberid"] = $id;
  $mmf["value"] = $value;
  $res = $dbh->autoExecute("engine.map_member_flag", $mmf, MDB2_AUTOQUERY_INSERT, array("text", "integer", "boolean"));
  if (PEAR::isError($res))
  {
    logentry("setflag.12: " . $res->toString());
    return $res;
  }

  return;
}

/**
 * returns flag value given the flag name and member id.
 *
 * @param string $flag flag name
 * @param integer $id member id
 * @return boolean
 */
function getflag($flag, $memberid)
{
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    return $dbh;
  }
  
  // @since 20130617
  // thanks to pingwin and teh1ghool on #php (oftc)

//  logentry("getflag.100: flag=".var_export($flag, true)." id=".var_export($id, true));

    $sql = <<<SQL
select 
  f.name, 
  coalesce(mmf.value, f.defaultvalue) as value 
from engine.flag as f
left outer join engine.map_member_flag as mmf on (f.name=mmf.name and mmf.memberid=?) 
where f.name=?;
SQL;

  $dat = array($memberid, $flag);
  $res = $dbh->getRow($sql, null, $dat, array("integer", "text"));
  if (PEAR::isError($res))
  {
    logentry("bbsengine3.getflag.0: " . $res->toString());
    return PEAR::raiseError($res);
  }

  $res = (isset($res["value"]) && $res["value"] == "t") ? true : false;
//  logentry("getflag.100: flag=".var_export($flag, true). " memberid=".var_export($memberid, true)." res=".var_export($res, true));
  return $res;
}

/**
 * return the set of flags and their values for a given memberid.
 * rewritten 2011-jun-23 so it actually works without smarty3 throwing notices about undefined vars
 *
 * @since 20081002
 * @param integer $memberid
 * @return array or PEAR_Error
 */
function getflags($memberid)
{
//  logentry("getflags.10: memberid=".var_export($memberid, true));
  $dbh = dbconnect(SYSTEMDSN);
//  var_export(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("getflags.1: " . $dbh->toString());
    return $dbh;
  }
  $sql = <<<SQL
select 
  flag.name, 
  coalesce(map_member_flag.value, flag.defaultvalue) as value
from engine.flag 
left outer join engine.map_member_flag on flag.name = engine.map_member_flag.name and engine.map_member_flag.memberid=?
SQL;
  $dat = array($memberid);
  $res = $dbh->getAll($sql, null, $dat);
  if (PEAR::isError($res))
  {
    logentry("getflags.10: " . $res->toString());
    return $res;
  }
  $flags = [];
  if ($memberid > 0)
  {
    $flags["AUTHENTICATED"] = true;
  }
  else
  {
    $flags["AUTHENTICATED"] = false;
  }

  foreach ($res as $rec)
  {
    $k = $rec["name"];
    $v = $rec["value"];

    if ($v == "t" || $v == "1")
    {
      $flags[$k] = true;
    }
    elseif ($v == "f" || $v == "0")
    {
      $flags[$k] = false;
    }
  }
//  var_export($flags);
  return $flags;
}

/**
 * returns the maturecontentwarning smarty template as a string.
 *
 * @since 20110601
 */
/*
function fetchmaturecontentwarning()
{
  $tmpl = getsmarty();
  return $tmpl->fetch("maturecontentwarning.tmpl");
}
*/
/**
 * set current page
 *
 * @param string $page
 * @since 20100510
 */
function setcurrentpage($page)
{
//  logentry("setcurrentpage.10: page=".var_export($page, true));
  $_SESSION["currentpage"] = $page;
  return;
}

/**
 * get current page
 *
 * @author Zoid Technologies
 * @since 20100510
 */
function getcurrentpage()
{
  $page = isset($_SESSION["currentpage"]) ? $_SESSION["currentpage"] : null;
  return $page;
}

/**
 * adds a set of html_quickform elements and rules for a captcha
 *
 * @since 20110614
 */
function buildcaptchafieldset($form, $options=null)
{
  $_options = array(
    "label" => "Are You Human?",

    // Captcha options
    "output" => CAPTCHAOUTPUT,
    "width"  => CAPTCHAWIDTH,
    "height" => CAPTCHAHEIGHT,

    // Path where to store images
    "imageDir" => CAPTCHAIMAGEDIR, // DOCUMENTROOT. "captchas/",
    "imageDirUrl" => CAPTCHAIMAGEDIRURL, // "/captchas/",
    "imageOptions" => [
      "font_path"        => CAPTCHAFONTPATH, // /usr/share/fonts/truetype/fonts/",
      "font_file"        => CAPTCHAFONTFILE, // "cour.ttf",
      "text_color"       => CAPTCHATEXTCOLOR, 
      "background_color" => CAPTCHABACKGROUNDCOLOR,
      "lines_color"      => CAPTCHALINESCOLOR
    ],
    "captchaHtmlAttributes" => [ "class" => "captchaclass" ]
  );
  if (is_array($options))
  {
   $_options = array_merge($_options, $options);
  }
  logentry("buildcaptchafieldset.100: " . var_export($_options, true));

  $fs = $form->addFieldset("captcha");
  $el = $fs->addElement(
    new HTML_QuickForm2_Element_Captcha_Image(
      "captcha[image]",
      ["id" => "captcha_image"],
      $_options)
  );
  $fs->setLabel("Human Verification");
  return;
}

/**
 * function which displays the "delete confirmation" template.
 *
 * @since 20110801
 */
/*
function displaydeleteconfirmation($message, $yesuri, $yestxt, $nouri, $notxt, $title=null)
{
  if ($title === null)
  {
    $title = SITETITLE . " - Delete Confirmation";
  }
  $tmpl = getsmarty();
  $tmpl->assign("message", $message);
  $tmpl->assign("yesuri", $yesuri);
  $tmpl->assign("yestxt", $yestxt);
  $tmpl->assign("nouri", $nouri);
  $tmpl->assign("notxt", $notxt);
  $tmpl->display("deleteconfirmation.tmpl");
  return;
}
*/
/**
 * function to set the current "action" so that "view" can be hidden when in view mode, etc
 *
 * @since 20110803
 */
function setcurrentaction($action)
{
  $_SESSION["currentaction"] = $action;
}

/**
 * function to get the current "action" so that "view" can be hidden when in view mode, etc
 *
 * @since 20110803
 */
function getcurrentaction()
{
  $op = isset($_SESSION["currentaction"]) ? $_SESSION["currentaction"] : null;
  return $op;
}

/**
 * function to clear the current action
 *
 * @since 20150309
 */
function clearcurrentaction()
{
  setcurrentaction(NULL);
  return;
}

/**
 * @since 20170505
 */
function get_request_url()
{
  return get_request_scheme() . '://' . $_SERVER['HTTP_HOST'] . $_SERVER['REQUEST_URI'];
}
    
/**
 * @since 20170505
 */
function get_request_scheme()
{
  return (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') ? 'https' : 'http';
}

/**
 * function that returns the current url (protocol, hostname, etc) even tho it is named ..uri()
 * 
 * @since 20110804
 */
function getcurrenturi()
{
  $protocol = (isset($_SERVER["HTTPS"]) && $_SERVER["HTTPS"] !== "off") ? "https" : "http";
  $host = $_SERVER["HTTP_HOST"];
  $uri = $_SERVER["REQUEST_URI"];
  $buf = "{$protocol}://{$host}{$uri}";
//  logentry("getcurrenturi.100: " . var_export($buf, true));
  return $buf;
}

/**
 * html_quickform callback function to check if an email address is already in use in the db
 * 
 * @todo is this a duplicate?
 * @see emailaddressformrule
 *
 * @return true if address is _not_ in the database
 * @since 20101011
 */
function uniqueemailaddresscallback($value)
{
  logentry("uniqueemailaddresscallback.0");

  $sql = "select id from member where emailaddress=?";
  $dat = array($value);

  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("uniqueemailaddresscallback.1: " . $res->toString());
    return PEAR::raiseError($dbh);
  }

  $res = $dbh->getOne($sql, null, $dat);
  if (PEAR::isError($res))
  {
    logentry("uniqueemailaddresscallback.2: " . $res->toString());
    return PEAR::raiseError($res);
  }
  if ($res === null)
  {
    return true;
  }
  return false;
}

/**
 * update user record in database
 *
 * @since 20111128
 */
function updatemember($memberid, $member)
{
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("updatemember.0: " . $dbh->toString());
    return PEAR::raiseError($dbh);
  }
  $res = $dbh->autoExecute("engine.__member", $member, MDB2_AUTOQUERY_UPDATE, "id={$memberid}");
  if (PEAR::isError($res))
  {
    logentry("updatemember.1: " . $res->toString());
    return PEAR::raiseError($res);
  }
  return $res;
}

/**
 * @since 20111215
 * @access public
 */
function startsession()
{
//  logentry("startsession.50: expire=".var_export(SESSIONCOOKIEEXPIRE, true)." domain=".var_export(SESSIONCOOKIEDOMAIN, true));
  
  session_set_cookie_params(SESSIONCOOKIEEXPIRE, "/", SESSIONCOOKIEDOMAIN, false, true);
  session_set_save_handler("_opensession", "_closesession", "_readsession", "_writesession", "_destroysession", "_gcsession");
  ini_set("session.gc_probability", 10);
  ini_set("session.gc_divisor", 100);
  session_name(SESSIONNAME);
  session_start();
  $lifetime = 0;
  setcookie(session_name(),session_id(),time()+$lifetime, false, true);
  return;
}

function checksession()
{
  return true;
}

function endsession()
{
  return true;
}

function getsession($sessionid)
{
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("bbsengine5.getsession.120: " . $dbh->toString());
    return $dbh;
  }
  if ($dbh === null)
  {
    logentry("bbsengine5.getsession.100: dbconnect() returned null");
    return null;
  }

  $sql = "select * from engine.session where sessionid=?";
  $dat = [$sessionid];
  $session = $dbh->getRow($sql, ["integer"], $dat, ["text"]);
  if (PEAR::isError($session))
  {
    logentry("bbsengine5.getsession.140: " . $session->toString());
    return $session;
  }
  if ($session === null)
  {
    logentry("bbsengine5.getsession.160: getsession(".var_export($sessionid, true).") returned null");
    return null;
  }
  
  return $session;
}

/** 
 * custom session handler open function
 *
 * @since 20111228
 * @access private
 */
function _opensession($path, $name)
{
//  logentry("_opensession.10: path=".var_export($path, true)." name=".var_export($name, true));
  return true;
}

/** 
 * custom session handler close function.
 *
 * @since 20111228
 * @access private
 */
function _closesession()
{
//  logentry("_closesession.10: called");
  return true;
}

/** 
 * custom session handler read function.
 *
 * @since 20111228
 * @access private
 */
function _readsession($sessionid)
{
//  logentry("_readsession.100: sessionid=".var_export($sessionid, true));
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("_readsession.120: " . var_export($dbh->toString(), true));
    return "";
  }
  $sql = "select data from engine.session where id=? and expiry >= now()";
  $data = $dbh->getOne($sql, ["text"], [$sessionid], ["text"]);
  if (PEAR::isError($data))
  {
    logentry("_readsession.140: " . var_export($data->toString(), true));
    return "";
  }

//  logentry("_readsession.14: data=".var_export($data, true));

  if ($data === null)
  {
    logentry("_readsession.160: data is null, returning empty string.");
    return "";
  }
  
  $decoded = $data;// decodejson($data);
//  logentry("_readsession.180: decoded=".var_export($decoded, true));
  if ($decoded === null)
  {
    return "";
  }
  return $decoded;
}

/** 
 * custom session handler write function
 *
 * updated 2020apr16 to use the node table
 * commented out and replaced w code from bbsengine4 on 20200503 since session no longer uses engine.node
 *
 * @since 20111228
 * @access private
 */
/*
function _writesession($sessionid, $data)
{
//  logentry("_writesession.100: sessionid=".var_export($sessionid, true)." data=".var_export($data, true));
  
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("_writesession.120: " . $dbh->toString());
    return false;
  }
  $sql = "select id from engine.session where sessionid=?";
  $nodeid = $dbh->getOne($sql, ["integer"], [$sessionid], ["text"]);
  if (PEAR::isError($nodeid))
  {
    logentry("_writesession.140: " . $nodeid->toString());
    return false;
  }
  
//  logentry("_writesession.160: nodeid=".var_export($nodeid, true)." sessionid=".var_export($sessionid, true));

  $memberid = getcurrentmemberid();
  $lastactivity = date(DATE_RFC822, time());
  $ipaddress = $_SERVER["REMOTE_ADDR"];
  $expiry = date(DATE_RFC822, time() + SESSIONCOOKIEEXPIRE);
  //  $data = session_encode();
  $useragent = $_SERVER["HTTP_USER_AGENT"];

//  logentry("_writesession.180: data=".var_export($data, true));

  if ($nodeid === null)
  {
    $session = [];
    $session["sessionid"] = $sessionid;
    $session["data"] = $data;
    $session["expiry"] = $expiry;
    $session["lastactivity"] = $lastactivity;
    $session["ipaddress"] = $ipaddress;
    $session["useragent"] = $useragent;
    $session["memberid"] = $memberid;

    $node = [];
    $node["attributes"] = $session;
    
//    logentry("_writesession.300: node=".var_export($node, true));
//    logentry("_writesession.18: new session=".var_export($session, true));

    $nodeid = insertnode($node);
    logentry("_writesession.200: new session. nodeid=".var_export($nodeid, true));
//    $res = $dbh->autoExecute("engine.__session", $session, MDB2_AUTOQUERY_INSERT);
    if (PEAR::isError($nodeid))
    {
      logentry("_writesession.210: " . $nodeid->toString());
      return false;
    }

    if ($nodeid === null)
    {
      logentry("_writesession.220: insertnode(...) returned null");
      return false;
    }
  }
  else
  {
    $session = [];
    $session["data"] = $data;
    $session["memberid"] = $memberid;
    $session["lastactivity"] = $lastactivity;
    $session["ipaddress"] = $ipaddress;
    $session["expiry"] = $expiry;
    $session["sessionid"] = $sessionid;
    
//    logentry("_writesession.320: session.expiry=".var_export($session["expiry"], true));
//    logentry("_writesession.340: session.lastactivity=".var_export($session["lastactivity"], true));

    $node = [];
    $node["dateupdated"] = "now()";
    $node["updatedbyid"] = $memberid;
    $node["attributes"] = $session;

    // $res = $dbh->autoExecute("engine.__session", $session, MDB2_AUTOQUERY_UPDATE, "id=".$dbh->quote($id, "text"));
//    logentry("_writesession.240: nodeid=".var_export($nodeid, true)." node=".var_export($node, true));
    $res = updatenode($nodeid, $node);
    if (PEAR::isError($res))
    {
      logentry("_writesession.24: ".$res->toString());
      return false;
    }
  }
  return true;
}
*/

/** 
 * custom session handler write function
 *
 * @since 20111228
 * @access private
 */
function _writesession($id, $data)
{
//  logentry("_writesession.10: id=".var_export($id, True)." data=".var_export($data, True));
//  logentry("_writesession.11: session=".var_export($_SESSION, True));
  
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("_writesession.14: " . $dbh->toString());
    return False;
  }
  $sql = "select 1 from engine.__session where id=?";
  $dat = array($id);
  $res = $dbh->getOne($sql, array("integer"), $dat, array("text"));
  if (PEAR::isError($res))
  {
    logentry("_writesession.16: " . $res->toString());
    return False;
  }

  $memberid = getcurrentmemberid();

  if ($res === null)
  {
    $expiry = time() + SESSIONCOOKIEEXPIRE;

    $session = array();
    $session["id"] = $id;
    $session["data"] = session_encode();
    $session["expiry"] = date(DATE_RFC822, $expiry);
    $session["ipaddress"] = $_SERVER["REMOTE_ADDR"];
    $session["useragent"] = isset($_SERVER["HTTP_USER_AGENT"]) ? $_SERVER["HTTP_USER_AGENT"] : "";
    $session["memberid"] = $memberid;
    $session["datecreated"] = "now()";
    
//    logentry("_writesession.18: new session=".var_export($session, True));

    $res = $dbh->autoExecute("engine.__session", $session, MDB2_AUTOQUERY_INSERT);
    if (PEAR::isError($res))
    {
      logentry("_writesession.20: " . $res->toString());
      return False;
    }

  }
  else
  {
    $session = array();
    $session["data"] = session_encode();
    $session["memberid"] = $memberid;

//    logentry("_writesession.22: update session=".var_export($session, True)." id=".var_export($id, True));
    $res = $dbh->autoExecute("engine.__session", $session, MDB2_AUTOQUERY_UPDATE, "id=".$dbh->quote($id, "text"));
    if (PEAR::isError($res))
    {
      logentry("_writesession.24: ".$res->toString());
      return False;
    }
  
  }
  
  return true;
}

/** 
 * custom session handler destroy function
 *
 * @since 20111228
 * @access private
 */
function _destroysession($sessionid)
{
  logentry("_destroy.10: sessionid=".var_export($sessionid, true));
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("_destroy.130: " . $dbh->toString());
    return false;
  }
  $sql = "delete from engine.__session where id=".$dbh->quote($sessionid, "text");
  $res = $dbh->exec($sql);
  if (PEAR::isError($res))
  {
    logentry("_destroy.120: " . $res->toString());
    return false;
  }
  return true;
}

/**
 * custom session handler garbage collection function
 *
 * @since 20111228
 * @access private
 */
function _gcsession($maxlifetime)
{
  if (defined("DEBUGSESSION"))
  {
    logentry("_gcsession.10: maxlifetime=".var_export($maxlifetime, true));
  }
  $dbh = dbconnect(SYSTEMDSN);
  $res = $dbh->autoExecute("engine.__session", null, MDB2_AUTOQUERY_DELETE, "expiry < now()");
  if (PEAR::isError($res))
  {
    logentry("_gcsession.20: " . $res->toString());
    return false;
  }
  return true;
}

/**
 * @since 20120507
 */
function buildlabel($buf)
{
  $buf = strtolower($buf);
  // replace anything that is not a-z0-9 with -
  $buf = preg_replace("@[^a-z0-9_]@","_", $buf);

  // replace 2 or more - with single -
  $buf = preg_replace("@[_-]{2,}@", "_", $buf);

  // trim '_' and '.' from both ends
  $buf = trim($buf, "_");
  $buf = trim($buf, ".");
  
  return $buf;
}

/**
 * @since 20121107
 *
 * transforms the given uri into something that can be used with the 'ltree' type.
 *
 * @param string $name
 * @return string
 */
function buildpath($buf)
{
  if ($buf == "/" || $buf == "")
  {
    return "top";
  }
  $buf = buildlabel($buf);
  $buf = "top.".$buf;

  return $buf;
}

/**
 * builds a uri from a given ltree labelpath
 * 
 * @since 20120507
 * @param labelpath ltree
 * @see buildlabelpath
 *
 */
function builduri($labelpath)
{
  $buf = str_replace("top.", "", $labelpath);
  $buf = str_replace(".", "/", $buf);
  $buf = str_replace("_", "-", $buf);
  $buf = trim($buf);
  $buf = trim($buf, ".");
  $buf .= "/";
  return $buf;
}

function processfile($file)
{
}

/**
 * process an uploaded file
 *
 * rewritten based on code in register.php 2010-10-20
 *
 * changed on 2015-09-01 so it accepts a dictionary (values) as a
 * parameter, because most times this function is called from an update() or
 * insert() function. this change is a COMPAT BUSTER.
 *
 * @since 20100730
 */
function processupload($value, $destinationdir, $prefix="")
{
  if (PEAR::isError($value))
  {
    logentry("bbsengine5.processupload.14: " . $value->toString());
    return $value;
  }

  logentry("---> bbsengine5.processupload.220: value=".var_export($value, true));

  if ($value === null)
  {
    logentry("bbsengine5.processupload.200: value is null");
    return null;
  }

  $multiple = is_array($value["tmp_name"]) ? true : false;
  $uploads = [];
  if ($multiple === false)
  {
    $uploads[] = ["tmp_name" => $value["tmp_name"], "error" => $value["error"], "type" => $value["type"], "size" => $value["size"], "name" => $value["name"]];
  }
  else
  {
    for ($i=0; $i < count($value["tmp_name"]); $i++)
    {
      $uploads[] = ["tmp_name" => $value["tmp_name"][$i], "error" => $value["error"][$i], "type" => $value["type"][$i], "size" => $value["size"][$i], "name" => $value["name"][$i]];
    }
  }
  
  $filenames = [];
  foreach ($uploads as $u)
  {
    logentry("processupload.240: u=".var_export($u, true));
    $error = $u["error"];
    $name = $u["name"];
    $tmpname = $u["tmp_name"];
    if (is_uploaded_file($tmpname) === false)
    {
      logentry("invalid upload: ".var_export($tmpname, true));
      continue;
    }

    switch ($error)
    {
      case 0:
      {
        $f = $prefix.buildlabel(rand(1,999).trim($name));
        if (move_uploaded_file($tmpname, $destinationdir.$f) === false)
        {
          logentry("processupload.460: error moving uploaded file");
          break;
        }
        $filenames[] = $f;
        break;
      }
      case 1:
      case 2:
      {
        logentry("processupload.400: file is too big error={$error}, tmpname={$tmpname}");
        break;
      }
      case 3:
      {
        logentry("processupload.420: partial upload (3)");
        break;
      }
      case 4:
      {
        logentry("processupload.440: no files uploaded (4)");
        break;
      }
    }
  }
  return $filenames;
}

/**
 * function to determine access to the "member" table
 *
 * @param string
 * @param array
 * @param integer
 * @since 20130225
 */
function accessmember($op, $data=null, $memberid=null)
{
  if ($memberid === null)
  {
    $memberid = getcurrentmemberid();
  }

  $member = isset($data["member"]) ? $data["member"] : null;

  switch ($op)
  {
    case "editcredits":
    {
      if (flag("SYSOP") == true)
      {
        $res = true;
        break;
      }
      $res = false;
      break;
    }
    case "detail":
    {
      $res = true;
      break;
    }
    case "changepassword":
    {
      if (flag("AUTHENTICATED") === false)
      {
        $res = false;
        break;
      }
      if (flag("SYSOP", $memberid) === true || ($memberid !== null && $data["id"] == $memberid))
      {
        $res = true;
        break;
      }
      $res = false; 
      break;
    }
    case "add":
    {
      return true;
     if (flag("SYSOP", $memberid) === true)
     {
       $res = true;
     }
     else
     {
       $res = false;
     }
     break;
    }
    case "edit":
    {
      if (flag("SYSOP", $memberid) === true || $data["id"] == $memberid)
      {
        $res = true; 
        break;
      }
      $res = false; 
      break;
    }
    case "editflags":
    {
      if (flag("SYSOP", $memberid) === true)
      {
        $res = true; 
        break;
      }
      $res = false; 
      break;
    }
    case "sendverifyemail":
    {
      if (flag("SYSOP", $memberid) === true)
      {
        $res = true; 
        break;
      }
      $res = false; 
      break;
    }
    default:
    {
      $res = null;
      break;
    }
  }
//  logentry("accessmember.50: op=".var_export($op, true)." member.id=".var_export($data["id"], true)." memberid=".var_export($memberid, true)." res=".var_export($res, true));
  return $res;  
}

/**
 * @since 20131031
 */
function setcurrentsite($site)
{
  $_SESSION["currentsite"] = $site;
//  logentry("setcurrentsite.10: site=".var_export($site, true));
  return;
}

/**
 * @since 20131031
 */
function getcurrentsite()
{
  $site = isset($_SESSION["currentsite"]) ? $_SESSION["currentsite"] : null;
//  logentry("getcurrentsite.10: site=".var_export($site, true));
  return $site;
}

/**
 * function to add a trailing slash if needed. also removes duplicate slashes.
 * @since 20140511
 *
 */
function normalizepath($path)
{
  $path = preg_replace('@[/]{2,}@', '/', $path);
  if (substr($path, -1) != "/")
  {
    $path .="/";
  }
  return $path;
}

/**
 * returns a template name for the given notify type
 *
 * @since 20200505
 * @return string
 * @param string $type
 */
function buildnotifytemplatename($type)
{
  $res = null;

/*
  switch ($type)
  {
    case "link-approved":
    {
      $res = "notify-link-approved.tmpl";
      break;
    }
    case "link-added":
    {
      $res = "notify-link-added.tmpl";
      break;
    }
    default:
    {
      $name = "notify-{$type}.tmpl";
      $smarty = getsmarty();
      if ($smarty->templateExists($name))
      {
        $res = $name;
      }
      break;
    }
  }
*/
  $template = "notify-{$type}.tmpl";
  $tmpl = getsmarty();
  if ($tmpl->templateExists($template))
  {
    return $template;
  }
  return null;
}

/**
 * @since 20200528
 * @return null or PEAR::Error
 * function which updates an existing notify record
 * @param id integer notify id
 * @param notify notify record
 */
function updatenotify($id, $notify)
{
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("updatenotify.200: " . $dbh->toString());
    return $dbh;
  }
  $notify["dateupdated"] = "now()";
  $notify["updatedbyid"] = getcurrentmemberid();
  $res = $dbh->autoExecute();
  return;
}
/**
 * @since 20140513
 * @param type string
 * @param memberid integer
 * @param data dictionary automagically converted to json
 */
function sendnotify($type, $memberid, $data=null, $status="sent")
{
  $currentmemberid = getcurrentmemberid();
  
  $notify = [];
  $notify["type"] = $type;
  $notify["memberid"] = $memberid;
  $notify["sessionid"] = session_id();
  $notify["data"] = encodejson($data);
  $notify["status"] = $status;
  $notify["datecreated"] = "now()";
  $notify["createdbyid"] = $currentmemberid;
  
  $notify["template"] = buildnotifytemplatename($type);

  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("sendnotify.100: " . $dbh->toString());
    return $dbh;
  }
  logentry("sendnotify.200: notify=".var_export($notify, true));
  
  $res = $dbh->autoExecute("engine.__notify", $notify, MDB2_AUTOQUERY_INSERT);
  if (PEAR::isError($res))
  {
    logentry("sendnotify.110: " . $res->toString());
    return $res;
  }
  logentry("sendnotify.120: type=".var_export($type, true)." memberid=".var_export($memberid, true));
  return;
}

/**
 * unset the "current member id" for the session aka "logout"
 * 
 * @since 20121018
 */
function clearcurrentmemberid()
{
  logentry("clearcurrentmemberid.10: unsetting session var");
  unset($_SESSION["currentmemberid"]);
  removesessioncookie();
  return;
}

/** 
 * invalidate session cookie. from {@link https://www.owasp.org/index.php/PHP_Security_Cheat_Sheet#Cookies OWASP Cookies}
 * 
 * @since 20140724
 */
function removesessioncookie()
{
  $name = session_name();
  setcookie($name, "", 1);
  setcookie($name, false);
  unset($_COOKIE[$name]);
  return;
}

/**
 * @since 20140727
 *
 */
function getsig($labelpath)
{
  $sql = "select * from engine.sig where path=?";
  $dat = array($labelpath);
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("getsig.110: " . $res->toString());
    return $dbh;
  }

  $res = $dbh->getRow($sql, null, $dat, array("text"));
  if (PEAR::isError($res))
  {
    logentry("getsig.100: " . $res->toString());
    return $res;
  }
  return $res;
}

// https://github.com/timostamm/NonceUtil-PHP
function generatenonce($secret, $timeoutSeconds=180) 
{
  if (is_string($secret) == false || strlen($secret) < NONCESALTLENGTH) 
  {
    // missing valid secret
    return PEAR::raiseError("generatenonce.100: secret is not a string or it is not of proper length (".var_export(NONCESALTLENGTH, true).")");
  }
  $salt = generatesalt();
  $time = time();
  $maxTime = $time + $timeoutSeconds;
  $nonce = $salt . "," . $maxTime . "," . sha1( $salt . $secret . $maxTime );
  return $nonce;
}

function checknonce($secret, $nonce) 
{
  if (is_string($nonce) == false) 
  {
    return false;
  }
  $a = explode(',', $nonce);
  if (count($a) != 3) 
  {
    return false;
  }
  $salt = $a[0];
  $maxTime = intval($a[1]);
  $hash = $a[2];
  $back = sha1( $salt . $secret . $maxTime );
  if ($back != $hash) 
  {
    return false;
  }
  if (time() > $maxTime) 
  {
    return false;
  }
  return true;
}

function generatesalt() 
{
  $length = NONCESALTLENGTH;
  $chars='1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM';
  $ll = strlen($chars)-1;
  $o = '';
  while (strlen($o) < $length) 
  {
    $o .= $chars[ rand(0, $ll) ];
  }
  return $o;
}

/**
 * @since 20140805
 */
function buildmemberfieldset($form, $flags=[])
{
  $fieldset = $form->addFieldset("member");
  $fieldset->setLabel("account");
  
  $username = $fieldset->addText("username");
  $username->setLabel("Username");
  $username->addRule("required", "'Username' is a required field");
  $uniqueusername = isset($flags["uniqueusername"]) ? $flags["uniqueusername"] : True;
  if ($uniqueusername === True)
  {
    $username->addRule("callback", "Username is currently in use", "uniqueusernamecallback");
  }

  $email = $fieldset->addElement(new HTML_QuickForm2_Element_InputEmail("email"));
  $email->setLabel("E-Mail address (must be valid for account verification)");
  $email->addRule("required", "'E-Mail address' is a required field.");
  
  $name = $fieldset->addText("name");
  $name->setLabel("Name");
  
  if (accessmember("editcredits"))
  {
    $credits = $fieldset->addText("credits", ["id" => "credits"]);
    $credits->setLabel("credits");
    $credits->addRule("regex", "'Credits' must be an integer", '/^[0-9]+$/');
  }
  return;
}

/**
 * @since 20140825
 */
function clearpageprotocol()
{
  $_SESSION["pageprotocol"] = "standard";
//  logentry("clearpageprotocol.100: cleared");
  return $_SESSION["pageprotocol"];
}

/**
 * @since 20140822
 *
 * @param string $pageproto
 */
function setpageprotocol($pageprotocol)
{
  $_SESSION["pageprotocol"] = $pageprotocol;
  logentry("setpageprotocol.100: pageprotocol=".var_export($pageprotocol, true));
  return;
}

/**
 * @since 20140829
 * @param ltree $labelpath ltree label path
 * @return ltree labelpath except for last element
 */
function buildparentlabelpath($labelpath)
{
  $res = implode(".",explode(".", $labelpath, -1));
  if (empty($res))
  {
    return "top";
  }
  return $res;
}

if (function_exists("buildmemberrecord") === false)
{
  function buildmemberrecord($values)
  {
    $member = [];
    $member["email"] = $values["email"];
    $member["name"] = $values["name"];
    $member["username"] = $values["username"];
    
    if (isset($values["credits"]))
    {
      $member["credits"] = intval($values["credits"]);
    }

    return $member;
  }
}

/**
 * @since 20180717
 */
function buildflagrecord($values)
{
  $flag = [];
  $flag["name"] = $values["name"];
  $flag["description"] = $values["description"];
  $flag["defaultvalue"] = isset($values["defaultvalue"]) ? true : false;
  return $flag;
}

/**
 * @since 20140901
 * @param $username text handle
 * @return mixed memberid for $name, NULL if name doesn't exist, PEAR::Error for errors
*/
function getmemberid($username)
{
  $sql = "select id from engine.member where username=?";
  $dat = array($username);
  $dbh = dbconnect(SYSTEMDSN);
  $res = $dbh->getOne($sql, array("integer"), $dat, array("text"));
  if (PEAR::isError($res))
  {
    logentry("getmemberid.100: " . $res->toString());
  }
  if ($res === NULL)
  {
    logentry("getmemberid.102: getmemberid(".var_export($name, true).") returned null");
  }
  return $res;
}

/**
 * @since 20140831
 * 
 */
function checkpassword($plaintext, $args) // $memberid, $plaintext)
{
  $memberid = $args[0];
  logentry("checkpassword.200: memberid=".var_export($memberid, true));
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("checkpassword.100: " . $dbh->toString());
    return $dbh;
  }
  $sql = "select crypt(?, password) as valid from engine.member where id=?";
  $dat = [$plaintext, $memberid];
  $res = $dbh->getOne($sql, ["boolean"], $dat, ["text", "integer"]);
  if (PEAR::isError($res))
  {
    logentry("checkpassword.130: " . $res->toString());
    return false;
  }
  logentry("checkpassword.160: res=".var_export($res, true));
  if (PEAR::isError($res))
  {
    logentry("checkpassword.120: " . $res->toString());
    return false;
  }
  if ($res === null)
  {
    logentry("checkpassword.122: res=null");
    return false;
  }
  if ($res === true)
  {
    logentry("checkpassword.140: password correct");
    return true;
  }
  return false;
}

/**
 * @since 20141016
 */
function buildnewpasswordfieldset($form)
{
 $fieldset = $form->addElement("fieldset");
 $fieldset->setLabel("Password");
 $newpassword = $fieldset->addElement("password", "password"/*, array("style" => "width: 200px;")*/)->setLabel("Password:");
 $newpassword->addRule("required", "'Password' is a required field.");
 $repeatpassword = $fieldset->addElement("password", "repeatpassword"/*, array("style" => "width: 200px;")*/)->setLabel("Repeat password:");
 $repeatpassword->addRule("required", "'PasswordRepeat' is a required field.");
// $newPassword->addRule("nonempty")->and_($repPassword->createRule("nonempty"))->or_($repPassword->createRule("eq", "The passwords do not match", $newPassword));
 $repeatpassword->addRule("eq", "The passwords do not match.", $newpassword);
 return;
}
/**
 * @since 20140831
 */
function buildchangepasswordfieldset($form, $data=[])
{
/*
  $group = $form->addGroup()->setLabel("group");
  $group->addPassword("password")->setLabel("Password");
  $group->addPassword("repeatpassword")->setLabel("Repeat Password");
*/
 $memberid = isset($data["memberid"]) ? intval($data["memberid"]) : null;
 logentry("buildpasswordfieldset.100: memberid=".var_export($memberid, true));
 
 $fieldset = $form->addElement("fieldset")->setLabel("Password");
 $oldPassword = $fieldset->addElement("password", "oldPassword", array("class" => "form-control"))->setLabel("Type your old password");

// $oldPassword->addRule("empty")->or_($oldPassword->createRule("callback", "wrong password", array("callback" => "checkpassword", "arguments" => array($memberid))));
 $oldPassword->addRule("empty")->or_($oldPassword->createRule("callback", "wrong password", ["callback"=> "checkpassword", "arguments" => [[$memberid]]]));
 $newPassword = $fieldset->addElement("password", "newPassword", array("class" => "form-control"))->setLabel("Type your new password");
 $repPassword = $fieldset->addElement("password", "newPasswordRepeat", array("class" => "form-control"))->setLabel("Confirm your new password");

 // this behaves exactly as it reads: either "password" and "password
 // repeat" are both empty or they should be equal

 $newPassword->addRule("empty")->and_($repPassword->createRule("empty"))->or_($repPassword->createRule("eq", "The passwords do not match", $newPassword));

 // Either new password is not given, or old password is required
 $newPassword->addRule("empty")->or_($oldPassword->createRule("nonempty", "Supply old password if you want to change it"));

 //  $newPassword->addRule("minlength", 'The password is too short', 6, HTML_QuickForm2_Rule::ONBLUR_CLIENT_SERVER);

 // No sense changing the password to the same value
 $newPassword->addRule("nonempty")->and_($newPassword->createRule("neq", "New password is the same as the old one", $oldPassword));

  return;
}

/**
 * @since 20140908
 */
/* removed function fetchtopbar */

/**
 * @since 20140910
 */
function normalizeuri($uri)
{
 $uri = preg_replace("@(/){2,}@", '$1', $uri);
 return $uri;
}

/**
  * this function is intended to be used as part of an html_quickform2 callback rule
  *
  * @return boolean
  * @param args dictionary with 'username' and 'password' as keys
*/
function checklogin($args)
{
  logentry("checklogin.40: args=".var_export($args, true));

  $username = $args["username"];
  $plaintext = $args["password"];

  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("checklogin.80: " . $dbh->toString());
    return false;
  }

  $sql = "SELECT (password = crypt(?, password)) AS correct FROM engine.member where username=?";
  $dat = [$plaintext, $username];

  $res = $dbh->getOne($sql, ["boolean"], $dat, ["text", "text"]);
  if (PEAR::isError($res))
  {
    logentry("checklogin.100: " . $res->toString());
    return false;
  }
  
  if ($res === null)
  {
    logentry("checklogin.120: fail");
    return false;
  }
  
  logentry("checklogin.160: res=".var_export($res, true));
  return toboolean($res);
}

function buildloginfieldset($form)
{
  $fieldset = $form->addElement("fieldset");
  $fieldset->setLabel("Authenticate");
  $username = $fieldset->addElement("text", "username");
  $username->setLabel("Username");
  $username->addRule("required", "'Username' is a required field");

  $password = $fieldset->addElement("password", "password");
  $password->setLabel("Password");
  $password->addRule("required", "'Password' is a required field");
  
  $fieldset->addRule("callback", "'Username' or 'Password' incorrect.", "checklogin"); // array("callback" => "checklogin"));
  
  return;
}


/**
 * calls json_encode() with default parameters
 *
 * @since 20140730
 * @since 20230329 copied from bbsengine5.php
 */
function encodejson($data)
{
 // @see http://us3.php.net/manual/en/json.constants.php
 return json_encode($data); // , JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_NUMERIC_CHECK); // JSON_UNESCAPED_UNICODE in 5.4+
}

/**
 * decodes given json data into a dictionary (associative array)
 * 
 * @since 20140730
 */
function decodejson($data)
{
 if (is_string($data) === false)
 {
  logentry("decodejson.100: data=".var_export($data, true));
  return;
 }
 return json_decode($data, true);
}

/**
 * @since 20141223
 */
function getlastlogin()
{
 $lastlogin = isset($_SESSION["lastlogin"]) ? $_SESSION["lastlogin"] : null;
 return $lastlogin;
}

/**
 * @since 20141223
 */
function setlastlogin($lastlogin)
{
 logentry("setlastlogin.100: lastlogin=".var_export($lastlogin, true));

 $_SESSION["lastlogin"] = $lastlogin;
 return;
}

/**
 * @since 20141223
 */
function getlastloginfrom()
{
 $lastloginfrom = isset($_SESSION["lastloginfrom"]) ? $_SESSION["lastloginfrom"] : null;
 return $lastloginfrom;
}

/**
 * @since 20141223
 */
function setlastloginfrom($lastloginfrom)
{
 $_SESSION["lastloginfrom"] = $lastloginfrom;
 return;
}

/**
 * @since 20121017
 *
 * a quickform2 callback to see if the given $value exists in the name field of the member table
 */
function uniqueusernamecallback($value)
{
  logentry("uniqueusernamecallback.0");

  $value = trim($value);
  $value = strip_tags($value);
  $sql = "select 1 from engine.member where name=?";
  $dat = array($value);

  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("uniqueusernamecallback.1: " . $res->toString());
    return PEAR::raiseError($dbh);
  }

  $res = $dbh->getOne($sql, null, $dat);
  if (PEAR::isError($res))
  {
    logentry("uniqueusernamecallback.2: " . $res->toString());
    return PEAR::raiseError($res);
  }
  if ($res === null)
  {
    return true;
  }
  return false;
}

function setpassword($memberid, $plaintext)
{
  logentry("setpassword.80: memberid=".var_export($memberid, true)." plaintext=".var_export($plaintext, true));
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("setpassword.100: " . $dbh->toString());
    return $dbh;
  }

  $sql = "update engine.__member set password=crypt(".$dbh->quote($plaintext, "text").", gen_salt('bf')) where id=".$dbh->quote($memberid);
  $res = $dbh->exec($sql);
  if (PEAR::isError($res))
  {
    logentry("setpassword.120: " . $res->toString());
    return $res;
  }
  return;
}

if (function_exists("buildnotifyrecord") === false)
{
 /**
  * @since 20160202
  */
 function buildnotifyrecord($key, $notify)
 {
  switch ($key)
  {
   default:
   {
    logentry("buildnotifyrecord.100: unhandled key '".var_export($key, true)."'");
    break;
   }
  }
 }
}

if (function_exists("buildnotifyactions") === false)
{
 // @since 20130520
 function buildnotifyactions($notify)
 {
//   logentry("buildnotifyactions.100: getcurrentaction() == ".var_export(getcurrentaction(), true));
 //    logentry("buildnotifyactions.150: notify=".var_export($notify, true));

   $type = isset($notify["type"]) ? $notify["type"] : null;
//   logentry("buildnotifyactions.120: type=".var_export($type, true));

//   $data = $notify["data"];
   
   $id = intval($notify["id"]);

   $actions = [];
   if (accessnotify("delete", $notify) === true)
   {
     $actions[] = [ "class" => "fa fa-fw fa-trash", "href" => ENGINEURL."notify-delete-{$id}", "title" => "delete" ];
   }

/*
   if (accessnotify("detail", $notify) === true)
   {
     $actions[] = [ "class" => "fa fa-fw fa-angle-double-down", "href" => ENGINEURL."notify-detail-{$id}", "title" => "detail" ];
   }
*/
   if (accessnotify("edit", $notify) === true)
   {
     $actions[] = [ "class" => "fa fa-fw fa-edit", "href" => ENGINEURL."notify-edit-{$id}", "title" => "edit" ];
   }
   if (accessnotify("markdelivered", $notify) === true)
   {
     $actions[] = [ "href" => ENGINEURL."notify-markdelivered-{$id}", "title" => "mark delivered" ];
   }
   if (accessnotify("marksent", $notify) === true)
   {
     $actions[] = [ "href" => ENGINEURL."notify-marksent-{$id}", "title" => "mark sent" ];
   }
   return $actions;
 }
}

function _buildnotifydata($notify)
{
    $type = $notify["type"];

    $data = $notify["data"];

    $dat = [];

    switch($type)
    {
      default:
      {
        logentry("bbsengine3._buildnotifydata: unhandled type ".var_export($type, true));
        break;
      }
    }

    return $dat;
}

if (function_exists("buildnotifydata") === false)
{  
  function buildnotifydata($notify)
  {
    logentry("buildnotifydata.999: using _buildnotifydata");
    return _buildnotifydata($notify);
  }
}

/**
 * @since 20130411
 */
function getnotify($notifyid)
{
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("getnotify.10: " . $dbh->toString());
    return $dbh;
  }
  $sql = "select * from engine.notify where id=?";
  $dat = array($notifyid);
  $res = $dbh->getRow($sql, null, $dat, array("integer"));
  if (PEAR::isError($res))
  {
    logentry("getnotify.12: " . $res->toString());
    return $res;
  }
  $res["data"] = decodejson($res["data"]);
  return $res;
}

/**
 * @since 20130401
 */
function gettotalnotifications($id)
{
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("gettotalnotifications.10: " . $dbh->toString());
    return $dbh;
  }
  $sql = "select count(id) from engine.notify where memberid=?";
  $dat = array($id);
  $res = $dbh->getOne($sql, null, $dat, array("integer"));
  if (PEAR::isError($res))
  {
    logentry("gettotalnotifications.12: " . $res->toString());
    return $res;
  }
  if ($res === null)
  {
    return 0;
  }
  return intval($res);
}

/**
 * @since 20130401
 */
function gettotalunreadnotifications($id)
{
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("gettotalunreadnotifications.10: " . $dbh->toString());
    return $dbh;
  }
  $sql = "select count(id) from engine.notify where memberid=? and datereadepoch is null and detailtemplate <> ''";
  $dat = array($id);
  $res = $dbh->getOne($sql, null, $dat, array("integer"));
  if (PEAR::isError($res))
  {
    logentry("gettotalunreadnotifications.12: " . $res->toString());
    return $res;
  }
  if ($res === null)
  {
    return 0;
  }
  return intval($res);
}

/**
 * @since 20130411
 */
function accessnotify($op, $notify=null, $memberid=null)
{
  $currentmemberid = getcurrentmemberid();
  $memberid = intval($notify["memberid"]);
  $status = $notify["status"];

//  logentry("accessnotify.42: op=".var_export($op, true)." currentmemberid=".var_export($currentmemberid, true)." memberid=".var_export($memberid, true));

  switch ($op)
  {
    case "edit":
    {
      if (flag("SYSOP") === true)
      {
        return true;
      }
      return false;
    }
    case "detail":
    {
      if ($notify["template"] == "")
      {
        return false;
      }
      if (flag("AUTHENTICATED") === true && ($memberid === $currentmemberid || flag("SYSOP") === true))
      {
        return true;
      }
      return false;
      
    }
    case "view":
    case "delete":
    case "display":
    {
      if (flag("AUTHENTICATED") === true && ($memberid === $currentmemberid || flag("SYSOP") === true))
      {
        return true;
      }
      return false;
    }
    case "marksent":
    {
      if ($status === "sent")
      {
        return false;
      }
      return true;
    }
    case "markdelivered":
    {
      if ($status === "delivered")
      {
        return false;
      }
      return true;
    }
    default:
    {
      logentry("accessnotify.200: undefined op");
      return null;
    }
  }
  return false;
}

/**
 * @since 20150410
 */
function getmemberidfromemail($email)
{
  $sql = "select id from engine.member where email=?";
  $dat =  array($email);
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("getmemberidfromemail.100: " . $dbh->toString());
    return $dbh;
  }
  $res = $dbh->getOne($sql, array("integer"), $dat, array("text"));
  if (PEAR::isError($res))
  {
    logentry("getmemberidfromemail.110: " . $res->toString());
    return $res;
  }
  if ($res === null)
  {
    logentry("getmemberidfromemail.120: query returned null");
    return PEAR::raiseError("Unable to get memberid from email address (code: getmemberidfromemail.120)");
  }
  return intval($res);
}

/**
 * @since 20150420
 */
function getmemberidfrom($name, $value, $type)
{
  logentry("getmemberidfrom.105: name=".var_export($name, true)." value=".var_export($value, true)." type=".var_export($type, true));

  $sql = "select id from engine.member where {$name}=?";
  $dat =  array($value);
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("getmemberidfrom.100: " . $dbh->toString());
    return $dbh;
  }
  $res = $dbh->getOne($sql, array("integer"), $dat, array($type));
  if (PEAR::isError($res))
  {
    logentry("getmemberidfrom.110: " . $res->toString());
    return $res;
  }
  
  return $res;
  
}

function getmemberidfromusername($username)
{
  $res = getmemberidfrom("name", $username, "text");
  if (PEAR::isError($res))
  {
    logentry("getmemberidfromusername.100: " . $res->toString());
  }
  return $res;
  
}

if (function_exists("buildbuttonfieldset") === false)
{
  /**
   * @since 20150418
   */
  function buildbuttonfieldset($form, $submitlabel="NEEDINFO", $attributes=null)
  {
    if (is_array($attributes))
    {
      $attributes["value"] = $submitlabel;
    }
    else
    {
      $attributes = array("value" => $submitlabel);
    }
    $fs = $form->addElement("fieldset");
    $el = $fs->addElement("submit", "submit", $attributes);
    return;
    
/*
    $buttons = [];
    
    $buttons[] = &HTML_QuickForm2_Factory::createElement("submit", null, $submitlabel, array("id" => "submitform"));
    $form->addGroup($buttons);
  //    $form->addElement("image", "clicktocontinue", "/images/clicktocontinue.png");

    return;
*/
  }
}

/**
 * @since 20180804
 * @param mixed field
 * @param string label
 * @param boolean default 
 * @return boolean
 */
function toboolean($value, $label="label", $default=false)
{
//  logentry("toboolean.100: {$label}=".var_export($value, true));
/*
  if (is_array($value) === true)
  {
    $dict = $value[0];
    $key = $value[1];
    
    if (isset($dict[$key]) === true)
    {
      $value = true;
    }
    else
    {
      $value = false;
    }
  }
*/  
//  logentry("toboolean.110: value=".var_export($value, true));

  if (is_null($value) === true)
  {
//    logentry("toboolean.114: ".var_export($label, true)."=null returning ".var_export($default, true));
    return $default;
  }

  if (is_bool($value) === true)
  {
//    logentry("toboolean.120: value ".var_export($value, true). " for {$label} is already a boolean value");
    return $value;
  }

  if ($value === "t" || $value == 1)
  {
//    logentry("toboolean.150: value ".var_export($value, true)." returns true for ".var_export($label, true));
    return true;
  }

  if ($value === "f" || $value == 0)
  {
//    logentry("toboolean.160: value ".var_export($value, true)." returns false for ".var_export($label, true));
    return false;
  }

  logentry("toboolean.170: returning default of ".var_export($default, true)." for ".var_export($label, true));
  return $default;
}

/**
 * handle a form given an html_quickform2 instance, a callback function and a page title. if the form validates, the callback function is called. 
 * 
 * @param form html_quickform2 instance
 * @param callback function/method to call if form validates
 * @param pagetitle string page title
 * @return whatever value the callback returns. 'true' should be used for 'success'.
 * @since 20150408
 */
function handleform($form, $callback)
{
  $issubmitted = $form->isSubmitted();
  $validate = $form->validate();

  logentry("handleform.100: issubmitted=".var_export($issubmitted, true)." validate=".var_export($validate, true));
  
  if ($issubmitted === true)
  {
    $value = $form->getValue();
  }
  if ($issubmitted === true && $validate === true)
  {
    foreach ($form->getElements() as $element)
    {
      // @FIX: handle nested fieldsets
//      logentry("handleform.200: inside foreach. class=".var_export(get_class($element), true));
      if ($element instanceof HTML_QuickForm2_Element_Captcha)
      {
        logentry("handleform.210: clearing captcha session");
        $element->clearCaptchaSession();
      }
    }

    logentry("handleform.110: form validated");
    
    $form->toggleFrozen(true);
    $values = $form->getValue();
    logentry("handleform.120: values=".var_export($values, true));
    if (is_callable($callback) === true)
    {
      logentry("handleform.150: calling form callback with form values");
      $res = call_user_func($callback, $values);
    }
    else
    {
      logentry("handleform.140: callback is not callable!");
      $res = null;
    }
    if (PEAR::isError($res))
    {
      logentry("handleform.130: " . $res->toString());
    }
    return $res;
  }

  return false;
}

/**
 * @since 20150903
 */
function getmembercredits($id)
{
  $sql = "select credits from engine.member where id=?";
  $dat = array($id);
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("getmembercredits.100: " . $dbh->toString());
    return $dbh;
  }
  $res = $dbh->getOne($sql, null, $dat, array("integer"));
  if (PEAR::isError($res))
  {
    logentry("getmembercredits.100: " . $res->toString());
    return $res;
  }
  return $res;
}

/**
 * @since 20150903
 */
function setmembercredits($id, $credits)
{
  $member = [];
  $member["credits"] = intval($credits);
  $res = updatemember($id, $member);
  if (PEAR::isError($res))
  {
    logentry("setmembercredits.100: " . $res->toString());
    return $res;
  }
  return;
}

/**
 * @since 20150903
 */
function getcurrentmembercredits()
{
  $id = getcurrentmemberid();
  return getmembercredits($id);
}

/**
 * @since 20150903
 */
function setcurrentmembercredits($credits)
{
  $id = getcurrentmemberid();
  return setmembercredits($id, $credits);
}

/**
 * @since 20171125
*/
function _displaypage($data=[])
{
  $nav = isset($data["nav"]) ? $data["nav"] : [];
  $data["nav"] = buildnav($nav);
  $pagetemplate = isset($data["pagetemplate"]) ? $data["pagetemplate"] : "page.tmpl";
//  $data["pagefooter"]["mantra"] = getrandommantra();

  $tmpl = getsmarty();
  $tmpl->assign("data", $data);
  $tmpl->display($pagetemplate);
//  logentry("bbsengine5.displaypage.100: data.nav=".var_export($nav, true));
  return;
}

/**
 * function which accepts a renderer instance converted to an array, a page
 * title, and an optional template name.  it composes an html_page2 instance
 * and calls displaypage() which is part of bbsengine3
 *
 * @param html_quickform2 $form
 * @param string $title
 * @param string $template
 * @since 20150629
 */
function displayform($renderer, $title, $data=[])
{
//  logentry("bbsengine5.displayform.100: enter. title=".var_export($title, true));
//  logentry("bbsengine5.displayform.110: options=".var_export($data, true));
  
  $pagetemplate = isset($data["pagetemplate"]) ? $data["pagetemplate"] : "form.tmpl";
//  logentry("bbsengine5.displayform.125: pagetemplate=".var_export($pagetemplate, true));
  $data["pagetemplate"] = $pagetemplate;
  $data["title"] = $title;
  $data["form"] = $renderer->toArray();
  
  displaypage($data);
}

/**
 *
 * given one or more URIs (the function has a variable number of arguments),
 * compose a proper labelpath, calling normalizelabelpath() at the end.
 *
 * @since 20120312
 * re-written 20160115
 */
function buildlabelpath()
{
  $argv = func_get_args();
  $argc = func_num_args();
  
  $teospath = parse_url(TEOSURL, PHP_URL_PATH);
  if ($teospath === null)
  {
      return PEAR::raiseError("unable to parse url (code: buildlabelpath.100)");
  }
  $teospath = ltrim($teospath, "/");
  logentry("buildlabelpath.120: teospath=".var_export($teospath, true));

  $foo = [];
  
  foreach ($argv as $arg)
  {
   $explode = explode("/", $arg);

   $uripath = parse_url($arg, PHP_URL_PATH);

   $count = 1;
   $res = str_replace($teospath, "", $uripath, $count);

     $fragments = explode("/", $res);
     foreach ($fragments as $fragment)
     {
      $foo[] = buildlabel($fragment);
     }
   
  }
  $foo = array_filter($foo);
  
  $path = implode($foo, ".");
   
  $path = normalizelabelpath($path);
  return $path;
}


/**
 * @since 20140903
 * @param string $labelpath
 * @return string 
*/
function normalizelabelpath()
{
 $argc = func_num_args();
 $argv = func_get_args();

 $foo = [];
 
 foreach ($argv as $arg)
 {
  $labels = explode(".", $arg);
  foreach ($labels as $label)
  {
   $foo[] = buildlabel($label);
  }
 }
 $foo = array_filter($foo);
// logentry("normalizelabelpath.102: foo=".var_export($foo, true));
 if (count($foo) > 0 && $foo[0] !== "top")
 {
  array_unshift($foo, "top");
 }
 $res = implode(".", $foo);
 if ($res === "")
 {
  $res = "top";
 }
// logentry("normalizepath.100: res=".var_export($res, true));
 return $res;
}

/**
 * @since 20200217
 */
function sigpathexists($value)
{
  $dbh = dbconnect(SYSTEMDSN);
  $sql = "select 1 from engine.sig where path=?";
  $dat = [$value];
  $res = $dbh->getRow($sql, ["integer"], $dat, ["text"]);
  if ($res == null)
  {
    return false;
  }
  return true;
}

/**
 * @since 20200217
 */
function validatesigpath($value)
{
  $action = getcurrentaction();
  switch ($action)
  {
    case "add":
    {
      if ($value === "top")
      {
        $res = true;
        break;
      }
      $res = true;
      break;
    }
    default:
    {
      $res = false;
      break;      
    }
  }
  return $res;
}

function buildsigrecord($values)
{
  $sig = [];
  $sig["title"] = $values["title"];
  $sig["intro"] = $values["intro"];
  $sig["path"] = $values["path"];
  
  return $sig;
}

/**
 * build a fieldset for handling the 'sig' table
 *
 * @since 20140730
 * @updated 20200217
 */
function buildsigfieldset($form)
{
  $form->addHidden("uri");
//  $form->addHidden("id");
  $fieldset = $form->addElement("fieldset")->setLabel("SIG");
  $field = $fieldset->addText("title", "size=60")->setLabel("title")->addRule("required", "'title' is a required field");

  $field = $fieldset->addText("path", "size=60")->setLabel("path")->addRule("required", "'path' field is required");
  //->and_($field->addRule("callback", "'path' must validate", "validatesigpath"));
  //$field->addRule("callback", "'path' already exists", "sigpathexists");

//  $res = $fieldset->addText("parentlabelpath", "size=60")->setLabel("Parent Path");
//  $res->addRule("callback", "parent sig must exist", "validatesigs");

//  $fieldset->addText("name", "size=60")->setLabel("Name")->addRule("required", "'sig name' is a required field");
  $fieldset->addElement("textarea", "intro", ["cols" => 50, "rows" => 7])->setLabel("Introduction");

  return;
} 

if (function_exists("accesssig") === false)
{
  /**
   * @since 20160202
   * @return boolean
   * @param string op delete, edit, add, view
   * @param dictionary sig dictionary containing a sig record
   * @param integer memberid memberid to check or null to use currentmemberid
   */
  function accesssig($op, $sig=null, $memberid=null)
  {
    if ($memberid === null)
    {
      $memberid = getcurrentmemberid();
    }
//    logentry("accesssig.200: op=".var_export($op, true));
    switch ($op)
    {
      case "delete":
      case "edit":
      case "add":
      {
        $adminflag = flag("SYSOP");
        logentry("accesssig.210: adminflag=".var_export($adminflag, true));
        if ($adminflag === true)
        {
          logentry("accesssig.220: adminflag is true");
          $res = true;
          break;
        }
        else
        {
          logentry("accesssig.230: adminflag is false");
          $res = false;
          break;
        }
      }
      case "view":
      {
        $res = true;
        break;
      }
      case "addsig":
      {
        if (flag("SYSOP") === true)
        {
          $res = true;
          break;
        }
      }
      case "addlisting":
      {
        if (flag("SYSOP") === true)
        {
          $res = true;
          break;
        }
      }
      default:
      {
        logentry("accesssig.100: unknown op ".var_export($op, true));
        $res = PEAR::raiseError("unknown mode (code: accesssig.100)");
        break;
      }
    }
    if (PEAR::isError($res))
    {
      logentry("accesssig.125: " . $res->toString());
      return $res;
    }
    logentry("accesssig.120: op=".var_export($op, true)." res=".var_export($res, true));
    return $res;
  }

}

if (function_exists("buildsigactions") === false)
{
  /**
   * @since 20150203
   */
  function buildsigactions($sig)
  {
    $uri = isset($sig["uri"]) ? $sig["uri"] : null;
    $labelpath = isset($sig["path"]) ? $sig["path"] : null;
    
    $currentmemberid = getcurrentmemberid();

    $actions = [];
    if (accesssig("edit") === true)
    {
      $actions[] = ["href" => TEOSURL . $uri . "edit-sig", "title" => "edit sig", "class" => "fa fa-edit fa-fw"];
    }
/*
    if (accesssig("addlink") === true)
    {
      $actions[] = ["href" => TEOSURL . $uri . "add-link", "title" => "add link", "class" => "fa fa-plus fa-fw"];
    }
    if (accesssig("addpost") === true)
    {
      $actions[] = ["href" => TEOSURL . $uri . "add-post", "title" => "add post", "class" => "fa fa-fw fa-plus"];
    }
*/
    if (accesssig("addsig") === true)
    {
      $actions[] = ["href" => TEOSURL . $uri . "add-sig", "title" => "add sig", "class" => "fa fa-fw fa-plus"];
    }

    return $actions;
  }
}

/**
 * @since 20151118
 */
function buildpagerinfo($sql, $params)
{
//  logentry("buildpagerinfo.100: params=".var_export($params, true));

  $pager = Pager::factory($params);
        
  $pageinfo = [];
  $pageinfo["totalItems"] = $params["totalItems"];
  $pageinfo["range"] = $pager->range;
  $pageinfo["numPages"] = $pager->numPages();
  $pageinfo["perPage"] = 10;
  $pageinfo["currentPageID"] = $pager->getCurrentPageID();
  list($pageinfo["from"], $pageinfo["to"]) = $pager->getOffsetByPageId();

  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("buildpagerinfo.110: " . $dbh->toString());
    return $dbh;
  }

//  logentry("buildpagerinfo.200: sql=".var_export($sql, true)." pageinfo=".var_export($pageinfo, true));
  
  $qry = $dbh->limitQuery($sql, null, $params["perPage"], $pageinfo["from"]-1);
  if (PEAR::isError($qry))
  {
    logentry("buildpagerinfo.112: " . $qry->toString());
    return $qry;
  }

  $filterfunction = isset($params["filterfunction"]) ? $params["filterfunction"] : null;

  $pageinfo["data"] = [];
  while ($row = $qry->fetchRow())
  {
    if (is_callable($filterfunction) === true)
    {
      $foo = call_user_func($filterfunction, $row);
      if (PEAR::isError($foo))
      {
        logentry("buildpagerinfo.114: " . $foo->toString());
        continue;
      }
      if ($foo === false)
      {
        continue;
      }
    }
    $pageinfo["data"][] = $row;
  }
  $qry->free();
  $pageinfo["links"] = $pager->getLinks();
  
  return $pageinfo;
}

/**
 * return a list of dictionaries with keys 'title' and 'uri' for each part of $sigpath (ltree)
 *
 * @since 20151118
 */
function buildbreadcrumbs($path)
{
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("buildbreadcrumbs.10: " . $dbh->toString());
    return PEAR::raiseError($dbh);
  }
  $sql = "select * from engine.sig where path @> ? order by path asc";
  $dat = [$path];
  $res = $dbh->getAll($sql, null, $dat);
  if (PEAR::isError($res))
  {
    logentry("buildbreadcrumbs.12: " . $res->toString());
    return PEAR::raiseError($res);
  }
  
  $crumbs = [];
  foreach ($res as $rec)
  {
    $crumbs[] = $rec;
  }

//  logentry("buildbreadcrumbs.200: crumbs=".var_export($crumbs, true));
  return $crumbs;
}

/**
 * get sigid for a given labelpath
 *
 * @since 20140713
 * moved from zoidweb2 2015nov22
 */
function getsigidfromlabelpath($labelpath)
{
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("getsigidfromlabelpath.100: " . $dbh->toString());
    return $dbh;
  }
  $sql = "select id from engine.sig where path=?";
  $dat = array($labelpath);
  $res = $dbh->getOne($sql, array("integer"), $dat, array("text"));
  if (PEAR::isError($res))
  {
    logentry("getsigidfromlabelpath.110: " . $res->toString());
    return $res;
  }
  return $res;
}

/**
 * @since 20151204
 */
function getcurrentpath($uri=null)
{
  if ($uri === null)
  {
    $uri = getcurrenturi();
  }
  $path = parse_url($uri, PHP_URL_PATH);
  if (substr($path, -1) !== "/")
  {
    $path .= "/";
  }
  
  return $path;
}

/**
 * @since 20160430
 */
function cartidexists($cartid)
{
  $sql = "select 1 from cart where id=?";
  $dat = [$cartid];
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("cartidexists.100: " . $dbh->toString());
    return $dbh;
  }
  $res = $dbh->getOne($sql, ["integer"], $dat, ["integer"]);
  if (PEAR::isError($res))
  {
    logentry("cartidexists.100: " . $res->toString());
    return $res;
  }
  if ($res == true)
  {
    return true;
  }
  return false;
}

/**
 * @since 20151214
 */
function getcurrentcart()
{
  $cartid = getcurrentcartid();
  if (PEAR::isError($cartid))
  {
    logentry("getcurrentcart.120: " . $cartid->toString());
    return $cartid;
  }
//  logentry("getcurrentcart.200: cartid=".var_export($cartid, true));
  $cart = getcart($cartid);
  if (PEAR::isError($cart))
  {
    logentry("getcurrentcart.140: " . $cart->toString());
    return $cart;
  }
  if ($cart === null)
  {
//    logentry("getcurrentcart.145: getcart(".var_export($cartid, true).") returned null");
    return null;
  }
//  logentry("getcurrentcart.150: cart=".var_export($cart, true));
/*
  $cartitems = getcartitems($cartid);
  if (PEAR::isError($cartitems))
  {
    logentry("getcurrentcart.160: " . $cartitems->toString());
    return $cartitems;
  }
  $cart["items"] = $cartitems;
*/
  return $cart;
}

function getcurrentcartid()
{
  $id = isset($_SESSION["cartid"]) ? intval($_SESSION["cartid"]) : null;
  if (cartidexists($id) === true)
  {
    return $id;
  }
  return null;
}

function setcurrentcartid($cartid)
{
//  logentry("setcurrentcartid.100: cartid=".var_export($cartid, true));
  $_SESSION["cartid"] = $cartid;
  return;
}

/**
 * @since 20151214
 */
/*
function addcartitem($item)
{
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
      logentry("addcartitem.102: " . $dbh->toString());
      return PEAR::raiseError("database connect error (code: addcartitem.102)");
  }
  if ($dbh === null)
  {
      logentry("addcartitem.103: dbh is null");
      return PEAR::raiseError("database connect error (code: addcartitem.103)");
  }
  logentry("addcartitem.152: about to insert cart record");
  $res = $dbh->autoExecute("__cart", $item, MDB2_AUTOQUERY_INSERT);
  if (PEAR::isError($res))
  {
      logentry("addcartitem.100: " . $res->toString());
      return PEAR::isError("database insert error (code: addcartitem.100)");
  }

  $cart = getcurrentcart();
  $cart[] = $item;
  setcurrentcart($cart);
  return;
}
*/

/** 
 * @since 20160503
 */
function clearcart($cartid)
{
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("clearcart.100: " . $dbh->toString());
    return $dbh;
  }
  $res = $dbh->autoExecute("__cartitem", null, MDB2_AUTOQUERY_DELETE, "cartid=".$dbh->quote($cartid, "integer"));
  if (PEAR::isError($res))
  {
    logentry("clearcart.110: " . $res->toString());
    return $res;
  }
  return;
}

/**
 * @since 20151214
 */
function clearcurrentcart()
{
  $cartid = getcurrentcartid();
  $res = clearcart($cartid);
  if (PEAR::isError($res))
  {
    logentry("clearcurrentcart.100: " . $res->toString());
    return $res;
  }
  $currentcart = getcurrentcart();
  if (PEAR::isError($currentcart))
  {
    logentry("clearcurrentcart.120: " . $currentcart->toString());
    return $currentcart;
  }
  $currentcart["items"] = [];
  setcurrentcart($currentcart);
  
  return;
}

/**
 * @since 20151214
 */
function normalizecart()
{
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("normalizecart.100: " . $dbh->toString());
    return $dbh;
  }
  $currentcart = getcurrentcart();
  if ($currentcart === null)
  {
    logentry("normalizecart.110: current cart is null");
    return null;
  }
  $cart = [];
  foreach ($currentcart as $cartitem)
  {
    $title = $cartitem["title"];
    $quantity = $cartitem["quantity"];
    $price = $cartitem["price"];
    logentry("normalizecart.118: title=".var_export($title, true)." price=".var_export($price, true));
    if ((in_array($title, $cartitem) && $cartitem["title"] === $title) &&
      (in_array($price, $cartitem) && $cartitem["price"] === $price))
    {
      logentry("normalizecart.120: title and price match");
      continue;
    }
    logentry("normalizecart.122: no match.");
    $cart[] = $cartitem;
  }
  return $cart;
}

/**
 * @since 20151214
 */
function setcurrentcart($cart)
{
  $_SESSION["cart"] = $cart;
  return;
}

/**
 * @since 20151220
 */
function getcart($cartid)
{
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("getcart.100: " . $dbh->toString());
    return $dbh;
  }
  $sql = "select * from cart where id=?";
  $dat = [$cartid];
  $res = $dbh->getRow($sql, null, $dat, ["integer"]);
  if (PEAR::isError($res))
  {
    logentry("getcart.110: ". $res->toString());
    return $res;
  }
  $items = getcartitems($cartid);
  if (PEAR::isError($items))
  {
    logentry("cart.120: " . $items->toString());
    return $items;
  }
  $res["items"] = $items;
  
  $actions = buildcartactions(["cartid" => $cartid, "cart" => $res]);
  $res["actions"] = $actions;
  return $res;
}

/**
 * @since 20151222
 */
function buildcartrecord()
{
  $currentmemberid = getcurrentmemberid();
  
  $cart = [];
  $cart["memberid"] = $currentmemberid;
  $cart["datecreated"] = "now()";
  $cart["datemodified"] = "now()";
  $cart["createdbyid"] = $currentmemberid;
  $cart["modifiedbyid"] = $currentmemberid;
  $cart["sessionid"] = session_id();
  
  return $cart;
}

/**
 * @since 20160411
 */
if (function_exists("getcartitems") === false)
{
  function getcartitems($cartid)
  {
    logentry("getcartitems.140: call getcartitems(".var_export($cartid, true).")");
    $dbh = dbconnect(SYSTEMDSN);
    if (PEAR::isError($dbh))
    {
      logentry("getcartitems.100: " . $dbh->toString());
      return $dbh;
    }
    $sql = "select * from cartitem where cartid=?";
    $dat = [$cartid];
    $res = $dbh->getAll($sql, null, $dat, ["integer"]);
    logentry("getcartitems.120: res=".var_export($res, true)." count=".count($res), true);
    if (PEAR::isError($res))
    {
      logentry("getcartitems.110: " . $res->toString());
    }
    return $res;
  }
}

/**
 * @since 20160429
 */
function accesscartitem($op, $cartitem=null)
{
  switch ($op)
  {
    case "delete":
    {
	$res = true;
	break;
    }
    case "edit":
    {
      if (flag("SYSOP") === true)
      {
        $res = true;
        break;
      }
      $res = false;
    }
  }
  return $res;
}
/**
 * @since 20160429
 */
function buildcartitemactions($data=[])
{
  $cartitemid = isset($data["cartitemid"]) ? intval($data["cartitemid"]) : null;
  $cartitem = isset($data["cartitem"]) ? $data["cartitem"] : null;

  $actions = [];
/*
  if (accesscartitem("edit", $cartitem) === true)
  {
    $actions[] = ["href" => "/edit-cartitem-{$cartitemid}", "title" => "edit item", "class" => "fa fa-edit fa-fw"];
  }
*/
/*
  if (accesscartitem("delete", $cartitem) === true)
  {
    $actions[] = ["href" => "/delete-cartitem-{$cartitemid}", "title" => "delete item", "class" => "fa fa-remove fa-fw"];
  }
*/
  return $actions;
}

/** 
 * @since 20160502
 */
function accesscart($op, $data=null)
{
  $currentmemberid = getcurrentmemberid();
  $currentsessionid = session_id();
  
  $cart = $data["cart"];
  
  switch ($op)
  {
    case "clear":
    {
      if (flag("SYSOP") === true)
      {
        $res = true;
        break;
      }
      if (iscartowner($cart) === true)
      {
        $res = true;
        break;
      }
      $res = false;
      break;
    }
    case "view":
    {
      if (flag("SYSOP") === true)
      {
        $res = true;
        break;
      }
      if (iscartowner($cart) === true)
      {
        $res = true;
        break;
      }
      $res = false;
      break;
    }
    default:
    {
      $res = null;
      break;
    }
  }
  return $res;
}

if (function_exists("buildcartactions") === false)
{
  /**
   * @since 20160429
   */
  function buildcartactions($data)
  {
    $cartid = $data["cartid"];
    $cart = $data["cart"];
    $actions = [];
    if (accesscart("clear", ["cart" => $cart]) === true)
    {
      $actions[] = ["href" => "/cart-clear-{$cartid}", "title" => "clear cart", "class" => "fa fa-remove fa-fw"];
    }
    return $actions;
  }
}

/**
 * moved from zoidweb2 to bbsengine
 * 
 * this function will update a sig mapping given the table name, the name of the id field, and the value of the idfield.
 *
 * @since 20151114
 * @param sigs string|array if string, call explodesiglabelpaths()
 * @param tablename name of mapping table
 * @param idfield name of id field marked unique in the db (example: "linkid")
 * @param id the actual id of the item (example: 42)
 * @return null if all is well else PEAR::Error
 */
function updatesigmap($sigs, $tablename, $idfield, $id, $ltreefield="siglabelpath")
{
  logentry("updatesigmap.100: sigs=".var_export($sigs, true)." tablename=".var_export($tablename, true)." idfield=".var_export($idfield, true)." id=".var_export($id, true));
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("updatesigmap.110: ".$dbh->toString());
    return $dbh;
  }

//  $res = $dbh->beginTransaction();
  $sigmap = [];
  if (is_string($sigs) === true)
  {
    $sigmap = explodesiglabelpaths($sigs);
  }
  else if (is_array($sigs))
  {
    $sigmap = $sigs;
  }

  logentry("updatesigmap.160: sigmap=".var_export($sigmap, true));
  
  $res = $dbh->autoExecute($tablename, null, MDB2_AUTOQUERY_DELETE, "{$idfield}=".$dbh->quote($id, "integer"));
  if (PEAR::isError($res))
  {
    logentry("updatesigmap.120: ". $res->toString());
    $dbh->rollback();
    return $res;
  }

  foreach ($sigmap as $sig)
  {
    $map = [];
    $map[$idfield] = $id;
    $map[$ltreefield] = normalizelabelpath($sig);
    logentry("updatesigmap.130: map=".var_export($map, true)); 
    $res = $dbh->autoExecute($tablename, $map, MDB2_AUTOQUERY_INSERT);
    if (PEAR::isError($res))
    {
      logentry("updatesigmap.140: " . $res->toString());
//      $res = $dbh->rollback();
      continue;
    }
  }
//  $dbh->commit();
  logentry("updatesigmap.150: sigs updated");
  return;
}

/**
 * @since 20160206
 */
function getsigmap($maptablename, $idfield, $id, $ltreefield="siglabelpath")
{
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("getsigmap.100: " . $dbh->toString());
    return $dbh;
  }
  $sql = "select {$ltreefield} from {$maptablename} where {$idfield}=?";
  $dat = [$id];
  $res = $dbh->getAll($sql, ["text"], $dat, ["integer"]);
  if (PEAR::isError($res))
  {
    logentry("getsigmap.110: " . $res->toString());
    return $res;
  }
  $sigmap = [];
  foreach($res as $rec)
  {
    $sigmap[] = $rec[$ltreefield];
  }
  return $sigmap;
}

function implodesigmap($sigmap)
{
//  logentry("implodesigmap.100: sigmap=".var_export($sigmap, true));

  $sigmap = array_filter($sigmap);
  $sigmap = array_map("trim", $sigmap);
  $sigmap = array_unique($sigmap, SORT_STRING);

  return implode(", ", $sigmap);
}

/**
  * accepts a string of comma separated label paths and returns an array.
  * @return array of siglabelpaths
  * @since 20150703
  * @deprecated
  */
function explodesigmap($sigmap)
{
  logentry("explodesigmap.100: deprecated. forwarded to explodesiglabelpaths()");
  return explodesiglabelpaths($sigmap);
  
    $sigmap = explode(",", $sigmap);
    $sigmap = array_filter($sigmap);
    $sigmap = array_map("trim", $sigmap);
    $sigmap = array_unique($sigmap, SORT_STRING);
    return $sigmap;
}

/**
 * @since 20160207
 */
function explodesiglabelpaths($siglabelpaths)
{
//  logentry("explodesiglabelpath.100: renamed to explodesigmap");
//  return explodesigmap($siglabelpath);
  
    $sigmap = explode(",", $siglabelpaths);
    $sigmap = array_filter($sigmap);
    $sigmap = array_map("trim", $sigmap);
    $sigmap = array_unique($sigmap, SORT_STRING);
    return $sigmap;
}

/**
 * @since 20160319
 */
function explodeuri($uri)
{
  $foo = explode("/", $uri);
  $foo = array_filter($foo);
  $foo = array_map("trim", $foo);
  return $foo;
}

/**
 * @since 20160427
 */
function getcurrentsig()
{
  $currentsig = isset($_SESSION["currentsig"]) ? $_SESSION["currentsig"] : null;
  return $currentsig;
}

/**
 * @since 20160427
 */
function setcurrentsig($sig=null)
{
  $_SESSION["currentsig"] = $sig;
  return;
}

/**
 * @since 20160502
 */
function cartitemexists($trailerid)
{
  $currentcart = getcurrentcart();
  
  logentry("cartitemexists.100: trailerid=".var_export($trailerid, true));
  $items = $cart["items"];
  foreach ($items as $item)
  {
    if ($item["items"]["trailerid"] === $trailerid)
    {
      logentry("cartitemexists.110: found trailerid");
      return true;
    }
  }
  logentry("cartitemexists.120: trailerid not found");
  return false;
}

function iscartowner($cart)
{
  $currentmemberid = getcurrentmemberid();
  
  if ($cart["memberid"] === $currentmemberid && flag("AUTH") === true)
  {
    return true;
  }
  if ($cart["sessionid"] === session_id())
  {
    return true;
  }
  return false;
}

function buildbutton($form, $name, $data)
{
  $value = isset($data["value"]) ? $data["value"] : null;
  $form->addElement("button", $name, $value);
  return;
}

/** 
 * @since 20160910
 */
function buildmantrafieldset($form)
{
  $fieldset = $form->addElement("fieldset")->setLabel("Mantra");
  $fieldset->addElement("textarea", "description", "rows=15 cols=70")->setLabel("Description")->addRule("required", "'Description' is a required field");
  $fieldset->addText("author", "size=60")->setLabel("Author")->addRule("required", "'Author' is a required field");
  $fieldset->addText("reference", "size=60")->setLabel("Reference")->addRule("required", "'Reference' is a required field");
  return;
}

/**
 * build a mantra record (dict) from html_quickform2 values
 *
 * @since 20160910
 */
function buildmantrarecord($values)
{
  $mantra = [];
  $mantra["description"] = $values["description"];
  $mantra["author"] = $values["author"];
  $mantra["reference"] = $values["reference"];
  return $mantra;
}

/**
 * given an operation, return a boolean or null if the operation is not handled
 * @param string op operation.. for example "summary" or "edit" or "delete"
 * @param dictionary data optional data needed to resolve access check
 * @param integer memberid member id to check or null to use result of getcurrentmemberid()
 * @return boolean|null true, false, or null if the operation is not handled
 * @since 20160910
 */
function accessmantra($op, $data=null, $memberid=null)
{
  switch ($op)
  {
    case "edit":
    {
      if (flag("SYSOP", $memberid) === true)
      {
        $res = true;
        break;
      }
      $res = false;
      break;
    }
    case "detail":
    {
      $res = true;
      break;
    }
    case "add":
    {
      if (flag("SYSOP", $memberid) === true)
      {
        $res = true;
        break;
      }
      $res = false;
      break;
    }
    case "summary":
    {
      $res = true;
      break;
    }
    default:
    {
      $res = null;
      break;
    }
  }
//  logentry("accessmantra.100: op=".var_export($op, true)." res=".var_export($res, true));
  return $res;
}

/**
 * @since 20160910
 */
function buildmantraactions($data)
{
  $id = intval($data["mantraid"]);

  $currentaction = getcurrentaction();
  $currentpage = getcurrentpage();
  $currentsite = getcurrentsite();
//  $currentsection = getcurrentsection();

//  logentry("buildmantraactions.100: currentaction=".var_export($currentaction, true));
  
  $actions = [];
  if (accessmantra("detail") === true)
  {
    $actions[] = array("contenturl" => ENGINEURL."mantra-detail-{$id}?bare", "href" => ENGINEURL."mantra-detail-{$id}", "title" => "detail", "desc" => "show detail for mantra #{$id}", "class" => "fa fa-fw fa-angle-double-down");
  }
  if (accessmantra("edit") === true)
  {
    $actions[] = array("href" => ENGINEURL."mantra-edit-{$id}", "title" => "edit", "desc" => "edit mantra #{$id}", "class" => "fa fa-fw fa-edit");
  }
/*
  if ($currentaction !== "summary" && accessmantra("summary") === true)
  {
    $actions[] = array("href" => ENGINEURL."mantra-summary", "title" => "summary", "desc" => "paged listing of mantras");
  }
*/
  return $actions;
}

/** 
 * @since 20140512
 */
function getmantra($mantraid)
{
  $mantraid = intval($mantraid);
  
  $sql = "select * from engine.mantra where id=?";
  $dat = array($mantraid);
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("getmantra.100: " . $dbh->toString());
    return $dbh;
  }

  $res = $dbh->getRow($sql, null, $dat, array("integer"));
  if (PEAR::isError($res))
  {
    logentry("getmantra.110: " . $res->toString());
    return $res;
  }
  
  $mantra = [];
  $mantra["description"] = $res["description"];
  $mantra["author"] = $res["author"];
  $mantra["reference"] = $res["reference"];
  $mantra["dateposted"] = $res["dateposted"];
  $mantra["datepostedepoch"] = $res["datepostedepoch"];
  $mantra["postedbyid"] = $res["postedbyid"];
  $mantra["postedbyname"] = $res["postedbyname"];
  $mantra["lastmodified"] = $res["lastmodified"];
  $mantra["lastmodifiedepoch"] = $res["lastmodifiedepoch"];
  $mantra["lastmodifiedbyid"] = $res["lastmodifiedbyid"];
  $mantra["actions"] = buildmantraactions(array("mantraid" => $mantraid));
  
  return $mantra;
}

/**
 * @since 20161023
 */
function validsitevar($name)
{
    $names = [ "smoothstate", "sitedebug" ];
    if (in_array($name, $names) === true)
    {
        return true;
    }
    logentry("validsitevar.100: unknown var ".var_export($name, true));
    return false;
}

/**
 * @since 20161022
 */
function setsitevar($name, $value)
{
    logentry("setsitevar.100: name=".var_export($name, true)." value=".var_export($value, true));
    if (validsitevar($name) === true)
    {
        $_SESSION["sitevars"][$name] = $value;
    }
    else
    {
        logentry("setsitevar.110: invalid name");
        return PEAR::raiseError("invalid sitevar name (code: setsitevar.110)");
    }
    return;
}

/**
 * @since 20161023
 */
function getsitevars()
{
    $sitevarnames = ["sitedebug", "smoothstate"];
    $foo = isset($_SESSION["sitevars"]) ? $_SESSION["sitevars"] : [];
    $vars = [];
    foreach ($sitevarnames as $name)
    {
        $vars[$name] = getsitevar($name);
    }
    return $vars;
}
/**
 * @since 20161022
 */
function getsitevar($name)
{
//    logentry("getsitevar.100: name=".var_export($name, true));
    if (validsitevar($name) === true)
    {
        if (isset($_SESSION["sitevars"][$name]) === true)
        {
            $value = $_SESSION["sitevars"][$name];
//            logentry("getsitevar.105: value=".var_export($value, true));
        }
        else
        {
            $value = getsitevardefault($name);
            if (PEAR::isError($value))
            {
                logentry("getsitevar.110: ".$value->toString());
                return PEAR::raiseError("error getting sitevar with name ".var_export($name, true)." (code: getsitevar.110)");
            }
//            logentry("getsitevar.115: using default value. name=".var_export($name, true)." value=".var_export($value, true));
        }
        return $value;
    }
    return PEAR::raiseError("invalid sitevar (code: getsitevar.100)");
}

/**
 * @since 20161023
 */
function getsitevardefault($name)
{
    switch ($name)
    {
        case "sitedebug":
        {
            $res = false;
            break;
        }
        case "smoothstate":
        {
            $res = true;
            break;
        }
        default:
        {
            logentry("getsitevardefault.100: unknown name ".var_export($name, true));
            $res = PEAR::raiseError("invalid variable name (code: getsitevardefault.100)");
            break;
        }
    }
    return $res;
}

/**
 * @since 20170621
 * @param integer memberid
 * @return integer|pear_error either integer count of undisplayed notifies or a pear_error
 * @package bbsengine5
 * @deprecated 20180830 moved to engine.member
 */
/*
function getunreadnotifycount($memberid)
{
  $memberid = intval($memberid);
  
  logentry("getunreadnotifycount.100: called");
  
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("getunreadnotifycount.100: " . $dbh->toString());
    return $dbh;
  }
  $sql = "select count(id) from engine.notify where displayed='f' and memberid=?";
  $dat = [$memberid];
  $res = $dbh->getOne($sql, ["integer"], $dat, ["integer"]);
  if (PEAR::isError($res))
  {
    logentry("getunreadnotifycount.100: " . $res->toString());
  }
  logentry("getunreadnotifycount.110: res=".var_export($res, true));
  return $res;
}
*/

/**
 * return the sidebar template as a string
 *
 * @since 20110413
 * @since 20171121
 * @param dictionary options keys 'menu' and 'template' accepted
 * @access private
 * @return string
 */
/*
function _fetchsidebar($options=null)
{
  $sidebar = isset($options["sidebar"]) ? $options["sidebar"] : null;
  $template = isset($options["template"]) ? $options["template"] : "nav.tmpl";

  $tmpl = getsmarty();
  $tmpl->assign("sidebar", $sidebar);
  return $tmpl->fetch($template);
}
*/
/*
if (!function_exists("fetchsidebar")) {
  function fetchsidebar($menu=null)
  {
    return _fetchsidebar(["menu" => $menu, "template" => "nav.tmpl"]);
  }
}
*/

function buildsiglist($siglabelpaths)
{
  $foo = preg_split("/[, ]/",$siglabelpaths);
  $foo = array_filter($foo);
  $foo = array_values($foo);
  logentry("buildsiglist.100: foo=".var_export($foo, True));
  return $foo;
}

function validatesigs($sigs)
{
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("bbsengine5.validatesigs.100: " . $dbh->toString());
    return $dbh;
  }
  $sql = "select 1 from engine.sig where path=?";
  $siglist = buildsiglist($sigs);
  foreach ($siglist as $sig)
  {
    logentry("bbsengine5.validatesigs.150: sig=".var_export($sig, true));
    if ($sig !== "top" && strpos($sig, "top.") !== 0)
    {
      logentry("bbsengine5.validatesigs.120: adjusting '{$sig}' by adding 'top.'");
      $sig = "top.{$sig}";
    }
    logentry("bbsengine5.validatesigs.130: sig=".var_export($sig, true));
    
    $dat = [$sig];
    $res = $dbh->getOne($sql, null, $dat, null);
    if (PEAR::isError($res))
    {
      logentry("bbsengine5.validatesigs.110: " . $res->toString());
      return $res;
    }
    if ($res === null)
    {
      logentry("bbsengine5.validatesigs.140: res is null");
      return false;
    }
  }
  return true;
}

/**
 * @since 20140512
 */
function getrandommantra($dsn)
{
  $sql = "select id from engine.mantra order by random() limit 1";

  $dbh = dbconnect($dsn);
  if (PEAR::isError($dbh))
  {
    logentry("getrandommantra.100: " . $dbh->toString());
    return $dbh;
  }

  $mantraid = $dbh->getOne($sql);
  if (PEAR::isError($mantraid))
  {
    logentry("getrandommantra.110: " . $mantraid->toString());
    return null;
  }

  $mantra = getmantra($mantraid);
  $mantra["id"] = $mantraid;
  return $mantra;
}

/**
 * @since 20180801
 */
function buildflagfieldset($form, $options=[])
{
  $fieldset = $form->addElement("fieldset", "flag");
  $fieldset->addElement("text", "name")->setLabel("name")->addRule("required", "'name' is a required field");
  $fieldset->addElement("text", "description")->setLabel("description")->addRule("required", "'description' is a required field");
  $fieldset->addElement("checkbox", "defaultvalue")->setLabel("default true");

  return;
}

function getnode($id)
{
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("bbsengine5.getnode.100: " . $dbh->toString());
    return $dbh;
  }
  $sql = "select * from engine.node where id=?";
  $dat = [$id];
  $res = $dbh->getRow($sql, null, $dat, ["integer"]);
  if (PEAR::isError($res))
  {
    logentry("getnode.100: " . $res->toString());
    return $res;
  }
  return $res;
}

/**
 * insertnode - insert a node dict into engine.__node
 * node.attributes is encoded to json before insert.
 *
 * @since 20200417
 * @param $node dict
 */
function insertnode($node)
{
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("bbsengine5.insertnode.100: " . $dbh->toString());
    return $dbh;
  }
  
  $sigs = isset($node["sigs"]) ? $node["sigs"] : [];
  unset($node["sigs"]);

  $dbh->beginTransaction();
  $node["createdbyid"] = getcurrentmemberid();
  $node["datecreated"] = "now()";
  $node["attributes"] = encodejson($node["attributes"]);
  $res = $dbh->autoExecute("engine.__node", $node, MDB2_AUTOQUERY_INSERT);
  if (PEAR::isError($res))
  {
    logentry("bbsengine5.insertnode.110: " . $res->toString());
    $dbh->rollback();
    return $res;
  }

  $nodeid = $dbh->lastInsertID();
  if (PEAR::isError($nodeid))
  {
    logentry("bbsengine5.insertnode.120: " . $nodeid->toString());
    return $nodeid;
  }
  
  $res = updatesigmap($sigs, "engine.map_node_sig", "nodeid", $nodeid, "sigpath");
  if (PEAR::isError($res))
  {
    logentry("bbsengine5.insertnode.130: " . $res->toString());
    return $res;
  }

  $dbh->commit();
  return $nodeid;
}

/**
 * update an existing node given an id
 * @since 20200222
 */
function updatenode($id, $node)
{
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("bbsengine5.updatenode.110: " . $res->toString());
    return $res;
  }
  $attributes = isset($node["attributes"]) ? $node["attributes"] : [];
  unset($node["attributes"]);
  
  $res = $dbh->beginTransaction();
//  logentry("updatenode.120: id=".var_export($id, true)." node=".var_export($node, true));
//  $node["attributes"] = encodejson($node["attributes"]);
  $res = $dbh->autoExecute("engine.__node", $node, MDB2_AUTOQUERY_UPDATE, "id=".$dbh->quote($id, "integer"));
  if (PEAR::isError($res))
  {
    logentry("bbsengine5.updatenode.100: " . $res->toString());
    $dbh->rollback();
    return $res;
  }
  $attributes = encodejson($attributes);
  $sql = "update engine.__node set attributes = attributes||".$dbh->quote($attributes, "text")." where id=".$dbh->quote($id, "integer");
  $res = $dbh->exec($sql);
  if (PEAR::isError($res))
  {
    logentry("bbsengine5.updatenode.140: " . $res->toString());
    return $res;
  }
  $dbh->commit();
  return $res;
}

/**
 * Takes one or more path/filenames and joins them using DIRECTORY_SEPARATOR. then it strips a leading or trailing DIRECTORY_SEPARATOR, then it replaces "//" with "/"
 * Example: joinpath('/var','www/html/','/try.php'); // returns 'var/www/html/try.php'
 * original idea from http://www.bin-co.com/php//scripts/filesystem/join_path/
 * re-written to not use for loops (array_filter, join instead)
 * 
 * @since 20190806
 * @todo consider using preg_replace
 */
function joinpath()
{
    $arguments = func_get_args();
//    logentry("bbsengine5.joinpath.100: arguments=".var_export($arguments, true));
    $arguments = array_filter($arguments);

    $path = join(DIRECTORY_SEPARATOR, $arguments);
    if ($path === "")
    {
      return "";
    }

//    logentry("joinpath.140: before // removal: path=".var_export($path, true));
    $path = preg_replace("@[/]{2,}@", "/", $path);
//    $path = str_replace(DIRECTORY_SEPARATOR.DIRECTORY_SEPARATOR, DIRECTORY_SEPARATOR, $path);
//    logentry("joinpath.160: after // removal: path=".var_export($path, true));

//    logentry("bbsengine5.joinpath.120: path=".var_export($path, true));
    if ($path[0] === DIRECTORY_SEPARATOR)
    {
      $path = substr($path, 1);
    }

    if (substr($path, -1) === DIRECTORY_SEPARATOR)
    {
      $path = substr($path, 0, -1);
    }
//    logentry("joinpath.110: path=".var_export($path, true));
    return $path;
}

/**
 * function which converts a postgres array (comma separated text) to a php array
 * https://prosuncsedu.wordpress.com/2009/10/13/postgres-array-to-php-array-or-vice-versa/
 *
 * @since 20190822 in bbsengine4
 * @since 20200223 in bbsengine5
 *
 * @param $text postgres array in text format
 * @return array
 */
function postgres_to_php_array($text)
{
  $text = trim($text, "{}");
  $res = explode(",", $text);
  return $res;
}

/**
 * build a list of breadcrumbs given a specific nodeid
 * @since 20200302 in bbsengine5
 * @since 20150924 in bbsengine
 */
function buildbreadcrumbslist($nodeid)
{
  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("buildbreadcrumblist.10: " . $dbh->toString());
    return $dbh;
  }
  $sql = "select unnest(sigs) as siglabelpath from engine.node where id=?";
  $dat = [$nodeid];
  $res = $dbh->getAll($sql, null, $dat, ["integer"]);
  if (PEAR::isError($res))
  {
    logentry("buildbreadcrumblist.42: " . $res->toString());
    return $res;
  }
//  logentry("buildbreadcrumblist.50: res=".var_export($res, True));
  $breadcrumbs = [];
  foreach ($res as $rec)
  {
    $siglabelpath = $rec["siglabelpath"];
    $breadcrumbs[] = buildbreadcrumbs($siglabelpath);
  }
//  logentry("buildbreadcrumblist.100: breadcrumbs=".var_export($breadcrumbs, True));
  return $breadcrumbs;
}

function hashcode($buf)
{
  $hash = 0;
  if (strlen($buf) === 0)
  {
    return $hash;
  }
  foreach ($buf as $b)
  {
    $hash = (($hash << 3) - $hash) + ord($b);
#    $hash = $hash & $hash;
  }
  return $hash;
  
}
?>
