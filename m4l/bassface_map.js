// Bass Face v1.3 - auto-wire face channels to macros by NAME.
// On device-ready (live.thisdevice) or Rescan, walk every device on this
// track and find parameters named exactly like our targets. Emits:
//   <slot 0-3> <param id> <min> <max>
// Name-resolution runs fresh every load, so it survives set reloads,
// track moves, and Live's session-only ids.

autowatch = 0;

var TARGETS = ["BROW OTT", "MOUTH DRIVE", "SQUINT PHASE", "FACE FILTH"];

function bang() {
    var found = 0;
    var parent = new LiveAPI("this_device canonical_parent");
    if (!parent.id || parent.id === 0) {
        post("bassface: no parent chain found\n");
        return;
    }
    var ndev = parent.getcount("devices");
    for (var d = 0; d < ndev; d++) {
        scan_device("this_device canonical_parent devices " + d);
    }
    // also scan inside rack chains one level deep
    for (var d2 = 0; d2 < ndev; d2++) {
        var dev = new LiveAPI("this_device canonical_parent devices " + d2);
        if (dev.get("can_have_chains") == 1) {
            var nch = dev.getcount("chains");
            for (var c = 0; c < nch; c++) {
                var chain = new LiveAPI(dev.path.replace(/"/g, "") +
                                        " chains " + c);
                var ncd = chain.getcount("devices");
                for (var cd = 0; cd < ncd; cd++) {
                    scan_device(chain.path.replace(/"/g, "") +
                                " devices " + cd);
                }
            }
        }
    }

    function scan_device(path) {
        var np = 0;
        var probe = new LiveAPI(path);
        if (!probe.id || probe.id === 0) return;
        try { np = probe.getcount("parameters"); } catch (e) { return; }
        for (var p = 0; p < np; p++) {
            var par = new LiveAPI(path + " parameters " + p);
            var nm = String(par.get("name"));
            var ix = TARGETS.indexOf(nm);
            if (ix >= 0) {
                outlet(0, ix, parseInt(par.id),
                       parseFloat(par.get("min")),
                       parseFloat(par.get("max")));
                post("bassface: " + nm + " -> id " + par.id + "\n");
                found++;
            }
        }
    }
    post("bassface: wired " + found + " target(s)\n");
}
