<?php

/**
 * contains member class which handles some account-related functions
 *
 * @package bbsengine5
 */

require_once("config.php");
require_once(SITENAME.".php");
require_once("bbsengine5.php");

/**
 * contains member management functions (add, update, delete, view, summary)
 *
 * @package bbsengine5
 */
class member
{
  var $dbh = null;

  function getcount()
  {
    $sql = "select count(*) from engine.member";
    return $this->dbh->getOne($sql);
  }

  function getmemberform()
  {
    $currentmemberid = getcurrentmemberid();
    
    $form = getquickform(SITENAME."-member");
    if (PEAR::isError($form))
    {
      logentry("member.100: " . $form->toString());
      return $form;
    }

    return $form;
  }

  function buildmemberactions($id)
  {
    $actions = [];
    if (accessmember("detail", array("id" => $id)) === true && getcurrentaction() !== "detail")
    {
      $actions[] = array("href" => "/member-detail-{$id}", "title" => "detail");
    }

    if (accessmember("edit", array("id" => $id)) === true && getcurrentaction() !== "edit")
    {
      $actions[] = array("href" => "/member-edit-{$id}", "title" => "edit");
    }
    return $actions;

  }

  function detail()
  {
    $id = isset($_REQUEST["id"]) ? intval($_REQUEST["id"]) : null;
    
//    logentry("member.detail.100: cookie=".var_export($_COOKIE, true));
    
    if (accessmember("detail", array("id" => $id)) === false)
    {
      displaypermissiondenied();
      return;
    }

    $member = getmemberbyid($id);
    if (PEAR::isError($member))
    {
      displayerrorpage("Database error (code: member.detail.1)");
      logentry("member.detail.1: " . $member->toString());
      return;
    }

    if ($member === null)
    {
      displayerrorpage("Database error (code: member.detail.2)");
      logentry("member.detail.2: getmember returned null");
      return;
    }

    setcurrentaction("detail");
    
    $allflags = $this->buildallflags($id);
    $flags = [];
    foreach ($allflags as $flag)
    {
      if ($flag["value"] === true)
      {
        $flags[] = $flag["name"];
      }
    }

    $member["id"] = $id;
    $member["flags"] = $flags; // implode(", ", $flags);
    $member["actions"] = $this->buildmemberactions($id);

    $membername = $member["name"];
    
    $data["pagetemplate"] = "member-detail.tmpl";
    $data["member"] = $member;
    displaypage($data);
    return;
  }

  function buildallflags($memberid)
  {
    $sql = "select upper(flag.name) as name, coalesce(mmf.value, flag.defaultvalue) as value, flag.description from engine.flag left outer join engine.map_member_flag as mmf on flag.name = mmf.name and mmf.memberid=?";
    $dat = array($memberid);
    $res = $this->dbh->getAll($sql, null, $dat, array("integer"));
    if (PEAR::isError($res))
    {
      logentry("_buildflagarray.10: " . $res->toString());
      return;
    }

    $allflags = [];
    foreach ($res as $rec)
    {
      $flag = [];
      $flag["name"] = $rec["name"];
      $flag["description"] = $rec["description"];
      
      $flag["value"] = ($rec["value"] === "t") ? true : false;
      $allflags[] = $flag;
    }
    
    return $allflags;
  }

  function addmemberflagfieldset($form, $memberid)
  {
    $fieldset = $form->addElement("fieldset", "flagfieldset")->setLabel("Flags");
    $group = $fieldset->addElement("group", "flags"); // ->setSeparator("<br />");

    $allflags = $this->buildallflags($memberid);
    foreach($allflags as $flag)
    {
      $name = $flag["name"];
      $element = $group->addCheckbox($name);
      $element->setLabel($flag["description"]); // addElement("checkbox", $name)->setLabel($name." - ".$flag["description"]);
    }
    return;
  }

