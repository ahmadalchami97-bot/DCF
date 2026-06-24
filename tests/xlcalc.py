"""
A small, faithful Excel-formula evaluator used to VERIFY the generated workbook
without depending on Excel/LibreOffice.

It loads the workbook's formula strings (via openpyxl) and evaluates them in
dependency order with memoisation and cycle detection, resolving cross-sheet
references. It implements exactly the function/operator subset the model uses
and follows Excel value semantics for that subset:

  * a blank cell is 0 in arithmetic, "" in text, and not a number
  * text used in arithmetic yields #VALUE!; division by zero yields #DIV/0!
  * IFERROR catches errors; ISNUMBER/ISBLANK/N behave as in Excel

Cross-checking its results for the Inputs subtotals against the independent
roll-forward in ``sample_data`` validates both the evaluator and the formulas.
This is a TEST tool, not part of the shipped product.
"""

from __future__ import annotations

import re

import openpyxl


# --- value model ------------------------------------------------------------
class Blank:
    _inst = None

    def __new__(cls):
        if cls._inst is None:
            cls._inst = super().__new__(cls)
        return cls._inst

    def __repr__(self):
        return "<blank>"


BLANK = Blank()


class XlError(str):
    """An Excel error value, e.g. '#DIV/0!'. Subclasses str for easy display."""


ERR_VALUE = XlError("#VALUE!")
ERR_DIV0 = XlError("#DIV/0!")
ERR_REF = XlError("#REF!")
ERR_NA = XlError("#N/A")
ERR_NUM = XlError("#NUM!")


# --- tokenizer --------------------------------------------------------------
_TOKEN_RE = re.compile(
    r"""
    (?P<WS>\s+)
  | (?P<STRING>"(?:[^"]|"")*")
  | (?P<NUMBER>(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?)
  | (?P<REF>(?:'[^']+'|[A-Za-z_][\w.]*)!\$?[A-Za-z]{1,3}\$?\d+
            |\$?[A-Za-z]{1,3}\$?\d+)
  | (?P<NAME>[A-Za-z_][\w.]*)
  | (?P<OP><=|>=|<>|[-+*/^&()<>=,:%])
    """,
    re.VERBOSE,
)


def _tokenize(s: str):
    pos, out = 0, []
    while pos < len(s):
        m = _TOKEN_RE.match(s, pos)
        if not m:
            raise ValueError(f"cannot tokenize at {pos}: {s[pos:pos+20]!r} in {s!r}")
        pos = m.end()
        kind = m.lastgroup
        if kind == "WS":
            continue
        out.append((kind, m.group()))
    out.append(("EOF", ""))
    return out


# --- parser (recursive descent) --------------------------------------------
# AST nodes are tuples; see eval for shapes.
class _Parser:
    def __init__(self, tokens):
        self.toks = tokens
        self.i = 0

    def peek(self):
        return self.toks[self.i]

    def next(self):
        t = self.toks[self.i]
        self.i += 1
        return t

    def expect(self, val):
        k, v = self.next()
        if v != val:
            raise ValueError(f"expected {val!r} got {v!r}")

    # precedence climbing
    def parse(self):
        node = self.comparison()
        if self.peek()[0] != "EOF":
            raise ValueError(f"trailing tokens: {self.toks[self.i:]}")
        return node

    def comparison(self):
        node = self.concat()
        while self.peek()[1] in ("=", "<>", "<", ">", "<=", ">="):
            op = self.next()[1]
            node = ("bin", op, node, self.concat())
        return node

    def concat(self):
        node = self.addsub()
        while self.peek()[1] == "&":
            self.next()
            node = ("bin", "&", node, self.addsub())
        return node

    def addsub(self):
        node = self.muldiv()
        while self.peek()[1] in ("+", "-"):
            op = self.next()[1]
            node = ("bin", op, node, self.muldiv())
        return node

    def muldiv(self):
        node = self.power()
        while self.peek()[1] in ("*", "/"):
            op = self.next()[1]
            node = ("bin", op, node, self.power())
        return node

    def power(self):
        node = self.unary()
        if self.peek()[1] == "^":
            self.next()
            return ("bin", "^", node, self.power())  # right assoc
        return node

    def unary(self):
        if self.peek()[1] == "-":
            self.next()
            return ("unary", "-", self.unary())
        if self.peek()[1] == "+":
            self.next()
            return self.unary()
        return self.postfix()

    def postfix(self):
        node = self.primary()
        if self.peek()[1] == "%":
            self.next()
            node = ("unary", "%", node)
        return node

    def primary(self):
        k, v = self.peek()
        if v == "(":
            self.next()
            node = self.comparison()
            self.expect(")")
            return node
        if k == "NUMBER":
            self.next()
            return ("num", float(v))
        if k == "STRING":
            self.next()
            return ("str", v[1:-1].replace('""', '"'))
        if k == "REF":
            self.next()
            if self.peek()[1] == ":":
                self.next()
                k2, v2 = self.next()
                return ("range", v, v2)
            return ("ref", v)
        if k == "NAME":
            name = self.next()[1]
            if self.peek()[1] == "(":
                self.next()
                args = self.arglist()
                self.expect(")")
                return ("func", name.upper(), args)
            up = name.upper()
            if up == "TRUE":
                return ("bool", True)
            if up == "FALSE":
                return ("bool", False)
            return ("name", up)  # a defined name (resolved at eval time)
        raise ValueError(f"unexpected token {v!r}")

    def arglist(self):
        args = []
        if self.peek()[1] == ")":
            return args
        args.append(self.comparison())
        while self.peek()[1] == ",":
            self.next()
            # allow empty arg (e.g. IF(a,b,)) -> represent as None
            if self.peek()[1] in (",", ")"):
                args.append(("blank",))
            else:
                args.append(self.comparison())
        return args


