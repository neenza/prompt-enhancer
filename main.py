import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import requests
import json
import os

class PromptEnhancerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Prompt Enhancer")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")
        
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
        
        # Gemini API key (you'll need to set this)
        self.api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyDRl2PR0JF8LhYFTZqzv8nqp2vp54tKfw4')
        
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
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="Prompt Enhancer", 
                              font=("Segoe UI", 24, "bold"),
                              fg=self.fg_color, 
                              bg=self.bg_color)
        title_label.pack(pady=(0, 20))
        
        # Input section
        input_label = tk.Label(main_frame, 
                              text="Enter your prompt:", 
                              font=("Segoe UI", 12),
                              fg=self.fg_color, 
                              bg=self.bg_color)
        input_label.pack(anchor='w', pady=(0, 5))
        
        # Input text area
        self.input_text = scrolledtext.ScrolledText(main_frame,
                                                   height=8,
                                                   font=("Consolas", 11),
                                                   bg=self.entry_bg,
                                                   fg=self.fg_color,
                                                   insertbackground=self.fg_color,
                                                   selectbackground="#404040",
                                                   relief='flat',
                                                   borderwidth=1,
                                                   wrap=tk.WORD)
        self.input_text.pack(fill=tk.X, pady=(0, 20))
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(pady=(0, 20))
        
        # Enhance button
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
        
        # Output section
        output_label = tk.Label(main_frame,
                               text="Enhanced prompt:",
                               font=("Segoe UI", 12),
                               fg=self.fg_color,
                               bg=self.bg_color)
        output_label.pack(anchor='w', pady=(0, 5))
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(main_frame,
                                                    height=8,
                                                    font=("Consolas", 11),
                                                    bg=self.entry_bg,
                                                    fg=self.fg_color,
                                                    insertbackground=self.fg_color,
                                                    selectbackground="#404040",
                                                    relief='flat',
                                                    borderwidth=1,
                                                    wrap=tk.WORD,
                                                    state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Copy button
        copy_frame = tk.Frame(main_frame, bg=self.bg_color)
        copy_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.copy_button = ttk.Button(copy_frame,
                                     text="Copy Enhanced Prompt",
                                     style='Dark.TButton',
                                     command=self.copy_output,
                                     state=tk.DISABLED)
        self.copy_button.pack(side=tk.RIGHT)
        
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
    
    def update_output(self, text, success):
        # Enable output text area for editing
        self.output_text.config(state=tk.NORMAL)
        
        # Clear previous output
        self.output_text.delete(1.0, tk.END)
        
        # Insert new text
        self.output_text.insert(1.0, text)
        
        # Disable output text area
        self.output_text.config(state=tk.DISABLED)
        
        # Update status and button states
        if success:
            self.status_label.config(text="Prompt enhanced successfully!", fg="#00aa00")
            self.copy_button.config(state=tk.NORMAL)
        else:
            self.status_label.config(text="Failed to enhance prompt", fg="#ff4444")
            self.copy_button.config(state=tk.DISABLED)
        
        # Re-enable enhance button
        self.enhance_button.config(state=tk.NORMAL)
    
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

def main():
    root = tk.Tk()
    app = PromptEnhancerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()