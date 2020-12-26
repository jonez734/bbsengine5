<?php

/**
 * this is a module to handle member registrations
 *
 * @package bbsengine5
 *
 */

require_once("config.prg");
require_once(SITENAME.".prg");
require_once("bbsengine5.prg");

class join
{
    var $dbh = null;
    
    function insert($values)
    {
      $member = [];
      $member["email"] = $values["email"];
      $member["name"] = $values["name"];
      $member["username"] = $values["username"];
      if (flag("SYSOP"))
      {
        $member["credits"] = $values["credits"];
      }
      $member["datecreated"] = "now()";
      $member["createdbyid"] = getcurrentmemberid();
      $member["dateupdated"] = "now()";
      $member["updatedbyid"] = getcurrentmemberid();

      $res = $this->dbh->beginTransaction();
      $res = $this->dbh->autoExecute("engine.__member", $member, MDB2_AUTOQUERY_INSERT);
      if (PEAR::isError($res))
      {
          logentry("join.20: " . $res->toString());
          $this->dbh->rollback();
          return PEAR::raiseError("error inserting member account (code: join.20)");
      }

      $memberid = $this->dbh->lastInsertID();
      $res = setpassword($memberid, $values["password"]);
      if (PEAR::isError($res))
      {
          logentry("join.22: " . $res->toString());
          return PEAR::raiseError("unable to set new member password (code: join.22)");
      }

      $res = $this->dbh->commit();
      if (PEAR::isError($res))
      {
        logentry("join.24: " . $res->toString());
        return PEAR::raiseError("unable to commit new member account (code: join.24)");
      }

      $data = [];
      $data["pagetemplate"] = "thankyouforjoining.tmpl";
      displaypage($data);
      return true;
    }
    
    function main()
    {
        startsession();
/*
        if (flag("AUTHENTICATED") === False)
        {
            displaypermissiondenied();
            return;
        }
*/
        $this->dbh = dbconnect(SYSTEMDSN);
        if (PEAR::isError($this->dbh))
        {
            logentry("join.10: " . $this->dbh->toString());
            return PEAR::raiseError("Database Error (code: join.10)");
        }
        
        setcurrentsite(SITENAME);
        setcurrentaction("join");

        logentry("join.100: site=".var_export(getcurrentsite(), True)." action=".var_export(getcurrentaction(), True));

        $form = getquickform(LOGENTRYPREFIX."-join");
        buildmemberfieldset($form, ["uniqueusername" => true]);
        // buldprofilefieldset($form);
        buildnewpasswordfieldset($form);
        buildcaptchafieldset($form);

        $form->addElement("submit", "submit", array("value" => "join"));
        
        $const = [];
        $const["memberid"] = isset($_REQUEST["memberid"]) ? intval($_REQUEST["memberid"]) : getcurrentmemberid();
        
        $form->addDataSource(new HTML_QuickForm2_DataSource_Array($const));
  
        $defaults = [];
        $form->addDataSource(new HTML_QuickForm2_DataSource_Array($defaults));
        
        $res = handleform($form, array($this, "insert"), "new user");
        if (PEAR::isError($res))
        {
            logentry("join.101: " . $res->toString());
            return $res;
        }
        if ($res === true)
        {
            logentry("join.130: handleform(...) returned True");
            return true;
        }
        $renderer = getquickformrenderer();
        $form->render($renderer);
        $res = displayform($renderer, "knock, knock neo...");
        if (PEAR::isError($res))
        {
          logentry("join.302: " . $res->toString());
          return $res;
        }
        $this->dbh->disconnect();
        return $res;
    }
};

$j = new join();
$r = $j->main();
if (PEAR::isError($r))
{
    logentry("join.100: " . $r->toString());
    displayerrorpage($r->getMessage());
    exit;
}
?>