  function edit()
  {
    $memberid = isset($_REQUEST["id"]) ? intval($_REQUEST["id"]) : null;
    $currentmemberid = getcurrentmemberid();
    
    logentry("member.210: memberid=".var_export($memberid, true));

    if (accessmember("edit", array("id" => $memberid)) === false)
    {
      displaypermissiondenied();
      return;
    }

    $member = getmemberbyid($memberid);
    if (PEAR::isError($member))
    {
      displayerrorpage("Database Error (code: member.200)");
      logentry("member.200: " . $member->toString());
      return;
    }
    
    if ($member === null)
    {
      displayerrorpage("input error (code: member.202)");
      logentry("member.202: getmember(".var_export($memberid, true).") returned null.");
      return;
    }

    setcurrentaction("edit");

    $form = $this->getmemberform();
    $res = buildmemberfieldset($form, ["uniqueusername" => false]);
    $res = buildchangepasswordfieldset($form, array("memberid" => $memberid));

    if (accessmember("editflags", array("id" => $memberid)) === true)
    {
      $this->addmemberflagfieldset($form, $memberid);
      logentry("memberedit.100: -- calling buildallflags");
      $allflags = $this->buildallflags($memberid);
      if (PEAR::isError($allflags))
      {
        logentry("memberedit.110: " . $allflags->toString());
        displayerrorpage("Database Error (memberedit.110)");
        return;
      }
      $flags = [];
      foreach ($allflags as $flag)
      {
        $name = $flag["name"];
        $value = $flag["value"];
        $flags[$name] = $value;
      }
      $data = [];
      $data["flags"] = $flags;
      $form->addDataSource(new HTML_QuickForm2_DataSource_Array($data));
    }

    $form->addDataSource(new HTML_QuickForm2_DataSource_Array($member));

    $constants = [];
    $constants["id"] = $memberid;
    $constants["mode"] = "edit";
    $form->addDataSource(new HTML_QuickForm2_DataSource_Array($constants));

    $form->addElement("submit", "submitmember", array("value" => "update"));
    
    $res = handleform($form, array($this, "update"), "edit member");
    if ($res === true)
    {
      logentry("editmember.102: handleform(...) returned true");
      return true;
    }

    $renderer = getquickformrenderer();
    $form->render($renderer);

    $res = displayform($renderer, "edit member");
    if (PEAR::isError($res))
    {
      logentry("editmember.101: " . $res->toString());
    }
    return $res;
  }
  
  function update($values)
  {
    logentry("update.110: values=".var_export($values, true));

    $memberid = isset($values["id"]) ? intval($values["id"]) : null;

    $currentmemberid = getcurrentmemberid();
    
    logentry("update.100: memberid=".var_export($memberid, true));
    if (accessmember("edit", array("id" => $memberid)) === false)
    {
      displaypermissiondenied();
      return;
    }

    $member = buildmemberrecord($values);
    
    $res = $this->dbh->beginTransaction();
    if (PEAR::isError($res))
    {
      displayerrorpage("Database Error. (code: updatemember.100)");
      logentry("updatemember.100: " . $res->toString());
      $this->dbh->rollback();
      return;
    }

//    logentry("update member record...");
    if (accessmember("edit", array("id" => $memberid)) === true)
    {
      $res = $this->dbh->autoExecute("engine.__member", $member, MDB2_AUTOQUERY_UPDATE, "id=" . $this->dbh->quote($memberid, "integer"));
      if (PEAR::isError($res))
      {
        logentry("updatemember.110: " . $res->toString());
        displayerrorpage("Database Error (code: updatemember.110)");
        return;
      }
    }
    
//    logentry("update member flags...");
    if (accessmember("editflags", array("id" => $memberid)) === true)
    {
      $allflags = $this->buildallflags($memberid);
      if (PEAR::isError($allflags))
      {
        logentry("updatemember.120: " . $allflags->toString());
        return;
      }
      
      $flags = [];
      foreach ($allflags as $flag)
      {
        $name = $flag["name"];
        $value = isset($values["flags"][$name]) ? true : false;
//        logentry("calling setflag...");
        $res = setflag($name, $value, $memberid);
        if (PEAR::isError($res))
        {
          logentry("updatemember.122: " . $res->toString());
          $this->dbh->rollback();
          break;
        }
      }
    }

    $plaintext = isset($values["newPassword"]) ? $values["newPassword"] : null;
    $plaintext = trim($plaintext);
    if ($plaintext != "")
    {
      setpassword($memberid, $plaintext);
    }
    $res = $this->dbh->commit();
    displayredirectpage("OK -- Account Details Updated");
    return true;
  }
  
  function delete()
  {
    if (!flag("SYSOP"))
    {
      displaypermissiondenied();
      logentry("member.delete: permission denied.");
      return;
    }
    
    $memberid = isset($_REQUEST["id"]) ? intval($_REQUEST["id"]) : null;
    $res = $this->dbh->autoExecute("member", null, MDB2_AUTOQUERY_DELETE, "id=" . $this->dbh->quote($memberid, "integer"));
    if (PEAR::isError($res))
    {
      displayerrorpage("Database error during delete operation");
      logentry("member.delete: " . $res->toString());
      return;
    }
    displayredirectpage("OK -- account deleted");
    return;
  }

