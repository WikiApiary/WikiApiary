<?php
require_once ('/home/thingles/wikibots/WikiApiary/apiary-config.php');

$id = $_GET['id'];
$durationParam = $_GET['duration'];

try {
    $db = sprintf('mysql:host=%s;dbname=%s', DB_HOST, DB_NAME);
    $conn = new PDO($db, DB_USER, DB_PASSWORD);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    date_default_timezone_set('America/Chicago');

    $duration = "-3 months";
    switch ($durationParam) {
        case '1w':
            $duration = "-1 week";
            break;
        case '1m':
            $duration = "-1 months";
            break;
        case '2m':
            $duration = "-2 months";
            break;
        case '3m':
            $duration = "-3 months";
            break;
        case '1y':
            $duration = "-1 year";
            break;
    }
    $date_filter = date('Y-m-d H:i:s', strtotime($duration));

    $stmt = $conn->prepare('SELECT capture_date, response_timer FROM statistics WHERE website_id = :id  AND capture_date > :date_filter AND response_timer IS NOT NULL');
    $stmt->execute(array('id' => $id, 'date_filter' => $date_filter));
    $result = $stmt->fetchAll();
    if ( count($result) ) {
        foreach($result as $row) {
            printf ("%s, %s\n",
		$row['capture_date'], $row['response_timer']);
        }
    } else {
        echo "No rows returned.";
    }
} catch(PDOException $e) {
    echo 'ERROR: ' . $e->getMessage();
}
?>
