<?php

require_once("config.prg");
require_once(SITENAME.".prg");
require_once("bbsengine5.prg");

/**
 * this module accepts a username and password and validates it against the postgresql database.
 *
 * @copyright (c) 2007-2020 {@link http://zoidtechnologies.com/ Zoid Technologies} all rights reserved
 * @package bbsengine5
 */
class login
{
  /**
   * if this function gets called, it is because the 'checklogin' callback (and the other login form rules) passed. there is no need to check the password again (ala bbsengine4).
   *
   * @return bool
   */
  function validate($values)
  {
    logentry("login.80: values=".var_export($values, true));

    $username = isset($values["username"]) ? $values["username"] : null;
    $password = isset($values["password"]) ? $values["password"] : null;

    $member = getmember($username);
    if (PEAR::isError($member))
    {
      displayerrorpage("Error getting memberid from username (code: login.110)");
      return false;
    }
    if ($member === null)
    {
      displayerrorpage("Error getting member (code: login.210)");
      logentry("login.210: getmember(".var_export($username, true).") returned null");
      return false;
    }

    logentry("login.100: username=".var_export($username, true)." password=".var_export($password, true));

    logentry("login.220: member=".var_export($member, true));
    
    setlastlogin($member["lastlogin"]);
    setlastloginfrom($member["lastloginfrom"]);
    
    $memberid = getmemberid($username);
    if (PEAR::isError($memberid))
    {
      displayerrorpage("login process error (code: login.130)");
      logentry("login.130: " . $memberid->toString());
    }

    if ($memberid === null)
    {
      displayerrorpage("login process error (code: login.132)");
      logentry("login.132: getmemberid(".var_export($username, true).") returned null, username does not exist.");
    }

    session_regenerate_id(true);

    setcurrentmemberid($memberid);

    setcookie(session_name(),session_id(),time()+SESSIONCOOKIEEXPIRE, SESSIONCOOKIEPATH, SESSIONCOOKIEDOMAIN);
                
    displayredirectpage("OK -- logged in");

    $username = isset($member["username"]) ? $member["username"] : null;
    
    logentry("login.20: success for ".var_export($username, true)." (#{$memberid})");
    return true;
  }
  
  function main()
  {
    startsession();
    
    setcurrentsite(SITENAME);
    setcurrentaction("login");

    $form = getquickform(SITENAME."-login", "post", ["action" => "/login"]);
    buildloginfieldset($form);
    buildcaptchafieldset($form);

    $group = $form->addGroup("buttons");
    $group->setSeparator("&nbsp;");
    
    $group->addElement("submit", "submit", ["value" => "red pill (login)"]);
    $group->addElement("submit", "cancel", ["value" => "blue pill (reset form)"]);

    $const = [];
    $form->addDataSource(new HTML_QuickForm2_DataSource_Array($const));

    $res = handleform($form, [$this, "validate"], "follow the white rabbit...");
    if (PEAR::isError($res))
    {
      logentry("login.300: " . $res->toString());
      return PEAR::raiseError("login form handling error (code: login.300)");
    }
    if ($res === true)
    {
      logentry("login.310: handleform(...) returned true");
      return $res;
    }
    $renderer = getquickformrenderer();
    $form->render($renderer);
    $options = [];
//    $options["stylesheets"] = [STATICSKINURL."css/login.css"];
    $res = displayform($renderer, "knock, knock, neo...", $options);
    if (PEAR::isError($res))
    {
      logentry("login.320: " . $res->toString());
      return PEAR::raiseError("error displaying form (code: login.320)");
    }
    return $res;
  }
}

$l = new login();
$m = $l->main();
if (PEAR::isError($m))
{
  logentry("login.400: " . $m->toString());
}

?>
