<?php
require_once ('/home/thingles/wikibots/WikiApiary/apiary-config.php');

$id = $_GET['id'];

try {
    $db = sprintf('mysql:host=%s;dbname=%s', DB_HOST, DB_NAME);
    $conn = new PDO($db, DB_USER, DB_PASSWORD);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    date_default_timezone_set('America/Chicago');
    $date_filter = date('Y-m-d H:i:s', strtotime('-3 months'));

    $stmt = $conn->prepare('SELECT capture_date, size1, size2, size3, size4, size5, size6, size7, size8, size9, size10plus FROM smwextinfo WHERE website_id = :id AND capture_date > :date_filter ORDER BY capture_date ASC');
    $stmt->execute(array('id' => $id, 'date_filter' => $date_filter));
    $result = $stmt->fetchAll();
    if ( count($result) ) {
        foreach($result as $row) {
            printf ("%s, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d\n",
                $row['capture_date'],
                $row['size1'],
                $row['size2'],
                $row['size3'],
                $row['size4'],
                $row['size5'],
                $row['size6'],
                $row['size7'],
                $row['size8'],
                $row['size9'],
                $row['size10plus']
                );
        }
    } else {
        echo "No rows returned.";
    }
} catch(PDOException $e) {
    echo 'ERROR: ' . $e->getMessage();
}
?>
