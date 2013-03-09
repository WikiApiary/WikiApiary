<?php
require_once ('/home/thingles/wikibots/WikiApiary/apiary-config.php');

$id = $_GET['id'];

try {
    $db = sprintf('mysql:host=%s;dbname=%s', DB_HOST, DB_NAME);
    $conn = new PDO($db, DB_USER, DB_PASSWORD);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $stmt = $conn->prepare('SELECT capture_date, jobs FROM statistics WHERE website_id = :id');
    $stmt->execute(array('id' => $id));
    $result = $stmt->fetchAll();
    if ( count($result) ) {
        printf ("%s, %s\n",
		'capture_date', 'jobs');
        foreach($result as $row) {
            printf ("%s, %s\n",
		$row['capture_date'], $row['jobs']);
        }
    } else {
        echo "No rows returned.";
    }
} catch(PDOException $e) {
    echo 'ERROR: ' . $e->getMessage();
}
?>
