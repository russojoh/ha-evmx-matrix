# EVMX HDMI Matrix for Home Assistant

Control a Vanco **Evolution EVMX**-family HDMI matrix (EVMX4K44, EVMX4K88 and the
other units that share the same ASCII control firmware) from Home Assistant.

Each output becomes a `select` entity whose options are the matrix inputs, so
`select.taproom_matrix_output_1` set to `3` means "output 1 shows input 3".
The current value is read back from the matrix, so changes made with the front
panel, the IR remote or another controller appear in Home Assistant within 15
seconds.

## How it talks to the matrix

These units listen on **TCP 4001** and speak plain ASCII, one command per line,
CR+LF terminated. There is no authentication on that port.

| Purpose | Command | Reply |
|---|---|---|
| Model | `/*Type;` | `EVMX4K44` |
| Firmware | `/^Version;` | `V1.0.2` |
| Routing table | `%9975.` | `Out 01 02 03 04` / `In 04 04 04 04` |
| Route input 4 to output 1 | `4B1.` | `AV:04->01` |
| Power state | `%9962.` | `PWON` |

The integration opens a short-lived connection per operation rather than holding
a socket open, because these matrices drop idle connections and refuse new ones
for about a second after a command.

The web UI on port 80 is *not* used: it is a separate, older CGI interface
(`MMX32_*.cgi`) that reports stale routing, and it is unauthenticated by default
which is worth knowing on a shared network.

## Install

1. HACS → Integrations → ⋮ → **Custom repositories**
2. Add `https://github.com/russojoh/ha-evmx-matrix`, category **Integration**
3. Install "EVMX HDMI Matrix", then restart Home Assistant
4. Settings → Devices & Services → **Add Integration** → EVMX HDMI Matrix
5. Host: the matrix IP (e.g. `192.168.0.178`), control port `4001`,
   inputs and outputs as fitted

## Entities

For a 4×4 unit:

- `select.*_output_1` … `select.*_output_4` — options `1`–`4`
- One device carrying model and firmware as reported by the unit

## Limitations

- Routing only. EDID, HDCP, per-output power and presets are not exposed yet.
- The matrix has no read-back for "which input is *actually* connected"; use
  the front panel display or `%9971.` over telnet for that.
- Tested against an EVMX4K44 running firmware V1.0.2 (GUI V1.0.0, hardware
  V1.0.2). Other models in the family should work; open an issue with your
  `/*Type;` and `/^Version;` replies if something misbehaves.

## Licence

MIT
