"""
Story mode boss management UI
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import logging
from pathlib import Path
from src.models.story_boss import StoryBoss
from src.services.image_processor import ImageProcessor
from config.settings import Settings

logger = logging.getLogger(__name__)


class StoryBossManagerWindow:
    """Window for managing story mode bosses"""

    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db_manager = db_manager
        self.window = tk.Toplevel(parent)
        self.window.title("ストーリーモード ボス管理")
        self.window.geometry("1000x700")

        self.current_boss = None
        self.image_processor = ImageProcessor()
        self.selected_image_path = None
        self.selected_sprite_path = None

        self._create_ui()
        self._load_bosses()

    def _create_ui(self):
        """Create the UI"""
        # Main container
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - Boss list
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))

        ttk.Label(left_panel, text="ボス一覧", font=("", 12, "bold")).pack(pady=(0, 5))

        # Boss level buttons
        self.boss_buttons = {}
        for level in range(1, 6):
            btn = ttk.Button(
                left_panel,
                text=f"Lv {level}",
                command=lambda l=level: self._select_boss(l)
            )
            btn.pack(fill=tk.X, pady=2)
            self.boss_buttons[level] = btn

        # Right panel - Boss details
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Boss info frame
        info_frame = ttk.LabelFrame(right_panel, text="ボス情報", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True)

        # Level
        level_frame = ttk.Frame(info_frame)
        level_frame.pack(fill=tk.X, pady=5)
        ttk.Label(level_frame, text="レベル:", width=12).pack(side=tk.LEFT)
        self.level_var = tk.StringVar()
        self.level_label = ttk.Label(level_frame, textvariable=self.level_var)
        self.level_label.pack(side=tk.LEFT)

        # Name
        name_frame = ttk.Frame(info_frame)
        name_frame.pack(fill=tk.X, pady=5)
        ttk.Label(name_frame, text="名前:", width=12).pack(side=tk.LEFT)
        self.name_entry = ttk.Entry(name_frame, width=30)
        self.name_entry.pack(side=tk.LEFT)

        # Stats
        stats_frame = ttk.LabelFrame(info_frame, text="ステータス", padding=10)
        stats_frame.pack(fill=tk.X, pady=10)

        self.hp_var = tk.IntVar(value=100)
        self.attack_var = tk.IntVar(value=50)
        self.defense_var = tk.IntVar(value=50)
        self.speed_var = tk.IntVar(value=50)
        self.magic_var = tk.IntVar(value=50)
        self.luck_var = tk.IntVar(value=50)

        stats = [
            ("HP (10-300):", self.hp_var, 10, 300),
            ("攻撃力 (10-200):", self.attack_var, 10, 200),
            ("防御力 (10-150):", self.defense_var, 10, 150),
            ("速さ (10-150):", self.speed_var, 10, 150),
            ("魔力 (10-150):", self.magic_var, 10, 150),
            ("運 (0-100):", self.luck_var, 0, 100)
        ]

        for label_text, var, min_val, max_val in stats:
            frame = ttk.Frame(stats_frame)
            frame.pack(fill=tk.X, pady=3)
            ttk.Label(frame, text=label_text, width=15).pack(side=tk.LEFT)
            scale = ttk.Scale(frame, from_=min_val, to=max_val, variable=var, orient=tk.HORIZONTAL)
            scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            ttk.Label(frame, textvariable=var, width=5).pack(side=tk.LEFT)

        # Total stats label
        total_frame = ttk.Frame(stats_frame)
        total_frame.pack(fill=tk.X, pady=(10, 0))
        self.total_stats_label = ttk.Label(total_frame, text="Total: 350/500", foreground="blue", font=("", 10, "bold"))
        self.total_stats_label.pack(side=tk.LEFT)

        # Bind stat changes to update total
        for var in [self.hp_var, self.attack_var, self.defense_var, self.speed_var, self.magic_var, self.luck_var]:
            var.trace('w', self._update_total_stats)

        # Description
        desc_frame = ttk.Frame(info_frame)
        desc_frame.pack(fill=tk.X, pady=5)
        ttk.Label(desc_frame, text="説明:").pack(anchor=tk.W)
        self.desc_text = tk.Text(desc_frame, height=4, width=50)
        self.desc_text.pack(fill=tk.BOTH, expand=True)

        # Images
        image_frame = ttk.LabelFrame(info_frame, text="画像", padding=10)
        image_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Original image
        original_frame = ttk.Frame(image_frame)
        original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        ttk.Label(original_frame, text="オリジナル画像").pack()
        self.original_image_label = ttk.Label(original_frame, text="画像なし", relief=tk.SUNKEN)
        self.original_image_label.pack(fill=tk.BOTH, expand=True)
        ttk.Button(original_frame, text="画像選択", command=self._select_image).pack(pady=5)

        # Sprite image
        sprite_frame = ttk.Frame(image_frame)
        sprite_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        ttk.Label(sprite_frame, text="スプライト").pack()
        self.sprite_image_label = ttk.Label(sprite_frame, text="画像なし", relief=tk.SUNKEN)
        self.sprite_image_label.pack(fill=tk.BOTH, expand=True)
        ttk.Button(sprite_frame, text="スプライト生成", command=self._generate_sprite).pack(pady=5)

        # Buttons
        button_frame = ttk.Frame(right_panel)
        button_frame.pack(fill=tk.X, pady=10)
        ttk.Button(button_frame, text="保存", command=self._save_boss).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="削除", command=self._delete_boss).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="閉じる", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)

    def _update_total_stats(self, *args):
        """Update total stats display"""
        try:
            total = (self.hp_var.get() + self.attack_var.get() + self.defense_var.get() +
                    self.speed_var.get() + self.magic_var.get() + self.luck_var.get())

            # Update label color based on total (500 max for bosses)
            if total > 500:
                self.total_stats_label.config(text=f"Total: {total}/500", foreground="red")
            elif total == 500:
                self.total_stats_label.config(text=f"Total: {total}/500", foreground="green")
            else:
                self.total_stats_label.config(text=f"Total: {total}/500", foreground="blue")
        except:
            # If any value is invalid, don't update
            pass

    def _load_bosses(self):
        """Load all bosses"""
        try:
            for level in range(1, 6):
                boss = self.db_manager.get_story_boss(level)
                if boss:
                    self.boss_buttons[level].config(text=f"Lv {level}: {boss.name}")
                else:
                    self.boss_buttons[level].config(text=f"Lv {level} (未設定)")
        except Exception as e:
            logger.error(f"Error loading bosses: {e}")

    def _select_boss(self, level: int):
        """Select a boss to edit"""
        try:
            self.current_boss = self.db_manager.get_story_boss(level)

            if self.current_boss:
                # Load existing boss data
                self.level_var.set(f"Lv {self.current_boss.level}")
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, self.current_boss.name)
                self.hp_var.set(self.current_boss.hp)
                self.attack_var.set(self.current_boss.attack)
                self.defense_var.set(self.current_boss.defense)
                self.speed_var.set(self.current_boss.speed)
                self.magic_var.set(self.current_boss.magic)
                self.luck_var.set(self.current_boss.luck)
                self.desc_text.delete("1.0", tk.END)
                self.desc_text.insert("1.0", self.current_boss.description)

                # Load images
                self.selected_image_path = self.current_boss.image_path
                self.selected_sprite_path = self.current_boss.sprite_path
                self._update_image_display()
            else:
                # Create new boss
                self.level_var.set(f"Lv {level}")
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, f"Boss Lv{level}")
                self.hp_var.set(100 + (level - 1) * 40)
                self.attack_var.set(50 + (level - 1) * 30)
                self.defense_var.set(50 + (level - 1) * 20)
                self.speed_var.set(50 + (level - 1) * 25)
                self.magic_var.set(50 + (level - 1) * 20)
                self.luck_var.set(50)
                self.desc_text.delete("1.0", tk.END)
                self.selected_image_path = None
                self.selected_sprite_path = None
                self._update_image_display()

                self.current_boss = StoryBoss(
                    level=level,
                    name=f"Boss Lv{level}",
                    hp=self.hp_var.get(),
                    attack=self.attack_var.get(),
                    defense=self.defense_var.get(),
                    speed=self.speed_var.get(),
                    magic=self.magic_var.get(),
                    luck=self.luck_var.get(),
                    description=""
                )

        except Exception as e:
            logger.error(f"Error selecting boss: {e}")
            messagebox.showerror("エラー", f"ボスの読み込みに失敗しました: {e}")

    def _select_image(self):
        """Select original image"""
        file_path = filedialog.askopenfilename(
            title="画像を選択",
            filetypes=[("Image files", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            self.selected_image_path = file_path
            self._update_image_display()

    def _generate_sprite(self):
        """Generate sprite from original image"""
        if not self.selected_image_path:
            messagebox.showwarning("警告", "先にオリジナル画像を選択してください")
            return

        try:
            # Process image to create sprite
            success, message, sprite_path = self.image_processor.process_character_image(
                self.selected_image_path,
                str(Settings.SPRITES_DIR),
                f"boss_lv{self.current_boss.level}"
            )

            if success and sprite_path:
                self.selected_sprite_path = sprite_path
                self._update_image_display()
                messagebox.showinfo("成功", "スプライトを生成しました")
            else:
                messagebox.showerror("エラー", f"スプライト生成失敗: {message}")

        except Exception as e:
            logger.error(f"Error generating sprite: {e}")
            messagebox.showerror("エラー", f"スプライト生成エラー: {e}")

    def _update_image_display(self):
        """Update image displays"""
        # Update original image
        if self.selected_image_path and Path(self.selected_image_path).exists():
            try:
                img = Image.open(self.selected_image_path)
                img.thumbnail((150, 150))
                photo = ImageTk.PhotoImage(img)
                self.original_image_label.config(image=photo, text="")
                self.original_image_label.image = photo
            except:
                self.original_image_label.config(text="画像エラー")
        else:
            self.original_image_label.config(image="", text="画像なし")

        # Update sprite image
        if self.selected_sprite_path and Path(self.selected_sprite_path).exists():
            try:
                img = Image.open(self.selected_sprite_path)
                img.thumbnail((150, 150))
                photo = ImageTk.PhotoImage(img)
                self.sprite_image_label.config(image=photo, text="")
                self.sprite_image_label.image = photo
            except:
                self.sprite_image_label.config(text="画像エラー")
        else:
            self.sprite_image_label.config(image="", text="画像なし")

    def _save_boss(self):
        """Save boss data"""
        if not self.current_boss:
            messagebox.showwarning("警告", "ボスを選択してください")
            return

        try:
            # Get values from UI
            name = self.name_entry.get().strip()
            if not name:
                messagebox.showwarning("警告", "名前を入力してください")
                return

            description = self.desc_text.get("1.0", tk.END).strip()

            # Check total stats limit (500 for bosses)
            total_stats = (self.hp_var.get() + self.attack_var.get() + self.defense_var.get() +
                          self.speed_var.get() + self.magic_var.get() + self.luck_var.get())
            if total_stats > 500:
                messagebox.showwarning("警告", f"ステータス合計 ({total_stats}) が上限 (500) を超えています")
                return

            # Update boss data
            self.current_boss.name = name
            self.current_boss.hp = self.hp_var.get()
            self.current_boss.attack = self.attack_var.get()
            self.current_boss.defense = self.defense_var.get()
            self.current_boss.speed = self.speed_var.get()
            self.current_boss.magic = self.magic_var.get()
            self.current_boss.luck = self.luck_var.get()
            self.current_boss.description = description

            # Upload images if they are local files
            if self.selected_image_path and not self.selected_image_path.startswith('http'):
                # Upload to Google Drive
                from src.services.sheets_manager import SheetsManager
                if isinstance(self.db_manager, SheetsManager):
                    image_url = self.db_manager.upload_to_drive(
                        self.selected_image_path,
                        f"boss_lv{self.current_boss.level}_original{Path(self.selected_image_path).suffix}"
                    )
                    if image_url:
                        self.current_boss.image_path = image_url
                    else:
                        self.current_boss.image_path = self.selected_image_path
                else:
                    self.current_boss.image_path = self.selected_image_path

            if self.selected_sprite_path and not self.selected_sprite_path.startswith('http'):
                # Upload to Google Drive
                from src.services.sheets_manager import SheetsManager
                if isinstance(self.db_manager, SheetsManager):
                    sprite_url = self.db_manager.upload_to_drive(
                        self.selected_sprite_path,
                        f"boss_lv{self.current_boss.level}_sprite.png"
                    )
                    if sprite_url:
                        self.current_boss.sprite_path = sprite_url
                    else:
                        self.current_boss.sprite_path = self.selected_sprite_path
                else:
                    self.current_boss.sprite_path = self.selected_sprite_path

            # Save to database
            if self.db_manager.save_story_boss(self.current_boss):
                messagebox.showinfo("成功", "ボスを保存しました")
                self._load_bosses()
            else:
                messagebox.showerror("エラー", "保存に失敗しました")

        except Exception as e:
            logger.error(f"Error saving boss: {e}")
            messagebox.showerror("エラー", f"保存エラー: {e}")

    def _delete_boss(self):
        """Delete boss"""
        if not self.current_boss:
            messagebox.showwarning("警告", "ボスを選択してください")
            return

        if messagebox.askyesno("確認", f"Lv{self.current_boss.level} のボスを削除しますか?"):
            try:
                # Clear boss data (set to default)
                default_boss = StoryBoss(
                    level=self.current_boss.level,
                    name=f"Boss Lv{self.current_boss.level}",
                    hp=100,
                    attack=50,
                    defense=50,
                    speed=50,
                    magic=50,
                    luck=50,
                    description=""
                )
                if self.db_manager.save_story_boss(default_boss):
                    messagebox.showinfo("成功", "ボスを削除しました")
                    self._load_bosses()
                    self._select_boss(self.current_boss.level)
                else:
                    messagebox.showerror("エラー", "削除に失敗しました")
            except Exception as e:
                logger.error(f"Error deleting boss: {e}")
                messagebox.showerror("エラー", f"削除エラー: {e}")
