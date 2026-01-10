#!/usr/bin/env python3
"""Desktop GUI application for Trash Collection Route Generator"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path
import webbrowser

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.route_generator import TrashRouteGenerator


class TrashRouteGUI:
    """Desktop GUI application for trash collection route generation"""
    
    def __init__(self, root):
        """Initialize the GUI application"""
        self.root = root
        self.root.title("Trash Collection Route Generator")
        self.root.geometry("700x650")
        self.root.resizable(True, True)
        
        # Variables
        self.osm_file_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=os.path.join(os.getcwd(), "output"))
        self.gpx_name_var = tk.StringVar(value="trash_collection_route")
        self.report_name_var = tk.StringVar(value="route_report")
        self.verbose_var = tk.BooleanVar(value=False)
        
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
        main_frame = ttk.Frame(self.root, padding="10")
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
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 20))
        row += 1
        
        # OSM File Selection
        ttk.Label(main_frame, text="OSM File:", font=("Arial", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(
            main_frame,
            textvariable=self.osm_file_var,
            width=50,
            state="readonly"
        ).grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(
            main_frame,
            text="Browse...",
            command=self.browse_osm_file
        ).grid(row=row, column=2, pady=5)
        row += 1
        
        # Output Directory
        ttk.Label(main_frame, text="Output Folder:", font=("Arial", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(
            main_frame,
            textvariable=self.output_dir_var,
            width=50
        ).grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(
            main_frame,
            text="Browse...",
            command=self.browse_output_dir
        ).grid(row=row, column=2, pady=5)
        row += 1
        
        # GPX Filename
        ttk.Label(main_frame, text="GPX Filename:", font=("Arial", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(
            main_frame,
            textvariable=self.gpx_name_var,
            width=50
        ).grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        row += 1
        
        # Report Filename
        ttk.Label(main_frame, text="Report Filename:", font=("Arial", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(
            main_frame,
            textvariable=self.report_name_var,
            width=50
        ).grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        row += 1
        
        # Verbose option
        ttk.Checkbutton(
            main_frame,
            text="Show detailed progress",
            variable=self.verbose_var
        ).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Generate Button
        self.generate_btn = ttk.Button(
            main_frame,
            text="Generate Route",
            command=self.on_generate,
            style="Accent.TButton"
        )
        self.generate_btn.grid(row=row, column=0, columnspan=3, pady=20)
        row += 1
        
        # Status Label
        self.status_var = tk.StringVar(value="Ready - Select OSM file and click Generate")
        self.status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            font=("Arial", 9),
            foreground="gray"
        )
        self.status_label.grid(row=row, column=0, columnspan=3, pady=(10, 5))
        row += 1
        
        # Progress/Results Text Area
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(row, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(
            text_frame,
            width=70,
            height=15,
            wrap=tk.WORD,
            font=("Consolas", 9)
        )
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.results_text.insert("1.0", "Route generation results will appear here...\n\n")
        self.results_text.config(state=tk.DISABLED)
        row += 1
        
        # Action Buttons Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)
        
        self.open_folder_btn = ttk.Button(
            button_frame,
            text="Open Output Folder",
            command=self.open_output_folder,
            state=tk.DISABLED
        )
        self.open_folder_btn.pack(side=tk.LEFT, padx=5)
        
        self.view_gpx_btn = ttk.Button(
            button_frame,
            text="View GPX File",
            command=self.view_gpx_file,
            state=tk.DISABLED
        )
        self.view_gpx_btn.pack(side=tk.LEFT, padx=5)
        
        self.view_report_btn = ttk.Button(
            button_frame,
            text="View Report",
            command=self.view_report_file,
            state=tk.DISABLED
        )
        self.view_report_btn.pack(side=tk.LEFT, padx=5)
        
        # Configure style for accent button
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 11, "bold"))
    
    def browse_osm_file(self):
        """Open file dialog to select OSM file"""
        filename = filedialog.askopenfilename(
            title="Select OSM File",
            filetypes=[
                ("OSM files", "*.osm *.xml"),
                ("XML files", "*.xml"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.osm_file_var.set(filename)
            self.status_var.set(f"Selected: {os.path.basename(filename)}")
    
    def browse_output_dir(self):
        """Open directory dialog to select output folder"""
        dirname = filedialog.askdirectory(
            title="Select Output Folder",
            initialdir=self.output_dir_var.get()
        )
        if dirname:
            self.output_dir_var.set(dirname)
    
    def update_status(self, message: str, color: str = "black"):
        """Update status label"""
        self.status_var.set(message)
        self.status_label.config(foreground=color)
        self.root.update_idletasks()
    
    def append_results(self, text: str):
        """Append text to results area"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, text + "\n")
        self.results_text.see(tk.END)
        self.results_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def clear_results(self):
        """Clear results text area"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.config(state=tk.DISABLED)
    
    def on_generate(self):
        """Handle generate button click"""
        # Validate inputs
        osm_file = self.osm_file_var.get()
        if not osm_file or not os.path.exists(osm_file):
            messagebox.showerror(
                "Error",
                "Please select a valid OSM file"
            )
            return
        
        output_dir = self.output_dir_var.get()
        if not output_dir:
            messagebox.showerror(
                "Error",
                "Please specify an output directory"
            )
            return
        
        # Create output directory if it doesn't exist
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Cannot create output directory: {e}"
            )
            return
        
        # Disable generate button and enable results
        self.generate_btn.config(state=tk.DISABLED)
        self.open_folder_btn.config(state=tk.DISABLED)
        self.view_gpx_btn.config(state=tk.DISABLED)
        self.view_report_btn.config(state=tk.DISABLED)
        
        self.update_status("Generating route...", "blue")
        self.clear_results()
        self.append_results("=" * 70)
        self.append_results("TRASH COLLECTION ROUTE GENERATOR")
        self.append_results("=" * 70)
        self.append_results(f"OSM File: {os.path.basename(osm_file)}")
        self.append_results(f"Output: {output_dir}")
        self.append_results("")
        
        # Run generation in background thread
        thread = threading.Thread(
            target=self.generate_route_worker,
            args=(osm_file, output_dir),
            daemon=True
        )
        thread.start()
    
    def generate_route_worker(self, osm_file: str, output_dir: str):
        """Worker thread for route generation"""
        try:
            # Create generator
            generator = TrashRouteGenerator(osm_file, output_dir)
            
            # Generate route
            self.append_results("[Step 1] Parsing OSM data...")
            self.root.after(0, self.update_status, "Parsing OSM data...", "blue")
            
            gpx_path, report_path = generator.generate(
                output_gpx=self.gpx_name_var.get(),
                output_report=self.report_name_var.get(),
                start_node=None
            )
            
            # Store paths
            self.gpx_path = gpx_path
            self.report_path = report_path
            
            # Get summary
            summary = generator.get_summary()
            
            # Display results
            self.root.after(0, self.append_results, "")
            self.root.after(0, self.append_results, "✓ Route generation complete!")
            self.root.after(0, self.append_results, "")
            self.root.after(0, self.append_results, "Summary:")
            self.root.after(0, self.append_results, f"  Nodes parsed: {summary['nodes_parsed']}")
            self.root.after(0, self.append_results, f"  Driveable ways: {summary['driveable_ways']}")
            self.root.after(0, self.append_results, f"  Road segments: {summary['segments']}")
            self.root.after(0, self.append_results, f"  Circuit edges: {summary['circuit_edges']}")
            
            if 'route' in summary['stats']:
                route_stats = summary['stats']['route']
                self.root.after(0, self.append_results, "")
                self.root.after(0, self.append_results, "Route Statistics:")
                self.root.after(0, self.append_results, f"  Distance: {route_stats.get('total_distance_km')} km")
                self.root.after(0, self.append_results, f"  Drive time: {route_stats.get('estimated_drive_time_hours')} hours")
                self.root.after(0, self.append_results, f"  Traversals: {route_stats.get('directed_traversals')}")
            
            if 'turns' in summary['stats']:
                turn_stats = summary['stats']['turns']
                self.root.after(0, self.append_results, "")
                self.root.after(0, self.append_results, "Turn Analysis:")
                self.root.after(0, self.append_results, f"  Right turns: {turn_stats.get('right_turns')}")
                self.root.after(0, self.append_results, f"  Left turns: {turn_stats.get('left_turns')}")
                self.root.after(0, self.append_results, f"  Straight: {turn_stats.get('straight')}")
                self.root.after(0, self.append_results, f"  U-turns: {turn_stats.get('u_turns')}")
            
            self.root.after(0, self.append_results, "")
            self.root.after(0, self.append_results, f"GPX file: {os.path.basename(gpx_path)}")
            self.root.after(0, self.append_results, f"Report: {os.path.basename(report_path)}")
            
            # Update UI
            self.root.after(0, self.update_status, "✓ Route generated successfully!", "green")
            self.root.after(0, self.generate_btn.config, {"state": tk.NORMAL})
            self.root.after(0, self.open_folder_btn.config, {"state": tk.NORMAL})
            self.root.after(0, self.view_gpx_btn.config, {"state": tk.NORMAL})
            self.root.after(0, self.view_report_btn.config, {"state": tk.NORMAL})
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, self.append_results, "")
            self.root.after(0, self.append_results, f"✗ ERROR: {error_msg}")
            self.root.after(0, self.update_status, "Generation failed", "red")
            self.root.after(0, self.generate_btn.config, {"state": tk.NORMAL})
            self.root.after(0, messagebox.showerror, "Error", f"Route generation failed:\n\n{error_msg}")
    
    def open_output_folder(self):
        """Open output folder in file explorer"""
        if self.output_dir_var.get():
            path = Path(self.output_dir_var.get())
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                os.system(f"open {path}")
            else:
                os.system(f"xdg-open {path}")
    
    def view_gpx_file(self):
        """Open GPX file in default application"""
        if self.gpx_path and os.path.exists(self.gpx_path):
            if sys.platform == "win32":
                os.startfile(self.gpx_path)
            elif sys.platform == "darwin":
                os.system(f"open {self.gpx_path}")
            else:
                os.system(f"xdg-open {self.gpx_path}")
        else:
            messagebox.showwarning("Warning", "GPX file not found")
    
    def view_report_file(self):
        """Open report file in default text editor"""
        if self.report_path and os.path.exists(self.report_path):
            if sys.platform == "win32":
                os.startfile(self.report_path)
            elif sys.platform == "darwin":
                os.system(f"open {self.report_path}")
            else:
                os.system(f"xdg-open {self.report_path}")
        else:
            messagebox.showwarning("Warning", "Report file not found")


def main():
    """Main entry point for GUI application"""
    root = tk.Tk()
    app = TrashRouteGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
