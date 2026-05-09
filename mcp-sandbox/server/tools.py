import os
import sys
import tempfile
import subprocess
from loguru import logger

# Configure logger
logger.remove()

logger.add(
    sys.stdout,
    level="INFO",
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level}</level> | "
        "{name}:{function}:{line} | "
        "{message}"
    ),
)

def run_shell(command: str) -> str:
    """Run shell command"""

    logger.info(f"Executing shell command: {command}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,
        )

        logger.info(
            f"Shell command completed | returncode={result.returncode}"
        )

        if result.stdout:
            logger.debug(f"STDOUT:\n{result.stdout}")

        if result.stderr:
            logger.warning(f"STDERR:\n{result.stderr}")

        return (
            f"RETURN CODE: {result.returncode}\n\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )

    except subprocess.TimeoutExpired:
        logger.error("Shell command timed out")
        return "ERROR: Command timed out"

    except Exception as e:
        logger.exception("Shell command failed")
        return f"ERROR: {str(e)}"

def run_python(code: str) -> str:
    """Execute python code in temp file"""

    logger.info("Executing python code")

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".py",
            mode="w"
        ) as f:
            f.write(code)
            temp_path = f.name

        logger.info(f"Temporary python file created: {temp_path}")

        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=300,
        )

        logger.info(
            f"Python execution completed | returncode={result.returncode}"
        )

        if result.stdout:
            logger.debug(f"STDOUT:\n{result.stdout}")

        if result.stderr:
            logger.warning(f"STDERR:\n{result.stderr}")

        return (
            f"RETURN CODE: {result.returncode}\n\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )

    except subprocess.TimeoutExpired:
        logger.error("Python execution timed out")
        return "ERROR: Python execution timed out"

    except Exception as e:
        logger.exception("Python execution failed")
        return f"ERROR: {str(e)}"

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
            logger.info(f"Deleted temp file: {temp_path}")

def read_file(path: str) -> str:
    """Read file content"""

    logger.info(f"Reading file: {path}")

    try:
        with open(path, "r") as f:
            content = f.read()

        logger.info(f"Read successful: {path}")

        return content

    except Exception as e:
        logger.exception(f"Failed reading file: {path}")
        return f"ERROR: {str(e)}"

def write_file(
    path: str,
    content: str = "",
    mode: str = "w"
) -> str:
    """Write content to file"""

    logger.info(f"Writing file: {path} | mode={mode}")

    try:
        if mode not in ("w", "a"):
            logger.error(f"Invalid write mode: {mode}")
            return "ERROR: Invalid mode"

        with open(path, mode) as f:
            f.write(content)

        logger.info(f"Write successful: {path}")

        return "OK"

    except Exception as e:
        logger.exception(f"Failed writing file: {path}")
        return f"ERROR: {str(e)}"

def list_dir(path: str) -> list:
    """List directory contents"""

    logger.info(f"Listing directory: {path}")

    try:
        items = os.listdir(path)

        logger.info(
            f"Directory listed successfully | items={len(items)}"
        )

        return items

    except Exception as e:
        logger.exception(f"Failed listing directory: {path}")
        return [f"ERROR: {str(e)}"]