def _parse(formula: str):
    return _Parser(_tokenize(formula)).parse()


# --- evaluator --------------------------------------------------------------
def _split_ref(ref: str):
    """('Sheet'!$C$12 | C12) -> (sheet_or_None, 'C12')."""
    sheet = None
    if "!" in ref:
        sp, ref = ref.split("!", 1)
        sheet = sp[1:-1] if sp.startswith("'") else sp
    coord = ref.replace("$", "").upper()
    return sheet, coord


_COL_RE = re.compile(r"([A-Z]+)(\d+)")


def _coord_parts(coord):
    m = _COL_RE.match(coord)
    return m.group(1), int(m.group(2))


def _col_to_idx(col):
    idx = 0
    for ch in col:
        idx = idx * 26 + (ord(ch) - 64)
    return idx


class Evaluator:
    def __init__(self, path: str):
        self.wb = openpyxl.load_workbook(path, data_only=False)
        self._memo: dict[tuple[str, str], object] = {}
        self._stack: list[tuple[str, str]] = []
        self.cycles: list[tuple[str, str]] = []
        # workbook-level defined names (single cells or ranges) for formula use
        self.names: dict[str, tuple[str, str]] = {}
        try:
            for nm, dn in self.wb.defined_names.items():
                try:
                    dest = list(dn.destinations)
                except Exception:
                    dest = []
                if dest:
                    sheet, coord = dest[0]
                    self.names[nm.upper()] = (sheet, coord)
        except Exception:
            pass

    # public API
    def value(self, sheet: str, coord: str):
        coord = coord.replace("$", "").upper()
        key = (sheet, coord)
        if key in self._memo:
            return self._memo[key]
        if key in self._stack:
            self.cycles.append(key)
            return ERR_REF  # circular reference
        self._stack.append(key)
        try:
            cell = self.wb[sheet][coord]
            raw = cell.value
            if raw is None:
                val = BLANK
            elif isinstance(raw, str) and raw.startswith("="):
                val = self._eval(_parse(raw[1:]), sheet)
            elif isinstance(raw, str):
                val = raw
            elif isinstance(raw, bool):
                val = raw
            else:
                val = float(raw)
            self._memo[key] = val
            return val
        finally:
            self._stack.pop()

    # AST evaluation
    def _eval(self, node, sheet):
        tag = node[0]
        if tag == "num":
            return node[1]
        if tag == "str":
            return node[1]
        if tag == "bool":
            return node[1]
        if tag == "blank":
            return BLANK
        if tag == "name":
            key = node[1]
            if key not in self.names:
                raise ValueError(f"unknown defined name {key!r}")
            s, coord = self.names[key]
            coord = coord.replace("$", "")
            if ":" in coord:
                a, b = coord.split(":")
                return self._range(f"'{s}'!{a}", b, s)
            return self.value(s, coord.upper())
        if tag == "ref":
            s, c = _split_ref(node[1])
            return self.value(s or sheet, c)
        if tag == "range":
            return self._range(node[1], node[2], sheet)
        if tag == "unary":
            return self._unary(node[1], self._eval(node[2], sheet))
        if tag == "bin":
            return self._bin(node[1], node[2], node[3], sheet)
        if tag == "func":
            return self._func(node[1], node[2], sheet)
        raise ValueError(f"bad node {node!r}")

    def _range(self, a, b, sheet):
        sa, ca = _split_ref(a)
        sb, cb = _split_ref(b)
        s = sa or sheet
        col_a, row_a = _coord_parts(ca)
        col_b, row_b = _coord_parts(cb)
        ci0, ci1 = sorted((_col_to_idx(col_a), _col_to_idx(col_b)))
        r0, r1 = sorted((row_a, row_b))
        vals = []
        for ci in range(ci0, ci1 + 1):
            col = openpyxl.utils.get_column_letter(ci)
            for r in range(r0, r1 + 1):
                vals.append(self.value(s, f"{col}{r}"))
        return ("array", vals)

    # operators
    def _unary(self, op, v):
        if isinstance(v, XlError):
            return v
        if op == "-":
            n = _to_num(v)
            return n if isinstance(n, XlError) else -n
        if op == "%":
            n = _to_num(v)
            return n if isinstance(n, XlError) else n / 100.0
        raise ValueError(op)

    def _bin(self, op, ln, rn, sheet):
        if op in ("=", "<>", "<", ">", "<=", ">="):
            return _compare(op, self._eval(ln, sheet), self._eval(rn, sheet))
        lv = self._eval(ln, sheet)
        rv = self._eval(rn, sheet)
        if op == "&":
            if isinstance(lv, XlError):
                return lv
            if isinstance(rv, XlError):
                return rv
            return _to_text(lv) + _to_text(rv)
        a = _to_num(lv)
        b = _to_num(rv)
        if isinstance(a, XlError):
            return a
        if isinstance(b, XlError):
            return b
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "/":
            return ERR_DIV0 if b == 0 else a / b
        if op == "^":
            try:
                return float(a) ** float(b)
            except (ValueError, OverflowError):
                return ERR_NUM
        raise ValueError(op)

    # functions
    def _func(self, name, args, sheet):
        if name == "IF":
            cond = _to_bool(self._eval(args[0], sheet))
            if isinstance(cond, XlError):
                return cond
            if cond:
                return self._eval(args[1], sheet)
            if len(args) >= 3:
                return self._eval(args[2], sheet)
            return False
        if name == "IFERROR":
            v = self._eval(args[0], sheet)
            return self._eval(args[1], sheet) if isinstance(v, XlError) else v
        if name == "AND":
            return self._andor(args, sheet, all)
        if name == "OR":
            return self._andor(args, sheet, any)
        if name == "NOT":
            b = _to_bool(self._eval(args[0], sheet))
            return b if isinstance(b, XlError) else (not b)
        if name == "ISNUMBER":
            v = self._eval(args[0], sheet)
            return isinstance(v, float)
        if name == "ISBLANK":
            v = self._eval(args[0], sheet)
            return v is BLANK
        if name == "ISTEXT":
            v = self._eval(args[0], sheet)
            return isinstance(v, str) and not isinstance(v, XlError)
        if name == "COUNTIF":
            rng = self._eval(args[0], sheet)
            crit = self._eval(args[1], sheet)
            vals = rng[1] if (isinstance(rng, tuple) and rng[0] == "array") else [rng]
            cnt = 0
            for x in vals:
                if isinstance(crit, str) and isinstance(x, str):
                    if x.upper() == crit.upper():
                        cnt += 1
                elif isinstance(crit, float) and isinstance(x, float):
                    if x == crit:
                        cnt += 1
            return float(cnt)
        if name == "N":
            v = self._eval(args[0], sheet)
            if isinstance(v, XlError):
                return v
            if isinstance(v, bool):
                return 1.0 if v else 0.0
            if isinstance(v, float):
                return v
            return 0.0
        if name == "CHOOSE":
            idx = _to_num(self._eval(args[0], sheet))
            if isinstance(idx, XlError):
                return idx
            i = int(idx)
            if i < 1 or i > len(args) - 1:
                return ERR_VALUE
            return self._eval(args[i], sheet)
        if name in ("SUM", "AVERAGE", "MAX", "MIN", "COUNT"):
            nums = self._collect_numbers(args, sheet)
            if isinstance(nums, XlError):
                return nums
            if name == "SUM":
                return float(sum(nums))
            if name == "COUNT":
                return float(len(nums))
            if not nums:
                return ERR_DIV0 if name == "AVERAGE" else 0.0
            if name == "AVERAGE":
                return sum(nums) / len(nums)
            if name == "MAX":
                return float(max(nums))
            if name == "MIN":
                return float(min(nums))
        if name == "MEDIAN":
            nums = self._collect_numbers(args, sheet)
            if isinstance(nums, XlError):
                return nums
            if not nums:
                return ERR_NUM
            s = sorted(nums)
            mid = len(s) // 2
            return s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2
        if name == "RANK":
            num = _to_num(self._eval(args[0], sheet))
            rng = self._eval(args[1], sheet)
            vals = [x for x in (rng[1] if (isinstance(rng, tuple) and rng[0] == "array") else [rng])
                    if isinstance(x, float)]
            order = 0.0 if len(args) < 3 else _to_num(self._eval(args[2], sheet))
            if isinstance(num, XlError):
                return num
            if order and order != 0:
                return float(1 + sum(1 for v in vals if v < num))
            return float(1 + sum(1 for v in vals if v > num))
        if name == "ABS":
            n = _to_num(self._eval(args[0], sheet))
            return n if isinstance(n, XlError) else abs(n)
        if name in ("TODAY", "NOW"):
            return 46000.0  # a fixed date serial; value irrelevant to verification
        if name == "SIGN":
            n = _to_num(self._eval(args[0], sheet))
            if isinstance(n, XlError):
                return n
            return float((n > 0) - (n < 0))
        if name == "REPT":
            txt = self._eval(args[0], sheet)
            cnt = _to_num(self._eval(args[1], sheet))
            if isinstance(cnt, XlError):
                return cnt
            txt = "" if txt is BLANK else _to_text(txt)
            return txt * max(0, int(cnt))
        if name == "ROUND":
            n = _to_num(self._eval(args[0], sheet))
            d = _to_num(self._eval(args[1], sheet))
            if isinstance(n, XlError):
                return n
            if isinstance(d, XlError):
                return d
            return float(round(n, int(d)))
        if name == "MAXA":
            return self._func("MAX", args, sheet)
        if name == "TEXT":
            raw = self._eval(args[0], sheet)
            if isinstance(raw, XlError):
                return raw
            if isinstance(raw, str):
                return raw  # Excel TEXT() passes a text value through unchanged
            val = _to_num(raw)
            if isinstance(val, XlError):
                return val
            fmt = self._eval(args[1], sheet)
            return _format_number(val, fmt if isinstance(fmt, str) else _to_text(fmt))
        if name == "SQRT":
            n = _to_num(self._eval(args[0], sheet))
            if isinstance(n, XlError):
                return n
            if n < 0:
                return ERR_NUM
            return n ** 0.5
        if name == "SUMPRODUCT":
            arrays = []
            for a in args:
                v = self._eval(a, sheet)
                arrays.append(v[1] if (isinstance(v, tuple) and v[0] == "array") else [v])
            if not arrays:
                return 0.0
            length = max(len(a) for a in arrays)
            total = 0.0
            for idx in range(length):
                prod = 1.0
                for arr in arrays:
                    x = _to_num(arr[idx]) if idx < len(arr) else 0.0
                    if isinstance(x, XlError):
                        return x
                    prod *= x
                total += prod
            return total
        if name == "INDEX":
            rng = self._eval(args[0], sheet)
            vals = rng[1] if (isinstance(rng, tuple) and rng[0] == "array") else [rng]
            k = _to_num(self._eval(args[1], sheet))
            if isinstance(k, XlError):
                return k
            i = int(k)
            if i < 1 or i > len(vals):
                return ERR_REF
            return vals[i - 1]
        if name == "MATCH":
            target = self._eval(args[0], sheet)
            rng = self._eval(args[1], sheet)
            vals = rng[1] if (isinstance(rng, tuple) and rng[0] == "array") else [rng]
            mtype = 1.0 if len(args) < 3 else _to_num(self._eval(args[2], sheet))
            if isinstance(mtype, XlError):
                return mtype
            if mtype == 0:
                for i, x in enumerate(vals):
                    if not isinstance(x, XlError) and _compare("=", x, target) is True:
                        return float(i + 1)
                return ERR_NA
            tnum = _to_num(target)
            best = None
            for i, x in enumerate(vals):
                xn = _to_num(x)
                if isinstance(xn, XlError):
                    continue
                if mtype > 0 and xn <= tnum:
                    best = i + 1
                elif mtype < 0 and xn >= tnum:
                    best = i + 1
            return float(best) if best else ERR_NA
        if name == "ROUND":  # (defensive duplicate; handled above)
            pass
        raise ValueError(f"unsupported function {name}")

    def _andor(self, args, sheet, agg):
        bools = []
        for a in args:
            v = self._eval(a, sheet)
            if isinstance(v, tuple) and v[0] == "array":
                for x in v[1]:
                    b = _to_bool(x)
                    if isinstance(b, XlError):
                        return b
                    if b is not None:
                        bools.append(b)
            else:
                b = _to_bool(v)
                if isinstance(b, XlError):
                    return b
                if b is not None:
                    bools.append(b)
        return agg(bools) if bools else ERR_VALUE

    def _collect_numbers(self, args, sheet):
        out = []
        for a in args:
            v = self._eval(a, sheet)
            if isinstance(v, tuple) and v[0] == "array":
                for x in v[1]:
                    if isinstance(x, XlError):
                        return x
                    if isinstance(x, float):
                        out.append(x)
                    elif isinstance(x, bool):
                        pass  # bools in ranges ignored by SUM
            else:
                if isinstance(v, XlError):
                    return v
                if isinstance(v, bool):
                    out.append(1.0 if v else 0.0)
                elif isinstance(v, float):
                    out.append(v)
                elif v is BLANK:
                    pass
                elif isinstance(v, str):
                    # a numeric string is summed; pure text ignored
                    try:
                        out.append(float(v))
                    except ValueError:
                        pass
        return out


