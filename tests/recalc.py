"""
Test helper: recalculate a generated workbook with LibreOffice and read the
computed values back via openpyxl.

openpyxl writes formula *strings* but never evaluates them, so a freshly built
workbook has no cached numeric results. We drive LibreOffice's real formula
engine through the UNO API (the ``--convert-to`` dispatcher is unreliable in
this environment, but UNO ``loadComponentFromURL`` + ``calculateAll`` works):
start a headless listener, load the file, recalc, store as xlsx, then read it
back with ``data_only=True``.
"""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import tempfile
import time

import openpyxl

_PORT = 2002


def _find_soffice() -> str:
    for cand in ("soffice", "libreoffice"):
        path = shutil.which(cand)
        if path:
            return path
    raise RuntimeError("LibreOffice (soffice) not found on PATH")


def _port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


class _Office:
    """Manages a headless LibreOffice UNO listener for the duration of a recalc."""

    def __init__(self, port: int = _PORT):
        self.port = port
        self.proc = None
        self.home = tempfile.mkdtemp(prefix="lo_home_")
        self.user = os.path.join(self.home, "u")

    def __enter__(self):
        soffice = _find_soffice()
        env = dict(os.environ)
        env["HOME"] = self.home
        accept = f"socket,host=127.0.0.1,port={self.port};urp;StarOffice.ServiceManager"
        self.proc = subprocess.Popen(
            [soffice, f"-env:UserInstallation=file://{self.user}",
             "--headless", "--invisible", "--norestore", "--nologo",
             "--nofirststartwizard", f"--accept={accept}"],
            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        deadline = time.time() + 60
        while time.time() < deadline:
            if _port_open(self.port):
                time.sleep(0.5)
                return self
            if self.proc.poll() is not None:
                raise RuntimeError("LibreOffice listener exited prematurely")
            time.sleep(0.4)
        raise RuntimeError("Timed out waiting for LibreOffice UNO listener")

    def __exit__(self, *exc):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        shutil.rmtree(self.home, ignore_errors=True)


def _connect(port: int):
    import uno  # provided by the system LibreOffice install

    local_ctx = uno.getComponentContext()
    resolver = local_ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local_ctx)
    last_err = None
    for _ in range(20):
        try:
            ctx = resolver.resolve(
                f"uno:socket,host=127.0.0.1,port={port};urp;StarOffice.ComponentContext")
            smgr = ctx.ServiceManager
            desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
            return desktop
        except Exception as e:  # bridge not ready yet
            last_err = e
            time.sleep(0.5)
    raise RuntimeError(f"Could not connect to LibreOffice UNO bridge: {last_err}")


def _prop(name, value):
    import uno  # noqa: F401  -- installs the com.sun.star import hook
    from com.sun.star.beans import PropertyValue

    p = PropertyValue()
    p.Name = name
    p.Value = value
    return p


def recalc_to_file(src_path: str, out_path: str | None = None) -> str:
    """Recalculate *src_path* via LibreOffice UNO; return path to the recalc'd copy."""
    import uno

    src_path = os.path.abspath(src_path)
    out_path = os.path.abspath(out_path or (os.path.splitext(src_path)[0] + ".recalc.xlsx"))
    with _Office() as office:
        desktop = _connect(office.port)
        src_url = uno.systemPathToFileUrl(src_path)
        # Specify the import filter explicitly: this install's automatic type
        # detection is unreliable, so we bypass it.
        load_props = (_prop("Hidden", True),
                      _prop("FilterName", "Calc MS Excel 2007 XML"))
        doc = desktop.loadComponentFromURL(src_url, "_blank", 0, load_props)
        if doc is None:
            raise RuntimeError(f"LibreOffice failed to load {src_path}")
        try:
            doc.calculateAll()
            out_url = uno.systemPathToFileUrl(out_path)
            doc.storeToURL(out_url, (_prop("FilterName", "Calc MS Excel 2007 XML"),))
        finally:
            doc.close(False)
    return out_path


def recalc_values(src_path: str) -> openpyxl.Workbook:
    """Return an openpyxl workbook (data_only) with LibreOffice-computed values."""
    return openpyxl.load_workbook(recalc_to_file(src_path), data_only=True)


def cell_value(wb, sheet: str, coord: str):
    return wb[sheet][coord].value
