# etxDIR

**etxDIR** is a lightweight, dual-mode Python utility that generates filesystem scaffolding directly from [PlantUML](https://plantuml.com/) design files. 

It parses a `.puml` or `.txt` file and recursively creates the directories and empty files defined within it. This allows developers to instantly transition from the **Planning Phase** to the **Implementation Phase** by ensuring the project structure exactly matches the architectural diagram.

## Features

* **Dual Syntax Support:** Automatically detects and parses both:
    * **Standard PlantUML:** `package`, `folder`, `class`, `file`.
    * **Salt (Tree) Syntax:** `+`, `++`, `+++` hierarchy.
* **Zero Dependencies:** Runs on standard Python 3 libraries (`argparse`, `pathlib`).
* **Windows 11 Optimized:** Handles path sanitization and backslashes automatically.
* **Smart Inference:** In Salt mode, automatically distinguishes folders from files based on hierarchy.

## Prerequisites

* **Python 3.6+** installed.
* **Windows OS** (Recommended, though script is cross-platform).

## Installation

1.  Clone this repository or download the files.
2.  Place `etxDIR.py` and `etxDIR.bat` in a permanent folder (e.g., `C:\Tools\etxDIR`).
3.  **Add to Path (Recommended):**
    * Search for "Edit the system environment variables" in Windows.
    * Click **Environment Variables** -> Select **Path** in "User variables" -> **Edit**.
    * Add the full path to your `etxDIR` folder.
    
Now you can run `etxDIR` from any command prompt.

## Usage

Run the tool via the command line by providing the source file and the target destination.

```powershell
etxDIR <source_file> <target_directory>