  function add()
  {
    if (accessmember("add", []) === false)
    {
      displaypermissiondenied();
      return;
    }

    $memberid = null;

    setcurrentaction("add");

    $form = $this->getmemberform();
    $res = buildmemberfieldset($form);
    $res = buildnewpasswordfieldset($form);
    if (accessmember("editflags", array("id" => $memberid)) === true)
    {
      $this->addmemberflagfieldset($form, $memberid);
    }

    logentry("memberadd.100: -- calling buildallflags");
    $allflags = $this->buildallflags($memberid);
    if (PEAR::isError($allflags))
    {
      logentry("memberadd.110: " . $allflags->toString());
      displayerrorpage("Database Error (memberadd.110)");
      return;
    }
    $flags = [];
    foreach ($allflags as $flag)
    {
      $name = $flag["name"];
      $value = $flag["value"];
      $flags[$name] = $value;
    }

    $data = [];
    $data["flags"] = $flags;
    $form->addDataSource(new HTML_QuickForm2_DataSource_Array($data));

//    $form->addDataSource(new HTML_QuickForm2_DataSource_Array($member));

    $const = [];
    $const["id"] = $memberid;
    $const["mode"] = "add";
    $form->addDataSource(new HTML_QuickForm2_DataSource_Array($const));

    $form->addElement("submit", "submitmember", ["value" => "add"]);

    $res = handleform($form, [$this, "insert"], "add member");
    if (PEAR::isError($res))
    {
      logentry("member.500: " . $res->toString());
      return PEAR::raiseError("member form handling error (code: member.500)");
    }
    if ($res === true)
    {
      return $res;
    }

    $renderer = getquickformrenderer();
    $form->render($renderer);
    $options = [];
    $res = displayform($renderer, "member form", $options);
    if (PEAR::isError($res))
    {
      logentry("member.540: " . $res->toString());
      return PEAR::raiseError("error displaying form (code: member.540)");
    }
    return $res;
  }
  
  function insert($values)
  {
    $member = [];
    $member["username"] = $values["username"];
    $member["name"] = $values["name"];
    $member["email"]  = $values["email"];
    $member["createdbyid"] = getcurrentmemberid();
    $member["datecreated"] = "now()";
    $member["updatedbyid"] = getcurrentmemberid();
    $member["dateupdated"] = "now()";

    $dbh = dbconnect(SYSTEMDSN);
    $res = $dbh->beginTransaction();
    $res = $dbh->autoExecute("engine.__member", $member, MDB2_AUTOQUERY_INSERT);
    if (PEAR::isError($res))
    {
        logentry("member.400: " . $res->toString());
        $dbh->rollback();
        return PEAR::raiseError("Database Error (insert) (code: member.400)");
    }
    $memberid = $dbh->lastInsertID();
    if (PEAR::isError($memberid))
    {
      logentry("member.420: " . $memberid->toString());
      $dbh->rollback();
      return PEAR::raiseError("Database Error (lastinsertid) (code: member.420)");
    }
    $plaintext = $values["password"];
    $res = setpassword($memberid, $plaintext);
    if (PEAR::isError($res))
    {
      logentry("member.440: " . $res->toString());
      $dbh->rollback();
      return PEAR::raiseError("Unable to set password (code: member.440)");
    }

    $res = $dbh->commit();
    displayredirectpage("OK -- member added");
    return true;
  }
  
  function main()
  {
    $this->dbh = &dbconnect(SYSTEMDSN);
    if (PEAR::isError($this->dbh))
    {
      logentry("member: " . $this->dbh->toString());
      displayerrorpage("Database Connect Error");
      return;
    }
    
    startsession();

    setcurrentsite(SITENAME);
    setcurrentpage("member");

//    setreturnto(SITEURL);

    $mode = isset($_REQUEST["mode"]) ? $_REQUEST["mode"] : null;
    switch ($mode)
    {
      case "add":
      {
        $res = $this->add();
        break;
      }
      case "edit":
      {
        $res = $this->edit();
        break;
      }
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
      case "summary":
      {
        $res = $this->summary();
        break;
      }
      default:
        displayerrorpage("unknown mode");
        break;
    }
    
    $this->dbh->disconnect();
    return;
  }
}

$m = new member();
$m->main();

?>
