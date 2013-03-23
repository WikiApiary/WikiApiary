<?php
require_once ('/home/thingles/wikibots/WikiApiary/apiary-config.php');

$id = $_GET['id'];

try {
    $db = sprintf('mysql:host=%s;dbname=%s', DB_HOST, DB_NAME);
    $conn = new PDO($db, DB_USER, DB_PASSWORD);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $stmt = $conn->prepare('SELECT capture_date, size1, size2, size3, size4, size5, size6, size7, size8, size9, size10plus FROM smwextinfo WHERE website_id = :id ORDER BY capture_date ASC');
    $stmt->execute(array('id' => $id));
    $result = $stmt->fetchAll();
    if ( count($result) ) {
        printf ("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n",
    		'capture_date', 'size1', 'size2', 'size3', 'size4', 'size5', 'size6', 'size7', 'size8', 'size9', 'size10plus');
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
