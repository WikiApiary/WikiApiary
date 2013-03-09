<?php
require_once ('/home/thingles/wikibots/WikiApiary/apiary-config.php');

$id = $_GET['id'];

try {
    $db = sprintf('mysql:host=%s;dbname=%s', DB_HOST, DB_NAME);
    $conn = new PDO($db, DB_USER, DB_PASSWORD);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $stmt = $conn->prepare('SELECT * FROM statistics WHERE website_id = :id');
    $stmt->execute(array('id' => $id));
    $result = $stmt->fetchAll();
    if ( count($result) ) {
        printf ("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n",
		'capture_date', 'users', 'activeusers', 'admins',
		'articles', 'edits', 'images', 'jobs', 'pages', 'views');
        foreach($result as $row) {
            printf ("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n",
		$row['capture_date'], $row['users'], $row['activeusers'], $row['admins'],
		$row['articles'], $row['edits'], $row['images'], $row['jobs'], $row['pages'], $row['views']);
        }
    } else {
        echo "No rows returned.";
    }
} catch(PDOException $e) {
    echo 'ERROR: ' . $e->getMessage();
}
?>
