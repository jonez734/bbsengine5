<?php

require_once("config.prg");
require_once(SITENAME.".prg");
require_once("bbsengine5.prg");

require_once("Markdown.inc.prg");

class page
{
  function main()
  {
    startsession();

    $file = isset($_REQUEST["file"]) ? $_REQUEST["file"] : null;
    if ($file === null)
    {
      logentry("page.200: 'file' is null");
      displayerrorpage("page not found", 404);
      return;
    }


    $info = pathinfo($file);
    $fileextension = $info["extension"];
    $filename = $info["filename"];

    setreturnto(getcurrenturi());
    setcurrentsite(SITENAME);
    setcurrentaction("view");
    setcurrentpage($filename);

    switch ($fileextension)
    {
      case "md":
      {
        $pagetemplate = "page-markdown.tmpl";
        $content = Markdown::defaultTransform(file_get_contents($file));
        break;
      }
      case "tmpl":
      {
        $pagetemplate = $file;
        $smarty = getsmarty();
        if ($smarty->templateExists($file) == false)
        {
          displayerrorpage("template does not exist", 404);
          return;
        }
        $content = $smarty->fetch($file);
        break;
      }
    }

    $data = [];
    $data["content"] = $content;
    $data["pagetemplate"] = $pagetemplate;
    
    $res = displaypage($data);
    return $res;
  }
};

$a = new page();
$b = $a->main();
if (PEAR::isError($b))
{
  displayerrorpage($b->getMessage());
  exit;
}
