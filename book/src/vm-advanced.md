# Advanced VM Flows: Calls, Methods & Unwinding

<div class="youarehere">📍 <strong>You are here:</strong> Part Seven · The Engine Room — 4 of 4</div>

Three flows are too intricate for the field guide and deserve full diagrams: calling a Sindlish function, dispatching a method, and how errors acquire their beautiful tracebacks.

## Flow 1 · Calling a function

```mermaid
sequenceDiagram
    participant C as CALL_FUNCTION
    participant VM
    participant NF as new BytecodeFrame
    C->>VM: pop args (reverse), expand markers
    VM->>VM: globals.lookup_record(name)
    alt SdFunction
        VM->>VM: _call_sd_function: bind params<br>(kwargs > positional > defaults)<br>type-check each binding
        VM->>NF: create frame (slots=slot_count,<br>cells from cell_names+free_specs)
        VM->>NF: fill param slots / cells
        VM->>VM: frames.append(new)
    else builtin
        VM->>VM: simple_handler.fn(args)<br>(no kwargs allowed)
    end
```

Details worth knowing (`vm.py:_call_sd_function`):

- **Binding priority**: explicit kwargs beat positionals; defaults evaluated *at definition time* ride on the `SdFunction`.
- **Result-aware binding**: an Ok parcel passed to a parameter is unwrapped before the declared type check; Ghalti passes through.
- **`*param` collects leftovers into a list, `**kw` into a dict.** Unknown kwarg names → clean `MatalabJeGhalti`.
- The caller's stack is untouched by the callee — it gets a fresh frame with its own slots.

## Flow 2 · Method dispatch

```mermaid
flowchart TD
    A["CALL_METHOD (name, n)"] --> B["pop n args → pop receiver obj"]
    B --> C{"name in ok/ghalti?"}
    C -->|yes| D["inspection path:<br>Results → their bool attr<br>raw values → success default"]
    C -->|no| E["obj.type.lookup_method(name)<br>walk MRO skill books"]
    E --> F{"found?"}
    F -->|yes| G["method(obj, args)<br>SindhiBaseError re-raised with line info;<br>others laundered"]
    F -->|no| H["NaleJeGhalti:<br>'Method X ji wazahat na milyo'"]
```

The `ok/ghalti` special case exists because Results must be inspectable *without* consuming them — `.ok` is attribute-like syntax over this opcode.

## Flow 3 · How errors get dressed

Two independent traceback sources, one renderer:

```mermaid
flowchart TD
    subgraph PATH_A["exception during execution"]
        A1["SindhiBaseError raised"] --> A2["run() catches"]
        A2 --> A3["_build_traceback<br>if error.traceback EMPTY:<br>walk live frames,<br>line_col_map[ip-1]"]
        A3 --> A4["re-raise → interpreter reports"]
    end
    subgraph PATH_B["Ghalti parcel raised later"]
        B1["parcel created<br>_binary_op_result or ghalti()"] --> B2["capture_traceback FREEZES frames now"]
        B2 --> B3["parcel travels…"]
        B3 --> B4["!! / .lazmi / strict consumption<br>ERROR_MAP rebuilds class,<br>attach frozen trace"]
    end
    A4 --> R["ErrorReporter.report → stderr"]
    B4 --> R
```

The guard in `_build_traceback` ("only if empty") is what gives Result-born errors their birthplace fidelity — the freeze-at-creation trace wins over where the error finally detonated.

## Frame lifecycle recap

Frames push on call (`frames.append`) and pop on `RETURN_VALUE`. When `instructions` run out mid-frame (main program end), the loop pops single-frame programs via `HALT` pinning ip at the end — small subtlety: `HALT` doesn't stop the machine globally, it just ends the current frame's stream.

<div class="recap">
<p>Calls = bind → fresh frame → append; builtins skip frames entirely.</p>
<p>Method dispatch = MRO walk with an ok/ghalti inspection shortcut.</p>
<p>Tracebacks: live-walk for plain exceptions, frozen capture for parcels; capture wins.</p>
</div>
