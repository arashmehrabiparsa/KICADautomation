import skip
import sexpdata
import os
import shutil
from datetime import datetime

# Load the schematic
sch_path = "C:/Users/Guest2/Personal/Github/CNT/KICAD/nowiretraces.kicad_sch"
sch = skip.Schematic(sch_path)

print("\nDebug: Available methods and attributes of the sch object:")
print(dir(sch))

# Check what type of object wire expects
if hasattr(sch, 'wire'):
    print("\nDebug: Available methods and attributes of a wire object:")
    print(dir(sch.wire))
    if len(sch.wire) > 0:
        print("\nDebug: Structure of an existing wire:")
        print(vars(sch.wire[0]))

print("here")

# Locate the Teensy component with reference "U5" and value "Teensy4.1"
teensy_component = next((s for s in sch.symbol if s.property.Reference.value == "U5" and "Teensy4.1" in s.property.Value.value), None)

if teensy_component:
    print("\n")
    print(f"Teensy component found: {teensy_component.property.Reference.value} - {teensy_component.property.Value.value}")
else:
    exit()  # Stop execution if Teensy is not found

# Define ADC and PWM Pins based on schematic
ADC_Pins = {
    16: "24_A10_TX6_SCL2",      # A10 F
    17: "25_A11_RX6_SDA2",      # A11 F
    18: "26_A12_MOSI1",         # A12 F
    19: "27_A13_SCK1",          # A13 F
    30: "38_CS1_IN1",           # A16 F
    31: "39_MISO1_OUT1A",       # A17 F
    32: "40_A16",               # A14 F
    33: "41_A17",               # A15 F
    36: "14_A0_TX3_SPDIF_OUT",  # A0 F
    37: "15_A1_RX3_SPDIF_IN",   # A1 F
    38: "16_A2_RX4_SCL1",       # A2 F
    39: "17_A3_TX4_SDA1",       # A3 F
    40: "18_A4_SDA",            # A4 F
    41: "19_A5_SCL",            # A5 F
    42: "20_A6_TX5_LRCLK1",     # A6 F
    43: "21_A7_RX5_BCLK1",      # A7 F
    44: "22_A8_CTX1",           # A8 F
    45: "23_A9_CRX1_MCLK1",     # A9 F
}

PWM_Pins = {
    2: "0_RX1_CRX2_CS1",        # 0 F
    3: "1_TX1_CTX2_MISO1",      # 1 F
    4: "2_OUT2",                # 2 F
    5: "3_LRCLK2",              # 3 F
    6: "4_BCLK2",               # 4 F
    7: "5_IN2",                 # 5 F
    8: "6_OUT1D",               # 6 F
    9: "7_RX2_OUT1A",           # 7 F
    10: "8_TX2_IN1",            # 10 F
    11: "9_OUT1C",              # 11  F
    12: "10_CS_MQSR",
    13: "11_MOSI_CTX1",
    20: "28_RX7",
    21: "29_TX7",
    25: "33_MCLK2",             # 33 F
    28: "36_CS",                # 28  F
    29: "37_CS",                # 29 F
    35: "13_SCK_LED",           # 13 F
}

# Locate Op-Amp Negative Inputs and Outputs
opamp_neg_pins = {}
opamp_outputs = {}

print("\nDebug: Listing all OP-AMP pins with location data")
print("\n")
for sym in sch.symbol:
    ref = sym.property.Reference.value  # Access the correct reference property
    val = sym.property.Value.value.lower()  # Convert to lowercase for consistency

    # Check for OpAmp types
    if "opamp" in val or "lm358" in val or "mcp6004" in val or "amplifier" in val or "tl072" in val:
        
        # Initialize storage for pins
        pin_types = {"-": None, "+": None, "~": None}
        print(f"DEBUG: ref: {ref} for op-amp {val}")  # Debugging the ref value

        # Debugging: Print pin name and location
        for pin in sym.pin:
            print(f"  Pin Name: {pin.name}, Location: {pin.location.value}")  # Debugging

            # Check for the negative pin
            if "neg" in pin.name.lower() or "-" in pin.name:  
                pin_types["-"] = pin.location.value
            # Check for positive pin
            elif "+" in pin.name:
                pin_types["+"] = pin.location.value
            # Check for output pin
            elif "~" in pin.name.lower():
                pin_types["~"] = pin.location.value

        # Only add if all three required pins exist
        if all(pin_types.values()):
            if ref not in opamp_neg_pins:
                opamp_neg_pins[ref] = []
            opamp_neg_pins[ref].append(pin_types["-"])  # Store only the negative pin
            print(f"DEBUG: Found OpAmp negative input {ref} ({val}) at {pin_types['-']}")  # Debugging

            # For output pins
            if pin_types["~"]:  # Check if output pin is defined
                # Store only the negative pin
                if ref not in opamp_outputs:
                    opamp_outputs[ref] = []
                opamp_outputs[ref].append(pin_types["~"])

                print(f"DEBUG: Found OpAmp Output {ref} ({val}) at {pin_types['~']}")  # Debugging

