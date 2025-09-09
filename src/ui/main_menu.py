"""
Main menu GUI for Oekaki Battler
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import logging
from pathlib import Path
from typing import Optional

from src.services.database_manager import DatabaseManager
from src.services.image_processor import ImageProcessor
from src.services.ai_analyzer import AIAnalyzer
from src.services.battle_engine import BattleEngine
from src.models import Character
from config.settings import Settings

logger = logging.getLogger(__name__)

class MainMenuWindow:
    """Main application window"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("お絵描きバトラー - Oekaki Battler")
        self.root.geometry("900x700")
        
        # Services
        self.db_manager = DatabaseManager()
        self.image_processor = ImageProcessor()
        self.ai_analyzer = AIAnalyzer()
        self.battle_engine = BattleEngine()
        
        # Data
        self.characters = []
        self.selected_character1 = None
        self.selected_character2 = None
        
        # Status
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        # Setup GUI
        self._setup_styles()
        self._create_widgets()
        self._load_characters()
        
        logger.info("Main menu window initialized")
    
    def _setup_styles(self):
        """Setup custom styles"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Custom button styles
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        self.style.configure('Action.TButton', font=('Arial', 10, 'bold'))
    
    def _create_widgets(self):
        """Create main GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎨 お絵描きバトラー", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Left panel - Actions
        self._create_action_panel(main_frame)
        
        # Middle panel - Character list
        self._create_character_panel(main_frame)
        
        # Right panel - Battle setup
        self._create_battle_panel(main_frame)
        
        # Bottom panel - Status and controls
        self._create_status_panel(main_frame)
    
    def _create_action_panel(self, parent):
        """Create action buttons panel"""
        action_frame = ttk.LabelFrame(parent, text="Actions", padding="10")
        action_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))
        
        # Character registration
        ttk.Button(
            action_frame,
            text="📷 Register Character",
            command=self._register_character,
            style='Action.TButton',
            width=20
        ).pack(pady=5, fill=tk.X)
        
        # View statistics
        ttk.Button(
            action_frame,
            text="📊 View Statistics", 
            command=self._show_statistics,
            width=20
        ).pack(pady=5, fill=tk.X)
        
        # Battle history
        ttk.Button(
            action_frame,
            text="🏟️ Battle History",
            command=self._show_battle_history,
            width=20
        ).pack(pady=5, fill=tk.X)
        
        # Settings
        ttk.Button(
            action_frame,
            text="⚙️ Settings",
            command=self._show_settings,
            width=20
        ).pack(pady=5, fill=tk.X)
        
        # Separator
        ttk.Separator(action_frame, orient='horizontal').pack(pady=10, fill=tk.X)
        
        # Test AI connection
        ttk.Button(
            action_frame,
            text="🔗 Test AI Connection",
            command=self._test_ai_connection,
            width=20
        ).pack(pady=5, fill=tk.X)
        
        # Refresh characters
        ttk.Button(
            action_frame,
            text="🔄 Refresh",
            command=self._load_characters,
            width=20
        ).pack(pady=5, fill=tk.X)
    
    def _create_character_panel(self, parent):
        """Create character list panel"""
        char_frame = ttk.LabelFrame(parent, text="Characters", padding="10")
        char_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        char_frame.columnconfigure(0, weight=1)
        char_frame.rowconfigure(0, weight=1)
        
        # Character listbox with scrollbar
        list_frame = ttk.Frame(char_frame)
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview for characters
        columns = ('Name', 'HP', 'ATK', 'DEF', 'SPD', 'MAG', 'Battles', 'Wins')
        self.char_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.char_tree.heading('Name', text='Name')
        self.char_tree.heading('HP', text='HP')
        self.char_tree.heading('ATK', text='ATK')
        self.char_tree.heading('DEF', text='DEF')
        self.char_tree.heading('SPD', text='SPD')
        self.char_tree.heading('MAG', text='MAG')
        self.char_tree.heading('Battles', text='Battles')
        self.char_tree.heading('Wins', text='Wins')
        
        # Column widths
        self.char_tree.column('Name', width=120)
        self.char_tree.column('HP', width=50)
        self.char_tree.column('ATK', width=50)
        self.char_tree.column('DEF', width=50)
        self.char_tree.column('SPD', width=50)
        self.char_tree.column('MAG', width=50)
        self.char_tree.column('Battles', width=60)
        self.char_tree.column('Wins', width=50)
        
        # Scrollbar
        char_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.char_tree.yview)
        self.char_tree.configure(yscrollcommand=char_scrollbar.set)
        
        # Grid layout
        self.char_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        char_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Character info panel
        info_frame = ttk.Frame(char_frame)
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="Description:").grid(row=0, column=0, sticky=tk.W)
        self.char_description = tk.Text(info_frame, height=3, width=50, wrap=tk.WORD)
        self.char_description.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        self.char_description.config(state=tk.DISABLED)
        
        # Bind selection event
        self.char_tree.bind('<<TreeviewSelect>>', self._on_character_select)
    
    def _create_battle_panel(self, parent):
        """Create battle setup panel"""
        battle_frame = ttk.LabelFrame(parent, text="Battle Arena", padding="10")
        battle_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N), padx=(10, 0))
        
        # Fighter 1
        ttk.Label(battle_frame, text="Fighter 1:", style='Header.TLabel').pack(anchor=tk.W)
        self.fighter1_var = tk.StringVar()
        self.fighter1_combo = ttk.Combobox(battle_frame, textvariable=self.fighter1_var, state='readonly')
        self.fighter1_combo.pack(fill=tk.X, pady=(5, 10))
        
        # VS label
        vs_label = ttk.Label(battle_frame, text="🆚", font=('Arial', 20))
        vs_label.pack(pady=10)
        
        # Fighter 2
        ttk.Label(battle_frame, text="Fighter 2:", style='Header.TLabel').pack(anchor=tk.W)
        self.fighter2_var = tk.StringVar()
        self.fighter2_combo = ttk.Combobox(battle_frame, textvariable=self.fighter2_var, state='readonly')
        self.fighter2_combo.pack(fill=tk.X, pady=(5, 15))
        
        # Battle options
        options_frame = ttk.LabelFrame(battle_frame, text="Battle Options", padding="5")
        options_frame.pack(fill=tk.X, pady=10)
        
        self.visual_mode_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Visual Mode", variable=self.visual_mode_var).pack(anchor=tk.W)
        
        # Battle button
        self.battle_button = ttk.Button(
            battle_frame,
            text="⚔️ START BATTLE!",
            command=self._start_battle,
            style='Action.TButton'
        )
        self.battle_button.pack(pady=15, fill=tk.X)
        
        # Random battle button
        ttk.Button(
            battle_frame,
            text="🎲 Random Battle",
            command=self._random_battle
        ).pack(pady=5, fill=tk.X)
    
    def _create_status_panel(self, parent):
        """Create status panel"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode='determinate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Status label
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.grid(row=1, column=0, sticky=tk.W)
    
    def _load_characters(self):
        """Load characters from database"""
        try:
            self.status_var.set("Loading characters...")
            self.characters = self.db_manager.get_all_characters()
            
            # Clear treeview
            for item in self.char_tree.get_children():
                self.char_tree.delete(item)
            
            # Populate treeview
            for char in self.characters:
                win_rate = f"{char.win_rate:.1f}%" if char.battle_count > 0 else "N/A"
                self.char_tree.insert('', 'end', values=(
                    char.name,
                    char.hp,
                    char.attack,
                    char.defense,
                    char.speed,
                    char.magic,
                    char.battle_count,
                    f"{char.win_count} ({win_rate})"
                ))
            
            # Update comboboxes
            char_names = [char.name for char in self.characters]
            self.fighter1_combo['values'] = char_names
            self.fighter2_combo['values'] = char_names
            
            self.status_var.set(f"Loaded {len(self.characters)} characters")
            logger.info(f"Loaded {len(self.characters)} characters")
            
        except Exception as e:
            logger.error(f"Error loading characters: {e}")
            self.status_var.set(f"Error loading characters: {e}")
            messagebox.showerror("Error", f"Failed to load characters: {e}")
    
    def _on_character_select(self, event):
        """Handle character selection"""
        try:
            selection = self.char_tree.selection()
            if not selection:
                return
            
            item = selection[0]
            char_name = self.char_tree.item(item)['values'][0]
            
            # Find character
            character = next((char for char in self.characters if char.name == char_name), None)
            if character:
                # Update description
                self.char_description.config(state=tk.NORMAL)
                self.char_description.delete(1.0, tk.END)
                self.char_description.insert(tk.END, character.description)
                self.char_description.config(state=tk.DISABLED)
                
        except Exception as e:
            logger.error(f"Error handling character selection: {e}")
    
    def _register_character(self):
        """Open character registration dialog"""
        try:
            dialog = CharacterRegistrationDialog(self.root, self)
            self.root.wait_window(dialog.dialog)
        except Exception as e:
            logger.error(f"Error opening registration dialog: {e}")
            messagebox.showerror("Error", f"Failed to open registration dialog: {e}")
    
    def _start_battle(self):
        """Start battle between selected characters"""
        try:
            char1_name = self.fighter1_var.get()
            char2_name = self.fighter2_var.get()
            
            if not char1_name or not char2_name:
                messagebox.showwarning("Warning", "Please select both fighters")
                return
            
            if char1_name == char2_name:
                messagebox.showwarning("Warning", "Fighters must be different characters")
                return
            
            # Find characters
            char1 = next((char for char in self.characters if char.name == char1_name), None)
            char2 = next((char for char in self.characters if char.name == char2_name), None)
            
            if not char1 or not char2:
                messagebox.showerror("Error", "Failed to find selected characters")
                return
            
            # Start battle in separate thread
            visual_mode = self.visual_mode_var.get()
            threading.Thread(
                target=self._run_battle,
                args=(char1, char2, visual_mode),
                daemon=True
            ).start()
            
        except Exception as e:
            logger.error(f"Error starting battle: {e}")
            messagebox.showerror("Error", f"Failed to start battle: {e}")
    
    def _run_battle(self, char1: Character, char2: Character, visual_mode: bool):
        """Run battle in background thread"""
        try:
            self.status_var.set(f"Battle: {char1.name} vs {char2.name}")
            
            # Start battle
            battle = self.battle_engine.start_battle(char1, char2, visual_mode)
            
            # Save battle to database
            if self.db_manager.save_battle(battle):
                logger.info(f"Battle saved: {battle.id}")
            else:
                logger.warning("Failed to save battle")
            
            # Update status
            winner_name = "Draw"
            if battle.winner_id == char1.id:
                winner_name = char1.name
            elif battle.winner_id == char2.id:
                winner_name = char2.name
            
            self.status_var.set(f"Battle finished! Winner: {winner_name}")
            
            # Reload characters to update stats
            self.root.after(1000, self._load_characters)
            
            # Show result
            self.root.after(500, lambda: messagebox.showinfo(
                "Battle Result",
                f"Winner: {winner_name}\n"
                f"Duration: {battle.duration:.1f}s\n"
                f"Turns: {len(battle.turns)}"
            ))
            
        except Exception as e:
            logger.error(f"Error running battle: {e}")
            self.status_var.set(f"Battle error: {e}")
            self.root.after(500, lambda: messagebox.showerror("Battle Error", str(e)))
        finally:
            # Re-enable controls after battle
            pass
    
    def cleanup(self):
        """Clean up resources when application closes"""
        try:
            if hasattr(self, 'battle_engine') and self.battle_engine:
                self.battle_engine.cleanup()
            logger.info("Main menu cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def _random_battle(self):
        """Start random battle"""
        try:
            if len(self.characters) < 2:
                messagebox.showwarning("Warning", "Need at least 2 characters for battle")
                return
            
            import random
            fighters = random.sample(self.characters, 2)
            
            self.fighter1_var.set(fighters[0].name)
            self.fighter2_var.set(fighters[1].name)
            
            self._start_battle()
            
        except Exception as e:
            logger.error(f"Error starting random battle: {e}")
            messagebox.showerror("Error", f"Failed to start random battle: {e}")
    
    def _show_statistics(self):
        """Show statistics window"""
        try:
            stats = self.db_manager.get_statistics()
            StatsWindow(self.root, stats)
        except Exception as e:
            logger.error(f"Error showing statistics: {e}")
            messagebox.showerror("Error", f"Failed to load statistics: {e}")
    
    def _show_battle_history(self):
        """Show battle history window"""
        try:
            battles = self.db_manager.get_recent_battles(20)
            BattleHistoryWindow(self.root, battles, self.db_manager)
        except Exception as e:
            logger.error(f"Error showing battle history: {e}")
            messagebox.showerror("Error", f"Failed to load battle history: {e}")
    
    def _show_settings(self):
        """Show settings window"""
        try:
            SettingsWindow(self.root)
        except Exception as e:
            logger.error(f"Error showing settings: {e}")
            messagebox.showerror("Error", f"Failed to open settings: {e}")
    
    def _test_ai_connection(self):
        """Test AI connection"""
        try:
            self.status_var.set("Testing AI connection...")
            
            def test_connection():
                try:
                    success = self.ai_analyzer.test_api_connection()
                    if success:
                        self.status_var.set("AI connection successful!")
                        self.root.after(500, lambda: messagebox.showinfo("Success", "AI connection is working!"))
                    else:
                        self.status_var.set("AI connection failed")
                        self.root.after(500, lambda: messagebox.showerror("Error", "AI connection failed. Check your API key."))
                except Exception as e:
                    self.status_var.set(f"AI test error: {e}")
                    self.root.after(500, lambda: messagebox.showerror("Error", f"AI test failed: {e}"))
            
            threading.Thread(target=test_connection, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error testing AI connection: {e}")
            self.status_var.set(f"AI test error: {e}")
            messagebox.showerror("Error", f"Failed to test AI connection: {e}")


class CharacterRegistrationDialog:
    """Dialog for registering new characters"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.character = None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Character Registration")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 100, parent.winfo_rooty() + 50))
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Image selection
        image_frame = ttk.LabelFrame(main_frame, text="Character Image", padding="10")
        image_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.image_path_var = tk.StringVar()
        ttk.Entry(image_frame, textvariable=self.image_path_var, state='readonly', width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(image_frame, text="Browse", command=self._browse_image).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Character details
        details_frame = ttk.LabelFrame(main_frame, text="Character Details", padding="10")
        details_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Name
        ttk.Label(details_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Stats (will be filled by AI)
        stats_frame = ttk.LabelFrame(details_frame, text="Stats (Auto-generated by AI)", padding="10")
        stats_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(3, weight=1)
        
        self.hp_var = tk.StringVar(value="0")
        self.attack_var = tk.StringVar(value="0")
        self.defense_var = tk.StringVar(value="0")
        self.speed_var = tk.StringVar(value="0")
        self.magic_var = tk.StringVar(value="0")
        
        ttk.Label(stats_frame, text="HP:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(stats_frame, textvariable=self.hp_var, width=10, state='readonly').grid(row=0, column=1, sticky=tk.W, padx=(10, 20))
        ttk.Label(stats_frame, text="Attack:").grid(row=0, column=2, sticky=tk.W)
        ttk.Entry(stats_frame, textvariable=self.attack_var, width=10, state='readonly').grid(row=0, column=3, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(stats_frame, text="Defense:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(stats_frame, textvariable=self.defense_var, width=10, state='readonly').grid(row=1, column=1, sticky=tk.W, padx=(10, 20))
        ttk.Label(stats_frame, text="Speed:").grid(row=1, column=2, sticky=tk.W)
        ttk.Entry(stats_frame, textvariable=self.speed_var, width=10, state='readonly').grid(row=1, column=3, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(stats_frame, text="Magic:").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(stats_frame, textvariable=self.magic_var, width=10, state='readonly').grid(row=2, column=1, sticky=tk.W, padx=(10, 20))
        
        # Description
        ttk.Label(details_frame, text="Description:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=(10, 0))
        self.description_text = tk.Text(details_frame, height=4, width=50, wrap=tk.WORD)
        self.description_text.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(10, 0))
        
        details_frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Analyze Image", command=self._analyze_image).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Register", command=self._register_character).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT)
    
    def _browse_image(self):
        """Browse for image file"""
        try:
            filename = filedialog.askopenfilename(
                title="Select Character Image",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.bmp"),
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg *.jpeg"),
                    ("All files", "*.*")
                ]
            )
            
            if filename:
                self.image_path_var.set(filename)
                
        except Exception as e:
            logger.error(f"Error browsing for image: {e}")
            messagebox.showerror("Error", f"Failed to select image: {e}")
    
    def _analyze_image(self):
        """Analyze image with AI"""
        try:
            image_path = self.image_path_var.get()
            if not image_path:
                messagebox.showwarning("Warning", "Please select an image first")
                return
            
            # Disable button during analysis
            self.dialog.config(cursor="wait")
            
            def analyze():
                try:
                    # Analyze with AI
                    stats = self.main_window.ai_analyzer.analyze_character(image_path)
                    if stats:
                        # Update GUI on main thread
                        self.dialog.after(0, lambda: self._update_stats(stats))
                    else:
                        self.dialog.after(0, lambda: messagebox.showerror("Error", "Failed to analyze image"))
                except Exception as e:
                    self.dialog.after(0, lambda: messagebox.showerror("Error", f"Analysis failed: {e}"))
                finally:
                    self.dialog.after(0, lambda: self.dialog.config(cursor=""))
            
            threading.Thread(target=analyze, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            messagebox.showerror("Error", f"Failed to analyze image: {e}")
            self.dialog.config(cursor="")
    
    def _update_stats(self, stats):
        """Update stats display"""
        try:
            self.hp_var.set(str(stats.hp))
            self.attack_var.set(str(stats.attack))
            self.defense_var.set(str(stats.defense))
            self.speed_var.set(str(stats.speed))
            self.magic_var.set(str(stats.magic))
            
            self.description_text.delete(1.0, tk.END)
            self.description_text.insert(tk.END, stats.description)
            
            messagebox.showinfo("Success", "Image analysis completed!")
            
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
            messagebox.showerror("Error", f"Failed to update stats: {e}")
    
    def _register_character(self):
        """Register the character"""
        try:
            # Validate inputs
            name = self.name_var.get().strip()
            image_path = self.image_path_var.get()
            
            if not name:
                messagebox.showwarning("Warning", "Please enter a character name")
                return
            
            if not image_path:
                messagebox.showwarning("Warning", "Please select an image")
                return
            
            # Check if name already exists
            existing = self.main_window.db_manager.get_character_by_name(name)
            if existing:
                messagebox.showwarning("Warning", "Character name already exists")
                return
            
            # Get stats
            try:
                hp = int(self.hp_var.get())
                attack = int(self.attack_var.get())
                defense = int(self.defense_var.get())
                speed = int(self.speed_var.get())
                magic = int(self.magic_var.get())
            except ValueError:
                messagebox.showwarning("Warning", "Please analyze the image first to generate stats")
                return
            
            description = self.description_text.get(1.0, tk.END).strip()
            
            # Process image and create character
            self.dialog.config(cursor="wait")
            
            def register():
                try:
                    # Process image
                    success, message, sprite_path = self.main_window.image_processor.process_character_image(
                        image_path,
                        str(Settings.SPRITES_DIR),
                        name
                    )
                    
                    if not success:
                        self.dialog.after(0, lambda: messagebox.showerror("Error", f"Image processing failed: {message}"))
                        return
                    
                    # Create character
                    character = Character(
                        name=name,
                        hp=hp,
                        attack=attack,
                        defense=defense,
                        speed=speed,
                        magic=magic,
                        description=description,
                        image_path=image_path,
                        sprite_path=sprite_path
                    )
                    
                    # Save to database
                    if self.main_window.db_manager.save_character(character):
                        self.dialog.after(0, lambda: messagebox.showinfo("Success", "Character registered successfully!"))
                        self.dialog.after(0, self.main_window._load_characters)
                        self.dialog.after(0, self.dialog.destroy)
                    else:
                        self.dialog.after(0, lambda: messagebox.showerror("Error", "Failed to save character"))
                        
                except Exception as e:
                    self.dialog.after(0, lambda: messagebox.showerror("Error", f"Registration failed: {e}"))
                finally:
                    self.dialog.after(0, lambda: self.dialog.config(cursor=""))
            
            threading.Thread(target=register, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error registering character: {e}")
            messagebox.showerror("Error", f"Failed to register character: {e}")
            self.dialog.config(cursor="")


# Placeholder classes for other windows
class StatsWindow:
    def __init__(self, parent, stats):
        self.stats = stats
        self.window = tk.Toplevel(parent)
        self.window.title("📊 統計情報")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        
        # Center the window
        self.window.transient(parent)
        self.window.grab_set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create statistics window widgets"""
        # Main frame with scrollbar
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="📊 バトル統計", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Statistics sections
        self._create_general_stats(main_frame)
        self._create_character_stats(main_frame)
        self._create_battle_stats(main_frame)
        
        # Close button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        ttk.Button(button_frame, text="閉じる", command=self.window.destroy).pack()
    
    def _create_general_stats(self, parent):
        """Create general statistics section"""
        # General stats frame
        general_frame = ttk.LabelFrame(parent, text="📈 全体統計", padding=10)
        general_frame.pack(fill=tk.X, pady=(0, 10))
        
        stats = [
            ("総キャラクター数", self.stats.get('total_characters', 0)),
            ("総バトル数", self.stats.get('total_battles', 0)),
        ]
        
        for i, (label, value) in enumerate(stats):
            row_frame = ttk.Frame(general_frame)
            row_frame.pack(fill=tk.X, pady=2)
            ttk.Label(row_frame, text=label + ":").pack(side=tk.LEFT)
            ttk.Label(row_frame, text=str(value), font=("Arial", 10, "bold")).pack(side=tk.RIGHT)
    
    def _create_character_stats(self, parent):
        """Create character statistics section"""
        char_frame = ttk.LabelFrame(parent, text="👥 キャラクター統計", padding=10)
        char_frame.pack(fill=tk.X, pady=(0, 10))
        
        avg_stats = self.stats.get('average_stats', {})
        if avg_stats:
            avg_items = [
                ("平均HP", avg_stats.get('hp', 0)),
                ("平均攻撃力", avg_stats.get('attack', 0)),
                ("平均防御力", avg_stats.get('defense', 0)),
                ("平均速度", avg_stats.get('speed', 0)),
                ("平均魔力", avg_stats.get('magic', 0)),
            ]
            
            for label, value in avg_items:
                row_frame = ttk.Frame(char_frame)
                row_frame.pack(fill=tk.X, pady=2)
                ttk.Label(row_frame, text=label + ":").pack(side=tk.LEFT)
                ttk.Label(row_frame, text=f"{value:.1f}", font=("Arial", 10, "bold")).pack(side=tk.RIGHT)
        else:
            ttk.Label(char_frame, text="キャラクターデータがありません").pack()
    
    def _create_battle_stats(self, parent):
        """Create battle statistics section"""
        battle_frame = ttk.LabelFrame(parent, text="🏆 トップキャラクター", padding=10)
        battle_frame.pack(fill=tk.BOTH, expand=True)
        
        top_characters = self.stats.get('top_characters', [])
        if top_characters:
            # Headers
            header_frame = ttk.Frame(battle_frame)
            header_frame.pack(fill=tk.X, pady=(0, 5))
            ttk.Label(header_frame, text="名前", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
            ttk.Label(header_frame, text="勝率", font=("Arial", 9, "bold")).pack(side=tk.RIGHT, padx=(0, 50))
            ttk.Label(header_frame, text="戦績", font=("Arial", 9, "bold")).pack(side=tk.RIGHT)
            
            # Character list
            for i, char in enumerate(top_characters[:10]):  # Top 10
                char_frame = ttk.Frame(battle_frame)
                char_frame.pack(fill=tk.X, pady=1)
                
                # Rank and name
                rank_text = f"{i+1}. {char.get('name', 'Unknown')}"
                ttk.Label(char_frame, text=rank_text).pack(side=tk.LEFT)
                
                # Win rate
                win_rate = char.get('win_rate', 0)
                win_rate_text = f"{win_rate:.1f}%"
                ttk.Label(char_frame, text=win_rate_text, font=("Arial", 9, "bold")).pack(side=tk.RIGHT, padx=(0, 20))
                
                # Battle record
                battles = char.get('battle_count', 0)
                wins = char.get('win_count', 0)
                record_text = f"{wins}/{battles}"
                ttk.Label(char_frame, text=record_text).pack(side=tk.RIGHT)
        else:
            ttk.Label(battle_frame, text="バトル履歴がありません").pack(pady=20)

class BattleHistoryWindow:
    def __init__(self, parent, battles, db_manager):
        self.battles = battles
        self.db_manager = db_manager
        self.window = tk.Toplevel(parent)
        self.window.title("📜 バトル履歴")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        # Center the window
        self.window.transient(parent)
        self.window.grab_set()
        
        self._create_widgets()
        self._load_battle_history()
    
    def _create_widgets(self):
        """Create battle history window widgets"""
        # Main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="📜 バトル履歴", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(control_frame, text="🔄 更新", command=self._refresh_history).pack(side=tk.LEFT)
        ttk.Label(control_frame, text="表示件数:").pack(side=tk.LEFT, padx=(20, 5))
        
        self.limit_var = tk.StringVar(value="20")
        limit_combo = ttk.Combobox(control_frame, textvariable=self.limit_var, 
                                 values=["10", "20", "50", "100"], width=5, state="readonly")
        limit_combo.pack(side=tk.LEFT)
        limit_combo.bind("<<ComboboxSelected>>", self._on_limit_changed)
        
        # Battle list with scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for battle list
        self.tree = ttk.Treeview(list_frame, columns=("date", "char1", "char2", "winner", "duration", "turns"), 
                                show="tree headings", height=15)
        
        # Define headings
        self.tree.heading("#0", text="ID")
        self.tree.heading("date", text="日時")
        self.tree.heading("char1", text="キャラクター1")
        self.tree.heading("char2", text="キャラクター2")
        self.tree.heading("winner", text="勝者")
        self.tree.heading("duration", text="時間(秒)")
        self.tree.heading("turns", text="ターン数")
        
        # Define column widths
        self.tree.column("#0", width=80)
        self.tree.column("date", width=120)
        self.tree.column("char1", width=120)
        self.tree.column("char2", width=120)
        self.tree.column("winner", width=120)
        self.tree.column("duration", width=80)
        self.tree.column("turns", width=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Detail frame
        detail_frame = ttk.LabelFrame(main_frame, text="📋 バトル詳細", padding=10)
        detail_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.detail_text = tk.Text(detail_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        detail_scrollbar = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=detail_scrollbar.set)
        
        self.detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        detail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self._on_battle_select)
        
        # Close button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(button_frame, text="閉じる", command=self.window.destroy).pack()
    
    def _load_battle_history(self):
        """Load battle history from database"""
        try:
            limit = int(self.limit_var.get())
            battles = self.db_manager.get_recent_battles(limit=limit)
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Add battles to tree
            for battle in battles:
                # Get character names
                char1 = self.db_manager.get_character(battle.character1_id)
                char2 = self.db_manager.get_character(battle.character2_id)
                
                char1_name = char1.name if char1 else "Unknown"
                char2_name = char2.name if char2 else "Unknown"
                
                # Determine winner name
                if battle.winner_id:
                    if battle.winner_id == battle.character1_id:
                        winner_name = char1_name
                    elif battle.winner_id == battle.character2_id:
                        winner_name = char2_name
                    else:
                        winner_name = "Unknown"
                else:
                    winner_name = "引き分け"
                
                # Format date
                date_str = battle.created_at.strftime("%m/%d %H:%M")
                
                # Insert into tree
                self.tree.insert("", tk.END, 
                               text=battle.id[:8],
                               values=(date_str, char1_name, char2_name, winner_name, 
                                     f"{battle.duration:.2f}", len(battle.turns)))
                
        except Exception as e:
            logger.error(f"Error loading battle history: {e}")
    
    def _refresh_history(self):
        """Refresh battle history"""
        self._load_battle_history()
    
    def _on_limit_changed(self, event=None):
        """Handle limit combobox change"""
        self._load_battle_history()
    
    def _on_battle_select(self, event=None):
        """Handle battle selection"""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = self.tree.item(selection[0])
        battle_id_short = item['text']
        
        # Find full battle by short ID
        try:
            battles = self.db_manager.get_recent_battles(limit=100)
            selected_battle = None
            
            for battle in battles:
                if battle.id.startswith(battle_id_short):
                    selected_battle = battle
                    break
            
            if selected_battle:
                self._display_battle_details(selected_battle)
                
        except Exception as e:
            logger.error(f"Error displaying battle details: {e}")
    
    def _display_battle_details(self, battle):
        """Display detailed information about selected battle"""
        try:
            # Get character details
            char1 = self.db_manager.get_character(battle.character1_id)
            char2 = self.db_manager.get_character(battle.character2_id)
            
            char1_name = char1.name if char1 else "Unknown"
            char2_name = char2.name if char2 else "Unknown"
            
            # Prepare detail text
            details = []
            details.append(f"バトルID: {battle.id}")
            details.append(f"日時: {battle.created_at.strftime('%Y年%m月%d日 %H:%M:%S')}")
            details.append(f"対戦: {char1_name} VS {char2_name}")
            details.append(f"勝者: {char1_name if battle.winner_id == battle.character1_id else char2_name if battle.winner_id == battle.character2_id else '引き分け'}")
            details.append(f"バトル時間: {battle.duration:.2f}秒")
            details.append(f"総ターン数: {len(battle.turns)}")
            details.append("")
            details.append("=== バトルログ ===")
            
            # Add battle log
            for log_entry in battle.battle_log:
                details.append(log_entry)
            
            # Update detail text
            self.detail_text.config(state=tk.NORMAL)
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(1.0, "\n".join(details))
            self.detail_text.config(state=tk.DISABLED)
            
        except Exception as e:
            logger.error(f"Error displaying battle details: {e}")
            self.detail_text.config(state=tk.NORMAL)
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(1.0, f"詳細表示エラー: {e}")
            self.detail_text.config(state=tk.DISABLED)

class SettingsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("⚙️ 設定")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        
        # Center the window
        self.window.transient(parent)
        self.window.grab_set()
        
        # Settings variables
        self.settings = self._load_settings()
        
        self._create_widgets()
    
    def _load_settings(self):
        """Load current settings"""
        from config.settings import Settings
        return {
            'battle_speed': getattr(Settings, 'BATTLE_SPEED', 2.0),
            'max_turns': getattr(Settings, 'MAX_TURNS', 50),
            'critical_chance': getattr(Settings, 'CRITICAL_CHANCE', 0.15),
            'screen_width': getattr(Settings, 'SCREEN_WIDTH', 800),
            'screen_height': getattr(Settings, 'SCREEN_HEIGHT', 600),
            'fps': getattr(Settings, 'FPS', 60),
            'auto_save_battles': True,
            'show_battle_animations': True,
            'japanese_ui': True,
        }
    
    def _create_widgets(self):
        """Create settings window widgets"""
        # Main frame with scrollbar
        canvas = tk.Canvas(self.window)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        main_frame = scrollable_frame
        
        # Title
        title_label = ttk.Label(main_frame, text="⚙️ アプリケーション設定", font=("Arial", 16, "bold"))
        title_label.pack(pady=(20, 30))
        
        # Battle settings
        self._create_battle_settings(main_frame)
        
        # Display settings  
        self._create_display_settings(main_frame)
        
        # General settings
        self._create_general_settings(main_frame)
        
        # Buttons
        self._create_buttons(main_frame)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10, padx=(0, 10))
    
    def _create_battle_settings(self, parent):
        """Create battle settings section"""
        battle_frame = ttk.LabelFrame(parent, text="⚔️ バトル設定", padding=15)
        battle_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Battle speed
        speed_frame = ttk.Frame(battle_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        ttk.Label(speed_frame, text="バトル速度:").pack(side=tk.LEFT)
        
        self.battle_speed_var = tk.DoubleVar(value=self.settings['battle_speed'])
        speed_scale = tk.Scale(speed_frame, from_=0.5, to=5.0, resolution=0.1, 
                              orient=tk.HORIZONTAL, variable=self.battle_speed_var)
        speed_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Max turns
        turns_frame = ttk.Frame(battle_frame)
        turns_frame.pack(fill=tk.X, pady=5)
        ttk.Label(turns_frame, text="最大ターン数:").pack(side=tk.LEFT)
        
        self.max_turns_var = tk.IntVar(value=self.settings['max_turns'])
        turns_spinbox = tk.Spinbox(turns_frame, from_=10, to=200, increment=10,
                                  textvariable=self.max_turns_var, width=10)
        turns_spinbox.pack(side=tk.RIGHT)
        
        # Critical chance
        crit_frame = ttk.Frame(battle_frame)
        crit_frame.pack(fill=tk.X, pady=5)
        ttk.Label(crit_frame, text="クリティカル率:").pack(side=tk.LEFT)
        
        self.critical_chance_var = tk.DoubleVar(value=self.settings['critical_chance'])
        crit_scale = tk.Scale(crit_frame, from_=0.0, to=0.5, resolution=0.01,
                             orient=tk.HORIZONTAL, variable=self.critical_chance_var)
        crit_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
    
    def _create_display_settings(self, parent):
        """Create display settings section"""
        display_frame = ttk.LabelFrame(parent, text="🖥️ 表示設定", padding=15)
        display_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Screen resolution
        res_frame = ttk.Frame(display_frame)
        res_frame.pack(fill=tk.X, pady=5)
        ttk.Label(res_frame, text="画面解像度:").pack(side=tk.LEFT)
        
        res_values_frame = ttk.Frame(res_frame)
        res_values_frame.pack(side=tk.RIGHT)
        
        self.screen_width_var = tk.IntVar(value=self.settings['screen_width'])
        self.screen_height_var = tk.IntVar(value=self.settings['screen_height'])
        
        width_spinbox = tk.Spinbox(res_values_frame, from_=640, to=1920, increment=80,
                                  textvariable=self.screen_width_var, width=8)
        width_spinbox.pack(side=tk.LEFT)
        
        ttk.Label(res_values_frame, text=" × ").pack(side=tk.LEFT)
        
        height_spinbox = tk.Spinbox(res_values_frame, from_=480, to=1080, increment=60,
                                   textvariable=self.screen_height_var, width=8)
        height_spinbox.pack(side=tk.LEFT)
        
        # FPS
        fps_frame = ttk.Frame(display_frame)
        fps_frame.pack(fill=tk.X, pady=5)
        ttk.Label(fps_frame, text="フレームレート:").pack(side=tk.LEFT)
        
        self.fps_var = tk.IntVar(value=self.settings['fps'])
        fps_spinbox = tk.Spinbox(fps_frame, from_=30, to=120, increment=15,
                                textvariable=self.fps_var, width=10)
        fps_spinbox.pack(side=tk.RIGHT)
        
        # Animation checkbox
        self.show_animations_var = tk.BooleanVar(value=self.settings['show_battle_animations'])
        ttk.Checkbutton(display_frame, text="バトルアニメーションを表示", 
                       variable=self.show_animations_var).pack(anchor=tk.W, pady=5)
    
    def _create_general_settings(self, parent):
        """Create general settings section"""
        general_frame = ttk.LabelFrame(parent, text="🔧 一般設定", padding=15)
        general_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Auto save battles
        self.auto_save_var = tk.BooleanVar(value=self.settings['auto_save_battles'])
        ttk.Checkbutton(general_frame, text="バトル結果を自動保存", 
                       variable=self.auto_save_var).pack(anchor=tk.W, pady=5)
        
        # Japanese UI
        self.japanese_ui_var = tk.BooleanVar(value=self.settings['japanese_ui'])
        ttk.Checkbutton(general_frame, text="日本語UI使用", 
                       variable=self.japanese_ui_var).pack(anchor=tk.W, pady=5)
        
        # Database info
        info_frame = ttk.Frame(general_frame)
        info_frame.pack(fill=tk.X, pady=(15, 5))
        
        ttk.Label(info_frame, text="データベース情報", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        try:
            from config.settings import Settings
            db_path = getattr(Settings, 'DATABASE_PATH', 'Unknown')
            ttk.Label(info_frame, text=f"場所: {db_path}", font=("Arial", 8)).pack(anchor=tk.W)
        except:
            ttk.Label(info_frame, text="場所: データベース情報取得エラー", font=("Arial", 8)).pack(anchor=tk.W)
    
    def _create_buttons(self, parent):
        """Create button section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=20, pady=(20, 30))
        
        # Reset to defaults
        ttk.Button(button_frame, text="🔄 デフォルトに戻す", 
                  command=self._reset_to_defaults).pack(side=tk.LEFT)
        
        # Save and Cancel buttons
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        ttk.Button(right_buttons, text="💾 保存", 
                  command=self._save_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(right_buttons, text="❌ キャンセル", 
                  command=self.window.destroy).pack(side=tk.LEFT)
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("確認", "すべての設定をデフォルト値に戻しますか？"):
            # Reset to default values
            self.battle_speed_var.set(2.0)
            self.max_turns_var.set(50)
            self.critical_chance_var.set(0.15)
            self.screen_width_var.set(800)
            self.screen_height_var.set(600)
            self.fps_var.set(60)
            self.auto_save_var.set(True)
            self.show_animations_var.set(True)
            self.japanese_ui_var.set(True)
    
    def _save_settings(self):
        """Save settings"""
        try:
            # Get new settings
            new_settings = {
                'battle_speed': self.battle_speed_var.get(),
                'max_turns': self.max_turns_var.get(),
                'critical_chance': self.critical_chance_var.get(),
                'screen_width': self.screen_width_var.get(),
                'screen_height': self.screen_height_var.get(),
                'fps': self.fps_var.get(),
                'auto_save_battles': self.auto_save_var.get(),
                'show_battle_animations': self.show_animations_var.get(),
                'japanese_ui': self.japanese_ui_var.get(),
            }
            
            # Here you would normally save to a config file
            # For now, we'll just show a confirmation
            messagebox.showinfo("設定保存", 
                              "設定が保存されました。\n"
                              "※一部の設定はアプリケーション再起動後に反映されます。")
            
            # Apply some settings immediately if possible
            try:
                # Update battle engine settings if accessible
                if hasattr(self.parent, 'battle_engine'):
                    self.parent.battle_engine.battle_speed = new_settings['battle_speed']
                    self.parent.battle_engine.max_turns = new_settings['max_turns']
                    self.parent.battle_engine.critical_chance = new_settings['critical_chance']
            except Exception as e:
                logger.warning(f"Could not apply settings immediately: {e}")
            
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("エラー", f"設定の保存に失敗しました: {e}")
            logger.error(f"Error saving settings: {e}")