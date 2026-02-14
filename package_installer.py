import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import sys
import os
from typing import List, Optional


class PackageInstallerWindow:
    """
    A GUI package installer similar to Thonny's package installer.
    Allows users to search, install, upgrade, and uninstall Python packages.
    """
    
    def __init__(self, parent=None, colors=None):
        self.parent = parent
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        self.root.title("Python Package Installer")
        self.root.geometry("800x600")
        
        # Set up color scheme
        if colors is None:
            colors = {
                "bg": "#1e1e1e",
                "panel": "#252526",
                "entry_bg": "#1e1e1e",
                "text": "#d4d4d4",
                "muted": "#858585",
                "button": "#0e7490",
                "border": "#3e3e42",
            }
        self.colors = colors
        self.root.configure(bg=self.colors["panel"])
        
        # Set up the GUI elements
        self.setup_gui()
        
    def setup_gui(self):
        """Set up the GUI elements."""
        # Configure ttk style for dark theme
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=self.colors["panel"])
        style.configure('TLabel', background=self.colors["panel"], foreground=self.colors["text"])
        style.configure('TButton', background=self.colors["panel"], foreground=self.colors["text"])
        style.map('TButton',
                 background=[('active', self.colors["button"])],
                 foreground=[('active', self.colors["text"])])
        style.configure('TEntry', fieldbackground=self.colors["entry_bg"], foreground=self.colors["text"],
                       background=self.colors["entry_bg"], insertcolor=self.colors["text"])
        
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.colors["panel"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Package name entry label
        label = tk.Label(main_frame, text="Package Name:", bg=self.colors["panel"], 
                        fg=self.colors["text"], font=("Segoe UI", 10))
        label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Package name entry
        self.package_entry = tk.Entry(main_frame, width=30, bg=self.colors["entry_bg"],
                                      fg=self.colors["text"], insertbackground=self.colors["text"],
                                      relief="flat", bd=1, highlightthickness=1,
                                      highlightbackground=self.colors["border"])
        self.package_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5), padx=(5, 5))
        self.package_entry.bind('<Return>', lambda e: self.search_packages())
        
        # Search button
        self.search_btn = tk.Button(main_frame, text="Search", command=self.search_packages,
                                   bg=self.colors["button"], fg=self.colors["text"],
                                   activebackground=self.colors["button"], 
                                   activeforeground=self.colors["text"],
                                   relief="flat", bd=0, padx=12, pady=5,
                                   font=("Segoe UI", 9, "bold"), cursor="hand2",
                                   highlightthickness=1, highlightbackground=self.colors["border"])
        self.search_btn.grid(row=0, column=2, padx=(5, 0), pady=(0, 5))
        
        # Search results label
        results_label = tk.Label(main_frame, text="Search Results:", bg=self.colors["panel"],
                                fg=self.colors["text"], font=("Segoe UI", 10))
        results_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        # Search results listbox
        self.results_listbox = tk.Listbox(main_frame, bg=self.colors["entry_bg"],
                                         fg=self.colors["text"],
                                         selectbackground=self.colors["button"],
                                         selectforeground=self.colors["text"],
                                         relief="flat", bd=1, highlightthickness=1,
                                         highlightbackground=self.colors["border"],
                                         activestyle="none", font=("Segoe UI", 9))
        self.results_listbox.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), 
                                 pady=(0, 5))
        self.results_listbox.bind('<<ListboxSelect>>', self.on_package_select)
        
        # Scrollbar for results
        scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.results_listbox.yview,
                                bg=self.colors["entry_bg"], activebackground=self.colors["button"],
                                troughcolor=self.colors["panel"], bd=0, highlightthickness=0)
        scrollbar.grid(row=2, column=3, sticky=(tk.N, tk.S), padx=(5, 0))
        self.results_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Package info label
        info_label = tk.Label(main_frame, text="Package Information:", bg=self.colors["panel"],
                             fg=self.colors["text"], font=("Segoe UI", 10))
        info_label.grid(row=3, column=0, sticky=tk.W, pady=(5, 5))
        
        # Package info text area
        self.info_text = scrolledtext.ScrolledText(main_frame, height=8, width=70,
                                                  bg=self.colors["entry_bg"],
                                                  fg=self.colors["text"],
                                                  insertbackground=self.colors["text"],
                                                  relief="flat", bd=1, highlightthickness=1,
                                                  highlightbackground=self.colors["border"],
                                                  font=("Consolas", 9))
        self.info_text.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        self.info_text.config(state=tk.DISABLED)
        
        # Configure scrollbar for info text
        self.info_text.vbar.config(bg=self.colors["entry_bg"], activebackground=self.colors["button"],
                                  troughcolor=self.colors["panel"], bd=0, highlightthickness=0)
        
        # Action buttons frame
        btn_frame = tk.Frame(main_frame, bg=self.colors["panel"])
        btn_frame.grid(row=5, column=0, columnspan=4, pady=(10, 0))
        
        # Helper function to create styled buttons
        def create_button(parent, text, command, state=tk.NORMAL):
            btn = tk.Button(parent, text=text, command=command, state=state,
                           bg=self.colors["button"], fg=self.colors["text"],
                           activebackground=self.colors["button"],
                           activeforeground=self.colors["text"],
                           relief="flat", bd=0, padx=10, pady=5,
                           font=("Segoe UI", 9, "bold"), cursor="hand2",
                           highlightthickness=1, highlightbackground=self.colors["border"])
            return btn
        
        self.install_btn = create_button(btn_frame, "Install", self.install_package, tk.DISABLED)
        self.install_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.upgrade_btn = create_button(btn_frame, "Upgrade", self.upgrade_package, tk.DISABLED)
        self.upgrade_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.uninstall_btn = create_button(btn_frame, "Uninstall", self.uninstall_package, tk.DISABLED)
        self.uninstall_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.refresh_btn = create_button(btn_frame, "Refresh Installed", self.list_installed_packages)
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Progress/status label
        self.status_label = tk.Label(main_frame, text="Ready", bg=self.colors["panel"],
                                    fg=self.colors["muted"], font=("Segoe UI", 9))
        self.status_label.grid(row=6, column=0, columnspan=4, sticky=tk.W, pady=(10, 0))
        
        # Initially populate with installed packages
        self.list_installed_packages()
    
    def search_packages(self):
        """Search for packages using PyPI."""
        query = self.package_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a package name to search.")
            return
        
        self.status_label.config(text="Searching...")
        self.root.update()
        
        # Run search in a separate thread to prevent GUI freezing
        thread = threading.Thread(target=self._search_packages_thread, args=(query,))
        thread.daemon = True
        thread.start()
    
    def _search_packages_thread(self, query):
        """Thread function to search for packages."""
        try:
            # Use pip search (though this may not work with newer pip versions)
            # Alternative: use PyPI API or search manually
            result = subprocess.run([
                sys.executable, "-m", "pip", "index", "versions", query
            ], capture_output=True, text=True, timeout=30)
            
            self.root.after(0, self._handle_search_result, result.stdout, result.stderr, result.returncode)
        except subprocess.TimeoutExpired:
            self.root.after(0, self._handle_timeout)
        except Exception as e:
            self.root.after(0, self._handle_search_error, str(e))
    
    def _handle_search_result(self, stdout, stderr, returncode):
        """Handle the search result in the main thread."""
        self.results_listbox.delete(0, tk.END)
        self.status_label.config(text="Search completed")
        
        if returncode == 0:
            # Parse the search result
            lines = stdout.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('WARNING'):
                    # Simple parsing - in reality, we'd want more robust parsing
                    if ' - ' in line:
                        parts = line.split(' - ', 1)
                        if len(parts) >= 2:
                            name = parts[0].split()[0]  # Get just the package name
                            self.results_listbox.insert(tk.END, name)
                    else:
                        # Fallback: just add the line if it looks like a package name
                        if line and ' ' not in line[:20]:  # Rough check
                            self.results_listbox.insert(tk.END, line.split()[0])
        else:
            # If index command doesn't work, try showing installed packages or a message
            messagebox.showinfo("Info", f"Direct search may not be available with this pip version.\nError: {stderr}")
            self.list_installed_packages()
    
    def _handle_timeout(self):
        """Handle search timeout."""
        self.status_label.config(text="Search timed out")
        messagebox.showerror("Error", "Search timed out. Please try again.")
    
    def _handle_search_error(self, error_msg):
        """Handle search error."""
        self.status_label.config(text="Search failed")
        messagebox.showerror("Error", f"Search failed: {error_msg}")
    
    def on_package_select(self, event):
        """Handle package selection in the listbox."""
        selection = self.results_listbox.curselection()
        if selection:
            package_name = self.results_listbox.get(selection[0])
            self.show_package_info(package_name)
            self.install_btn.config(state=tk.NORMAL)
            self.upgrade_btn.config(state=tk.NORMAL)
            self.uninstall_btn.config(state=tk.NORMAL)
        else:
            self.install_btn.config(state=tk.DISABLED)
            self.upgrade_btn.config(state=tk.DISABLED)
            self.uninstall_btn.config(state=tk.DISABLED)
    
    def show_package_info(self, package_name):
        """Show package information."""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        try:
            # Get package info using pip show
            result = subprocess.run([
                sys.executable, "-m", "pip", "show", package_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.info_text.insert(tk.END, result.stdout)
            else:
                self.info_text.insert(tk.END, f"Package '{package_name}' not found locally.\n")
                self.info_text.insert(tk.END, "This might be a new package to install.\n")
        except Exception as e:
            self.info_text.insert(tk.END, f"Error getting package info: {str(e)}")
        
        self.info_text.config(state=tk.DISABLED)
    
    def install_package(self):
        """Install the selected package."""
        selection = self.results_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a package to install.")
            return
        
        package_name = self.results_listbox.get(selection[0])
        if not package_name.strip():
            return
        
        confirm = messagebox.askyesno("Confirm Installation", f"Do you want to install '{package_name}'?")
        if not confirm:
            return
        
        self.status_label.config(text=f"Installing {package_name}...")
        self.root.update()
        
        # Run installation in a separate thread
        thread = threading.Thread(target=self._install_package_thread, args=(package_name,))
        thread.daemon = True
        thread.start()
    
    def _install_package_thread(self, package_name):
        """Thread function to install a package."""
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package_name
            ], capture_output=True, text=True, timeout=120)
            
            self.root.after(0, self._handle_install_result, result.stdout, result.stderr, result.returncode, package_name)
        except subprocess.TimeoutExpired:
            self.root.after(0, self._handle_install_timeout, package_name)
        except Exception as e:
            self.root.after(0, self._handle_install_error, str(e), package_name)
    
    def _handle_install_result(self, stdout, stderr, returncode, package_name):
        """Handle the installation result in the main thread."""
        if returncode == 0:
            self.status_label.config(text=f"Successfully installed {package_name}")
            messagebox.showinfo("Success", f"Successfully installed {package_name}")
        else:
            self.status_label.config(text=f"Failed to install {package_name}")
            messagebox.showerror("Error", f"Failed to install {package_name}:\n{stderr}")
        
        # Refresh the installed packages list
        self.list_installed_packages()
    
    def _handle_install_timeout(self, package_name):
        """Handle installation timeout."""
        self.status_label.config(text="Installation timed out")
        messagebox.showerror("Error", f"Installation of {package_name} timed out.")
    
    def _handle_install_error(self, error_msg, package_name):
        """Handle installation error."""
        self.status_label.config(text=f"Installation failed for {package_name}")
        messagebox.showerror("Error", f"Installation failed for {package_name}: {error_msg}")
    
    def upgrade_package(self):
        """Upgrade the selected package."""
        selection = self.results_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a package to upgrade.")
            return
        
        package_name = self.results_listbox.get(selection[0])
        if not package_name.strip():
            return
        
        confirm = messagebox.askyesno("Confirm Upgrade", f"Do you want to upgrade '{package_name}'?")
        if not confirm:
            return
        
        self.status_label.config(text=f"Upgrading {package_name}...")
        self.root.update()
        
        # Run upgrade in a separate thread
        thread = threading.Thread(target=self._upgrade_package_thread, args=(package_name,))
        thread.daemon = True
        thread.start()
    
    def _upgrade_package_thread(self, package_name):
        """Thread function to upgrade a package."""
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", package_name
            ], capture_output=True, text=True, timeout=120)
            
            self.root.after(0, self._handle_upgrade_result, result.stdout, result.stderr, result.returncode, package_name)
        except subprocess.TimeoutExpired:
            self.root.after(0, self._handle_upgrade_timeout, package_name)
        except Exception as e:
            self.root.after(0, self._handle_upgrade_error, str(e), package_name)
    
    def _handle_upgrade_result(self, stdout, stderr, returncode, package_name):
        """Handle the upgrade result in the main thread."""
        if returncode == 0:
            self.status_label.config(text=f"Successfully upgraded {package_name}")
            messagebox.showinfo("Success", f"Successfully upgraded {package_name}")
        else:
            self.status_label.config(text=f"Failed to upgrade {package_name}")
            messagebox.showerror("Error", f"Failed to upgrade {package_name}:\n{stderr}")
        
        # Refresh the installed packages list
        self.list_installed_packages()
    
    def _handle_upgrade_timeout(self, package_name):
        """Handle upgrade timeout."""
        self.status_label.config(text="Upgrade timed out")
        messagebox.showerror("Error", f"Upgrade of {package_name} timed out.")
    
    def _handle_upgrade_error(self, error_msg, package_name):
        """Handle upgrade error."""
        self.status_label.config(text=f"Upgrade failed for {package_name}")
        messagebox.showerror("Error", f"Upgrade failed for {package_name}: {error_msg}")
    
    def uninstall_package(self):
        """Uninstall the selected package."""
        selection = self.results_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a package to uninstall.")
            return
        
        package_name = self.results_listbox.get(selection[0])
        if not package_name.strip():
            return
        
        confirm = messagebox.askyesno("Confirm Uninstallation", f"Do you want to uninstall '{package_name}'?\nThis action cannot be undone!")
        if not confirm:
            return
        
        self.status_label.config(text=f"Uninstalling {package_name}...")
        self.root.update()
        
        # Run uninstallation in a separate thread
        thread = threading.Thread(target=self._uninstall_package_thread, args=(package_name,))
        thread.daemon = True
        thread.start()
    
    def _uninstall_package_thread(self, package_name):
        """Thread function to uninstall a package."""
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "uninstall", "-y", package_name
            ], capture_output=True, text=True, timeout=60)
            
            self.root.after(0, self._handle_uninstall_result, result.stdout, result.stderr, result.returncode, package_name)
        except subprocess.TimeoutExpired:
            self.root.after(0, self._handle_uninstall_timeout, package_name)
        except Exception as e:
            self.root.after(0, self._handle_uninstall_error, str(e), package_name)
    
    def _handle_uninstall_result(self, stdout, stderr, returncode, package_name):
        """Handle the uninstall result in the main thread."""
        if returncode == 0 or "Successfully uninstalled" in stdout:
            self.status_label.config(text=f"Successfully uninstalled {package_name}")
            messagebox.showinfo("Success", f"Successfully uninstalled {package_name}")
        else:
            self.status_label.config(text=f"Failed to uninstall {package_name}")
            messagebox.showerror("Error", f"Failed to uninstall {package_name}:\n{stderr}")
        
        # Refresh the installed packages list
        self.list_installed_packages()
    
    def _handle_uninstall_timeout(self, package_name):
        """Handle uninstall timeout."""
        self.status_label.config(text="Uninstall timed out")
        messagebox.showerror("Error", f"Uninstall of {package_name} timed out.")
    
    def _handle_uninstall_error(self, error_msg, package_name):
        """Handle uninstall error."""
        self.status_label.config(text=f"Uninstall failed for {package_name}")
        messagebox.showerror("Error", f"Uninstall failed for {package_name}: {error_msg}")
    
    def list_installed_packages(self):
        """List installed packages."""
        self.status_label.config(text="Loading installed packages...")
        self.root.update()
        
        # Run listing in a separate thread
        thread = threading.Thread(target=self._list_installed_packages_thread)
        thread.daemon = True
        thread.start()
    
    def _list_installed_packages_thread(self):
        """Thread function to list installed packages."""
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "list"
            ], capture_output=True, text=True, timeout=30)
            
            self.root.after(0, self._handle_list_result, result.stdout, result.stderr, result.returncode)
        except subprocess.TimeoutExpired:
            self.root.after(0, self._handle_list_timeout)
        except Exception as e:
            self.root.after(0, self._handle_list_error, str(e))
    
    def _handle_list_result(self, stdout, stderr, returncode):
        """Handle the list result in the main thread."""
        self.results_listbox.delete(0, tk.END)
        self.status_label.config(text="Installed packages loaded")
        
        if returncode == 0:
            lines = stdout.strip().split('\n')
            # Skip header lines
            for i, line in enumerate(lines):
                if i == 0 and 'Package' in line and 'Version' in line:
                    continue  # Skip header
                if line.strip():
                    # Extract package name (first word in the line)
                    parts = line.split()
                    if parts:
                        package_name = parts[0]
                        self.results_listbox.insert(tk.END, package_name)
        else:
            messagebox.showerror("Error", f"Failed to list packages:\n{stderr}")
    
    def _handle_list_timeout(self):
        """Handle list timeout."""
        self.status_label.config(text="Package list timed out")
        messagebox.showerror("Error", "Listing packages timed out.")
    
    def _handle_list_error(self, error_msg):
        """Handle list error."""
        self.status_label.config(text="Failed to load packages")
        messagebox.showerror("Error", f"Failed to load packages: {error_msg}")
    
    def show(self):
        """Show the window."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()


if __name__ == "__main__":
    app = PackageInstallerWindow()
    app.root.mainloop()