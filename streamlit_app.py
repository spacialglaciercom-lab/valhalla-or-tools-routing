#!/usr/bin/env python3
"""Desktop GUI application for Trash Collection Route Generator"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.route_generator import TrashRouteGenerator


class TrashRouteGUI:
    """Desktop GUI application for trash collection route generation"""
    
    def __init__(self, root):
        """Initialize the GUI application"""
        self.root = root
        self.root.title("Trash Collection Route Generator")
        self.root.geometry("750x750")  # Increased height for new fields
        self.root.resizable(True, True)
        
        # Variables
        self.osm_file_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=os.path.join(os.getcwd(), "output"))
        self.gpx_name_var = tk.StringVar(value="trash_collection_route")
        self.report_name_var = tk.StringVar(value="route_report")
        self.verbose_var = tk.BooleanVar(value=False)
        
        # New: Starting Coordinates
        self.start_lat_var = tk.StringVar()
        self.start_lon_var = tk.StringVar()
        
        # Results
        self.gpx_path = None
        self.report_path = None
        
        # Setup UI
        self.setup_ui()
        
        # Center window
        self.center_window()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Create and layout all UI components"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Trash Collection Route Generator",
            font=("Segoe UI", 18, "bold")
        )
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 20))
        row += 1
        
        # --- File Section ---
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(1, weight=1)
        
        f_row = 0
        # OSM File Selection
        ttk.Label(file_frame, text="OSM File:").grid(row=f_row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.osm_file_var, width=50, state="readonly").grid(row=f_row, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_osm_file).grid(row=f_row, column=2)
        f_row += 1
        
        # Output Directory
        ttk.Label(file_frame, text="Output Folder:").grid(row=f_row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_dir_var, width=50).grid(row=f_row, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_output_dir).grid(row=f_row, column=2)
        
        row += 1

        # --- Settings Section ---
        settings_frame = ttk.LabelFrame(main_frame, text="Route Settings", padding="10")
        settings_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        settings_frame.columnconfigure(1, weight=1)
        
        s_row = 0
        # Filenames
        ttk.Label(settings_frame, text="GPX Name:").grid(row=s_row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(settings_frame, textvariable=self.gpx_name_var).grid(row=s_row, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Label(settings_frame, text="Report Name:").grid(row=s_row, column=2, sticky=tk.W, pady=5)
        ttk.Entry(settings_frame, textvariable=self.report_name_var).grid(row=s_row, column=3, sticky=(tk.W, tk.E), padx=5)
        s_row += 1

        # Start Coordinates (New Feature)
        ttk.Label(settings_frame, text="Start Lat (Optional):").grid(row=s_row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(settings_frame, textvariable=self.start_lat_var, width=15).grid(row=s_row, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(settings_frame, text="Start Lon (Optional):").grid(row=s_row, column=2, sticky=tk.W, pady=5)
        ttk.Entry(settings_frame, textvariable=self.start_lon_var, width=15).grid(row=s_row, column=3, sticky=tk.W, padx=5)
        
        # Add a tooltip or helper text
        s_row += 1
        ttk.Label(settings_frame, text="Leave Lat/Lon empty to auto-detect best start point", 
                 font=("Segoe UI", 8, "italic"), foreground="gray").grid(row=s_row, column=0, columnspan=4, sticky=tk.W)

        row += 1

        # Verbose option
        ttk.Checkbutton(main_frame, text="Show detailed progress logs", variable=self.verbose_var).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=5)
        row += 1
        
        # Generate Button
        self.generate_btn = ttk.Button(
            main_frame,
            text="Generate Route",
            command=self.on_generate,
            style="Accent.TButton"
        )
        self.generate_btn.grid(row=row, column=0, columnspan=3, pady=15)
        row += 1
        
        # Status Label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 9),
            foreground="gray"
        )
        self.status_label.grid(row=row, column=0, columnspan=3, pady=(0, 5))
        row += 1
        
        # Progress/Results Text Area
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(row, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(
            text_frame,
            height=12,
            wrap=tk.WORD,
            font=("Consolas", 9)
        )
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.results_text.insert("1.0", "Route generation results will appear here...\n")
        self.results_text.config(state=tk.DISABLED)
        row += 1
        
        # Action Buttons Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)
        
        self.open_folder_btn = ttk.Button(button_frame, text="Open Output Folder", command=self.open_output_folder, state=tk.DISABLED)
        self.open_folder_btn.pack(side=tk.LEFT, padx=5)
        
        self.view_gpx_btn = ttk.Button(button_frame, text="View GPX File", command=self.view_gpx_file, state=tk.DISABLED)
        self.view_gpx_btn.pack(side=tk.LEFT, padx=5)
        
        self.view_report_btn = ttk.Button(button_frame, text="View Report", command=self.view_report_file, state=tk.DISABLED)
        self.view_report_btn.pack(side=tk.LEFT, padx=5)
        
        # Configure style for accent button
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"))
    
    def browse_osm_file(self):
        """Open file dialog to select OSM file"""
        filename = filedialog.askopenfilename(
            title="Select OSM File",
            filetypes=[("OSM/PBF files", "*.osm *.xml *.pbf"), ("All files", "*.*")]
        )
        if filename:
            self.osm_file_var.set(filename)
            self.status_var.set(f"Selected: {os.path.basename(filename)}")
    
    def browse_output_dir(self):
        dirname = filedialog.askdirectory(title="Select Output Folder", initialdir=self.output_dir_var.get())
        if dirname:
            self.output_dir_var.set(dirname)
    
    def update_status(self, message: str, color: str = "black"):
        self.status_var.set(message)
        self.status_label.config(foreground=color)
        self.root.update_idletasks()
    
    def append_results(self, text: str):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, text + "\n")
        self.results_text.see(tk.END)
        self.results_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def clear_results(self):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.config(state=tk.DISABLED)
    
    def on_generate(self):
        osm_file = self.osm_file_var.get()
        if not osm_file or not os.path.exists(osm_file):
            messagebox.showerror("Error", "Please select a valid OSM file")
            return
        
        output_dir = self.output_dir_var.get()
        if not output_dir:
            messagebox.showerror("Error", "Please specify an output directory")
            return
        
        # Parse start coordinates if provided
        start_lat = None
        start_lon = None
        if self.start_lat_var.get() and self.start_lon_var.get():
            try:
                start_lat = float(self.start_lat_var.get())
                start_lon = float(self.start_lon_var.get())
            except ValueError:
                messagebox.showerror("Error", "Invalid coordinates. Please enter numbers.")
                return

        # Create output directory
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot create output directory: {e}")
            return
        
        # UI State updates
        self.generate_btn.config(state=tk.DISABLED)
        self.open_folder_btn.config(state=tk.DISABLED)
        self.view_gpx_btn.config(state=tk.DISABLED)
        self.view_report_btn.config(state=tk.DISABLED)
        
        self.update_status("Generating route...", "blue")
        self.clear_results()
        self.append_results("=" * 60)
        self.append_results("TRASH COLLECTION ROUTE GENERATOR")
        self.append_results("=" * 60)
        
        # Run in thread
        thread = threading.Thread(
            target=self.generate_route_worker,
            args=(osm_file, output_dir, start_lat, start_lon),
            daemon=True
        )
        thread.start()
    
    def generate_route_worker(self, osm_file, output_dir, start_lat, start_lon):
        try:
            generator = TrashRouteGenerator(osm_file, output_dir)
            
            # Progress callback wrapper
            def progress_cb(step, pct, msg, stats):
                self.root.after(0, self.update_status, msg, "blue")
                if self.verbose_var.get():
                    self.root.after(0, self.append_results, f"[{pct}%] {msg}")

            generator.progress_callback = progress_cb
            
            self.root.after(0, self.append_results, "Starting generation...")
            
            gpx_path, report_path = generator.generate(
                output_gpx=self.gpx_name_var.get(),
                output_report=self.report_name_var.get(),
                start_lat=start_lat,
                start_lon=start_lon
            )
            
            self.gpx_path = gpx_path
            self.report_path = report_path
            
            # Show summary stats
            summary = generator.get_summary()
            self.root.after(0, self.append_results, "\n" + "="*30)
            self.root.after(0, self.append_results, "GENERATION COMPLETE")
            self.root.after(0, self.append_results, "="*30)
            
            if 'route' in summary['stats']:
                s = summary['stats']['route']
                self.root.after(0, self.append_results, f"Distance: {s.get('total_distance_km')} km")
                self.root.after(0, self.append_results, f"Est. Time: {s.get('estimated_drive_time_hours')} hours")

            self.root.after(0, self.update_status, "✓ Success!", "green")
            self.root.after(0, self.generate_btn.config, {"state": tk.NORMAL})
            self.root.after(0, self.open_folder_btn.config, {"state": tk.NORMAL})
            self.root.after(0, self.view_gpx_btn.config, {"state": tk.NORMAL})
            self.root.after(0, self.view_report_btn.config, {"state": tk.NORMAL})
            
        except Exception as e:
            self.root.after(0, self.append_results, f"\n✗ ERROR: {str(e)}")
            self.root.after(0, self.update_status, "Failed", "red")
            self.root.after(0, self.generate_btn.config, {"state": tk.NORMAL})

    def open_output_folder(self):
        if self.output_dir_var.get():
            path = Path(self.output_dir_var.get())
            if sys.platform == "win32": os.startfile(path)
            elif sys.platform == "darwin": os.system(f"open {path}")
            else: os.system(f"xdg-open {path}")
    
    def view_gpx_file(self):
        if self.gpx_path and os.path.exists(self.gpx_path):
            if sys.platform == "win32": os.startfile(self.gpx_path)
            elif sys.platform == "darwin": os.system(f"open {self.gpx_path}")
            else: os.system(f"xdg-open {self.gpx_path}")
    
    def view_report_file(self):
        if self.report_path and os.path.exists(self.report_path):
            if sys.platform == "win32": os.startfile(self.report_path)
            elif sys.platform == "darwin": os.system(f"open {self.report_path}")
            else: os.system(f"xdg-open {self.report_path}")

def main():
    root = tk.Tk()
    app = TrashRouteGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
