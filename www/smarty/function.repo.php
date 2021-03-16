<?php
require_once("config.php");
require_once("bbsengine4.php");

function buildpluginfilepath($smarty, $name)
{
  foreach ($smarty->getPluginsDir() as $plugindir)
  {
    $p = $plugindir.DIRECTORY_SEPARATOR.basename($name);
    if (file_exists($p))
    {
      return $p;
    }
  }
  return null;
}

function smarty_function_repo($options, Smarty_Internal_Template $template)
{
//  logentry("options=".var_export($options, True));

  require_once(buildpluginfilepath($template->smarty, "modifier.escape.php"));
  require_once(buildpluginfilepath($template->smarty, "modifier.wpprop.php"));

  $dbh = dbconnect(SYSTEMDSN);
  if (PEAR::isError($dbh))
  {
    logentry("function.repo.100: ". $dbh->toString());
    return "REPO.100";
  }

  $project = isset($options["project"]) ? $options["project"] : null;
  
  $sql = "select title from repo.project where name=?";
  $dat = array($project);
  $res = $dbh->getRow($sql, array("text"), $dat, array("text"));
  if (PEAR::isError($res))
  {
    logentry("function.repo.102: " . $res->toString());
    return "REPO.102";
  }

  if ($res === null)
  {
    logentry("function.repo.104: path ".var_export($project, True)." not found");
    return "REPO.104";
  }
  
  $title = isset($res["title"]) ? $res["title"] : $project;

  $href = PROJECTURL.$project;

  $title = smarty_modifier_escape($title);
  $title = smarty_modifier_wpprop($title);

//  logentry("title=".var_export($title, True));
  
  $repo = "<a class=\"repo\" href=\"{$href}\">{$title}</a>";
  return $repo;
}

?>
