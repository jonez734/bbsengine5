<?php
/*
 * this module performs a "logout" of the currently logged in member.
 *
 * @copyright (C) 2020 {@link http://zoidtechnologies.com/ Zoid Technologies} All Rights Reserved.
 */
require_once("config.prg");
require_once(SITENAME.".prg");
require_once("bbsengine5.prg");

class logout
{
  function main()
  {
    startsession();
    
    clearpageprotocol();

    $id = $_SESSION["currentmemberid"];

    displayredirectpage("OK -- logged out");
    logentry("logout: OK for id #{$id}");
    clearcurrentmemberid();
    removesessioncookie();
    session_regenerate_id(true);

    return;
  }
}

$l = new logout();
$l->main();

?>
