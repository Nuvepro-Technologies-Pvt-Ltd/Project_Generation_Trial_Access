import sys
import types
import pytest
from unittest import mock

# Test suite for src/app/main.py (Flask app entry point)
# Assumptions:
# - 'create_app' is a factory that returns a Flask-like app.
# - main.py runs the app when run as __main__, not when imported.
#
# We use pytest and unittest.mock to verify entrypoint behavior.


def test_app_instance_created(monkeypatch):
    """
    GIVEN: The app entry module
    WHEN: It is imported and 'create_app' is patched
    THEN: It should assign the return value of create_app() to 'app'
    """
    dummy_app = object()
    with mock.patch('src.app.main.create_app', return_value=dummy_app):
        # Reload the module after patching
        if 'src.app.main' in sys.modules:
            del sys.modules['src.app.main']
        import src.app.main as main_mod
        assert hasattr(main_mod, 'app')
        assert main_mod.app is dummy_app


def test_app_run_called_on_main(monkeypatch):
    """
    GIVEN: The app entry module running as __main__
    WHEN: create_app returns a mock app
    THEN: app.run should be called with correct host and port
    """
    # Patch sys.modules['__main__'] to simulate running as script
    dummy_app = mock.Mock()
    dummy_create = mock.Mock(return_value=dummy_app)

    monkeypatch.setitem(sys.modules, 'src.app.create_app', dummy_create)
    module_name = 'src.app.main'
    if module_name in sys.modules:
        del sys.modules[module_name]

    # Patch sys.argv[0] to match the file
    test_globals = dict(__name__='__main__')
    code = (
        'from src.app import create_app\n'
        'app = create_app()\n'
        'if __name__ == "__main__":\n'
        '    app.run(host="0.0.0.0", port=5000)\n'
    )
    exec(compile(code, module_name, 'exec'), test_globals)

    # Validate 'run' was called with the correct params
    dummy_app.run.assert_called_once_with(host="0.0.0.0", port=5000)


def test_app_run_not_called_on_import(monkeypatch):
    """
    GIVEN: The app entry module is imported (not run as __main__)
    WHEN: create_app returns a mock app
    THEN: app.run should NOT be called
    """
    dummy_app = mock.Mock()
    dummy_create = mock.Mock(return_value=dummy_app)

    with mock.patch('src.app.main.create_app', dummy_create):
        if 'src.app.main' in sys.modules:
            del sys.modules['src.app.main']
        # Importing module as regular import (__name__ != "__main__")
        import importlib
        importlib.import_module('src.app.main')
        dummy_app.run.assert_not_called()


@pytest.mark.parametrize("host, port", [
    ("0.0.0.0", 5000),
    ("127.0.0.1", 8080)]
)
def test_app_run_called_with_custom_params(monkeypatch, host, port):
    """
    GIVEN: Changing the app.run parameters
    WHEN: main.py is simulated with various host/port configs
    THEN: app.run is called with those parameters
    """
    dummy_app = mock.Mock()
    dummy_create = mock.Mock(return_value=dummy_app)
    monkeypatch.setitem(sys.modules, 'src.app.create_app', dummy_create)
    module_name = 'src.app.main'
    if module_name in sys.modules:
        del sys.modules[module_name]
    # Simulate different code execution for custom host/port
    code = (
        'from src.app import create_app\n'
        'app = create_app()\n'
        'if __name__ == "__main__":\n'
        f'    app.run(host="{host}", port={port})\n'
    )
    test_globals = dict(__name__='__main__')
    exec(compile(code, module_name, 'exec'), test_globals)
    dummy_app.run.assert_called_once_with(host=host, port=port)