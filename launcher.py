import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys
import webbrowser
import atexit

class AppLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Restaurant Recommender - Launcher")
        self.root.geometry("400x250")
        self.root.configure(bg="#f0f0f0")
        
        self.backend_process = None
        self.frontend_process = None
        
        # UI Elements
        title = tk.Label(root, text="AI Restaurant Recommender", font=("Helvetica", 16, "bold"), bg="#f0f0f0")
        title.pack(pady=20)
        
        self.status_label = tk.Label(root, text="Status: Stopped", font=("Helvetica", 10), fg="red", bg="#f0f0f0")
        self.status_label.pack(pady=5)
        
        self.start_btn = tk.Button(root, text="Start Application", command=self.start_app, bg="#4CAF50", fg="white", font=("Helvetica", 11, "bold"), width=20)
        self.start_btn.pack(pady=10)
        
        self.stop_btn = tk.Button(root, text="Stop Application", command=self.stop_app, state=tk.DISABLED, bg="#f44336", fg="white", font=("Helvetica", 11, "bold"), width=20)
        self.stop_btn.pack(pady=5)
        
        # Ensure cleanup on exit
        atexit.register(self.stop_app)
        
    def start_app(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        frontend_dir = os.path.join(base_dir, "frontend")
        
        try:
            # Start FastAPI Backend
            # Using creationflags=subprocess.CREATE_NO_WINDOW to hide the console window
            self.backend_process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "src.api.main:app", "--port", "8000"],
                cwd=base_dir,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Start Next.js Frontend
            self.frontend_process = subprocess.Popen(
                ["npm.cmd", "run", "dev"],
                cwd=frontend_dir,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            self.status_label.config(text="Status: Running", fg="green")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            # Open browser after a short delay
            self.root.after(3000, lambda: webbrowser.open("http://localhost:3000"))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start application:\n{str(e)}")
            self.stop_app()

    def stop_app(self):
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process = None
            
        if self.frontend_process:
            # Taskkill is used to kill the npm process tree on Windows
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.frontend_process.pid)], creationflags=subprocess.CREATE_NO_WINDOW)
            self.frontend_process = None
            
        self.status_label.config(text="Status: Stopped", fg="red")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = AppLauncher(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop_app(), root.destroy()))
    root.mainloop()
