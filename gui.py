import customtkinter as ctk
import threading
import requests
from tkinter import messagebox

import analytics
import plotter
import scrapper
from work import Work

# 1. Setup Theme
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class AO3AnalyticsApp(ctk.CTk):
    def __init__(self, session: requests.Session):
        super().__init__()
        
        # Global session
        self.session = session

        # Window Setup
        self.title("AO3 Analytics Tool 📊")
        self.geometry("1280x720")
        
        # Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Title
        self.grid_rowconfigure(1, weight=0) # Input
        self.grid_rowconfigure(2, weight=0) # Options
        self.grid_rowconfigure(3, weight=0) # Button
        self.grid_rowconfigure(4, weight=1) # Log/Status

        # 1. Title
        self.logo_label = ctk.CTkLabel(self, text="AO3 Fanfic Analytics", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        # 2. Input Area
        self.url_entry = ctk.CTkEntry(self, placeholder_text="Paste AO3 Work URL here...", width=500)
        self.url_entry.grid(row=1, column=0, padx=20, pady=10)

        # 3. Options (Checkboxes)
        self.options_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.options_frame.grid(row=2, column=0, pady=10)

        self.check_show_var = ctk.BooleanVar(value=True)
        self.check_save_var = ctk.BooleanVar(value=False)

        self.chk_show = ctk.CTkCheckBox(self.options_frame, text="Show Graphs (Popup)", variable=self.check_show_var)
        self.chk_show.grid(row=0, column=0, padx=10)
        
        self.chk_save = ctk.CTkCheckBox(self.options_frame, text="Save Graphs to Disk", variable=self.check_save_var)
        self.chk_save.grid(row=0, column=1, padx=10)

        # 4. Action Button
        self.analyze_btn = ctk.CTkButton(self, text="Start Analysis", command=self.start_thread, height=40, font=ctk.CTkFont(size=14))
        self.analyze_btn.grid(row=3, column=0, padx=20, pady=20)
        
        # 5. Status / Logs
        self.status_label = ctk.CTkLabel(self, text="Ready.", text_color="gray")
        self.status_label.grid(row=4, column=0, pady=20)

    def start_thread(self):
        """Starts the analysis in a background thread to keep GUI responsive."""
        url = self.url_entry.get()
        if not url:
            self.status_label.configure(text="❌ Error: Please enter a URL", text_color="salmon")
            return

        self.analyze_btn.configure(state="disabled", text="Working...")
        self.status_label.configure(text="⏳ Scraping data... (This may take a moment)", text_color="white")
        
        # Launch the heavy lifting in a separate thread
        threading.Thread(target=self.run_analysis, args=(url,), daemon=True).start()

    def run_analysis(self, url: str):
        """The actual backend logic."""
        try:
            # --- STEP 1: SCRAPE ---
            # Initialize Work (this runs the scraper)
            fic = Work(self.session, url)
            fic.fetch_data()
            # Update Status
            self.update_status(f"Found: {fic.title} (Chapters: {fic.chapters})")
            
            # --- STEP 2: ANALYZE ---
            # Calculate stats (you might need to ensure Work calls this internally or here)
            # Assuming Work.__init__ or Work.calculate_stats() populates the data
            if not hasattr(fic, 'chapter_word_counts'):
                    fic.calculate_stats()

            # --- STEP 3: PLOT ---
            should_show = self.check_show_var.get()
            should_save = self.check_save_var.get()
            
            # We need to run plotting in the main thread usually, but Matplotlib 
            # handles popups okay from threads. Ideally, we schedule this back.
            # For now, let's just call the plotter functions.
            
            # # A. Word Counts per Chapter
            # save_name = f"{fic.title}_counts.png" if should_save else None
            # if should_show or should_save:
            #     plotter.plot_chapter_word_counts(fic.chapter_word_counts, save_to=save_name)
            
            # # B. Cumulative Word Count
            # save_name = f"{fic.title}_growth.png" if should_save else None
            # if should_show or should_save:
            #     plotter.plot_cumulative_word_counts(fic.chapter_word_counts, save_to=save_name)
            
            # C. Top used words
            save_name = f"{fic.title}_word_frequency.png" if should_save else None
            if should_show or should_save:
                plotter.plot_top_words(analytics.filter_frequency(fic.work_word_frequency), 15, save_name)

            self.update_status(f"Analysis Complete for '{fic.title}'!")

        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            print(e) # Print full error to console for debugging
        
        finally:
            # Re-enable button
            self.analyze_btn.configure(state="normal", text="Start Analysis")

    def update_status(self, message):
        """Helper to update label safely."""
        self.status_label.configure(text=message, text_color="white")