import os, time, collections, tkinter as tk
import importlib.machinery, importlib.util
l = importlib.machinery.SourceFileLoader("p", "app/prompt.pyw"); sp = importlib.util.spec_from_loader("p", l)
m = importlib.util.module_from_spec(sp); l.exec_module(m)
m.find_claude_app = lambda: None
m.REGISTRY_FILE = m.Path("/tmp/h/none.json")
v = os.environ.get("VARIANT", "")
if "nowrap" in v:
    m.App.wrap_to = lambda self, label, container, minus=0: label.configure(wraplength=300)
if "noflow" in v:
    def flow(self, frame, widgets, gap=None):
        for w in widgets: w.pack(side="left")
    m.App.flow = flow
if "noscrollcfg" in v:
    orig = m.App.make_scroll
    def make_scroll(self, parent):
        c, inner = orig(self, parent)
        c.unbind("<Configure>"); inner.unbind("<Configure>")
        return c, inner
    m.App.make_scroll = make_scroll
if "nowidth" in v or "noregion" in v:
    orig2 = m.App.make_scroll
    def make_scroll2(self, parent):
        c, inner = orig2(self, parent)
        if "nowidth" in v: c.unbind("<Configure>")
        if "noregion" in v: inner.unbind("<Configure>")
        return c, inner
    m.App.make_scroll = make_scroll2
    if "noregion" in v:
        m.App.restore_scroll = lambda self, canvas, pos: None
if "fewrows" in v:
    m.scan_all = (lambda f: (lambda: f()[:15]))(m.scan_all)
cnt = collections.Counter()
o = tk.CallWrapper.__call__
def w(self, *a):
    f = self.func; c = getattr(f, "__code__", None)
    cnt[f"{getattr(f,'__qualname__',f)}:{c.co_firstlineno if c else ''}"] += 1
    return o(self, *a)
tk.CallWrapper.__call__ = w
root = tk.Tk()
app = m.App(root)
t = time.time(); root.update(); dt = time.time() - t
print(f"{v or 'baseline':28s} first draw {dt:6.2f}s  callbacks {sum(cnt.values())}  rows {len(app.items)}", flush=True)
for k, n in cnt.most_common(4): print("      ", n, k)
root.destroy()
