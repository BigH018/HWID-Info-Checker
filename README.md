# HWID Information Retrieval Tool

## Overview

This Python script gathers hardware information from a Windows system, including disk information, MAC address, motherboard details, CPU ID, and volume information. It presents the collected data in a Tkinter-based graphical user interface (GUI).

## Features

- Retrieves Disk Information using WMI (Windows Management Instrumentation).
- Fetches MAC Address by executing the `ipconfig /all` command.
- Obtains Motherboard Information via the `wmic baseboard get Manufacturer,Product,SerialNumber` command.
- Fetches CPU ID using the `wmic cpu get ProcessorID` command.
- Retrieves Volume Information using WMI.

## Prerequisites

- Python 3.x installed on a Windows system.
- Necessary Python packages (`wmi` and `tkinter`) installed. You can install them via pip:

    ```
    pip install wmi
    pip install tkinter
    ```

## Usage

1. Clone or download the repository to your local machine.
2. Navigate to the project directory.
3. Run the script using Python:

    ```  
    python main.py
    ```

## Compiling into an Executable

You can compile the Python script into an executable file for easier distribution. One popular tool for this purpose is `pyinstaller`. Install it via pip:

   ```
   pip install pyinstaller
   ```

Then, navigate to the project directory in the terminal and run: pyinstaller --onefile --noconsole main.py

   ```
   pyinstaller --onefile --noconsole main.py
   ```

This command will create a standalone executable file in the `dist` directory.

## Troubleshooting

- If encountering errors during execution, ensure that the required Python packages are installed (`wmi` and `tkinter`).

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or create a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