# Find some op-amps which are quad or a single chip op-amp
print("\n")
print("DEBUG: Final opamp_neg_pins mapping:")
for ref, locs in opamp_neg_pins.items():
    print(f"  {ref}: {locs}")

print("\n")
print("DEBUG: Final opamp_outputs mapping:")
for ref, locs in opamp_outputs.items():
    print(f"  {ref}: {locs}")
print("End of Property and Pin List")

teensy_pins = {}  # Initialize dictionary

print("\nDebug: Listing all Teensy pins with location data:\n")

for pin in teensy_component.pin:
    pin_number = int(pin.number)  # Ensure it matches dictionary keys
    pin_name = pin.name
    pin_location = pin.location.value

    print(f"Checking Teensy Pin: {pin_number}, Name: {pin_name}, Location: {pin_location}")

    # Store pin data in dictionary
    teensy_pins[pin_number] = {
        "Pin Name": pin_name,
        "Location": pin_location
    }

# Now iterate over `teensy_pins` to match with ADC/PWM dictionaries
for pin_number in list(teensy_pins.keys()):  # Use list() to avoid runtime modification issues
    if pin_number in ADC_Pins:
        teensy_pins[pin_number]["Type"] = "ADC"
        teensy_pins[pin_number]["Description"] = ADC_Pins[pin_number]
    elif pin_number in PWM_Pins:
        teensy_pins[pin_number]["Type"] = "PWM"
        teensy_pins[pin_number]["Description"] = PWM_Pins[pin_number]
    
# Debug output
print("\nMatched Teensy Pins in kicad_sch environment with ADC_pins/PWM_pins dicitonary values and writen in teensy_pins{}:")
for pin_num, pin_info in teensy_pins.items():
    pin_name = pin_info["Pin Name"]

    # Check if the pin name exists in ADC_Pins or PWM_Pins values
    if pin_name in ADC_Pins.values() or pin_name in PWM_Pins.values():
        print(f"Pin Number: {pin_num}, Type: {pin_info.get('Type', 'N/A')}, Pin Name: {pin_info['Pin Name']}, Description: {pin_info.get('Description', 'N/A')}, Location: {pin_info['Location']}")

# Print all available keys and their descriptions
print("Keys in teensy_pins:")
for key in teensy_pins.keys():
    print(f"'{key}'")

print("\nKeys in PWM_pins:")
for key in PWM_Pins.keys():
    print(f"'{key}'")

# Reverse the PWM_Pins dictionary to get a pin function -> pin number mapping
PWM_function_to_number = {v: str(k) for k, v in PWM_Pins.items()}

# Printing the reverse map
print("\nKeys in PWM_pins (Functions -> Numbers):")
for function, number in PWM_function_to_number.items():
    print(f"'{function}' -> '{number}'")

