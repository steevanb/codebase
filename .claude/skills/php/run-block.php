<?php

// Runs a block of code of a page, written in the file given as argument (see run-blocks.py), and prints its result:
// the value of the last variable it sets (var_export), or the exception (or the Error, PHP >= 7.0) it throws, written
// like in the pages (short name of its class, then its message).
// Written for every PHP version run by run-blocks.py, PHP 5.6 included.

require '/package/vendor/autoload.php';

function printThrown($thrown)
{
    $class = explode('\\', get_class($thrown));
    echo end($class), ': ', $thrown->getMessage(), "\n";
}

// A function, so that the variables of the block are the only ones of its scope, besides $file
function runBlock($file)
{
    try {
        include $file;
    } catch (Throwable $thrown) {
        printThrown($thrown);

        return;
    } catch (Exception $thrown) {
        printThrown($thrown);

        return;
    }

    $variables = get_defined_vars();
    unset($variables['file']);
    if (count($variables) > 0) {
        var_export(end($variables));
        echo "\n";
    }
}

runBlock($argv[1]);
