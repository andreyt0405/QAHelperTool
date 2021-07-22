import logging
from argparse import ArgumentParser, FileType
from os import remove, rename
from platform import system as osType
from sys import stdout, argv
indent = ';3'
ANSI_COLOURS = {"noColour": '\x1b[0' + indent + 'm',
                "magenta": '\x1b[35' + indent + 'm',
                "red": '\x1b[31' + indent + 'm',
                "yellow": '\x1b[33' + indent + 'm',
                "green": '\x1b[32' + indent + 'm',
                "cyan": '\x1b[36' + indent + 'm'}
FORMAT = "[[%(asctime)s] [%(name)s] [%(levelname)s] [%(filename)s:%(lineno)d - %(funcName)s] %(message)s"
MONO_LOGS_SWITCH = "--mono_logs"
LOG_FILE_NAME = "fusing.log"  # For when using quiet mode, otherwise, logger is to screen


def add_colouring_to_emit_windows(handler, fn):
    def _set_colour(handler, code):
        import ctypes
        handler.STD_OUTPUT_HANDLE = -11
        hdl = ctypes.windll.kernel32.GetStdHandle(handler.STD_OUTPUT_HANDLE)
        ctypes.windll.kernel32.SetConsoleTextAttribute(hdl, code)

    def new(*args):
        FOREGROUND_BLUE = 0x0001
        FOREGROUND_GREEN = 0x0002
        FOREGROUND_RED = 0x0004
        FOREGROUND_WHITE = FOREGROUND_BLUE | FOREGROUND_GREEN | FOREGROUND_RED
        FOREGROUND_INTENSITY = 0x0008  # foreground colour is intensified.
        FOREGROUND_GREEN = 0x0002 | FOREGROUND_INTENSITY
        FOREGROUND_CYAN = 0x0003 | FOREGROUND_INTENSITY
        FOREGROUND_RED = 0x0004 | FOREGROUND_INTENSITY
        FOREGROUND_MAGENTA = 0x0005 | FOREGROUND_INTENSITY
        FOREGROUND_YELLOW = 0x0006 | FOREGROUND_INTENSITY

        levelno = args[0].levelno
        if levelno >= 50:
            colour = FOREGROUND_MAGENTA
        elif levelno >= 40:
            colour = FOREGROUND_RED
        elif levelno >= 30:
            colour = FOREGROUND_YELLOW
        elif levelno >= 20:
            colour = FOREGROUND_GREEN
        elif levelno >= 10:
            colour = FOREGROUND_CYAN
        else:
            colour = FOREGROUND_WHITE
        _set_colour(handler, colour)
        ret = fn(*args)
        _set_colour(handler, FOREGROUND_WHITE)
        return ret

    return new


def add_colouring_to_emit_ansi(fn):
    def new(*args):
        levelno = args[0].levelno
        if levelno >= 50:
            colour = ANSI_COLOURS["magenta"]
        elif levelno >= 40:
            colour = ANSI_COLOURS["red"]
        elif levelno >= 30:
            colour = ANSI_COLOURS["yellow"]
        elif levelno >= 20:
            colour = ANSI_COLOURS["green"]
        elif levelno >= 10:
            colour = ANSI_COLOURS["cyan"]
        else:
            colour = ANSI_COLOURS["noColour"]
        if type(args[0].msg) in [str, unicode]:
            args[0].msg = colour + args[0].msg + ANSI_COLOURS["noColour"]
        else:
            args[0].msg = colour + '\n'.join(args[0].msg) + ANSI_COLOURS["noColour"]
        args[0].levelname = colour + args[0].levelname + ANSI_COLOURS["noColour"]
        return fn(*args)
    return new


def getScreenLogger(name, log_to_file=None, colorize_logger=True):
    """
        @name Logger's name.
        @returns A logger object which will log to the screen (only).
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    formatter = logging.Formatter(fmt=FORMAT)
    if log_to_file:
        handler = logging.FileHandler(log_to_file)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    handler = logging.StreamHandler(stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    if colorize_logger and MONO_LOGS_SWITCH not in argv:
        if osType() == 'Windows':
            handler.emit = add_colouring_to_emit_windows(handler, handler.emit)
        else:
            handler.emit = add_colouring_to_emit_ansi(handler.emit)
    return logger


def changeToFileLogging(path, loggersToChange):
    fileh = logging.FileHandler(path, "w")
    formatter = logging.Formatter(fmt=FORMAT)
    fileh.setFormatter(formatter)
    for logger in loggersToChange:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
        logger.addHandler(fileh)


def cleanupColoursFromFile(logFile):
    try:
        finalName = logFile.name
        tempName = finalName + ".clean"
        with open(tempName, "w") as cleanLog:
            for line in logFile:
                for colour in ANSI_COLOURS.values():
                    line = line.replace(colour, "")
                cleanLog.write(line)
        logFile.close()
        remove(finalName)
        rename(tempName, finalName)
    except Exception as e:
        print e


def addFileHandler(logger, log_file):
    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt=FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return handler


def getArgs():
    parser = ArgumentParser(description="Logger tool")
    parser.add_argument("-c", "--clean", type=FileType('rt'), help="Logged file to clean of ansi colour characters.")
    return parser.parse_args()


def main():
    args = getArgs()
    if args.clean:
        cleanupColoursFromFile(args.clean)


logger = getScreenLogger("AppdomeQA")

if __name__ == "__main__":
    main()
