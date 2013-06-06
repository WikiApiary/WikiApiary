<?php
require_once ('/home/thingles/wikibots/WikiApiary/apiary-config.php');

$id = $_GET['id'];

try {
    $db = sprintf('mysql:host=%s;dbname=%s', DB_HOST, DB_NAME);
    $conn = new PDO($db, DB_USER, DB_PASSWORD);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    date_default_timezone_set('America/Chicago');
    $date_filter = date('Y-m-d H:i:s', strtotime('-3 months'));

    $stmt = $conn->prepare('SELECT capture_date, articles, pages FROM statistics WHERE website_id = :id AND capture_date > :date_filter');
    $stmt->execute(array('id' => $id, 'date_filter' => $date_filter));
    $result = $stmt->fetchAll();
    if ( count($result) ) {
        printf ("%s, %s, %s\n",
		'capture_date', 'articles', 'pages');
        # Change the date to be 2009/07/12 12:34:56, currently 2013-03-06 11:15:26
        foreach($result as $row) {
            printf ("%s, %s, %s\n",
		$row['capture_date'], $row['articles'], $row['pages']);
        }
    } else {
        echo "No rows returned.";
    }
} catch(PDOException $e) {
    echo 'ERROR: ' . $e->getMessage();
}
?>
