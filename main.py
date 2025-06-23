import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font
import threading
import requests
import json
import os
import ctypes
from dotenv import load_dotenv

load_dotenv()

class PromptEnhancerApp:
    def __init__(self, root):
        self.root = root
        # Set minimal initial size
        self.root.geometry("650x250")
        self.root.minsize(420, 180)
        self.root.configure(bg="#1e1e1e")
        self.root.attributes('-alpha', 0.92)
        self.root = root
        self.root.title("Prompt Enhancer")
        # Remove window decorations (title bar, minimize, maximize, close buttons)
        # self.root.overrideredirect(True)  # Commented out so app appears in taskbar
        
        # Set fixed width for consistent appearance
        self.fixed_width = 500
        self.root.geometry(f"{self.fixed_width}x250")
        self.root.minsize(self.fixed_width, 180)
        self.root.maxsize(self.fixed_width, 1000)
        
        # Add drag functionality to move the window
        self.root.bind('<Button-1>', self.start_drag)
        self.root.bind('<B1-Motion>', self.drag_window)
        
        # Add close functionality with Escape key
        self.root.bind('<Escape>', lambda e: self.root.quit())
        self.root.focus_set()  # Make sure the window can receive key events
        
        # Dark theme colors
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.entry_bg = "#2d2d2d"
        self.button_bg = "#404040"
        self.button_hover = "#505050"
        
        # Configure style for ttk widgets
        self.setup_styles()
        # Create GUI elements
        self.create_widgets()
        
        # Bind window resize event to recalculate text heights
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Gemini API key (you'll need to set this)
        self.api_key = os.getenv('GEMINI_API_KEY')
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
          # Configure button style
        style.configure('Dark.TButton',
                       background=self.button_bg,
                       foreground=self.fg_color,
                       borderwidth=1,
                       focuscolor='none')
        style.map('Dark.TButton',
                 background=[('active', self.button_hover),
                           ('pressed', '#606060')])
    
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.bg_color, width=self.fixed_width)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        main_frame.pack_propagate(False)
        self.main_frame = main_frame
        
        # Title bar area (for dragging and close button)
        # title_frame = tk.Frame(main_frame, bg=self.bg_color)
        # title_frame.pack(fill=tk.X, pady=(0, 10))
        
        # # Title (make it draggable)
        # title_label = tk.Label(title_frame, 
        #                       text="Prompt Enhancer", 
        #                       font=("Segoe UI", 16, "bold"),
        #                       fg=self.fg_color, 
        #                       bg=self.bg_color,
        #                       cursor="fleur")  # Show drag cursor
        # title_label.pack(side=tk.LEFT, pady=(0, 10))
        
        # # Bind drag events to title
        # title_label.bind('<Button-1>', self.start_drag)
        # title_label.bind('<B1-Motion>', self.drag_window)
        
        # # Close button
        # close_button = tk.Label(title_frame,
        #                        text="✕",
        #                        font=("Segoe UI", 12, "bold"),
        #                        fg="#ff4444",
        #                        bg=self.bg_color,
        #                        cursor="hand2")
        # close_button.pack(side=tk.RIGHT)
        # close_button.bind('<Button-1>', lambda e: self.root.quit())
        # close_button.bind('<Enter>', lambda e: close_button.config(fg="#ff6666"))
        # close_button.bind('<Leave>', lambda e: close_button.config(fg="#ff4444"))
        
        # Input section
        input_label = tk.Label(main_frame, 
                              text="Enter your prompt:", 
                              font=("Segoe UI", 12),
                              fg=self.fg_color, 
                              bg=self.bg_color)
        input_label.pack(anchor='w', pady=(0, 5))# Input text area
        self.input_text = scrolledtext.ScrolledText(main_frame,
                                                   height=3,
                                                   font=("Consolas", 11),
                                                   bg=self.entry_bg,
                                                   fg=self.fg_color,
                                                   insertbackground=self.fg_color,
                                                   selectbackground="#404040",
                                                   relief='flat',
                                                   borderwidth=1,
                                                   wrap=tk.WORD)
        self.input_text.pack(fill=tk.X, pady=(0, 20))
        
        # Configure scrollbar colors for dark theme
        input_scrollbar = self.input_text.vbar
        input_scrollbar.config(bg=self.entry_bg, 
                              troughcolor=self.bg_color,
                              activebackground=self.button_bg,
                              relief='flat',
                              borderwidth=0)
        
        # Bind events for dynamic height adjustment
        self.input_text.bind('<KeyRelease>', lambda e: self.adjust_text_height(self.input_text))
        self.input_text.bind('<Button-1>', lambda e: self.root.after(10, lambda: self.adjust_text_height(self.input_text)))
        self.input_text.bind('<Control-v>', lambda e: self.root.after(10, lambda: self.adjust_text_height(self.input_text)))
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(pady=(0, 20))
        self.button_frame = button_frame
        # Enhance button (always visible)
        self.enhance_button = ttk.Button(button_frame,
                                        text="Enhance",
                                        style='Dark.TButton',
                                        command=self.enhance_prompt)
        self.enhance_button.pack(side=tk.LEFT, padx=(0, 10))
        # Clear button
        self.clear_button = ttk.Button(button_frame,
                                      text="Clear",
                                      style='Dark.TButton',
                                      command=self.clear_text)
        self.clear_button.pack(side=tk.LEFT)
        
        # Status label
        self.status_label = tk.Label(main_frame,
                                    text="Ready",
                                    font=("Segoe UI", 10),
                                    fg="#888888",
                                    bg=self.bg_color)
        self.status_label.pack(pady=(0, 10))
        
        # Output section (hidden by default)
        self.output_label = tk.Label(main_frame,
                               text="Enhanced prompt:",
                               font=("Segoe UI", 12),
                               fg=self.fg_color,
                               bg=self.bg_color)
        # self.output_label.pack(anchor='w', pady=(0, 5))  # Do not pack yet
        
        self.output_text = scrolledtext.ScrolledText(main_frame,
                                                    height=3,
                                                    font=("Consolas", 11),
                                                    bg=self.entry_bg,
                                                    fg=self.fg_color,
                                                    insertbackground=self.fg_color,
                                                    selectbackground="#404040",
                                                    relief='flat',
                                                    borderwidth=1,
                                                    wrap=tk.WORD,
                                                    state=tk.DISABLED)
        # self.output_text.pack(fill=tk.BOTH, expand=True)  # Do not pack yet
        
        # Copy button (also hidden by default)
        copy_frame = tk.Frame(main_frame, bg=self.bg_color)
        self.copy_button = ttk.Button(copy_frame,
                                     text="Copy Enhanced Prompt",
                                     style='Dark.TButton',
                                     command=self.copy_output,
                                     state=tk.DISABLED)
        self.copy_frame = copy_frame
        # self.copy_button.pack(side=tk.RIGHT)  # Do not pack yet
        
    def enhance_prompt(self):
        user_input = self.input_text.get(1.0, tk.END).strip()
        
        if not user_input:
            messagebox.showwarning("Warning", "Please enter a prompt to enhance.")
            return
            
        if not self.api_key:
            messagebox.showerror("Error", "Please set your GEMINI_API_KEY environment variable.")
            return
        
        # Disable button and show status
        self.enhance_button.config(state=tk.DISABLED)
        self.status_label.config(text="Enhancing prompt...", fg="#ffaa00")
        
        # Run API call in separate thread to prevent GUI freezing
        thread = threading.Thread(target=self.call_gemini_api, args=(user_input,))
        thread.daemon = True
        thread.start()
    
    def call_gemini_api(self, user_input):
        try:
            # Gemini API endpoint
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"
            
            # Prepare the prompt
            prompt = f"Generate an enhanced version of this prompt (reply with only the enhanced prompt - no conversation, explanations, lead-in, bullet points, placeholders, markdown formatting, or surrounding quotes. maintaining a comparable level of detail, length and complexity as the original input prompt while focusing on improving clarity, specificity, and potential for generating high-quality outputs.):\n\n{user_input}"
            
            # Request payload
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 1,
                    "topP": 1,
                    "maxOutputTokens": 2048,
                }
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            # Make the API call
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                enhanced_prompt = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Update GUI in main thread
                self.root.after(0, self.update_output, enhanced_prompt, True)
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                self.root.after(0, self.update_output, error_msg, False)
                
        except requests.exceptions.Timeout:
            self.root.after(0, self.update_output, "Request timed out. Please try again.", False)
        except requests.exceptions.RequestException as e:
            self.root.after(0, self.update_output, f"Network error: {str(e)}", False)
        except Exception as e:
            self.root.after(0, self.update_output, f"Error: {str(e)}", False)
    def adjust_text_height(self, text_widget, min_height=3, max_height=15):
        """Dynamically adjust the height of a text widget based on content"""
        content = text_widget.get(1.0, tk.END)
        lines = content.split('\n')
        
        # Calculate the number of visual lines considering word wrapping
        visual_lines = 0
        widget_width = text_widget.winfo_width()
        if widget_width <= 1:  # Widget not yet rendered
            widget_width = 600  # Approximate width
            
        font = text_widget['font']
        if isinstance(font, str):
            font_obj = tk.font.Font(family="Consolas", size=11)
        else:
            font_obj = font
            
        char_width = font_obj.measure('0')  # Approximate character width
        chars_per_line = max(1, (widget_width - 30) // char_width)  # Account for padding/scrollbar
        
        for line in lines:
            if not line:
                visual_lines += 1
            else:
                visual_lines += max(1, len(line) // chars_per_line + (1 if len(line) % chars_per_line else 0))
        
        # Ensure we stay within min/max bounds
        new_height = max(min_height, visual_lines + 1)
        
        # Only update if height changed
        current_height = int(text_widget['height'])
        if new_height != current_height:
            text_widget.config(height=new_height)
            
        # Hide scrollbar if content fits within the widget
        if visual_lines <= new_height:
            try:
                text_widget.vbar.pack_forget()
            except:
                pass
        else:
            try:
                text_widget.vbar.pack(side=tk.RIGHT, fill=tk.Y)
            except:
                pass
    
    def on_window_resize(self, event):
        """Handle window resize events to recalculate text heights"""
        # Only process resize events for the main window
        if event.widget == self.root:
            self.root.after(100, self.recalculate_text_heights)
    
    def recalculate_text_heights(self):
        """Recalculate text heights after window resize"""
        self.adjust_text_height(self.input_text)
        self.adjust_text_height(self.output_text)
    
    def update_output(self, text, success):
        # Show output section if not already visible
        if not self.output_label.winfo_ismapped():
            self.main_frame.pack_propagate(True)  # Allow frame to grow in height
            self.output_label.pack(anchor='w', pady=(0, 5))
            self.output_text.pack(fill=tk.BOTH, expand=True)
            self.copy_frame.pack(fill=tk.X, pady=(10, 0))
            self.copy_button.pack(side=tk.RIGHT)
        # Enable output text area for editing
        self.output_text.config(state=tk.NORMAL)
        # Clear previous output
        self.output_text.delete(1.0, tk.END)
        # Insert new text
        self.output_text.insert(1.0, text)
        # Disable output text area
        self.output_text.config(state=tk.DISABLED)
        # Adjust output text height based on content
        self.root.after(10, self._resize_window_to_fit)
        # Update status and button states
        if success:
            self.status_label.config(text="Prompt enhanced successfully!", fg="#00aa00")
            self.copy_button.config(state=tk.NORMAL)
        else:
            self.status_label.config(text="Failed to enhance prompt", fg="#ff4444")
            self.copy_button.config(state=tk.DISABLED)
        # Re-enable enhance button
        self.enhance_button.config(state=tk.NORMAL)

    def _resize_window_to_fit(self):
        self.root.update_idletasks()
        req_height = self.root.winfo_reqheight()
        self.root.geometry(f"{self.fixed_width}x{req_height}")

    def copy_output(self):
        output_content = self.output_text.get(1.0, tk.END).strip()
        if output_content:
            self.root.clipboard_clear()
            self.root.clipboard_append(output_content)
            self.status_label.config(text="Enhanced prompt copied to clipboard!", fg="#00aa00")
    
    def clear_text(self):
        self.input_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.copy_button.config(state=tk.DISABLED)
        self.status_label.config(text="Ready", fg="#888888")
        # Reset text area heights to minimum
        self.input_text.config(height=3)
        self.output_text.config(height=3)
        # Hide output section and shrink window
        if self.output_label.winfo_ismapped():
            self.output_label.pack_forget()
            self.output_text.pack_forget()
            self.copy_frame.pack_forget()
            self.copy_button.pack_forget()
            self.main_frame.pack_propagate(True)
            self.root.after(10, self._resize_window_to_fit)
    
    def start_drag(self, event):
        """Start dragging the window"""
        self.x = event.x
        self.y = event.y
    
    def drag_window(self, event):
        """Drag the window to a new position"""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

def main():
    root = tk.Tk()
    app = PromptEnhancerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()