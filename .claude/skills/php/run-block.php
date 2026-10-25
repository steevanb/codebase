<?php

// Runs a block of code of a page, written in the file given as argument (see run-blocks.py), and prints its result:
// the value of the last variable it sets (var_export), or the exception (or the Error, PHP >= 7.0) it throws, written
// like in the pages (short name of its class, then its message). The PHP errors are printed like in the pages too:
// the name of their constant, then their message (E_WARNING: Undefined array key "key").
// Written for every PHP version run by run-blocks.py, PHP 5.6 included.

require '/package/vendor/autoload.php';

function errorName($level)
{
    $names = array(
        'E_ERROR', 'E_WARNING', 'E_NOTICE', 'E_DEPRECATED', 'E_RECOVERABLE_ERROR',
        'E_USER_ERROR', 'E_USER_WARNING', 'E_USER_NOTICE', 'E_USER_DEPRECATED',
    );
    foreach ($names as $name) {
        if (constant($name) === $level) {
            return $name;
        }
    }

    return 'E_' . $level;
}

set_error_handler(function ($level, $message, $file) {
    // The deprecations triggered by the package itself are left out: an old package triggers some with a recent PHP
    if (in_array($level, array(E_DEPRECATED, E_USER_DEPRECATED), true) && 0 === strpos($file, '/package/')) {
        return true;
    }
    echo errorName($level), ': ', $message, "\n";
    // An E_RECOVERABLE_ERROR not handled stops the script
    if (E_RECOVERABLE_ERROR === $level) {
        exit(255);
    }

    return true;
});

// An E_ERROR cannot be handled: printed once the script has stopped, instead of the message of PHP
ini_set('display_errors', '0');
register_shutdown_function(function () {
    $error = error_get_last();
    if (null !== $error && E_ERROR === $error['type']) {
        echo 'E_ERROR: ', $error['message'], "\n";
    }
});

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
