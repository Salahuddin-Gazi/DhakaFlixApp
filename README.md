# DhakaFlix Streamer

**DhakaFlix Streamer** is a desktop application designed to browse, stream, and download content from the DhakaFlix local server (`172.16.50.9`). Built with Python and PyQt6, it offers a fast, native interface for accessing your favorite movies and TV shows, powered by the high-performance MPV player.

## Features

-   **Browse Server**: Navigate the DhakaFlix file server structure with a clean, responsive UI.
-   **Instant Streaming**: Stream videos directly within the app using the embedded MPV player. No need to wait for downloads.
-   **Download Manager**: Queue and download files to your local machine (`downloads/` folder) with progress tracking.
-   **Local Indexing**: Indexes file paths locally for faster searching and browsing experience.

## Prerequisites

Before running the application, ensure you have the following installed:

1.  **Python 3.8 or higher**: [Download Here](https://www.python.org/downloads/)
2.  **libmpv**: A critical dependency for the video player. (See installation instructions below).

---

## Installation & Setup

### 1. Clone or Extract the Repository
Open a terminal (or Command Prompt) and navigate to the project folder:
```bash
cd path/to/DhakaFlixApp
```

### 2. Set Up Virtual Environment (Recommended)

It is best practice to use a virtual environment to manage dependencies.

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
With the virtual environment activated, install the required Python packages:
```bash
pip install -r requirements.txt
```

---

## **Critical Step: Installing libmpv**

This application requires `libmpv` (a shared library for the MPV player) to function. **The app will not launch or play video without it.**

### **For Windows Users**

1.  **Download libmpv**:
    -   Go to the [Shinchiro mpv builds](https://sourceforge.net/projects/mpv-player-windows/files/64bit/) (look for `mpv-dev-x86_64-...`).
    -   Or use [SourceForge libmpv](https://sourceforge.net/projects/mpv-player-windows/files/libmpv/).
2.  **Extract the DLL**:
    -   Open the downloaded `.7z` or `.zip` file.
    -   Find the file named `mpv-2.dll` (or sometimes `mpv-1.dll`).
3.  **Place the DLL**:
    -   Copy `mpv-2.dll` into the **root directory** of this project (the same folder as `run.sh` and `requirements.txt`).
    -   Alternatively, you can place it in `C:\Windows\System32` for system-wide access.

### **For Linux Users**

Install `libmpv` using your package manager.

**Ubuntu / Debian:**
```bash
sudo apt update
sudo apt install libmpv-dev libmpv1
```

**Fedora:**
```bash
sudo dnf install mpv-libs-devel
```

**Arch Linux:**
```bash
sudo pacman -S mpv
```

---

## How to Use

### Running the App

**Windows:**
Ensure your virtual environment is activated, then run:
```cmd
python src/main.py
```

**Linux:**
You can use the provided script:
```bash
./run.sh
```
Or run manually:
```bash
source venv/bin/activate
python3 src/main.py
```

### Using the Features

1.  **Update Index**: On first launch, click the **"Update Index"** button in the sidebar. This scans the server (`172.16.50.9`) to build a list of available files. *Note: This requires access to the local network.*
2.  **Browse**: improved navigation to find movies and series.
3.  **Play**: Double-click any video file to start streaming immediately in the **Player** tab.
4.  **Download**: Right-click a file or use the download button to add it to the **Downloads** queue. Files are saved in the `downloads/` folder.

---

## Building for Windows (Executable)

If you want to create a standalone `.exe` file that doesn't require Python to run:

1.  Ensure you have installed the requirements (`pip install -r requirements.txt`).
2.  Run the build script:
    ```cmd
    build_windows.bat
    ```
3.  Once finished, check the `dist/` folder.
4.  **Important**: You **MUST** manually copy the `mpv-2.dll` file into the `dist/DhakaFlix Streamer/` folder for the executable to work.

---

## Troubleshooting

-   **"OSError: usually caused by missing libmpv"**:
    -   Make sure you followed the "Installing libmpv" section above.
    -   On Windows, ensure `mpv-2.dll` is in the project root or the `dist` folder (if using the exe).
    -   On Linux, ensure `libmpv1` is installed.

-   **"Connection Timeout" or "Server not found"**:
    -   Ensure you are connected to the network that has access to `172.16.50.9`.
    -   Check if the server is online.

-   **Video not playing**:
    -   Ensure the file format is supported (MKV, MP4, AVI, etc.).
    -   Check your network connection speed.
