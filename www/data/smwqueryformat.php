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

    $stmt = $conn->prepare("SELECT capture_date, format_broadtable, format_csv, format_category, format_count, format_dsv, format_debug, format_embedded, format_feed, format_json, format_list, format_ol, format_rdf, format_table, format_template, format_ul FROM smwextinfo WHERE website_id = :id AND capture_date > :date_filter ORDER BY capture_date ASC");
    $stmt->execute(array('id' => $id, 'date_filter' => $date_filter));
    $result = $stmt->fetchAll();
    if ( count($result) ) {
        foreach($result as $row) {
            printf ("%s, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d\n",
                $row['capture_date'],
                $row['format_broadtable'],
                $row['format_csv'],
                $row['format_category'],
                $row['format_count'],
                $row['format_dsv'],
                $row['format_debug'],
                $row['format_embedded'],
                $row['format_feed'],
                $row['format_json'],
                $row['format_list'],
                $row['format_ol'],
                $row['format_rdf'],
                $row['format_table'],
                $row['format_template'],
                $row['format_ul']
                );
        }
    } else {
        echo "No rows returned.";
    }
} catch(PDOException $e) {
    echo 'ERROR: ' . $e->getMessage();
}
?>