def wire_components(sch, start_loc, end_loc, description=""):
    """
    Creates a wire in the schematic connecting two points
    """
    print(f"Wiring {description}: {start_loc} -> {end_loc}")
    
    try:
        # Extract coordinates from location tuples - handle potential 3D coordinates
        if len(start_loc) >= 3:
            start_x, start_y = float(start_loc[0]), float(start_loc[1])
        else:
            start_x, start_y = float(start_loc[0]), float(start_loc[1])
            
        if len(end_loc) >= 3:
            end_x, end_y = float(end_loc[0]), float(end_loc[1])
        else:
            end_x, end_y = float(end_loc[0]), float(end_loc[1])
        
        # Create a new wire using the wire.new() method
        new_wire = sch.wire.new()
        
        # Debug: Print the type and attributes of the new wire
        print(f"New wire type: {type(new_wire)}")
        print(f"New wire attributes: {dir(new_wire)}")
        
        # Attempt to set points using different methods
        try:
            # Method 1: Direct pts.xy manipulation
            new_wire.pts.xy[0].value = [start_x, start_y]
            new_wire.pts.xy[1].value = [end_x, end_y]
        except Exception as e:
            print(f"Error setting pts.xy: {e}")
        
        try:
            # Method 2: start_at and end_at if available
            if hasattr(new_wire, 'start_at'):
                new_wire.start_at([start_x, start_y])
            if hasattr(new_wire, 'end_at'):
                new_wire.end_at([end_x, end_y])
        except Exception as e:
            print(f"Error using start_at/end_at: {e}")
        
        # Add the wire to the schematic
        sch.wire.append(new_wire)
        
        print(f"Wire added: {new_wire}")
        print("Successfully added wire")
        return True
    
    except Exception as e:
        print(f"Error creating wire: {e}")
        import traceback
        traceback.print_exc()
        return False

def connect_controlled_wiring(sch, teensy_pins, opamp_neg_pins):
    """
    Connect PWM pins to op-amp inputs, ensuring each negative input
    gets exactly one PWM connection
    """
    connection_count = 0
    
    # Get all available PWM pins
    pwm_pin_numbers = sorted([pin for pin in teensy_pins.keys() if pin in PWM_Pins])
    
    # Create a flat list of all negative pins with their op-amp references
    all_neg_pins = []
    for opamp_ref, neg_locs in opamp_neg_pins.items():
        for neg_loc in neg_locs:
            all_neg_pins.append((opamp_ref, neg_loc))
    
    # Create connections until we run out of PWM pins or negative pins
    connections = []
    for i, (opamp_ref, neg_loc) in enumerate(all_neg_pins):
        if i >= len(pwm_pin_numbers):
            break
            
        pwm_pin = pwm_pin_numbers[i]
        pwm_loc = teensy_pins[pwm_pin]["Location"]
        
        connections.append({
            "pwm_pin": pwm_pin,
            "pwm_func": PWM_Pins[pwm_pin],
            "pwm_loc": pwm_loc,
            "opamp": opamp_ref,
            "neg_loc": neg_loc
        })
    
    # Now create the wires based on our connections
    for conn in connections:
        success = wire_components(
            sch,
            conn["pwm_loc"],
            conn["neg_loc"],
            f"PWM {conn['pwm_pin']} ({conn['pwm_func']}) to OpAmp {conn['opamp']}"
        )
        
        if success:
            connection_count += 1
    
    print(f"Created {connection_count} controlled connections")
    return connection_count

# Use the controlled wiring approach
connection_count = connect_controlled_wiring(sch, teensy_pins, opamp_neg_pins)
# After adding all the wires
print(f"Attempting to save {connection_count} new connections...")

# Force the schematic to recognize it's been modified
if hasattr(sch, '_modified'):
    sch._modified = True

# Some libraries have a "dirty" flag
if hasattr(sch, 'dirty'):
    sch.dirty = True

# Try to flush any pending changes
if hasattr(sch, 'flush'):
    sch.flush()

# Create a backup
output_path = sch_path
backup_path = output_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
if os.path.exists(output_path):
    shutil.copy2(output_path, backup_path)
    print(f"Created backup at {backup_path}")

# Try direct save approach
try:
    # Try to force overwrite mode
    sch.overwrite = True
    
    # Write the modified schematic to a new file
    new_file_path = output_path + ".new"
    sch.write(new_file_path)
    
    # Verify the new file exists and has content
    if os.path.exists(new_file_path) and os.path.getsize(new_file_path) > 0:
        # Replace the original file with the new one
        if os.path.exists(output_path):
            os.remove(output_path)
        os.rename(new_file_path, output_path)
        print(f"Schematic saved successfully to {output_path} with {connection_count} new connections.")
        
        # Verify
        file_stats = os.stat(output_path)
        print(f"File size: {file_stats.st_size} bytes, Modified: {datetime.fromtimestamp(file_stats.st_mtime)}")
    else:
        print(f"Error: New file was not created properly at {new_file_path}")
except Exception as e:
    print(f"Error saving schematic: {e}")
    import traceback
    traceback.print_exc()