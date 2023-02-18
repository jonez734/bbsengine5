<?php

/**
 * @since 20221116
 */
function databaseconnect($dsn)
{
  static $pdocache = [];

  if (array_key_exists($dsn, $pdocache))
  {
//    logentry("databaseconnect.100: returning cached pdo ref");
    return $pdocache[$dsn];
  }

  $options = [
    \PDO::ATTR_ERRMODE            => \PDO::ERRMODE_EXCEPTION,
    \PDO::ATTR_DEFAULT_FETCH_MODE => \PDO::FETCH_ASSOC,
    \PDO::ATTR_EMULATE_PREPARES   => false,
  ];
  
  $user = "apache";
  
  $pass = "";

  try {
    $pdo = new \PDO($dsn, $user, $pass, $options);
  } catch (\PDOException $e) {
    throw new \PDOException($e->getMessage(), (int)$e->getCode());
  }
  
  $pdocache[$dsn] = $pdo;
  return $pdo;
}
?>