# --- value coercions (Excel semantics) -------------------------------------
def _to_num(v):
    if isinstance(v, XlError):
        return v
    if v is BLANK:
        return 0.0
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    if isinstance(v, float):
        return v
    if isinstance(v, int):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v)
        except ValueError:
            return ERR_VALUE
    if isinstance(v, tuple) and v[0] == "array":
        return _to_num(v[1][0]) if v[1] else ERR_VALUE
    return ERR_VALUE


def _to_bool(v):
    if isinstance(v, XlError):
        return v
    if isinstance(v, bool):
        return v
    if v is BLANK:
        return False
    if isinstance(v, float):
        return v != 0
    if isinstance(v, str):
        if v.upper() == "TRUE":
            return True
        if v.upper() == "FALSE":
            return False
        return ERR_VALUE
    return ERR_VALUE


def _to_text(v):
    if v is BLANK:
        return ""
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, float):
        if v == int(v):
            return str(int(v))
        return repr(v)
    return str(v)


def _compare(op, lv, rv):
    if isinstance(lv, XlError):
        return lv
    if isinstance(rv, XlError):
        return rv
    # numeric vs numeric (blank treated as 0)
    lnum = isinstance(lv, (float, bool)) or lv is BLANK
    rnum = isinstance(rv, (float, bool)) or rv is BLANK
    if lnum and rnum:
        a, b = _to_num(lv), _to_num(rv)
    elif isinstance(lv, str) and isinstance(rv, str):
        a, b = lv.upper(), rv.upper()
    elif isinstance(lv, str) and (rnum):
        # Excel: any text > any number
        a, b = 1, 0
        if op == "=":
            return False
        if op == "<>":
            return True
    elif (lnum) and isinstance(rv, str):
        a, b = 0, 1
        if op == "=":
            return False
        if op == "<>":
            return True
    else:
        a, b = _to_text(lv), _to_text(rv)
    if op == "=":
        return a == b
    if op == "<>":
        return a != b
    if op == "<":
        return a < b
    if op == ">":
        return a > b
    if op == "<=":
        return a <= b
    if op == ">=":
        return a >= b


def _format_number(num: float, fmt: str) -> str:
    """Minimal Excel TEXT() number formatting for the codes the model uses."""
    fmt = fmt.split(";", 1)[0]  # use the positive section to derive decimals
    pct = "%" in fmt
    body = fmt.replace("%", "").replace("+", "")
    if pct:
        num = num * 100
    if "." in body:
        dec = body.split(".", 1)[1]
        ndec = sum(1 for ch in dec if ch in "0#")
    else:
        ndec = 0
    thousands = "," in body.split(".")[0]
    s = f"{num:,.{ndec}f}" if thousands else f"{num:.{ndec}f}"
    return s + "%" if pct else s


def evaluate_workbook(path: str) -> Evaluator:
    """Build an evaluator and pre-compute every formula cell (catches errors/cycles)."""
    ev = Evaluator(path)
    for ws in ev.wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    ev.value(ws.title, cell.coordinate)
    return ev
