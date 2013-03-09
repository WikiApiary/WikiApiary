<?php
require_once ('/home/thingles/wikibots/WikiApiary/apiary-config.php');

$id = $_GET['id'];

try {
    $db = sprintf('mysql:host=%s;dbname=%s', DB_HOST, DB_NAME);
    $conn = new PDO($db, DB_USER, DB_PASSWORD);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $stmt = $conn->prepare('SELECT capture_date, proppagecount, usedpropcount, declaredpropcount FROM smwinfo WHERE website_id = :id');
    $stmt->execute(array('id' => $id));
    $result = $stmt->fetchAll();
    if ( count($result) ) {
        printf ("%s, %s, %s, %s\n",
		'capture_date', 'proppagecount', 'usedpropcount', 'declaredpropcount');
        foreach($result as $row) {
            printf ("%s, %s, %s, %s\n",
		$row['capture_date'], $row['proppagecount'], $row['usedpropcount'], $row['declaredpropcount']);
        }
    } else {
        echo "No rows returned.";
    }
} catch(PDOException $e) {
    echo 'ERROR: ' . $e->getMessage();
}
?>
