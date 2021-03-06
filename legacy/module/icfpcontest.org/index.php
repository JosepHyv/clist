<?php
    require_once dirname(__FILE__) . "/../../config.php";

    if (!isset($URL)) $URL = "http://icfpcontest.org/";
    if (!isset($HOST)) $HOST = parse_url($URL, PHP_URL_HOST);
    if (!isset($RID)) $RID = -1;
    if (!isset($LANG)) $LANG = 'RU';
    if (!isset($TIMEZONE)) $TIMEZONE = 'UTC';
    if (!isset($contests)) $contests = array();

    $debug_ = $RID == -1;

    foreach(array($URL, 'http://icfpcontest.org/') as $url) {
        $page = curlexec($url);

        preg_match('#contest will start(?:\s*at|\s*on)\s*(?:<a[^>]*>)?(?P<start_time>[^<.]{4,})#', $page, $match);
        $start_time = preg_replace('/\s+at/', '', $match['start_time']);

        if (preg_match_all('#(?P<title>\b[\s*a-z]*)\s*will end(?:\s*at|\s*on)\s*(?:<a[^>]*>)?(?P<end_time>[^<.]*)#', $page, $matches, PREG_SET_ORDER)) {
            foreach ($matches as $m) {
                $title = ucfirst(trim($m['title']));
                $end_time = preg_replace('/\s+at/', '', $m['end_time']);
                $contests[] = array(
                    'start_time' => $start_time,
                    'end_time' => $end_time,
                    'title' => $title,
                    'url' => $url,
                    'host' => $HOST,
                    'rid' => $RID,
                    'timezone' => $TIMEZONE,
                );
            }
        } else {
            $contests[] = array(
                'start_time' => $start_time,
                'duration' => '72:00',
                'title' => 'ICFP Programming Contest',
                'url' => $url,
                'host' => $HOST,
                'rid' => $RID,
                'timezone' => $TIMEZONE,
            );
        }
    }
    if ($debug_) {
        print_r($contests);
    }
?>
