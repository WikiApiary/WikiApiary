<?php
require_once ('/home/thingles/wikibots/WikiApiary/apiary-config.php');

$id = $_GET['id'];

try {
    $db = sprintf('mysql:host=%s;dbname=%s', DB_HOST, DB_NAME);
    $conn = new PDO($db, DB_USER, DB_PASSWORD);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $stmt = $conn->prepare("SELECT capture_date, format_broadtable, format_csv, format_category, format_count, format_dsv, format_debug, format_embedded, format_feed, format_json, format_list, format_ol, format_rdf, format_table, format_template, format_ul FROM smwextinfo WHERE website_id = :id ORDER BY capture_date ASC");
    $stmt->execute(array('id' => $id));
    $result = $stmt->fetchAll();
    if ( count($result) ) {
        printf ("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n",
    		'capture_date', 'broadtable', 'csv', 'category', 'count', 
            'dsv', 'debug', 'embedded', 'feed', 'json', 'list','ol',
            'rdf','table', 'template', 'ul');
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