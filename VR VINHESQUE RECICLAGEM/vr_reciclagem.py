import customtkinter as ctk
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps, ImageTk, ImageWin
from datetime import datetime, timedelta
from tkinter import messagebox, simpledialog, ttk
from io import BytesIO
import os
import sqlite3
import sys

try:
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
except Exception:
    matplotlib = None
    plt = None


def enable_windows_dpi_awareness():
    if os.name != "nt":
        return
    try:
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


enable_windows_dpi_awareness()

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

USUARIO_ADMIN = "Adriel"
SENHA_ADMIN = "1357"


class MenuCard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        title,
        subtitle,
        icon="",
        icon_image=None,
        color="#EAF2E7",
        button_color="#84C75B",
        command=None,
        *args,
        **kwargs
    ):
        card_height = int(kwargs.get("height", 166))
        super().__init__(master, fg_color=color, corner_radius=18, *args, **kwargs)
        self.grid_propagate(False)
        self.command = command if command else lambda: None
        self.default_color = color

        tall_layout = card_height > 180
        extra_tall_layout = card_height > 260
        icon_y = 36 if extra_tall_layout else 24 if tall_layout else 14
        title_y = 104 if extra_tall_layout else 74 if tall_layout else 58
        subtitle_y = 146 if extra_tall_layout else 104 if tall_layout else 86

        self.icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=button_color
        )
        self.icon_label.place(relx=0.5, y=icon_y, anchor="n")

        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#1B1B1B"
        )
        self.title_label.place(relx=0.5, y=title_y, anchor="n")

        self.subtitle_label = ctk.CTkLabel(
            self,
            text=subtitle,
            justify="center",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#424242",
            wraplength=145
        )
        self.subtitle_label.place(relx=0.5, y=subtitle_y, anchor="n")

        self.action_button = ctk.CTkButton(
            self,
            text="›",
            width=32,
            height=32,
            corner_radius=16,
            fg_color=button_color,
            hover_color=button_color,
            text_color="white",
            font=ctk.CTkFont(size=21, weight="bold"),
            command=self.command
        )
        self.action_button.place(relx=0.5, y=button_y, anchor="n")
        self.bind("<Button-1>", lambda _event: self.command())


class TopInfoCard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        icon,
        title,
        value,
        accent="#2F80ED",
        subtitle="",
        dark=False,
        sparkline_image=None,
        *args,
        **kwargs
    ):
        fg = "#0B4A1F" if dark else "white"
        border = "#0B4A1F" if dark else "#E7E7E7"
        card_width = int(kwargs.get("width", 280))
        card_height = int(kwargs.get("height", 112))

        super().__init__(master, fg_color=fg, corner_radius=24, *args, **kwargs)
        self.grid_propagate(False)
        self.configure(border_width=1 if not dark else 0, border_color=border)
        self.sparkline_image = sparkline_image

        if dark:
            self.icon_box = ctk.CTkFrame(
                self,
                width=58,
                height=58,
                fg_color="#0F5A29",
                corner_radius=18
            )
            self.icon_box.place(x=18, y=18)
            self.icon_box.pack_propagate(False)

            self.icon_label = ctk.CTkLabel(
                self.icon_box,
                text=icon,
                font=ctk.CTkFont(size=26, weight="bold"),
                text_color="white"
            )
            self.icon_label.pack(expand=True)

            self.title_label = ctk.CTkLabel(
                self,
                text=title,
                font=ctk.CTkFont(size=15),
                text_color="#DDEBDD"
            )
            self.title_label.place(x=88, y=22)

            self.value_label = ctk.CTkLabel(
                self,
                text=value,
                font=ctk.CTkFont(size=17, weight="bold"),
                text_color="white"
            )
            self.value_label.place(x=88, y=48)

            self.subtitle_label = ctk.CTkLabel(
                self,
                text=subtitle,
                font=ctk.CTkFont(size=13),
                text_color="#DDEBDD"
            )
            self.subtitle_label.place(x=88, y=82)
        else:
            self.icon_box = ctk.CTkFrame(
                self,
                width=58,
                height=58,
                fg_color=accent,
                corner_radius=18
            )
            self.icon_box.place(x=18, y=18)
            self.icon_box.pack_propagate(False)

            self.icon_label = ctk.CTkLabel(
                self.icon_box,
                text=icon,
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="white"
            )
            self.icon_label.pack(expand=True)

            self.title_label = ctk.CTkLabel(
                self,
                text=title,
                font=ctk.CTkFont(size=15),
                text_color="#333333"
            )
            self.title_label.place(x=96, y=22)

            self.value_label = ctk.CTkLabel(
                self,
                text=value,
                font=ctk.CTkFont(size=25, weight="bold"),
                text_color="#111111"
            )
            self.value_label.place(x=96, y=46)

            self.subtitle_label = ctk.CTkLabel(
                self,
                text=subtitle,
                font=ctk.CTkFont(size=13),
                text_color="#6A6A6A"
            )
            self.subtitle_label.place(x=96, y=94)

            if self.sparkline_image is not None:
                sparkline_width = min(152, max(96, card_width - 190))
                sparkline_x = card_width - sparkline_width - 18
                self.sparkline_label = ctk.CTkLabel(
                    self,
                    text="",
                    image=self.sparkline_image,
                    fg_color="transparent",
                )
                self.sparkline_label.place(x=sparkline_x, y=26)


class VRReciclagemApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("VR Vinhesque Reciclagem")
        self.apply_screen_fit()
        self.configure_fullscreen()
        self.configure(fg_color="#F4F4F1")

        self.script_dir = self.app_base_dir()
        self.resource_dir = self.app_resource_dir()
        self.asset_dir = os.path.join(self.resource_dir, "assets")
        self.logo_path = self.first_existing_path(
            os.path.join(self.script_dir, "logo.png"),
            os.path.join(self.asset_dir, "logo_design.png"),
            os.path.join(self.asset_dir, "logo_vr.png"),
        )
        self.comprovante_logo_path = self.first_existing_path(
            os.path.join(self.asset_dir, "logo_comprovante_preta.png"),
            os.path.join(self.script_dir, "logo_comprovante_preta.png"),
            r"C:\Users\User\Downloads\logo-vinhesque-preta.png",
            self.logo_path,
        )
        self.login_background_path = self.first_existing_path(
            os.path.join(self.asset_dir, "fundo-login-vinhesque.png"),
            os.path.join(self.script_dir, "fundo-login-vinhesque.png"),
            r"C:\Users\User\Downloads\fundo-login-vinhesque.png",
        )
        self.login_brand_logo_path = self.first_existing_path(
            os.path.join(self.resource_dir, "logo.png"),
            os.path.join(self.script_dir, "logo.png"),
            os.path.join(self.asset_dir, "logo_design.png"),
            os.path.join(self.asset_dir, "logo_vr.png"),
            self.logo_path,
        )
        self.login_badge_icon_path = self.first_existing_path(
            os.path.join(self.asset_dir, "login-badge-shield.png"),
            os.path.join(self.script_dir, "login-badge-shield.png"),
            r"C:\Users\User\Downloads\ChatGPT Image 6 de mai. de 2026, 14_14_06.png",
        )
        self.auth_dialog_badge_icon_path = self.first_existing_path(
            os.path.join(self.asset_dir, "acesso-restrito-vinhesque.png"),
            os.path.join(self.script_dir, "acesso-restrito-vinhesque.png"),
            r"C:\Users\User\Downloads\acesso-restrito-vinhesque.png",
        )
        self.header_brand_logo_path = self.first_existing_path(
            os.path.join(self.asset_dir, "logo-vr-verde.png"),
            os.path.join(self.script_dir, "logo-vr-verde.png"),
            r"C:\Users\User\Downloads\logo-vr-verde.png",
            self.logo_path,
        )
        self.footer_security_icon_path = self.first_existing_path(
            os.path.join(self.asset_dir, "seguranca-png.png"),
            os.path.join(self.script_dir, "seguranca-png.png"),
            r"C:\Users\User\Downloads\segunrança-png.png",
        )
        self.whatsapp_logo_path = self.first_existing_path(
            os.path.join(self.asset_dir, "logo-whatsapp.png"),
            os.path.join(self.script_dir, "logo-whatsapp.png"),
            r"C:\Users\User\Downloads\logo-whatsapp.png",
        )
        self.poppins_semibold_font_path = self.first_existing_path(
            os.path.join(self.asset_dir, "Poppins-SemiBold.ttf"),
            os.path.join(self.script_dir, "Poppins-SemiBold.ttf"),
            r"C:\Windows\Fonts\Poppins-SemiBold.ttf",
        )
        self.inter_regular_font_path = self.first_existing_path(
            os.path.join(self.asset_dir, "Inter-Regular.ttf"),
            os.path.join(self.script_dir, "Inter-Regular.ttf"),
            r"C:\Windows\Fonts\Inter-Regular.ttf",
            r"C:\Windows\Fonts\Inter[opsz,wght].ttf",
        )
        self.login_feature_icon_paths = {
            "Sustentavel": self.first_existing_path(
                os.path.join(self.asset_dir, "icone-sustentavel-reciclagem.png"),
                os.path.join(self.script_dir, "icone-sustentavel-reciclagem.png"),
                r"C:\Users\User\Downloads\icone-sustentavel-reciclagem.png",
            ),
            "Seguro": self.first_existing_path(
                os.path.join(self.asset_dir, "icone-seguro-vinhesque.png"),
                os.path.join(self.script_dir, "icone-seguro-vinhesque.png"),
                r"C:\Users\User\Downloads\icone-seguro-vinhesque.png",
            ),
            "Eficiente": self.first_existing_path(
                os.path.join(self.asset_dir, "icone-eficiencia-vinhesque.png"),
                os.path.join(self.script_dir, "icone-eficiencia-vinhesque.png"),
                r"C:\Users\User\Downloads\icone-eficiencia-vinhesque.png",
            ),
        }
        self.menu_card_icon_paths = {
            "Nova Compra": self.first_existing_path(
                os.path.join(self.asset_dir, "icone-nova-compra.png"),
                os.path.join(self.script_dir, "icone-nova-compra.png"),
                r"C:\Users\User\Downloads\icone-nova-compra.png",
            ),
        }
        self.window_icon_preview_path = self.first_existing_path(
            os.path.join(self.asset_dir, "logo_app_icon_preview.png"),
            os.path.join(self.script_dir, "logo_app_icon_preview.png"),
            self.header_brand_logo_path,
            self.logo_path,
        )
        self.window_icon_source = self.first_existing_path(
            os.path.join(self.script_dir, "logo.png"),
            os.path.join(self.asset_dir, "logo_design.png"),
            os.path.join(self.asset_dir, "logo_vr.png")
        )

        self.logo_img = None
        self.header_logo_img = None
        self.login_background_img = None
        self.login_logo_img = None
        self.login_badge_icon_img = None
        self.auth_dialog_badge_icon_img = None
        self.footer_security_icon_img = None
        self.footer_whatsapp_img = None
        self.login_user_icon_img = None
        self.login_lock_icon_img = None
        self.login_eye_open_icon_img = None
        self.login_eye_closed_icon_img = None
        self.login_arrow_icon_img = None
        self.window_icon_photo = None
        self.menu_card_icon_images = {}
        self.window_icon_path = os.path.join(self.asset_dir, "logo_app_icon.ico")
        self.main_container = None
        self.clock_after_id = None
        self.welcome_subtitle_label = None
        self.db_path = self.ensure_runtime_database()
        self.current_items = []
        self.usuario_logado = None
        self.login_usuario_entry = None
        self.login_senha_entry = None
        self.login_feedback = None
        self.dashboard_search_var = None
        self.dashboard_search_entry = None
        self.dashboard_search_shell = None
        self.dashboard_search_popup = None
        self.dashboard_search_results = []
        self.dashboard_search_selected_index = 0
        self.notifications_button = None
        self.notifications_badge_label = None
        self.notifications_popup = None
        self.notifications_after_id = None
        self.login_remember_var = None
        self.login_password_toggle_btn = None
        self.login_password_visible = False
        self.suggestion_popup = None
        self.suggestion_state = None

        self.register_process_font(self.poppins_semibold_font_path)
        self.register_process_font(self.inter_regular_font_path)
        self.configure_window_branding()
        self.init_db()
        self.show_login()

    @staticmethod
    def app_base_dir():
        if getattr(sys, "frozen", False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def app_resource_dir():
        if getattr(sys, "frozen", False):
            return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        return os.path.dirname(os.path.abspath(__file__))

    def ensure_runtime_database(self):
        runtime_db_path = os.path.join(self.script_dir, "vr_reciclagem.db")
        bundled_db_path = os.path.join(self.resource_dir, "vr_reciclagem.db")

        if os.path.exists(runtime_db_path):
            return runtime_db_path

        if getattr(sys, "frozen", False) and os.path.exists(bundled_db_path):
            try:
                shutil.copy2(bundled_db_path, runtime_db_path)
                return runtime_db_path
            except Exception:
                return bundled_db_path

        return runtime_db_path

    @staticmethod
    def first_existing_path(*paths):
        for path in paths:
            if os.path.exists(path):
                return path
        return paths[0] if paths else ""

    @staticmethod
    def register_process_font(font_path):
        if os.name != "nt" or not font_path or not os.path.exists(font_path):
            return
        try:
            import ctypes
            ctypes.windll.gdi32.AddFontResourceExW(str(font_path), 0x10, 0)
        except Exception:
            pass

    def login_ctk_font(self, size, role="body"):
        role_name = str(role).strip().lower()
        if role_name == "title":
            families = ["Poppins SemiBold", "Poppins", "Segoe UI Semibold", "Segoe UI"]
            weight = "bold"
        else:
            families = ["Inter", "Segoe UI", "Arial"]
            weight = "normal"

        for family in families:
            try:
                return ctk.CTkFont(family=family, size=size, weight=weight)
            except Exception:
                continue
        return ctk.CTkFont(size=size, weight=weight)

    @staticmethod
    def format_current_datetime():
        now = datetime.now()
        weekdays = [
            "Segunda-feira",
            "Terça-feira",
            "Quarta-feira",
            "Quinta-feira",
            "Sexta-feira",
            "Sábado",
            "Domingo",
        ]
        months = [
            "Janeiro",
            "Fevereiro",
            "Março",
            "Abril",
            "Maio",
            "Junho",
            "Julho",
            "Agosto",
            "Setembro",
            "Outubro",
            "Novembro",
            "Dezembro",
        ]

        return (
            f"{now.day} de {months[now.month - 1]} de {now.year}   •   "
            f"{weekdays[now.weekday()]} - {now:%H:%M}"
        )

    @staticmethod
    def fit_image_size(image, max_width, max_height):
        width, height = image.size
        scale = min(max_width / width, max_height / height)
        return int(width * scale), int(height * scale)

    @staticmethod
    def mm_to_px(mm_value, dpi):
        return max(1, int(round((float(mm_value) / 25.4) * float(dpi))))

    @staticmethod
    def prepare_window_icon(image):
        source = image.copy().convert("RGBA")
        if source.width > source.height:
            crop_width = min(source.width, source.height)
            source = source.crop((0, 0, crop_width, source.height))

        fitted = ImageOps.contain(source, (220, 220))
        canvas = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        pos_x = (256 - fitted.width) // 2
        pos_y = (256 - fitted.height) // 2
        canvas.paste(fitted, (pos_x, pos_y), fitted)
        return canvas

    def login_background_art(self, target_width, target_height):
        width = max(1, int(target_width))
        height = max(1, int(target_height))
        base = Image.new("RGBA", (width, height), "#052414")

        if os.path.exists(self.login_background_path):
            with Image.open(self.login_background_path) as background_source:
                background = ImageOps.fit(
                    ImageOps.exif_transpose(background_source).convert("RGB"),
                    (width, height),
                    method=Image.Resampling.LANCZOS,
                    centering=(0.25, 0.5),
                )
                background = ImageEnhance.Brightness(background).enhance(1.34)
                background = ImageEnhance.Color(background).enhance(1.18)
                background = ImageEnhance.Contrast(background).enhance(1.04)
                background = background.convert("RGBA")
            base.paste(background, (0, 0), background)

        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        return Image.alpha_composite(base, overlay)

    def login_image_font(self, size, bold=False, family="default"):
        family_name = str(family).strip().lower()
        if family_name == "poppins":
            candidates = [
                self.poppins_semibold_font_path,
                "Poppins-SemiBold.ttf",
                "segoeuib.ttf",
                "arialbd.ttf",
            ]
        elif family_name == "inter":
            candidates = [
                self.inter_regular_font_path,
                "Inter-Regular.ttf",
                "segoeui.ttf",
                "arial.ttf",
            ]
        else:
            candidates = [
                "segoeuib.ttf" if bold else "segoeui.ttf",
                "arialbd.ttf" if bold else "arial.ttf",
            ]
        for candidate in candidates:
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                continue
        return ImageFont.load_default()

    def prepare_login_logo_pil(self, max_width, max_height):
        login_logo_path = self.login_brand_logo_path
        if not os.path.exists(login_logo_path):
            return None
        with Image.open(login_logo_path) as logo_source:
            logo = ImageOps.exif_transpose(logo_source).convert("RGBA")
            sanitized = []
            for r, g, b, a in logo.getdata():
                if a and r < 18 and g < 18 and b < 18:
                    sanitized.append((0, 0, 0, 0))
                else:
                    sanitized.append((r, g, b, a))
            logo.putdata(sanitized)
            alpha_bbox = logo.getchannel("A").getbbox() if "A" in logo.getbands() else None
            if alpha_bbox:
                logo = logo.crop(alpha_bbox)
            logo.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            return logo

    def prepare_login_badge_pil(self, max_width, max_height):
        if not os.path.exists(self.login_badge_icon_path):
            return None
        with Image.open(self.login_badge_icon_path) as badge_source:
            badge = ImageOps.exif_transpose(badge_source).convert("RGBA")
            side = min(badge.size)
            inset = max(0, int(side * 0.20))
            badge = badge.crop((inset, inset, side - inset, side - inset))

            cleaned_pixels = []
            for r, g, b, a in badge.getdata():
                green_bias = g - max(r, b)
                neutral_delta = max(r, g, b) - min(r, g, b)
                if neutral_delta < 22 and green_bias < 14:
                    cleaned_pixels.append((r, g, b, 0))
                elif neutral_delta < 36 and green_bias < 22:
                    cleaned_pixels.append((r, g, b, int(a * 0.22)))
                else:
                    cleaned_pixels.append((r, g, b, a))
            badge.putdata(cleaned_pixels)

            alpha_bbox = badge.getchannel("A").getbbox() if "A" in badge.getbands() else None
            if alpha_bbox:
                badge = badge.crop(alpha_bbox)
            badge.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            return badge

    def prepare_auth_dialog_badge_pil(self, max_width, max_height):
        if not os.path.exists(self.auth_dialog_badge_icon_path):
            return None
        with Image.open(self.auth_dialog_badge_icon_path) as badge_source:
            badge = ImageOps.exif_transpose(badge_source).convert("RGBA")
            side = min(badge.size)
            inset = max(0, int(side * 0.08))
            badge = badge.crop((inset, inset, side - inset, side - inset))

            cleaned_pixels = []
            for r, g, b, a in badge.getdata():
                green_bias = g - max(r, b)
                neutral_delta = max(r, g, b) - min(r, g, b)
                if neutral_delta < 26 and green_bias < 18:
                    cleaned_pixels.append((r, g, b, 0))
                elif neutral_delta < 42 and green_bias < 25:
                    cleaned_pixels.append((r, g, b, int(a * 0.18)))
                else:
                    cleaned_pixels.append((r, g, b, a))
            badge.putdata(cleaned_pixels)

            alpha_bbox = badge.getchannel("A").getbbox() if "A" in badge.getbands() else None
            if alpha_bbox:
                badge = badge.crop(alpha_bbox)
            badge.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            return badge

    def prepare_login_feature_icon_pil(self, feature_name, max_width, max_height):
        icon_path = self.login_feature_icon_paths.get(str(feature_name).strip())
        if not icon_path or not os.path.exists(icon_path):
            return None

        with Image.open(icon_path) as icon_source:
            icon = ImageOps.exif_transpose(icon_source).convert("RGBA")
            alpha_bbox = icon.getchannel("A").getbbox() if "A" in icon.getbands() else None
            if alpha_bbox:
                icon = icon.crop(alpha_bbox)
            icon = ImageOps.contain(icon, (max_width, max_height), Image.Resampling.LANCZOS)
            canvas = Image.new("RGBA", (max_width, max_height), (0, 0, 0, 0))
            pos_x = (max_width - icon.width) // 2
            pos_y = (max_height - icon.height) // 2
            canvas.paste(icon, (pos_x, pos_y), icon)
            return canvas

    def prepare_menu_card_icon_pil(self, card_name, max_width, max_height):
        icon_path = self.menu_card_icon_paths.get(str(card_name).strip())
        if not icon_path or not os.path.exists(icon_path):
            return None

        with Image.open(icon_path) as icon_source:
            icon = ImageOps.exif_transpose(icon_source).convert("RGBA")
            sampled_colors = [
                icon.getpixel((0, 0))[:3],
                icon.getpixel((icon.width - 1, 0))[:3],
                icon.getpixel((0, icon.height - 1))[:3],
                icon.getpixel((icon.width - 1, icon.height - 1))[:3],
            ]
            avg_bg = tuple(sum(color[idx] for color in sampled_colors) // len(sampled_colors) for idx in range(3))
            cleaned_pixels = []
            for r, g, b, a in icon.getdata():
                neutral_delta = max(r, g, b) - min(r, g, b)
                bg_distance = abs(r - avg_bg[0]) + abs(g - avg_bg[1]) + abs(b - avg_bg[2])
                green_bias = g - max(r, b)
                if bg_distance < 72 and neutral_delta < 44 and green_bias < 24:
                    cleaned_pixels.append((r, g, b, 0))
                else:
                    cleaned_pixels.append((r, g, b, a))
            icon.putdata(cleaned_pixels)
            alpha_bbox = icon.getchannel("A").getbbox() if "A" in icon.getbands() else None
            if alpha_bbox:
                icon = icon.crop(alpha_bbox)
            icon = ImageOps.contain(icon, (max_width, max_height), Image.Resampling.LANCZOS)
            canvas = Image.new("RGBA", (max_width, max_height), (0, 0, 0, 0))
            pos_x = (max_width - icon.width) // 2
            pos_y = (max_height - icon.height) // 2
            canvas.paste(icon, (pos_x, pos_y), icon)
            return canvas

    def get_menu_card_icon_image(self, card_name, size):
        cache_key = (str(card_name).strip(), int(size))
        if cache_key in self.menu_card_icon_images:
            return self.menu_card_icon_images[cache_key]

        icon_pil = self.prepare_menu_card_icon_pil(card_name, size, size)
        if icon_pil is None:
            return None

        icon_image = ctk.CTkImage(
            light_image=icon_pil,
            dark_image=icon_pil,
            size=icon_pil.size,
        )
        self.menu_card_icon_images[cache_key] = icon_image
        return icon_image

    def prepare_whatsapp_logo_pil(self, max_width, max_height):
        if not self.whatsapp_logo_path or not os.path.exists(self.whatsapp_logo_path):
            return None

        with Image.open(self.whatsapp_logo_path) as icon_source:
            icon = ImageOps.exif_transpose(icon_source).convert("RGBA")
            alpha_bbox = icon.getchannel("A").getbbox() if "A" in icon.getbands() else None
            if alpha_bbox:
                icon = icon.crop(alpha_bbox)
            icon = ImageOps.contain(icon, (max_width, max_height), Image.Resampling.LANCZOS)
            canvas = Image.new("RGBA", (max_width, max_height), (0, 0, 0, 0))
            pos_x = (max_width - icon.width) // 2
            pos_y = (max_height - icon.height) // 2
            canvas.paste(icon, (pos_x, pos_y), icon)
            return canvas

    def prepare_footer_security_icon_pil(self, max_width, max_height):
        if not self.footer_security_icon_path or not os.path.exists(self.footer_security_icon_path):
            return None

        with Image.open(self.footer_security_icon_path) as icon_source:
            icon = ImageOps.exif_transpose(icon_source).convert("RGBA")
            alpha_bbox = icon.getchannel("A").getbbox() if "A" in icon.getbands() else None
            if alpha_bbox:
                icon = icon.crop(alpha_bbox)
            icon = ImageOps.contain(icon, (max_width, max_height), Image.Resampling.LANCZOS)
            canvas = Image.new("RGBA", (max_width, max_height), (0, 0, 0, 0))
            pos_x = (max_width - icon.width) // 2
            pos_y = (max_height - icon.height) // 2
            canvas.paste(icon, (pos_x, pos_y), icon)
            return canvas

    def prepare_header_brand_logo_pil(self, max_width, max_height):
        if not self.header_brand_logo_path or not os.path.exists(self.header_brand_logo_path):
            return None

        with Image.open(self.header_brand_logo_path) as logo_source:
            logo = ImageOps.exif_transpose(logo_source).convert("RGBA")
            cleaned = []
            for r, g, b, a in logo.getdata():
                if a and r < 20 and g < 20 and b < 20:
                    cleaned.append((0, 0, 0, 0))
                else:
                    cleaned.append((r, g, b, a))
            logo.putdata(cleaned)
            alpha_bbox = logo.getchannel("A").getbbox() if "A" in logo.getbands() else None
            if alpha_bbox:
                logo = logo.crop(alpha_bbox)
            logo.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            return logo

    @staticmethod
    def rgba_from_hex(color, alpha=255):
        hex_color = str(color).strip().lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join(channel * 2 for channel in hex_color)
        if len(hex_color) != 6:
            return 0, 0, 0, alpha
        return (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
            alpha,
        )

    def prepare_login_line_icon_pil(self, icon_name, size, color="#7A877E"):
        pixel_size = max(16, int(size))
        scale = 6
        canvas_size = pixel_size * scale
        stroke = max(6, canvas_size // 18)
        radius = stroke * 2
        icon_color = self.rgba_from_hex(color)
        canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas, "RGBA")

        if icon_name == "user":
            draw.ellipse(
                (canvas_size * 0.33, canvas_size * 0.16, canvas_size * 0.67, canvas_size * 0.50),
                outline=icon_color,
                width=stroke,
            )
            draw.arc(
                (canvas_size * 0.17, canvas_size * 0.47, canvas_size * 0.83, canvas_size * 0.95),
                start=203,
                end=337,
                fill=icon_color,
                width=stroke,
            )
        elif icon_name == "lock":
            draw.arc(
                (canvas_size * 0.24, canvas_size * 0.10, canvas_size * 0.76, canvas_size * 0.56),
                start=204,
                end=336,
                fill=icon_color,
                width=stroke,
            )
            draw.rounded_rectangle(
                (canvas_size * 0.22, canvas_size * 0.42, canvas_size * 0.78, canvas_size * 0.84),
                radius=radius,
                outline=icon_color,
                width=stroke,
            )
            draw.line(
                (canvas_size * 0.50, canvas_size * 0.56, canvas_size * 0.50, canvas_size * 0.68),
                fill=icon_color,
                width=stroke,
            )
            draw.ellipse(
                (canvas_size * 0.45, canvas_size * 0.68, canvas_size * 0.55, canvas_size * 0.78),
                outline=icon_color,
                width=stroke,
            )
        elif icon_name in ("eye", "eye_off"):
            draw.arc(
                (canvas_size * 0.14, canvas_size * 0.18, canvas_size * 0.86, canvas_size * 0.80),
                start=18,
                end=162,
                fill=icon_color,
                width=stroke,
            )
            draw.arc(
                (canvas_size * 0.14, canvas_size * 0.18, canvas_size * 0.86, canvas_size * 0.80),
                start=198,
                end=342,
                fill=icon_color,
                width=stroke,
            )
            draw.ellipse(
                (canvas_size * 0.39, canvas_size * 0.34, canvas_size * 0.61, canvas_size * 0.56),
                outline=icon_color,
                width=stroke,
            )
            if icon_name == "eye_off":
                draw.line(
                    (canvas_size * 0.26, canvas_size * 0.76, canvas_size * 0.76, canvas_size * 0.24),
                    fill=icon_color,
                    width=stroke,
                )
        elif icon_name == "arrow":
            draw.line(
                (canvas_size * 0.18, canvas_size * 0.50, canvas_size * 0.78, canvas_size * 0.50),
                fill=icon_color,
                width=stroke,
            )
            draw.line(
                (canvas_size * 0.56, canvas_size * 0.28, canvas_size * 0.78, canvas_size * 0.50),
                fill=icon_color,
                width=stroke,
            )
            draw.line(
                (canvas_size * 0.56, canvas_size * 0.72, canvas_size * 0.78, canvas_size * 0.50),
                fill=icon_color,
                width=stroke,
            )

        return canvas.resize((pixel_size, pixel_size), Image.Resampling.LANCZOS)

    def login_line_icon_art(self, icon_name, size, color="#7A877E"):
        icon_pil = self.prepare_login_line_icon_pil(icon_name, size, color)
        return ctk.CTkImage(light_image=icon_pil, dark_image=icon_pil, size=icon_pil.size)

    def toggle_login_password_visibility(self):
        if not self.login_senha_entry:
            return
        self.login_password_visible = not self.login_password_visible
        self.login_senha_entry.configure(show="" if self.login_password_visible else "*")
        if self.login_password_toggle_btn:
            self.login_password_toggle_btn.configure(
                image=self.login_eye_open_icon_img if self.login_password_visible else self.login_eye_closed_icon_img
            )

    def ensure_auth_dialog_assets(self):
        if self.login_lock_icon_img is None:
            self.login_lock_icon_img = self.login_line_icon_art("lock", 18, "#7A867D")
        if self.login_eye_open_icon_img is None:
            self.login_eye_open_icon_img = self.login_line_icon_art("eye", 18, "#70826E")
        if self.login_eye_closed_icon_img is None:
            self.login_eye_closed_icon_img = self.login_line_icon_art("eye_off", 18, "#70826E")
        if self.auth_dialog_badge_icon_img is None:
            badge_icon = self.prepare_auth_dialog_badge_pil(58, 58)
            if badge_icon:
                self.auth_dialog_badge_icon_img = ctk.CTkImage(
                    light_image=badge_icon,
                    dark_image=badge_icon,
                    size=badge_icon.size,
                )

    def solicitar_senha_admin(self, area):
        self.ensure_auth_dialog_assets()
        colors = self.modelo_colors()
        widget_scale = self._get_widget_scaling() if hasattr(self, "_get_widget_scaling") else 1.0

        def logical(value):
            return max(1, int(round(float(value) / widget_scale)))

        dialog_width_px = 500
        dialog_height_px = 392
        card_width_px = 430
        card_height_px = 348

        result = {"password": None}
        dialog = ctk.CTkToplevel(self)
        dialog.withdraw()
        dialog.title("Acesso Restrito")
        dialog.configure(fg_color="#F6F8F5")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        width = logical(dialog_width_px)
        height = logical(dialog_height_px)

        try:
            if self.window_icon_path and os.path.exists(self.window_icon_path):
                dialog.iconbitmap(self.window_icon_path)
        except Exception:
            pass

        card_width = logical(card_width_px)
        card_height = logical(card_height_px)
        badge_size = logical(82)
        badge_radius = logical(41)
        input_height = logical(54)
        button_height = logical(46)
        field_x = logical(28)
        field_width = card_width - (field_x * 2)
        icon_pad_x = logical(16)
        icon_pad_y = logical(14)
        entry_pad_y = logical(8)
        title_y = logical(106)
        subtitle_y = logical(148)
        label_height = logical(18)
        label_y = logical(182)
        field_y = logical(208)
        feedback_height = logical(16)
        feedback_y = field_y + input_height + logical(4)
        buttons_y = feedback_y + feedback_height + logical(8)
        button_gap = logical(12)
        icon_size = logical(18)

        dialog.grid_rowconfigure(0, weight=1)
        dialog.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(
            dialog,
            width=card_width,
            height=card_height,
            fg_color="white",
            corner_radius=logical(22),
            border_width=1,
            border_color="#E4ECE3",
        )
        card.grid(row=0, column=0)
        card.grid_propagate(False)

        badge_outer = ctk.CTkFrame(
            card,
            width=badge_size,
            height=badge_size,
            fg_color="#EDF7EE",
            corner_radius=badge_radius,
            border_width=1,
            border_color="#DCE9DA",
        )
        badge_outer.place(relx=0.5, y=logical(18), anchor="n")

        if self.auth_dialog_badge_icon_img is not None:
            ctk.CTkLabel(
                badge_outer,
                image=self.auth_dialog_badge_icon_img,
                text="",
                fg_color="transparent",
            ).place(relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(
                badge_outer,
                text="VR",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#0E6B2E",
                fg_color="transparent",
            ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            card,
            text="Acesso Restrito",
            font=ctk.CTkFont(family="Segoe UI", size=23, weight="bold"),
            text_color="#151E18",
            fg_color="transparent",
        ).place(relx=0.5, y=title_y, anchor="n")
        ctk.CTkLabel(
            card,
            text=f"Para acessar {area}, informe sua senha.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#69756D",
            fg_color="transparent",
        ).place(relx=0.5, y=subtitle_y, anchor="n")

        ctk.CTkLabel(
            card,
            text="Senha",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#1A241D",
            fg_color="transparent",
            width=field_width,
            height=label_height,
            anchor="w",
        ).place(x=field_x, y=label_y)

        field_shell = ctk.CTkFrame(
            card,
            width=field_width,
            height=input_height,
            corner_radius=logical(16),
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#D9E2D8",
        )
        field_shell.place(x=field_x, y=field_y)
        field_shell.grid_propagate(False)
        field_shell.grid_columnconfigure(1, weight=1)

        icon_label = ctk.CTkLabel(
            field_shell,
            text="",
            image=self.login_lock_icon_img,
            width=icon_size,
            height=icon_size,
            fg_color="transparent",
        )
        icon_label.grid(row=0, column=0, padx=(icon_pad_x, logical(12)), pady=icon_pad_y)

        senha_entry = ctk.CTkEntry(
            field_shell,
            height=34,
            border_width=0,
            corner_radius=0,
            fg_color="#FFFFFF",
            text_color="#18221D",
            placeholder_text="Digite sua senha",
            placeholder_text_color="#9AA79D",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            show="*",
        )
        senha_entry.grid(row=0, column=1, sticky="ew", padx=(0, logical(6)), pady=entry_pad_y)

        password_visible = {"value": False}

        def toggle_password():
            password_visible["value"] = not password_visible["value"]
            senha_entry.configure(show="" if password_visible["value"] else "*")
            toggle_btn.configure(
                image=self.login_eye_open_icon_img if password_visible["value"] else self.login_eye_closed_icon_img
            )

        toggle_btn = ctk.CTkButton(
            field_shell,
            text="",
            image=self.login_eye_closed_icon_img,
            width=logical(30),
            height=logical(30),
            corner_radius=logical(15),
            fg_color="transparent",
            hover_color="#EFF6EE",
            command=toggle_password,
        )
        toggle_btn.grid(row=0, column=2, padx=(0, logical(14)), pady=entry_pad_y)

        feedback = ctk.CTkLabel(
            card,
            text="",
            justify="left",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#B84545",
            fg_color="transparent",
            width=field_width,
            height=feedback_height,
        )
        feedback.place(x=field_x, y=feedback_y)

        def focus_in(_event=None):
            field_shell.configure(border_color="#6DAA78")

        def focus_out(_event=None):
            field_shell.configure(border_color="#D9E2D8")

        def close_dialog():
            if dialog.winfo_exists():
                dialog.grab_release()
                dialog.destroy()

        def submit():
            senha = senha_entry.get().strip()
            if not senha:
                feedback.configure(text="Digite sua senha.")
                senha_entry.focus_set()
                return
            if senha != SENHA_ADMIN:
                feedback.configure(text="Senha incorreta.")
                senha_entry.delete(0, "end")
                senha_entry.focus_set()
                return
            result["password"] = senha
            close_dialog()

        field_shell.bind("<Button-1>", lambda _event: senha_entry.focus_set())
        icon_label.bind("<Button-1>", lambda _event: senha_entry.focus_set())
        senha_entry.bind("<FocusIn>", focus_in)
        senha_entry.bind("<FocusOut>", focus_out)
        senha_entry.bind("<Return>", lambda _event: submit())
        dialog.bind("<Escape>", lambda _event: close_dialog())
        dialog.protocol("WM_DELETE_WINDOW", close_dialog)

        buttons = ctk.CTkFrame(
            card,
            fg_color="transparent",
            width=field_width,
            height=button_height,
        )
        buttons.place(x=field_x, y=buttons_y)
        buttons.grid_propagate(False)
        buttons.grid_columnconfigure(0, weight=1, uniform="auth_dialog")
        buttons.grid_columnconfigure(1, weight=1, uniform="auth_dialog")

        ctk.CTkButton(
            buttons,
            text="Cancelar",
            height=button_height,
            corner_radius=logical(14),
            fg_color="white",
            hover_color="#F3F8F2",
            text_color=colors["green"],
            border_width=1,
            border_color="#7DB387",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=close_dialog,
        ).grid(row=0, column=0, sticky="nsew", padx=(0, button_gap // 2))
        ctk.CTkButton(
            buttons,
            text="Acessar",
            image=self.login_lock_icon_img,
            compound="left",
            height=button_height,
            corner_radius=logical(14),
            fg_color="#0E7A24",
            hover_color="#0A631D",
            text_color="white",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=submit,
        ).grid(row=0, column=1, sticky="nsew", padx=(button_gap // 2, 0))

        def center_dialog():
            if not dialog.winfo_exists():
                return
            dialog.update_idletasks()
            screen_w = dialog.winfo_screenwidth()
            screen_h = dialog.winfo_screenheight()
            current_w = max(dialog_width_px, dialog.winfo_width())
            current_h = max(dialog_height_px, dialog.winfo_height())
            pos_x = max(0, (screen_w - current_w) // 2)
            pos_y = max(0, (screen_h - current_h) // 2)
            dialog.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

        center_dialog()
        dialog.deiconify()
        dialog.lift()
        dialog.focus_force()
        dialog.after(30, center_dialog)
        dialog.after(100, lambda: senha_entry.focus_set() if senha_entry.winfo_exists() else None)
        self.wait_window(dialog)
        return result["password"]

    def login_scene_art(self, target_width, target_height, left_width):
        width = max(1, int(target_width))
        height = max(1, int(target_height))
        left_width = max(1, min(width, int(left_width)))
        scene_scale = max(0.78, min(1.0, min(height / 900.0, left_width / 860.0)))
        right_color = "#FAF8F2"
        scene = Image.new("RGBA", (width, height), right_color)
        curve_radius = max(150, int(height * 0.26))

        left_art = self.login_background_art(min(width, left_width + curve_radius), height)
        scene.paste(left_art, (0, 0), left_art)

        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay, "RGBA")
        right_fill = (250, 248, 242, 255)
        # Curva apenas no topo; abaixo dela a divisoria segue reta ate o final.
        draw.rectangle((left_width + curve_radius, 0, width, curve_radius), fill=right_fill)
        draw.rectangle((left_width, curve_radius, width, height), fill=right_fill)
        draw.ellipse((left_width, 0, left_width + (curve_radius * 2), curve_radius * 2), fill=right_fill)

        text_draw = ImageDraw.Draw(scene)

        def centered_x(text, font):
            left, _top, right, _bottom = text_draw.textbbox((0, 0), text, font=font)
            text_width = right - left
            return max(24, int((left_width - text_width) / 2))

        content_center_x = left_width // 2
        logo_top = max(int(72 * scene_scale), int(height * 0.18))
        logo = self.prepare_login_logo_pil(int(290 * scene_scale), int(176 * scene_scale))
        if logo:
            logo_x = max(26, content_center_x - (logo.width // 2))
            scene.paste(logo, (logo_x, logo_top), logo)
        else:
            logo_x = centered_x("VR VINHESQUE", self.login_image_font(34, bold=True))

        logo_block_height = logo.height if logo else int(176 * scene_scale)
        title_y = logo_top + logo_block_height + int(86 * scene_scale)
        accent_y = title_y - int(24 * scene_scale)
        accent_width = int(62 * scene_scale)
        accent_x = content_center_x - (accent_width // 2)
        text_draw.rounded_rectangle((accent_x, accent_y, accent_x + accent_width, accent_y + 4), radius=2, fill="#D5F347")

        title_font = self.login_image_font(max(30, int(39 * scene_scale)), bold=True, family="poppins")
        subtitle_font = self.login_image_font(max(16, int(21 * scene_scale)), bold=False, family="inter")
        title_text = "Sistema de Gestao"
        subtitle_text = "Sustentabilidade que gera valor"

        text_draw.text((centered_x(title_text, title_font), title_y), title_text, fill="white", font=title_font)
        subtitle_y = title_y + int(62 * scene_scale)
        text_draw.text((centered_x(subtitle_text, subtitle_font), subtitle_y), subtitle_text, fill="#C9D8CC", font=subtitle_font)

        feature_items = [
            ("Sustentavel", "Compromisso com\no meio ambiente"),
            ("Seguro", "Seus dados\nprotegidos"),
            ("Eficiente", "Gestao inteligente\ne resultados"),
        ]
        feature_row_width = min(left_width - int(48 * scene_scale), max(int(470 * scene_scale), int(left_width * 0.78)))
        feature_y = min(height - int(110 * scene_scale), subtitle_y + int(62 * scene_scale))
        feature_gap = int(24 * scene_scale)
        feature_width = int((feature_row_width - (feature_gap * 2)) / 3)
        feature_start_x = int((left_width - feature_row_width) / 2)
        feature_title_font = self.login_image_font(max(14, int(18 * scene_scale)), bold=True, family="inter")
        feature_subtitle_font = self.login_image_font(max(11, int(14 * scene_scale)), bold=False, family="inter")
        icon_size = max(50, int(66 * scene_scale))
        text_offset_x = max(64, int(76 * scene_scale))
        subtitle_line_gap = max(13, int(17 * scene_scale))
        for index, (title, subtitle) in enumerate(feature_items):
            item_x = feature_start_x + (index * (feature_width + feature_gap))
            icon_x = item_x
            icon_y = feature_y + 2
            feature_icon = self.prepare_login_feature_icon_pil(title, icon_size, icon_size)
            if feature_icon:
                scene.paste(feature_icon, (icon_x - 6, icon_y - 6), feature_icon)
            else:
                text_draw.rounded_rectangle((icon_x, icon_y, icon_x + 54, icon_y + 54), radius=16, fill="#0F5A29")
                text_draw.text((icon_x + 12, icon_y + 15), "VR", fill="#D5F347", font=self.login_image_font(14, bold=True))
            text_draw.text((icon_x + text_offset_x, feature_y - 1), title, fill="white", font=feature_title_font)
            subtitle_y = feature_y + int(28 * scene_scale)
            for line_index, line in enumerate(subtitle.splitlines()):
                text_draw.text((icon_x + text_offset_x, subtitle_y + (line_index * subtitle_line_gap)), line, fill="#B8CBC0", font=feature_subtitle_font)
            if index < len(feature_items) - 1:
                separator_x = item_x + feature_width + (feature_gap // 2)
                text_draw.rectangle((separator_x, feature_y + 4, separator_x + 1, feature_y + max(46, int(58 * scene_scale))), fill="#214935")

        return Image.alpha_composite(scene, overlay)

    def login_logo_art(self, max_width, max_height):
        logo = self.prepare_login_logo_pil(max_width, max_height)
        if logo is None:
            return None
        return ctk.CTkImage(light_image=logo, dark_image=logo, size=logo.size)

    def configure_window_branding(self):
        try:
            if self.window_icon_path and os.path.exists(self.window_icon_path):
                self.iconbitmap(self.window_icon_path)

            preview_source = None
            if self.window_icon_preview_path and os.path.exists(self.window_icon_preview_path):
                preview_source = ImageOps.exif_transpose(Image.open(self.window_icon_preview_path)).convert("RGBA")
            elif self.window_icon_source and os.path.exists(self.window_icon_source):
                preview_source = self.prepare_window_icon(ImageOps.exif_transpose(Image.open(self.window_icon_source)))

            if preview_source is not None:
                self.window_icon_photo = ImageTk.PhotoImage(preview_source)
                self.iconphoto(True, self.window_icon_photo)
        except Exception:
            self.window_icon_photo = None

    def apply_screen_fit(self):
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        width = max(1180, min(1600, screen_w - 36))
        height = max(660, min(900, screen_h - 88))
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2)

        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(1180, 660)

        if screen_h <= 768 or screen_w <= 1366:
            scale = 0.90
        elif screen_h <= 820 or screen_w <= 1440:
            scale = 0.95
        else:
            scale = 1.0

        try:
            ctk.set_widget_scaling(scale)
        except Exception:
            pass

    def configure_fullscreen(self):
        self.is_fullscreen = True
        self.bind("<F11>", lambda _event: self.toggle_fullscreen())
        self.bind("<Escape>", lambda _event: self.exit_fullscreen())
        self.after(150, self.enter_fullscreen)

    def enter_fullscreen(self):
        self.is_fullscreen = True
        self.attributes("-fullscreen", True)
        self.lift()
        self.focus_force()

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)

    def exit_fullscreen(self):
        self.is_fullscreen = False
        self.attributes("-fullscreen", False)

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL UNIQUE,
                    telefone TEXT DEFAULT '',
                    cnpj TEXT DEFAULT '',
                    cidade TEXT DEFAULT '',
                    observacao TEXT DEFAULT ''
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS materiais (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL UNIQUE,
                    preco_compra REAL NOT NULL DEFAULT 0,
                    preco_venda REAL NOT NULL DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT NOT NULL,
                    cliente_id INTEGER NOT NULL,
                    cliente_nome TEXT NOT NULL,
                    data TEXT NOT NULL,
                    total REAL NOT NULL DEFAULT 0,
                    observacao TEXT DEFAULT '',
                    FOREIGN KEY(cliente_id) REFERENCES clientes(id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transacao_itens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transacao_id INTEGER NOT NULL,
                    material_id INTEGER NOT NULL,
                    material_nome TEXT NOT NULL,
                    peso_bruto REAL NOT NULL DEFAULT 0,
                    desconto REAL NOT NULL DEFAULT 0,
                    peso_liquido REAL NOT NULL DEFAULT 0,
                    preco_kg REAL NOT NULL DEFAULT 0,
                    subtotal REAL NOT NULL DEFAULT 0,
                    FOREIGN KEY(transacao_id) REFERENCES transacoes(id),
                    FOREIGN KEY(material_id) REFERENCES materiais(id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS comprovantes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transacao_id INTEGER NOT NULL,
                    numero TEXT NOT NULL UNIQUE,
                    tipo TEXT NOT NULL,
                    cliente_nome TEXT NOT NULL,
                    data TEXT NOT NULL,
                    total REAL NOT NULL DEFAULT 0,
                    conteudo TEXT NOT NULL,
                    FOREIGN KEY(transacao_id) REFERENCES transacoes(id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sangrias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    categoria TEXT NOT NULL DEFAULT 'Outros',
                    descricao TEXT NOT NULL,
                    valor REAL NOT NULL DEFAULT 0,
                    observacao TEXT DEFAULT '',
                    usuario TEXT DEFAULT ''
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notificacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT NOT NULL DEFAULT '',
                    titulo TEXT NOT NULL,
                    mensagem TEXT NOT NULL,
                    criado_em TEXT NOT NULL,
                    lida INTEGER NOT NULL DEFAULT 0
                )
            """)
            try:
                conn.execute("ALTER TABLE clientes ADD COLUMN tipo TEXT DEFAULT 'Comprador'")
            except sqlite3.OperationalError:
                pass
            try:
                conn.execute("ALTER TABLE clientes ADD COLUMN email TEXT DEFAULT ''")
            except sqlite3.OperationalError:
                pass
            try:
                conn.execute("ALTER TABLE clientes ADD COLUMN estado TEXT DEFAULT ''")
            except sqlite3.OperationalError:
                pass
            try:
                conn.execute("ALTER TABLE clientes ADD COLUMN endereco TEXT DEFAULT ''")
            except sqlite3.OperationalError:
                pass
            try:
                conn.execute("ALTER TABLE materiais ADD COLUMN descricao TEXT DEFAULT ''")
            except sqlite3.OperationalError:
                pass
            try:
                conn.execute("ALTER TABLE materiais ADD COLUMN estoque_minimo REAL NOT NULL DEFAULT 0")
            except sqlite3.OperationalError:
                pass
            try:
                conn.execute("ALTER TABLE materiais ADD COLUMN ativo INTEGER NOT NULL DEFAULT 1")
            except sqlite3.OperationalError:
                pass
            try:
                conn.execute("ALTER TABLE transacoes ADD COLUMN pagamento TEXT DEFAULT ''")
            except sqlite3.OperationalError:
                pass
            try:
                conn.execute("ALTER TABLE transacoes ADD COLUMN destino_compra TEXT DEFAULT ''")
            except sqlite3.OperationalError:
                pass

    def db_fetchall(self, query, params=()):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute(query, params).fetchall()

    def db_fetchone(self, query, params=()):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute(query, params).fetchone()

    def parse_decimal(self, value):
        text = str(value).strip().replace(".", "").replace(",", ".")
        return float(text) if text else 0.0

    def format_kg(self, value):
        return f"{value:,.2f} kg".replace(",", "X").replace(".", ",").replace("X", ".")

    def format_money(self, value):
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def transacao_label(self, row):
        tipo = str(row["tipo"]).title()
        destino_compra = ""
        if "destino_compra" in row.keys() and row["tipo"] == "COMPRA":
            destino_compra = str(row["destino_compra"] or "").strip()
        if destino_compra:
            return f"{tipo} - {destino_compra} #{row['id']}"
        return f"{tipo} #{row['id']}"

    def today_iso(self):
        return datetime.now().strftime("%Y-%m-%d")

    def parse_date_value(self, value):
        text = str(value).strip()
        if not text:
            return None
        for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
            except ValueError:
                pass
        raise ValueError("Use o formato DD/MM/AAAA ou AAAA-MM-DD.")

    def normalize_date_range(self, start_value="", end_value=""):
        start_date = self.parse_date_value(start_value)
        end_date = self.parse_date_value(end_value)
        if start_date and end_date and start_date > end_date:
            raise ValueError("A data inicial nao pode ser maior que a data final.")
        return start_date, end_date

    def format_date_br(self, value):
        if not value:
            return ""
        text = str(value)
        for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(text, fmt).strftime("%d/%m/%Y")
            except ValueError:
                pass
        return text

    def build_date_range_conditions(self, column_name, start_date=None, end_date=None):
        conditions = []
        params = []
        if start_date:
            conditions.append(f"date({column_name}) >= ?")
            params.append(start_date)
        if end_date:
            conditions.append(f"date({column_name}) <= ?")
            params.append(end_date)
        return conditions, params

    def comprovante_print_config(self):
        return {
            "render_dpi": 203,
            "paper_width_mm": 80.0,
            "printable_width_mm": 72.1,
            "content_width_mm": 71.4,
            "paper_height_mm": 297.0,
        }

    @staticmethod
    def sangria_categories():
        return [
            "Gasolina / Combustivel",
            "Alimentacao",
            "Manutencao",
            "Pedagio",
            "Adiantamento",
            "Outros",
        ]

    def create_top_bar(self, title):
        self.clear_main()
        self.main_container = ctk.CTkFrame(self, fg_color="#F4F4F1", corner_radius=0)
        self.main_container.pack(fill="both", expand=True)

        topo = ctk.CTkFrame(self.main_container, height=100, fg_color="#053B16", corner_radius=0)
        topo.pack(fill="x")
        topo.pack_propagate(False)

        voltar = ctk.CTkButton(
            topo,
            text="← Voltar",
            width=120,
            height=42,
            corner_radius=12,
            fg_color="#0E5A25",
            hover_color="#147032",
            command=self.build_ui
        )
        voltar.pack(side="left", padx=20, pady=28)

        titulo = ctk.CTkLabel(
            topo,
            text=title,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        titulo.pack(side="left", padx=10)

        corpo = ctk.CTkScrollableFrame(self.main_container, fg_color="#F4F4F1")
        corpo.pack(fill="both", expand=True, padx=24, pady=20)
        return corpo

    def make_panel(self, master, title=None):
        panel = ctk.CTkFrame(master, fg_color="white", corner_radius=15)
        panel.pack(fill="x", pady=10)
        if title:
            label = ctk.CTkLabel(panel, text=title, font=ctk.CTkFont(size=16, weight="bold"))
            label.pack(anchor="w", padx=15, pady=(12, 6))
        return panel

    def get_clientes(self):
        return self.db_fetchall("SELECT * FROM clientes ORDER BY nome")

    def get_materiais(self):
        return self.db_fetchall("SELECT * FROM materiais ORDER BY nome")

    def get_materiais_mais_comprados(self, somente_ativos=False):
        filtro_ativos = "WHERE m.ativo = 1" if somente_ativos else ""
        return self.db_fetchall(f"""
            SELECT
                m.*,
                COALESCE(SUM(CASE WHEN t.tipo='COMPRA' THEN i.peso_liquido ELSE 0 END), 0) AS total_comprado,
                COALESCE(SUM(CASE WHEN t.tipo='COMPRA' THEN 1 ELSE 0 END), 0) AS compras_qtd
            FROM materiais m
            LEFT JOIN transacao_itens i ON i.material_id = m.id
            LEFT JOIN transacoes t ON t.id = i.transacao_id
            {filtro_ativos}
            GROUP BY m.id
            ORDER BY total_comprado DESC, compras_qtd DESC, m.nome
        """)

    def saldo_material(self, material_id):
        row = self.db_fetchone("""
            SELECT COALESCE(
                SUM(CASE
                    WHEN t.tipo='COMPRA' THEN i.peso_liquido
                    WHEN t.tipo='VENDA' THEN -i.peso_liquido
                    ELSE 0
                END),
                0
            ) AS saldo
            FROM transacao_itens i
            JOIN transacoes t ON t.id = i.transacao_id
            WHERE i.material_id = ?
        """, (material_id,))
        return float(row["saldo"] if row else 0.0)

    def validar_estoque_venda(self, items):
        solicitado = {}
        nomes = {}
        for item in items:
            material_id = item["material_id"]
            solicitado[material_id] = solicitado.get(material_id, 0.0) + float(item["peso_liquido"])
            nomes[material_id] = item["material_nome"]

        faltas = []
        for material_id, quantidade in solicitado.items():
            saldo = self.saldo_material(material_id)
            if quantidade > saldo + 1e-9:
                faltas.append(f"{nomes[material_id]}: disponivel {self.format_kg(saldo)} | venda {self.format_kg(quantidade)}")

        if faltas:
            raise ValueError("Estoque insuficiente para concluir a venda.\n\n" + "\n".join(faltas))

    def option_values(self, rows, name_key="nome"):
        values = [row[name_key] for row in rows]
        return values if values else ["Nenhum cadastrado"]

    def selected_row_by_name(self, rows, name, name_key="nome"):
        typed = str(name).strip().lower()
        for row in rows:
            if str(row[name_key]).strip().lower() == typed:
                return row
        return None

    def cliente_por_nome_ou_criar(self, nome, tipo_operacao, telefone="", cnpj=""):
        nome_limpo = " ".join(str(nome).strip().split())
        if not nome_limpo:
            return None

        cliente = self.selected_row_by_name(self.get_clientes(), nome_limpo)
        if cliente:
            return cliente

        tipo_cliente = "Vendedor" if tipo_operacao == "COMPRA" else "Comprador"
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO clientes
                    (nome, telefone, cnpj, cidade, observacao, tipo, email, estado, endereco)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        nome_limpo,
                        str(telefone).strip(),
                        str(cnpj).strip(),
                        "",
                        f"Cadastro automatico gerado na {tipo_operacao.lower()}.",
                        tipo_cliente,
                        "",
                        "",
                        "",
                    ),
                )
        except sqlite3.IntegrityError:
            pass

        return self.selected_row_by_name(self.get_clientes(), nome_limpo)

    def configure_autocomplete(self, combo, variable, rows, callback=None, name_key="nome"):
        all_values = self.option_values(rows, name_key)

        def refresh_options(*_args):
            typed = variable.get().strip().lower()
            if not typed or typed in ("nenhum cadastrado", "nenhum encontrado"):
                values = all_values
            else:
                starts = [row[name_key] for row in rows if str(row[name_key]).lower().startswith(typed)]
                contains = [
                    row[name_key]
                    for row in rows
                    if typed in str(row[name_key]).lower() and row[name_key] not in starts
                ]
                values = starts + contains
                if not values:
                    values = ["Nenhum encontrado"]
            combo.configure(values=values)
            if callback:
                callback()

        variable.trace_add("write", refresh_options)
        return refresh_options

    def clear_suggestion_popup(self):
        if self.suggestion_popup is not None and self.suggestion_popup.winfo_exists():
            self.suggestion_popup.destroy()
        self.suggestion_popup = None
        self.suggestion_state = None

    def _widget_is_descendant(self, widget, ancestor):
        current = widget
        while current is not None:
            if current == ancestor:
                return True
            try:
                parent_name = current.winfo_parent()
                if not parent_name:
                    break
                current = current.nametowidget(parent_name)
            except Exception:
                break
        return False

    def _suggestion_secondary_text(self, row, name_key="nome"):
        pieces = []
        row_keys = set(row.keys()) if hasattr(row, "keys") else set(row)
        for key in ("cnpj", "telefone", "descricao"):
            if key == name_key:
                continue
            if key in row_keys and row[key]:
                pieces.append(str(row[key]).strip())
        return " | ".join(piece for piece in pieces if piece)[:80]

    def _refresh_suggestion_highlight(self):
        state = self.suggestion_state
        if not state:
            return
        active_index = state.get("selected_index")
        for index, refs in enumerate(state.get("item_refs", [])):
            is_active = index == active_index
            refs["frame"].configure(fg_color="#EAF6EB" if is_active else "white")
            refs["primary"].configure(text_color="#0E6B2E" if is_active else "#18221D")
            if refs.get("secondary") is not None:
                refs["secondary"].configure(text_color="#3E7C52" if is_active else "#6B7280")

    def _suggestion_matches_widget(self, widget):
        state = self.suggestion_state
        if not state or widget is None:
            return False
        for tracked in (state.get("anchor_widget"), state.get("focus_widget")):
            if tracked is None:
                continue
            if widget == tracked:
                return True
            if self._widget_is_descendant(widget, tracked):
                return True
        return False

    def move_suggestion_selection(self, anchor_widget=None, step=1):
        state = self.suggestion_state
        if not state or not state.get("matches"):
            return None
        if anchor_widget is not None and not self._suggestion_matches_widget(anchor_widget):
            return None
        current = state.get("selected_index")
        if current is None:
            current = 0
        else:
            current = max(0, min(len(state["matches"]) - 1, current + step))
        state["selected_index"] = current
        self._refresh_suggestion_highlight()
        return "break"

    def confirm_suggestion_selection(self, anchor_widget=None):
        state = self.suggestion_state
        if not state or not state.get("matches"):
            return False
        if anchor_widget is not None and not self._suggestion_matches_widget(anchor_widget):
            return False
        choose = state.get("choose")
        if choose is None:
            return False
        choose(state.get("selected_index") if state.get("selected_index") is not None else 0)
        return True

    def schedule_suggestion_popup_close(self, anchor_widget=None):
        def close_if_needed():
            state = self.suggestion_state
            if not state:
                return
            if anchor_widget is not None and anchor_widget not in (state.get("anchor_widget"), state.get("focus_widget")):
                return
            focus_widget = self.focus_get()
            popup = state.get("popup")
            tracked_widgets = [state.get("anchor_widget"), state.get("focus_widget")]
            if any(widget is not None and focus_widget == widget for widget in tracked_widgets):
                return
            if popup is not None and focus_widget is not None and self._widget_is_descendant(focus_widget, popup):
                return
            self.clear_suggestion_popup()

        self.after(140, close_if_needed)

    def render_suggestions(self, frame, rows, text, on_choose, name_key="nome", limit=4, anchor_widget=None, focus_widget=None):
        for widget in frame.winfo_children():
            widget.destroy()

        query = str(text).strip().lower()
        if not rows:
            self.clear_suggestion_popup()
            return

        if query:
            starts = [row for row in rows if str(row[name_key]).lower().startswith(query)]
            contains = [
                row for row in rows
                if query in str(row[name_key]).lower() and row not in starts
            ]
            matches = starts + contains
        else:
            matches = list(rows)

        if not matches:
            self.clear_suggestion_popup()
            return

        popup_parent = self.main_container if self.main_container is not None and self.main_container.winfo_exists() else self
        anchor = anchor_widget if anchor_widget is not None and anchor_widget.winfo_exists() else frame
        focus_target = focus_widget if focus_widget is not None and focus_widget.winfo_exists() else anchor

        self.clear_suggestion_popup()
        popup_parent.update_idletasks()
        anchor.update_idletasks()

        widget_scale = self._get_widget_scaling() if hasattr(self, "_get_widget_scaling") else 1.0
        root_x = popup_parent.winfo_rootx()
        root_y = popup_parent.winfo_rooty()
        x = max(0, int((anchor.winfo_rootx() - root_x) / widget_scale))
        y = max(0, int((anchor.winfo_rooty() - root_y + anchor.winfo_height() + 4) / widget_scale))
        width = max(int(anchor.winfo_width() / widget_scale), 260 if name_key == "nome" else 220)
        visible_matches = matches[:max(1, limit)]
        row_height = 50
        popup_height = len(visible_matches) * row_height + 12
        popup = ctk.CTkFrame(
            popup_parent,
            width=width,
            height=popup_height,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#DCE7D9",
        )
        popup.grid_propagate(False)
        popup.place(x=x, y=y)
        popup.lift()

        item_refs = []

        def choose_index(index):
            selected = visible_matches[index]
            on_choose(selected)
            self.clear_suggestion_popup()
            if focus_target is not None and focus_target.winfo_exists():
                focus_target.focus_set()

        for index, row in enumerate(visible_matches):
            item = ctk.CTkFrame(popup, fg_color="white", corner_radius=10, height=row_height - 4)
            item.pack(fill="x", padx=6, pady=(6 if index == 0 else 0, 6))
            item.pack_propagate(False)

            primary = ctk.CTkLabel(
                item,
                text=str(row[name_key]),
                anchor="w",
                justify="left",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#18221D",
                fg_color="transparent",
            )
            primary.pack(anchor="w", padx=12, pady=(7, 0))

            secondary_text = self._suggestion_secondary_text(row, name_key=name_key)
            secondary = None
            if secondary_text:
                secondary = ctk.CTkLabel(
                    item,
                    text=secondary_text,
                    anchor="w",
                    justify="left",
                    font=ctk.CTkFont(size=10),
                    text_color="#6B7280",
                    fg_color="transparent",
                )
                secondary.pack(anchor="w", padx=12, pady=(0, 7))

            def bind_choose(widget, idx=index):
                widget.bind("<Button-1>", lambda _event, item_index=idx: choose_index(item_index))

            bind_choose(item)
            bind_choose(primary)
            if secondary is not None:
                bind_choose(secondary)

            item_refs.append({"frame": item, "primary": primary, "secondary": secondary})

        self.suggestion_popup = popup
        self.suggestion_state = {
            "popup": popup,
            "anchor_widget": anchor,
            "focus_widget": focus_target,
            "matches": visible_matches,
            "item_refs": item_refs,
            "selected_index": 0 if visible_matches else None,
            "choose": choose_index,
        }
        self._refresh_suggestion_highlight()

    def create_tree(self, master, columns, headings, height=10):
        frame = ctk.CTkFrame(master, fg_color="white", corner_radius=12)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        tree = ttk.Treeview(frame, columns=columns, show="headings", height=height)
        for col, heading in zip(columns, headings):
            tree.heading(col, text=heading)
            tree.column(col, width=130, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        return tree

    def dashboard_metrics(self):
        today = self.today_iso()
        peso_hoje = self.db_fetchone("""
            SELECT COALESCE(SUM(i.peso_liquido), 0) AS total
            FROM transacao_itens i
            JOIN transacoes t ON t.id = i.transacao_id
            WHERE t.tipo = 'COMPRA' AND date(t.data) = ?
        """, (today,))["total"]
        notas = self.db_fetchone("""
            SELECT COUNT(*) AS total
            FROM comprovantes
            WHERE date(data) = ?
        """, (today,))["total"]
        total_hoje = self.db_fetchone("""
            SELECT COALESCE(SUM(total), 0) AS total
            FROM transacoes
            WHERE date(data) = ?
        """, (today,))["total"]
        return peso_hoje, notas, total_hoje

    def metric_by_day(self, day):
        peso = self.db_fetchone("""
            SELECT COALESCE(SUM(i.peso_liquido), 0) AS total
            FROM transacao_itens i
            JOIN transacoes t ON t.id = i.transacao_id
            WHERE t.tipo = 'COMPRA' AND date(t.data) = ?
        """, (day,))["total"]
        notas = self.db_fetchone("""
            SELECT COUNT(*) AS total
            FROM comprovantes
            WHERE date(data) = ?
        """, (day,))["total"]
        return peso, notas

    def trend_vs_yesterday(self, today_value, yesterday_value):
        today_value = float(today_value or 0)
        yesterday_value = float(yesterday_value or 0)
        if yesterday_value == 0:
            text = "novo" if today_value > 0 else "0,0%"
            return f"{text}   vs. ontem"

        change = ((today_value - yesterday_value) / yesterday_value) * 100
        signal = "+" if change > 0 else "-" if change < 0 else ""
        percent = f"{abs(change):.1f}%".replace(".", ",")
        return f"{signal}{percent}   vs. ontem"

    def dashboard_trends(self):
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        peso_hoje, notas_hoje = self.metric_by_day(today.strftime("%Y-%m-%d"))
        peso_ontem, notas_ontem = self.metric_by_day(yesterday.strftime("%Y-%m-%d"))
        return (
            self.trend_vs_yesterday(peso_hoje, peso_ontem),
            self.trend_vs_yesterday(notas_hoje, notas_ontem),
        )

    def dashboard_series(self, days=7):
        base_day = datetime.now().date()
        peso_series = []
        notas_series = []
        for offset in range(days - 1, -1, -1):
            day = (base_day - timedelta(days=offset)).strftime("%Y-%m-%d")
            peso_dia, notas_dia = self.metric_by_day(day)
            peso_series.append(float(peso_dia or 0))
            notas_series.append(float(notas_dia or 0))
        return peso_series, notas_series

    def create_sparkline_image(self, values, color_hex, width=150, height=72):
        values = [float(v or 0) for v in values] if values else [0.0]
        if len(set(values)) == 1:
            base = values[0]
            values = [base + (0.1 * index) for index in range(len(values))]

        if plt is None:
            def hex_to_rgba(hex_color, alpha=255):
                raw = str(hex_color).strip().lstrip("#")
                if len(raw) == 3:
                    raw = "".join(ch * 2 for ch in raw)
                if len(raw) != 6:
                    return (47, 128, 237, alpha)
                return (int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16), alpha)

            scale = 4
            canvas_w = max(80, width) * scale
            canvas_h = max(40, height) * scale
            pad_x = 8 * scale
            pad_top = 8 * scale
            pad_bottom = 10 * scale
            usable_w = max(1, canvas_w - (pad_x * 2))
            usable_h = max(1, canvas_h - pad_top - pad_bottom)
            min_v = min(values)
            max_v = max(values)
            span = (max_v - min_v) or 1.0

            points = []
            for idx, value in enumerate(values):
                ratio_x = idx / float(max(1, len(values) - 1))
                ratio_y = (value - min_v) / span
                x = pad_x + (usable_w * ratio_x)
                y = pad_top + usable_h - (usable_h * ratio_y)
                points.append((x, y))

            canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(canvas, "RGBA")
            line_color = hex_to_rgba(color_hex, 255)
            fill_color = hex_to_rgba(color_hex, 42)

            area_points = [(points[0][0], canvas_h - pad_bottom)] + points + [(points[-1][0], canvas_h - pad_bottom)]
            draw.polygon(area_points, fill=fill_color)
            draw.line(points, fill=line_color, width=max(6, scale * 2), joint="curve")

            glow = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow, "RGBA")
            glow_draw.line(points, fill=hex_to_rgba(color_hex, 70), width=max(10, scale * 3), joint="curve")
            canvas = Image.alpha_composite(glow, canvas)

            chart = canvas.resize((width, height), Image.Resampling.LANCZOS)
            return ctk.CTkImage(light_image=chart, dark_image=chart, size=chart.size)

        fig = plt.figure(figsize=(width / 100.0, height / 100.0), dpi=100, facecolor=(1, 1, 1, 0))
        ax = fig.add_axes([0.02, 0.12, 0.96, 0.80])
        ax.set_facecolor((1, 1, 1, 0))

        x_values = list(range(len(values)))
        ax.plot(
            x_values,
            values,
            color=color_hex,
            linewidth=2.2,
            solid_capstyle="round",
            solid_joinstyle="round",
        )
        ax.fill_between(x_values, values, min(values), color=color_hex, alpha=0.12)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.margins(x=0.04, y=0.25)

        buffer = BytesIO()
        fig.savefig(buffer, format="png", transparent=True, bbox_inches="tight", pad_inches=0)
        plt.close(fig)
        buffer.seek(0)
        with Image.open(buffer) as chart_image:
            chart = chart_image.convert("RGBA")
            return ctk.CTkImage(light_image=chart, dark_image=chart, size=chart.size)

    def show_notifications(self):
        self.toggle_notifications_popup()

    def show_settings(self):
        messagebox.showinfo(
            "Configurações",
            f"Banco de dados ativo:\n{self.db_path}\n\n"
            "As informações são salvas automaticamente no SQLite local."
        )

    def show_profile(self):
        usuario_atual = self.usuario_logado or USUARIO_ADMIN
        if messagebox.askyesno(
            "Usuario",
            f"Usuario: {usuario_atual}\nPerfil: Administrador\n\nDeseja bloquear o sistema?"
        ):
            self.usuario_logado = None
            self.show_login()

    def dashboard_search_actions(self):
        return [
            {"label": "Nova Compra", "keywords": "compra comprar entrada material cadastrar", "command": self.tela_nova_compra},
            {"label": "Nova Venda", "keywords": "venda vender saida cliente", "command": self.tela_nova_venda},
            {"label": "Clientes", "keywords": "clientes fornecedores cadastro pessoa", "command": self.tela_clientes},
            {"label": "Materiais", "keywords": "materiais tipos cadastro", "command": lambda: self.pedir_senha_admin(self.tela_materiais, "Materiais")},
            {"label": "Historico", "keywords": "historico operacoes transacoes", "command": lambda: self.pedir_senha_admin(self.tela_historico, "Historico")},
            {"label": "Relatorios", "keywords": "relatorios analises financeiro", "command": lambda: self.pedir_senha_admin(self.tela_relatorios, "Relatorios")},
            {"label": "Estoque", "keywords": "estoque saldo movimentacoes", "command": self.tela_estoque},
            {"label": "Sangrias", "keywords": "sangria caixa retiradas", "command": self.tela_sangrias},
            {"label": "Comprovantes", "keywords": "comprovante comprovantes recibo recibos", "command": lambda: self.pedir_senha_admin(self.tela_comprovantes, "Comprovantes")},
            {"label": "Nota Fiscal", "keywords": "nota fiscal nfe emissao", "command": lambda: self.pedir_senha_admin(self.tela_nota_fiscal, "Nota Fiscal")},
            {"label": "Configuracoes", "keywords": "configuracoes ajustes banco dados", "command": self.show_settings},
            {"label": "Resumo do Dia", "keywords": "notificacoes resumo dia peso comprovantes", "command": self.show_notifications},
        ]

    def focus_dashboard_search(self, _event=None):
        if self.dashboard_search_entry is not None:
            self.dashboard_search_entry.focus_set()
            self.dashboard_search_entry.icursor("end")
        return "break"

    def close_dashboard_search_popup(self):
        if self.dashboard_search_popup is not None and self.dashboard_search_popup.winfo_exists():
            self.dashboard_search_popup.destroy()
        self.dashboard_search_popup = None
        self.dashboard_search_results = []
        self.dashboard_search_selected_index = 0

    def render_dashboard_search_popup(self):
        if self.dashboard_search_shell is None or not self.dashboard_search_results:
            self.close_dashboard_search_popup()
            return

        self.update_idletasks()
        shell = self.dashboard_search_shell
        root_x = self.winfo_rootx()
        root_y = self.winfo_rooty()
        popup_x = shell.winfo_rootx() - root_x
        popup_y = (shell.winfo_rooty() - root_y) + shell.winfo_height() + 6
        popup_w = shell.winfo_width()
        popup_h = min(6, len(self.dashboard_search_results)) * 42 + 12

        self.close_dashboard_search_popup()
        popup = ctk.CTkFrame(
            self.main_container,
            width=popup_w,
            height=popup_h,
            fg_color="#FFFFFF",
            corner_radius=14,
            border_width=1,
            border_color="#E5ECE5",
        )
        popup.place(x=popup_x, y=popup_y)
        popup.pack_propagate(False)
        self.dashboard_search_popup = popup

        inner = ctk.CTkFrame(popup, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=6, pady=6)

        for index, item in enumerate(self.dashboard_search_results[:6]):
            is_selected = index == self.dashboard_search_selected_index
            row = ctk.CTkButton(
                inner,
                text=item["label"],
                anchor="w",
                height=36,
                corner_radius=10,
                fg_color="#F3F8F1" if is_selected else "#FFFFFF",
                hover_color="#F3F8F1",
                text_color="#124B24" if is_selected else "#223126",
                font=self.login_ctk_font(12, "body"),
                command=lambda current=item: self.activate_dashboard_search_result(current),
            )
            row.pack(fill="x", pady=2)

    def update_dashboard_search_results(self, *_args):
        if self.dashboard_search_var is None:
            return
        query = (self.dashboard_search_var.get() or "").strip().casefold()
        actions = self.dashboard_search_actions()
        if not query:
            self.dashboard_search_results = actions[:6]
        else:
            filtered = []
            for item in actions:
                haystack = f"{item['label']} {item['keywords']}".casefold()
                if query in haystack:
                    filtered.append(item)
            self.dashboard_search_results = filtered[:6]
        self.dashboard_search_selected_index = 0
        self.render_dashboard_search_popup()

    def activate_dashboard_search_result(self, item=None):
        target = item
        if target is None and self.dashboard_search_results:
            safe_index = min(self.dashboard_search_selected_index, len(self.dashboard_search_results) - 1)
            target = self.dashboard_search_results[safe_index]
        self.close_dashboard_search_popup()
        if self.dashboard_search_var is not None:
            self.dashboard_search_var.set("")
        if self.dashboard_search_entry is not None:
            self.dashboard_search_entry.focus_set()
        if target:
            self.after(10, target["command"])

    def on_dashboard_search_enter(self, _event=None):
        if self.dashboard_search_results:
            self.activate_dashboard_search_result()
        return "break"

    def on_dashboard_search_escape(self, _event=None):
        self.close_dashboard_search_popup()
        return "break"

    def move_dashboard_search_selection(self, direction):
        if not self.dashboard_search_results:
            return "break"
        total = len(self.dashboard_search_results)
        self.dashboard_search_selected_index = (self.dashboard_search_selected_index + direction) % total
        self.render_dashboard_search_popup()
        return "break"

    def on_dashboard_search_down(self, _event=None):
        return self.move_dashboard_search_selection(1)

    def on_dashboard_search_up(self, _event=None):
        return self.move_dashboard_search_selection(-1)

    def notification_icon_style(self, tipo):
        key = str(tipo or "").strip().lower()
        styles = {
            "compra": {"bg": "#EEF8EA", "fg": "#2E9D62", "icon": "C"},
            "venda": {"bg": "#EEF8EA", "fg": "#2E9D62", "icon": "V"},
            "comprovante": {"bg": "#F5ECFA", "fg": "#9B51E0", "icon": "R"},
            "cliente": {"bg": "#EEF4FB", "fg": "#66A4EF", "icon": "U"},
            "material": {"bg": "#FBF4E7", "fg": "#F5B23B", "icon": "M"},
            "estoque": {"bg": "#FBF4E7", "fg": "#F5B23B", "icon": "E"},
            "relatorio": {"bg": "#FCECED", "fg": "#E67892", "icon": "R"},
            "sangria": {"bg": "#FFF4E8", "fg": "#D98939", "icon": "S"},
            "sistema": {"bg": "#ECF7EF", "fg": "#2E9D62", "icon": "!"}
        }
        return styles.get(key, {"bg": "#F3F5F2", "fg": "#6E796F", "icon": "i"})

    def notification_relative_time(self, created_at):
        try:
            created = datetime.strptime(str(created_at), "%Y-%m-%d %H:%M:%S")
        except Exception:
            return "Agora mesmo"
        delta = datetime.now() - created
        seconds = max(0, int(delta.total_seconds()))
        if seconds < 60:
            return "Agora mesmo"
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes} minuto{'s' if minutes != 1 else ''} atras"
        hours = minutes // 60
        if hours < 24:
            return f"{hours} hora{'s' if hours != 1 else ''} atras"
        days = hours // 24
        return f"{days} dia{'s' if days != 1 else ''} atras"

    def log_notification(self, tipo, titulo, mensagem, created_at=None):
        timestamp = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO notificacoes (tipo, titulo, mensagem, criado_em, lida) VALUES (?, ?, ?, ?, 0)",
                (str(tipo or ""), str(titulo or ""), str(mensagem or ""), timestamp),
            )
        self.refresh_notifications_ui()

    def fetch_notifications(self, limit=8):
        return self.db_fetchall(
            "SELECT id, tipo, titulo, mensagem, criado_em, lida FROM notificacoes ORDER BY datetime(criado_em) DESC, id DESC LIMIT ?",
            (int(limit),),
        )

    def unread_notifications_count(self):
        row = self.db_fetchone("SELECT COUNT(*) AS total FROM notificacoes WHERE lida = 0")
        return int(row["total"]) if row else 0

    def mark_all_notifications_read(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE notificacoes SET lida = 1 WHERE lida = 0")
        self.refresh_notifications_ui()
        self.render_notifications_popup()

    def mark_notification_read(self, notification_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE notificacoes SET lida = 1 WHERE id = ?", (notification_id,))
        self.refresh_notifications_ui()

    def update_notifications_badge(self):
        if self.notifications_badge_label is None or not self.notifications_badge_label.winfo_exists():
            return
        total = self.unread_notifications_count()
        if total > 0:
            self.notifications_badge_label.configure(text=str(min(total, 9)), fg_color="#1AA251")
            self.notifications_badge_label.place(relx=1.0, x=-8, y=8, anchor="ne")
        else:
            self.notifications_badge_label.place_forget()

    def close_notifications_popup(self):
        if self.notifications_popup is not None and self.notifications_popup.winfo_exists():
            self.notifications_popup.destroy()
        self.notifications_popup = None

    def render_notifications_popup(self):
        if self.notifications_button is None or not self.notifications_button.winfo_exists():
            return
        self.close_notifications_popup()
        self.update_idletasks()
        rows = self.fetch_notifications(6)
        root_x = self.winfo_rootx()
        root_y = self.winfo_rooty()
        popup_x = self.notifications_button.winfo_rootx() - root_x - 10
        popup_y = (self.notifications_button.winfo_rooty() - root_y) + self.notifications_button.winfo_height() + 8
        popup_w = 372
        popup_h = 72 + max(1, len(rows)) * 74 + 54

        popup = ctk.CTkFrame(
            self.main_container,
            width=popup_w,
            height=popup_h,
            fg_color="#FFFFFF",
            corner_radius=18,
            border_width=1,
            border_color="#E5ECE5",
        )
        popup.place(x=popup_x, y=popup_y)
        popup.pack_propagate(False)
        self.notifications_popup = popup

        header = ctk.CTkFrame(popup, fg_color="transparent", height=52)
        header.pack(fill="x", padx=16, pady=(12, 8))
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="Notificacoes", font=self.login_ctk_font(15, "title"), text_color="#163022").pack(side="left")
        ctk.CTkButton(
            header,
            text="Marcar todas como lidas",
            height=28,
            corner_radius=10,
            fg_color="#FFFFFF",
            hover_color="#F3F8F1",
            text_color="#1AA251",
            font=self.login_ctk_font(11, "body"),
            border_width=0,
            command=self.mark_all_notifications_read,
        ).pack(side="right")

        body = ctk.CTkFrame(popup, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=12)

        if not rows:
            ctk.CTkLabel(
                body,
                text="Nenhuma notificacao ainda.",
                font=self.login_ctk_font(12, "body"),
                text_color="#6E796F",
            ).pack(anchor="w", pady=16, padx=6)
        else:
            for row in rows:
                item = ctk.CTkButton(
                    body,
                    text="",
                    height=68,
                    corner_radius=14,
                    fg_color="#FFFFFF",
                    hover_color="#F7FAF7",
                    border_width=1,
                    border_color="#EEF1EE",
                    command=lambda notification_id=row["id"]: self.mark_notification_read(notification_id),
                )
                item.pack(fill="x", pady=4)
                item.pack_propagate(False)

                style = self.notification_icon_style(row["tipo"])
                icon_box = ctk.CTkFrame(item, width=34, height=34, fg_color=style["bg"], corner_radius=17)
                icon_box.place(x=12, rely=0.5, anchor="w")
                icon_box.pack_propagate(False)
                ctk.CTkLabel(icon_box, text=style["icon"], font=self.login_ctk_font(12, "title"), text_color=style["fg"]).pack(expand=True)

                ctk.CTkLabel(item, text=row["titulo"], font=self.login_ctk_font(12, "title"), text_color="#1C2320").place(x=54, y=10, anchor="w")
                ctk.CTkLabel(item, text=row["mensagem"], font=self.login_ctk_font(11, "body"), text_color="#5F6C63").place(x=54, y=31, anchor="w")
                ctk.CTkLabel(item, text=self.notification_relative_time(row["criado_em"]), font=self.login_ctk_font(10, "body"), text_color="#7F8B82").place(x=54, y=50, anchor="w")
                if not int(row["lida"] or 0):
                    dot = ctk.CTkFrame(item, width=8, height=8, fg_color="#1AA251", corner_radius=4)
                    dot.place(relx=1.0, x=-16, y=14, anchor="ne")

        footer = ctk.CTkFrame(popup, fg_color="transparent", height=42)
        footer.pack(fill="x", padx=14, pady=(4, 12))
        footer.pack_propagate(False)
        ctk.CTkButton(
            footer,
            text="Ver todas as notificacoes",
            height=30,
            corner_radius=12,
            fg_color="#FFFFFF",
            hover_color="#F3F8F1",
            text_color="#1AA251",
            font=self.login_ctk_font(11, "body"),
            border_width=0,
            command=self.show_all_notifications,
        ).pack(expand=True)

    def toggle_notifications_popup(self):
        if self.notifications_popup is not None and self.notifications_popup.winfo_exists():
            self.close_notifications_popup()
            return
        self.render_notifications_popup()

    def show_all_notifications(self):
        rows = self.fetch_notifications(30)
        if not rows:
            messagebox.showinfo("Notificacoes", "Nenhuma notificacao registrada.")
            return
        text = []
        for row in rows:
            text.append(f"{row['titulo']}\n{row['mensagem']}\n{self.notification_relative_time(row['criado_em'])}")
        messagebox.showinfo("Todas as notificacoes", "\n\n".join(text[:15]))

    def ensure_daily_notifications(self):
        now = datetime.now()
        if now.hour < 18:
            return
        today_key = now.strftime("%Y-%m-%d")
        existing = self.db_fetchone(
            "SELECT id FROM notificacoes WHERE tipo = 'relatorio' AND titulo = ? AND substr(criado_em, 1, 10) = ? LIMIT 1",
            ("Feche seu relatorio do dia", today_key),
        )
        if existing:
            return
        self.log_notification(
            "relatorio",
            "Feche seu relatorio do dia",
            "Ja sao 18h. Confira as operacoes e finalize o relatorio do dia.",
        )

    def refresh_notifications_ui(self):
        self.ensure_daily_notifications()
        self.update_notifications_badge()

    def schedule_notifications_refresh(self):
        self.refresh_notifications_ui()
        if self.notifications_after_id is not None:
            try:
                self.after_cancel(self.notifications_after_id)
            except Exception:
                pass
        self.notifications_after_id = self.after(60000, self.schedule_notifications_refresh)

    def show_login(self):
        self.clear_main()
        self.update_idletasks()
        widget_scale = self._get_widget_scaling() if hasattr(self, "_get_widget_scaling") else 1.0
        scene_width = max(self.winfo_screenwidth(), self.winfo_width(), 1366)
        scene_height = max(self.winfo_screenheight(), self.winfo_height(), 760)
        layout_width = max(1, int(scene_width / widget_scale))
        layout_height = max(1, int(scene_height / widget_scale))
        left_width = layout_width // 2
        right_width = layout_width - left_width
        left_scene_width = scene_width // 2

        self.main_container = ctk.CTkFrame(self, fg_color="#F7F5EF", corner_radius=0)
        self.main_container.pack(fill="both", expand=True)

        scene_art = self.login_scene_art(scene_width, scene_height, left_scene_width)
        self.login_background_img = ctk.CTkImage(
            light_image=scene_art,
            dark_image=scene_art,
            size=(layout_width, layout_height),
        )
        ctk.CTkLabel(self.main_container, image=self.login_background_img, text="").place(relx=0, rely=0, relwidth=1, relheight=1)

        login_card_width = min(430, max(388, right_width - 102))
        login_card_height = 504
        right_center_x = left_width + (right_width // 2)
        card_top = max(64, int(layout_height * 0.12))

        shadow_outer = ctk.CTkFrame(
            self.main_container,
            width=login_card_width + 10,
            height=login_card_height + 12,
            fg_color="#F5F8F2",
            corner_radius=32,
        )
        shadow_outer.place(x=right_center_x + 3, y=card_top + 6, anchor="n")
        shadow_outer.grid_propagate(False)

        card = ctk.CTkFrame(
            self.main_container,
            width=login_card_width,
            height=login_card_height,
            fg_color="white",
            corner_radius=28,
            border_width=1,
            border_color="#E2EBDD",
        )
        card.place(x=right_center_x, y=card_top, anchor="n")
        card.grid_propagate(False)

        badge_outer = ctk.CTkFrame(card, width=64, height=64, fg_color="#EFF7EE", corner_radius=32, border_width=1, border_color="#D8E8D8")
        badge_outer.place(relx=0.5, y=24, anchor="n")
        badge_outer.grid_propagate(False)
        badge_icon = self.prepare_login_badge_pil(34, 34)
        if badge_icon:
            self.login_badge_icon_img = ctk.CTkImage(light_image=badge_icon, dark_image=badge_icon, size=badge_icon.size)
            ctk.CTkLabel(badge_outer, image=self.login_badge_icon_img, text="", fg_color="transparent").place(relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(badge_outer, text="VR", font=ctk.CTkFont(size=12, weight="bold"), text_color="#0E6B2E").place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card, text="Entrar no sistema", font=self.login_ctk_font(24, role="title"), text_color="#18221D", fg_color="transparent").pack(anchor="center", pady=(98, 4))
        ctk.CTkLabel(card, text="Use seu acesso para continuar.", font=self.login_ctk_font(12, role="body"), text_color="#707A73", fg_color="transparent").pack(anchor="center", pady=(0, 18))

        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=42, pady=(0, 18))

        self.login_user_icon_img = self.login_line_icon_art("user", 16, "#6F7D73")
        self.login_lock_icon_img = self.login_line_icon_art("lock", 16, "#6F7D73")

        def build_login_field(label_text, icon_image, default_border, border_width, show_mask=False):
            ctk.CTkLabel(
                form,
                text=label_text,
                font=self.login_ctk_font(11, role="body"),
                text_color="#59665D",
                fg_color="transparent",
            ).pack(anchor="w", pady=(0, 6))

            shell = ctk.CTkFrame(
                form,
                height=48,
                corner_radius=14,
                fg_color="white",
                border_width=border_width,
                border_color=default_border,
            )
            shell.pack(fill="x", pady=(0, 10))
            shell.pack_propagate(False)
            shell.grid_columnconfigure(1, weight=1)

            icon_label = ctk.CTkLabel(shell, text="", image=icon_image, fg_color="transparent")
            icon_label.grid(row=0, column=0, padx=(14, 10), pady=12)

            entry = ctk.CTkEntry(
                shell,
                height=34,
                border_width=0,
                corner_radius=0,
                fg_color="white",
                text_color="#18221D",
                font=self.login_ctk_font(14, role="body"),
                placeholder_text=label_text,
                placeholder_text_color="#8B968F",
                show="*" if show_mask else "",
            )
            entry.grid(row=0, column=1, sticky="ew", padx=(0, 14), pady=7)

            def focus_in(_event=None):
                shell.configure(border_color="#2B8A46")

            def focus_out(_event=None):
                shell.configure(border_color=default_border)

            shell.bind("<Button-1>", lambda _event: entry.focus_set())
            icon_label.bind("<Button-1>", lambda _event: entry.focus_set())
            entry.bind("<FocusIn>", focus_in)
            entry.bind("<FocusOut>", focus_out)
            return entry

        self.login_usuario_entry = build_login_field("Usuario", self.login_user_icon_img, "#2B8A46", 2)
        self.login_usuario_entry.insert(0, USUARIO_ADMIN)

        self.login_senha_entry = build_login_field("Senha", self.login_lock_icon_img, "#D3DDD2", 1, show_mask=True)

        self.login_feedback = ctk.CTkLabel(
            form,
            text="",
            justify="left",
            font=self.login_ctk_font(12, role="body"),
            text_color="#B84545",
            fg_color="transparent",
        )
        self.login_feedback.pack(anchor="w", fill="x", pady=(0, 2))

        ctk.CTkButton(
            form,
            text="Entrar",
            height=50,
            corner_radius=14,
            fg_color="#11813A",
            hover_color="#0D6B30",
            border_width=1,
            border_color="#2BA253",
            font=self.login_ctk_font(15, role="title"),
            command=self.validar_login,
        ).pack(fill="x", pady=(4, 18))

        self.login_senha_entry.bind("<Return>", lambda _event: self.validar_login())
        self.login_usuario_entry.bind("<Return>", lambda _event: self.login_senha_entry.focus_set())
        self.after(100, lambda widget=self.login_senha_entry: widget.focus_set() if widget and widget.winfo_exists() else None)

    def _modern_show_login(self):
        self.clear_main()
        self.update_idletasks()
        widget_scale = self._get_widget_scaling() if hasattr(self, "_get_widget_scaling") else 1.0
        scene_width = max(self.winfo_screenwidth(), self.winfo_width(), 1366)
        scene_height = max(self.winfo_screenheight(), self.winfo_height(), 760)
        layout_width = max(1, int(scene_width / widget_scale))
        layout_height = max(1, int(scene_height / widget_scale))
        self.login_password_visible = False

        self.main_container = ctk.CTkFrame(self, fg_color="#FBFCFA", corner_radius=0)
        self.main_container.pack(fill="both", expand=True)

        scene_art = self.login_scene_art(scene_width, scene_height, scene_width)
        self.login_background_img = ctk.CTkImage(
            light_image=scene_art,
            dark_image=scene_art,
            size=(layout_width, layout_height),
        )
        ctk.CTkLabel(
            self.main_container,
            image=self.login_background_img,
            text="",
        ).place(relx=0, rely=0, relwidth=1, relheight=1)

        login_card_width = min(452, max(402, int(layout_width * 0.31)))
        login_card_height = min(596, max(528, int(layout_height * 0.72)))
        card_center_y = layout_height // 2

        shadow_far = ctk.CTkFrame(
            self.main_container,
            width=login_card_width + 48,
            height=login_card_height + 54,
            fg_color="#EEF4EC",
            corner_radius=38,
        )
        shadow_far.place(relx=0.5, y=card_center_y + 16, anchor="center")
        shadow_far.grid_propagate(False)

        shadow_soft = ctk.CTkFrame(
            self.main_container,
            width=login_card_width + 24,
            height=login_card_height + 28,
            fg_color="#F6F9F4",
            corner_radius=34,
        )
        shadow_soft.place(relx=0.5, y=card_center_y + 8, anchor="center")
        shadow_soft.grid_propagate(False)

        card = ctk.CTkFrame(
            self.main_container,
            width=login_card_width,
            height=login_card_height,
            fg_color="white",
            corner_radius=30,
            border_width=1,
            border_color="#E5ECE3",
        )
        card.place(relx=0.5, y=card_center_y, anchor="center")
        card.grid_propagate(False)

        heading_font = ctk.CTkFont(family="Segoe UI", size=31, weight="bold")
        subheading_font = ctk.CTkFont(family="Segoe UI", size=14)
        label_font = ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        field_font = ctk.CTkFont(family="Segoe UI", size=14)
        helper_font = ctk.CTkFont(family="Segoe UI", size=12)
        button_font = ctk.CTkFont(family="Segoe UI", size=15, weight="bold")

        self.login_user_icon_img = self.login_line_icon_art("user", 18, "#7A867D")
        self.login_lock_icon_img = self.login_line_icon_art("lock", 18, "#7A867D")
        self.login_eye_open_icon_img = self.login_line_icon_art("eye", 18, "#70826E")
        self.login_eye_closed_icon_img = self.login_line_icon_art("eye_off", 18, "#70826E")
        self.login_arrow_icon_img = self.login_line_icon_art("arrow", 16, "#FFFFFF")

        badge_outer = ctk.CTkFrame(
            card,
            width=76,
            height=76,
            fg_color="#EEF7EE",
            corner_radius=38,
            border_width=1,
            border_color="#D9E8D7",
        )
        badge_outer.place(relx=0.5, y=34, anchor="n")
        badge_outer.grid_propagate(False)

        badge_inner = ctk.CTkFrame(
            badge_outer,
            width=48,
            height=48,
            fg_color="#DDF0DE",
            corner_radius=24,
        )
        badge_inner.place(relx=0.5, rely=0.5, anchor="center")
        badge_inner.grid_propagate(False)

        badge_icon = self.prepare_login_badge_pil(34, 34)
        if badge_icon:
            self.login_badge_icon_img = ctk.CTkImage(
                light_image=badge_icon,
                dark_image=badge_icon,
                size=badge_icon.size,
            )
            ctk.CTkLabel(
                badge_inner,
                image=self.login_badge_icon_img,
                text="",
                fg_color="transparent",
            ).place(relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(
                badge_inner,
                text="VR",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#0E6B2E",
            ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            card,
            text="Entrar no sistema",
            font=heading_font,
            text_color="#16211B",
            fg_color="transparent",
        ).pack(anchor="center", pady=(128, 6))
        ctk.CTkLabel(
            card,
            text="Use seu acesso para continuar.",
            font=subheading_font,
            text_color="#718076",
            fg_color="transparent",
        ).pack(anchor="center", pady=(0, 30))

        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=42, pady=(0, 40))

        def build_login_field(label_text, placeholder_text, icon_image, password_mode=False):
            ctk.CTkLabel(
                form,
                text=label_text,
                font=label_font,
                text_color="#5F6D63",
                fg_color="transparent",
            ).pack(anchor="w", pady=(0, 8))

            field_shell = ctk.CTkFrame(
                form,
                height=56,
                corner_radius=18,
                fg_color="#FFFFFF",
                border_width=1,
                border_color="#D9E2D8",
            )
            field_shell.pack(fill="x", pady=(0, 18))
            field_shell.pack_propagate(False)
            field_shell.grid_columnconfigure(1, weight=1)

            icon_label = ctk.CTkLabel(field_shell, text="", image=icon_image, fg_color="transparent")
            icon_label.grid(row=0, column=0, padx=(18, 12), pady=14)

            entry = ctk.CTkEntry(
                field_shell,
                height=34,
                border_width=0,
                corner_radius=0,
                fg_color="#FFFFFF",
                text_color="#18221D",
                placeholder_text=placeholder_text,
                placeholder_text_color="#9AA79D",
                font=field_font,
            )
            entry.grid(row=0, column=1, sticky="ew", padx=(0, 12 if not password_mode else 6), pady=10)

            def focus_in(_event=None):
                field_shell.configure(border_color="#6DAA78")

            def focus_out(_event=None):
                field_shell.configure(border_color="#D9E2D8")

            field_shell.bind("<Button-1>", lambda _event: entry.focus_set())
            icon_label.bind("<Button-1>", lambda _event: entry.focus_set())
            entry.bind("<FocusIn>", focus_in)
            entry.bind("<FocusOut>", focus_out)

            toggle_btn = None
            if password_mode:
                entry.configure(show="*")
                toggle_btn = ctk.CTkButton(
                    field_shell,
                    text="",
                    image=self.login_eye_closed_icon_img,
                    width=30,
                    height=30,
                    corner_radius=15,
                    fg_color="transparent",
                    hover_color="#EFF6EE",
                    command=self.toggle_login_password_visibility,
                )
                toggle_btn.grid(row=0, column=2, padx=(0, 16), pady=10)

            return entry, toggle_btn

        self.login_usuario_entry, _unused_toggle = build_login_field(
            "Usuario",
            "Digite seu usuario",
            self.login_user_icon_img,
        )
        self.login_senha_entry, self.login_password_toggle_btn = build_login_field(
            "Senha",
            "Digite sua senha",
            self.login_lock_icon_img,
            password_mode=True,
        )


        self.login_feedback = ctk.CTkLabel(
            form,
            text="",
            justify="left",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#B84545",
            fg_color="transparent",
        )
        self.login_feedback.pack(anchor="w", fill="x", pady=(4, 14))

        button_shadow = ctk.CTkFrame(
            form,
            fg_color="#EDF4EC",
            corner_radius=19,
            height=58,
        )
        button_shadow.pack(fill="x", pady=(2, 0))
        button_shadow.pack_propagate(False)

        ctk.CTkButton(
            button_shadow,
            text="Entrar",
            image=self.login_arrow_icon_img,
            compound="right",
            height=50,
            corner_radius=16,
            fg_color="#11813E",
            hover_color="#0D6932",
            text_color="white",
            font=button_font,
            command=self.validar_login,
        ).pack(fill="x", padx=4, pady=4)

        self.login_senha_entry.bind("<Return>", lambda _event: self.validar_login())
        self.login_usuario_entry.bind("<Return>", lambda _event: self.login_senha_entry.focus_set())
        self.after(100, lambda widget=self.login_usuario_entry: widget.focus_set() if widget and widget.winfo_exists() else None)

    def validar_login(self):
        usuario_digitado = self.login_usuario_entry.get().strip() if self.login_usuario_entry else ""
        usuario = usuario_digitado.casefold()
        usuario_admin = USUARIO_ADMIN.casefold()
        senha = self.login_senha_entry.get().strip() if self.login_senha_entry else ""

        if usuario == usuario_admin and senha == SENHA_ADMIN:
            self.usuario_logado = usuario_digitado or USUARIO_ADMIN
            self.build_ui()
            return

        if self.login_feedback:
            self.login_feedback.configure(text="Usuario ou senha incorretos.")
        if self.login_senha_entry:
            self.login_senha_entry.delete(0, "end")
            self.login_senha_entry.focus_set()

    def pedir_senha_admin(self, destino, area):
        senha = self.solicitar_senha_admin(area)
        if senha is None:
            return
        if senha == SENHA_ADMIN:
            destino()
            return

    def update_clock(self):
        if self.welcome_subtitle_label is not None and self.welcome_subtitle_label.winfo_exists():
            self.welcome_subtitle_label.configure(text=self.format_current_datetime())
            self.clock_after_id = self.after(30000, self.update_clock)

    def clear_main(self):
        if self.clock_after_id is not None:
            self.after_cancel(self.clock_after_id)
            self.clock_after_id = None
        if self.notifications_after_id is not None:
            self.after_cancel(self.notifications_after_id)
            self.notifications_after_id = None
        self.welcome_subtitle_label = None
        self.close_dashboard_search_popup()
        self.close_notifications_popup()
        self.clear_suggestion_popup()

        if self.main_container is not None:
            self.main_container.destroy()

    def build_ui(self):
        self.clear_main()

        self.main_container = ctk.CTkFrame(self, fg_color="#F4F4F1", corner_radius=0)
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.build_header()
        self.build_body()
        self.build_footer()
        self.schedule_notifications_refresh()

    def build_header(self):
        header = ctk.CTkFrame(
            self.main_container,
            height=96,
            corner_radius=0,
            fg_color="#FBFCFA"
        )
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        header.pack_propagate(False)
        header.configure(border_width=1, border_color="#E7EEE4")

        brand_logo = self.prepare_header_brand_logo_pil(150, 62)
        if brand_logo is not None:
            self.header_logo_img = ctk.CTkImage(light_image=brand_logo, dark_image=brand_logo, size=brand_logo.size)
            logo = ctk.CTkLabel(header, image=self.header_logo_img, text="", fg_color="transparent")
            logo.place(x=24, rely=0.5, anchor="w")
        elif os.path.exists(self.logo_path):
            logo_pil = ImageOps.exif_transpose(Image.open(self.logo_path))
            logo_size = self.fit_image_size(logo_pil, max_width=150, max_height=62)
            self.header_logo_img = ctk.CTkImage(light_image=logo_pil, dark_image=logo_pil, size=logo_size)
            logo = ctk.CTkLabel(header, image=self.header_logo_img, text="")
            logo.place(x=24, rely=0.5, anchor="w")
        else:
            logo = ctk.CTkLabel(
                header,
                text="VR VINHESQUE\nRECICLAGEM",
                justify="left",
                font=self.login_ctk_font(24, "title"),
                text_color="#0D6A2A"
            )
            logo.place(x=24, rely=0.5, anchor="w")

        divider = ctk.CTkFrame(header, width=2, height=48, fg_color="#DFE7DF")
        divider.place(x=180, rely=0.5, anchor="center")

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.place(x=210, rely=0.5, anchor="w")

        title = ctk.CTkLabel(
            title_box,
            text="Sistema de Gestao",
            font=self.login_ctk_font(18, "title"),
            text_color="#124B24"
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            title_box,
            text="Sustentabilidade que gera valor",
            font=self.login_ctk_font(11, "body"),
            text_color="#687568"
        )
        subtitle.pack(anchor="w", pady=(4, 0))

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right", padx=18, pady=16)

        search_shell = ctk.CTkFrame(
            right,
            width=360,
            height=52,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=1,
            border_color="#E5ECE5",
        )
        search_shell.pack(side="left", padx=(0, 16))
        search_shell.pack_propagate(False)
        self.dashboard_search_shell = search_shell
        self.dashboard_search_var = ctk.StringVar(value="")

        ctk.CTkLabel(
            search_shell,
            text="⌕",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#7B8680",
        ).place(x=18, rely=0.5, anchor="w")
        self.dashboard_search_entry = ctk.CTkEntry(
            search_shell,
            textvariable=self.dashboard_search_var,
            placeholder_text="Buscar no sistema...",
            width=184,
            height=34,
            border_width=0,
            fg_color="#FFFFFF",
            text_color="#25332A",
            font=self.login_ctk_font(12, "body"),
        )
        self.dashboard_search_entry.place(x=48, y=9)
        self.dashboard_search_var.trace_add("write", self.update_dashboard_search_results)
        self.dashboard_search_entry.bind("<Return>", self.on_dashboard_search_enter)
        self.dashboard_search_entry.bind("<Escape>", self.on_dashboard_search_escape)
        self.dashboard_search_entry.bind("<Down>", self.on_dashboard_search_down)
        self.dashboard_search_entry.bind("<Up>", self.on_dashboard_search_up)
        self.dashboard_search_entry.bind("<FocusOut>", lambda _e: self.after(120, self.close_dashboard_search_popup))
        self.bind("<Control-k>", self.focus_dashboard_search)
        self.bind("<Control-K>", self.focus_dashboard_search)

        shortcut = ctk.CTkFrame(search_shell, width=64, height=28, fg_color="#F3F5F2", corner_radius=10)
        shortcut.place(relx=1.0, x=-14, rely=0.5, anchor="e")
        shortcut.pack_propagate(False)
        shortcut_label = ctk.CTkLabel(
            shortcut,
            text="Ctrl + K",
            font=self.login_ctk_font(10, "body"),
            text_color="#6E796F",
        )
        shortcut_label.pack(expand=True)
        shortcut.bind("<Button-1>", self.focus_dashboard_search)
        shortcut_label.bind("<Button-1>", self.focus_dashboard_search)

        bell = ctk.CTkButton(
            right,
            text="🔔",
            width=44,
            height=44,
            corner_radius=14,
            fg_color="#FFFFFF",
            hover_color="#F4F7F3",
            border_width=1,
            border_color="#E5ECE5",
            text_color="#15211A",
            font=ctk.CTkFont(size=18),
            command=self.show_notifications
        )
        bell.pack(side="left", padx=6)
        self.notifications_button = bell
        self.notifications_badge_label = None

        gear = ctk.CTkButton(
            right,
            text="⚙",
            width=44,
            height=44,
            corner_radius=14,
            fg_color="#FFFFFF",
            hover_color="#F4F7F3",
            border_width=1,
            border_color="#E5ECE5",
            text_color="#15211A",
            font=ctk.CTkFont(size=18),
            command=self.show_settings
        )
        gear.pack(side="left", padx=6)

        profile = ctk.CTkFrame(
            right,
            width=220,
            height=56,
            corner_radius=16,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#E5ECE5"
        )
        profile.pack(side="left", padx=(12, 0))
        profile.pack_propagate(False)

        avatar_shell = ctk.CTkFrame(profile, width=42, height=42, fg_color="#0C5C28", corner_radius=21)
        avatar_shell.place(x=12, rely=0.5, anchor="w")
        avatar_shell.pack_propagate(False)

        avatar = ctk.CTkLabel(
            avatar_shell,
            text="VR",
            font=self.login_ctk_font(14, "title"),
            text_color="#F1F8F1"
        )
        avatar.pack(expand=True)

        user_name = ctk.CTkLabel(
            profile,
            text=self.usuario_logado or "Administrador",
            font=self.login_ctk_font(12, "title"),
            text_color="#163022"
        )
        user_name.place(x=64, y=7)

        welcome = ctk.CTkLabel(
            profile,
            text="Bem-vindo(a)",
            font=self.login_ctk_font(10, "body"),
            text_color="#738076"
        )
        welcome.place(x=64, y=27)

        arrow = ctk.CTkLabel(
            profile,
            text="▾",
            font=self.login_ctk_font(12, "title"),
            text_color="#163022"
        )
        arrow.place(relx=1.0, x=-18, y=16, anchor="ne")
        profile.bind("<Button-1>", lambda _event: self.show_profile())

    def build_body(self):
        body = ctk.CTkFrame(self.main_container, fg_color="#F7F8F6", corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew", padx=28, pady=(6, 4))

        top_row = ctk.CTkFrame(body, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 12))

        for i in range(3):
            top_row.grid_columnconfigure(i, weight=1)

        peso_hoje, notas_hoje, _total_hoje = self.dashboard_metrics()
        peso_trend, notas_trend = self.dashboard_trends()
        peso_series, notas_series = self.dashboard_series(7)
        peso_sparkline = self.create_sparkline_image(peso_series, "#2F80ED", width=150, height=72)
        notas_sparkline = self.create_sparkline_image(notas_series, "#9B51E0", width=150, height=72)

        bem_vindo = TopInfoCard(
            top_row,
            icon="VR",
            title=f"Bem-vindo(a), {self.usuario_logado or 'Administrador'}!",
            value="Tenha um ótimo dia de trabalho.",
            subtitle=self.format_current_datetime(),
            dark=True,
            width=470,
            height=128
        )
        bem_vindo.grid(row=0, column=0, padx=(0, 14), sticky="nsew")
        self.welcome_subtitle_label = bem_vindo.subtitle_label
        self.update_clock()

        peso = TopInfoCard(
            top_row,
            icon="⚖",
            title="Peso Recebido Hoje",
            value=self.format_kg(peso_hoje),
            subtitle=peso_trend,
            accent="#2F80ED",
            sparkline_image=peso_sparkline,
            width=360,
            height=124
        )
        peso.grid(row=0, column=1, padx=8, pady=(2, 0), sticky="nsew")

        notas = TopInfoCard(
            top_row,
            icon="🧾",
            title="Comprovantes Emitidos",
            value=str(notas_hoje),
            subtitle=notas_trend,
            accent="#9B51E0",
            sparkline_image=notas_sparkline,
            width=360,
            height=124
        )
        notas.grid(row=0, column=2, padx=(8, 0), pady=(2, 0), sticky="nsew")

        menu_container = ctk.CTkFrame(body, fg_color="#F7F8F6")
        menu_container.pack(fill="both", expand=True)

        title_row = ctk.CTkFrame(menu_container, fg_color="#F7F8F6")
        title_row.pack(fill="x")

        menu_title = ctk.CTkLabel(
            title_row,
            text="Menu Principal",
            font=self.login_ctk_font(20, "title"),
            text_color="#1D1D1D"
        )
        menu_title.pack(anchor="w")

        menu_subtitle = ctk.CTkLabel(
            title_row,
            text="Acesse as principais funções do sistema",
            font=self.login_ctk_font(13, "body"),
            text_color="#555555"
        )
        menu_subtitle.pack(anchor="w", pady=(0, 0))

        cards_data = [
            ("Nova Compra", "Cadastrar entrada\nde materiais", "🛒", "#EEF8EA", "#73BE4E", self.tela_nova_compra),
            ("Nova Venda", "Vender materiais para\nclientes", "🏷", "#EFF8EC", "#73BE4E", self.tela_nova_venda),
            ("Clientes", "Gerenciar clientes e\nfornecedores", "👥", "#EEF4FB", "#66A4EF", self.tela_clientes),
            ("Materiais", "Gerenciar tipos de\nmateriais", "📦", "#FBF4E7", "#F5B23B", lambda: self.pedir_senha_admin(self.tela_materiais, "Materiais")),
            ("Histórico", "Consultar operações\nrealizadas", "🧾", "#F5ECFA", "#A970E0", lambda: self.pedir_senha_admin(self.tela_historico, "Histórico")),
            ("Relatórios", "Análises e relatórios\nfinanceiros", "📊", "#FCECED", "#E67892", lambda: self.pedir_senha_admin(self.tela_relatorios, "Relatórios")),
            ("Estoque", "Visualizar saldo e\nmovimentações", "🗂", "#E8F1FB", "#7EB0EA", self.tela_estoque),
            ("Sangrias", "Registrar retiradas\nde caixa", "💸", "#FFF4E8", "#D98939", self.tela_sangrias),
            ("Comprovante", "Consultar recibos\nde operações", "▤", "#ECF7EF", "#2E9D62", lambda: self.pedir_senha_admin(self.tela_comprovantes, "Comprovantes")),
            ("Nota Fiscal", "Emitir e consultar\nnotas fiscais", "📄", "#F9EFE4", "#E7A15F", lambda: self.pedir_senha_admin(self.tela_nota_fiscal, "Nota Fiscal")),
        ]

        max_columns = 5
        total_rows = (len(cards_data) + max_columns - 1) // max_columns
        card_width = 178
        card_height = 150 if total_rows > 1 else 164
        card_gap_x = 10
        card_gap_y = 20
        cards_frame = ctk.CTkFrame(menu_container, fg_color="#F7F8F6")
        cards_frame.pack(fill="x", padx=8, pady=(14, 0))
        cards_frame.grid_anchor("center")

        for i in range(max_columns):
            cards_frame.grid_columnconfigure(i, weight=1, uniform="menu_cards")

        for idx, (title, subtitle, icon, color, button_color, command) in enumerate(cards_data):
            row = idx // max_columns
            column = idx % max_columns
            card = MenuCard(
                cards_frame,
                title=title,
                subtitle=subtitle,
                icon=icon,
                icon_image=self.get_menu_card_icon_image(title, 42 if title == "Nova Compra" else 28),
                color=color,
                button_color=button_color,
                command=command,
                width=card_width,
                height=card_height
            )
            card.grid(
                row=row,
                column=column,
                padx=(card_gap_x // 2, card_gap_x // 2),
                pady=(0, card_gap_y if row < total_rows - 1 else 0),
                sticky="ew",
            )

    def build_footer(self):
        footer = ctk.CTkFrame(
            self.main_container,
            height=34,
            corner_radius=0,
            fg_color="#F7F8F6"
        )
        footer.grid(row=2, column=0, sticky="ew", padx=28, pady=(2, 6))
        footer.grid_propagate(False)

        footer_shell = ctk.CTkFrame(
            footer,
            fg_color="#FFFFFF",
            width=1,
            height=34,
            corner_radius=14,
            border_width=1,
            border_color="#E7EEE4"
        )
        footer_shell.place(relx=0.5, rely=0.5, relwidth=1.0, anchor="center")
        footer_shell.pack_propagate(False)

        if self.footer_whatsapp_img is None:
            whatsapp_icon = self.prepare_whatsapp_logo_pil(16, 16)
            if whatsapp_icon is not None:
                self.footer_whatsapp_img = ctk.CTkImage(
                    light_image=whatsapp_icon,
                    dark_image=whatsapp_icon,
                    size=whatsapp_icon.size,
                )

        if self.footer_security_icon_img is None:
            security_icon = self.prepare_footer_security_icon_pil(14, 14)
            if security_icon is not None:
                self.footer_security_icon_img = ctk.CTkImage(
                    light_image=security_icon,
                    dark_image=security_icon,
                    size=security_icon.size,
                )

        left = ctk.CTkLabel(
            footer_shell,
            text="Sistema seguro e protegido  •  Versão 2.2.0",
            image=self.footer_security_icon_img,
            compound="left",
            justify="left",
            font=self.login_ctk_font(10, "body"),
            text_color="#002F12"
        )
        left.place(x=16, rely=0.5, anchor="w")

        center = ctk.CTkLabel(
            footer_shell,
            text="VR Vinhesque Reciclagem - Todos os direitos reservados",
            font=self.login_ctk_font(10, "body"),
            text_color="#245335"
        )
        center.place(relx=0.5, rely=0.5, anchor="center")

        right = ctk.CTkFrame(footer_shell, fg_color="transparent", width=250, height=20)
        right.place(relx=1.0, x=-16, rely=0.5, anchor="e")
        right.pack_propagate(False)

        support_line = ctk.CTkFrame(right, fg_color="transparent", width=250, height=20)
        support_line.place(relx=1.0, x=0, rely=0.5, anchor="e")
        support_line.pack_propagate(False)

        ctk.CTkLabel(
            support_line,
            text="(18) 99610-9679   WhatsApp",
            justify="right",
            font=self.login_ctk_font(10, "body"),
            text_color="#002F12"
        ).pack(side="left", anchor="e")

        if self.footer_whatsapp_img is not None:
            ctk.CTkLabel(
                support_line,
                text="",
                image=self.footer_whatsapp_img,
                fg_color="transparent"
            ).pack(side="left", padx=(6, 0))

    def tela_nova_compra(self):
        self.clear_main()

        self.main_container = ctk.CTkFrame(self, fg_color="#F4F4F1")
        self.main_container.pack(fill="both", expand=True)

        topo = ctk.CTkFrame(self.main_container, height=100, fg_color="#053B16")
        topo.pack(fill="x")
        topo.pack_propagate(False)

        voltar = ctk.CTkButton(
            topo,
            text="← Voltar",
            width=120,
            height=40,
            fg_color="#0E5A25",
            hover_color="#147032",
            command=self.build_ui
        )
        voltar.pack(side="left", padx=20, pady=30)

        titulo = ctk.CTkLabel(
            topo,
            text="Nova Compra",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        titulo.pack(side="left", padx=10)

        body = ctk.CTkFrame(self.main_container, fg_color="#F4F4F1")
        body.pack(fill="both", expand=True, padx=20, pady=20)

        cliente_frame = ctk.CTkFrame(body, fg_color="white", corner_radius=15)
        cliente_frame.pack(fill="x", pady=10)

        titulo_cliente = ctk.CTkLabel(
            cliente_frame,
            text="Dados do Cliente",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        titulo_cliente.pack(anchor="w", padx=15, pady=(10, 5))

        cliente_select = ctk.CTkEntry(cliente_frame, placeholder_text="Selecionar cliente")
        cliente_select.pack(fill="x", padx=15, pady=5)

        cpf = ctk.CTkEntry(cliente_frame, placeholder_text="CPF / CNPJ")
        cpf.pack(fill="x", padx=15, pady=5)

        telefone = ctk.CTkEntry(cliente_frame, placeholder_text="Telefone")
        telefone.pack(fill="x", padx=15, pady=5)

        obs = ctk.CTkEntry(cliente_frame, placeholder_text="Observação")
        obs.pack(fill="x", padx=15, pady=(5, 10))

        itens_frame = ctk.CTkFrame(body, fg_color="white", corner_radius=15)
        itens_frame.pack(fill="x", pady=10)

        titulo_itens = ctk.CTkLabel(
            itens_frame,
            text="Itens da Compra",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        titulo_itens.pack(anchor="w", padx=15, pady=10)

        linha = ctk.CTkFrame(itens_frame, fg_color="transparent")
        linha.pack(fill="x", padx=10)

        for i in range(6):
            linha.grid_columnconfigure(i, weight=1)

        material = ctk.CTkEntry(linha, placeholder_text="Material")
        material.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        peso = ctk.CTkEntry(linha, placeholder_text="Peso Bruto")
        peso.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        desconto = ctk.CTkEntry(linha, placeholder_text="Desconto")
        desconto.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        liquido = ctk.CTkEntry(linha, placeholder_text="Peso Líquido")
        liquido.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        valor = ctk.CTkEntry(linha, placeholder_text="Valor por KG")
        valor.grid(row=0, column=4, padx=5, pady=5, sticky="ew")

        subtotal = ctk.CTkEntry(linha, placeholder_text="Subtotal")
        subtotal.grid(row=0, column=5, padx=5, pady=5, sticky="ew")

        add_btn = ctk.CTkButton(
            itens_frame,
            text="+ Adicionar Material",
            fg_color="#0E5A25",
            hover_color="#147032"
        )
        add_btn.pack(anchor="e", padx=10, pady=10)

        resumo_frame = ctk.CTkFrame(body, fg_color="white", corner_radius=15)
        resumo_frame.pack(fill="x", pady=10)

        resumo_label = ctk.CTkLabel(
            resumo_frame,
            text="Resumo da Operação",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        resumo_label.pack(anchor="w", padx=15, pady=10)

        resumo_grid = ctk.CTkFrame(resumo_frame, fg_color="transparent")
        resumo_grid.pack(fill="x", padx=10, pady=10)

        for i in range(4):
            resumo_grid.grid_columnconfigure(i, weight=1)

        campos = [
            ("Peso Bruto Total", "0,00 kg"),
            ("Desconto Total", "0,00 kg"),
            ("Peso Líquido", "0,00 kg"),
            ("Valor Total", "R$ 0,00"),
        ]

        for i, (campo, valor_texto) in enumerate(campos):
            box = ctk.CTkFrame(resumo_grid, fg_color="#F4F4F1", corner_radius=10)
            box.grid(row=0, column=i, padx=8, sticky="ew")

            label = ctk.CTkLabel(box, text=campo, font=ctk.CTkFont(size=14, weight="bold"))
            label.pack(padx=10, pady=(10, 5))

            valor_label = ctk.CTkLabel(box, text=valor_texto, font=ctk.CTkFont(size=18, weight="bold"))
            valor_label.pack(pady=(0, 10))

        acoes_frame = ctk.CTkFrame(body, fg_color="white", corner_radius=15)
        acoes_frame.pack(fill="x", pady=10)

        salvar = ctk.CTkButton(
            acoes_frame,
            text="Salvar Rascunho",
            fg_color="#B0B0B0",
            hover_color="#999999"
        )
        salvar.pack(side="left", padx=15, pady=15)

        finalizar = ctk.CTkButton(
            acoes_frame,
            text="Gerar Comprovante",
            fg_color="#0E5A25",
            hover_color="#147032",
            height=50,
            width=220
        )
        finalizar.pack(side="right", padx=15, pady=15)

    def abrir_tela_placeholder(self, titulo, descricao):
        self.clear_main()

        self.main_container = ctk.CTkFrame(self, fg_color="#F4F4F1", corner_radius=0)
        self.main_container.pack(fill="both", expand=True)

        topo = ctk.CTkFrame(self.main_container, height=100, fg_color="#053B16", corner_radius=0)
        topo.pack(fill="x")
        topo.pack_propagate(False)

        voltar = ctk.CTkButton(
            topo,
            text="← Voltar",
            width=120,
            height=42,
            corner_radius=12,
            fg_color="#0E5A25",
            hover_color="#147032",
            command=self.build_ui
        )
        voltar.pack(side="left", padx=20, pady=28)

        titulo_label = ctk.CTkLabel(
            topo,
            text=titulo,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        titulo_label.pack(side="left", padx=10)

        corpo = ctk.CTkFrame(self.main_container, fg_color="#F4F4F1")
        corpo.pack(fill="both", expand=True, padx=30, pady=30)

        card = ctk.CTkFrame(corpo, fg_color="white", corner_radius=20)
        card.pack(fill="both", expand=True)
        card.pack_propagate(False)

        texto = ctk.CTkLabel(
            card,
            text=descricao,
            font=ctk.CTkFont(size=20),
            text_color="#222222",
            justify="center"
        )
        texto.pack(expand=True)

    def tela_nova_venda(self):
        self.abrir_tela_placeholder(
            "Nova Venda",
            "Tela de Nova Venda\n\nAqui vamos montar o formulário completo de venda."
        )

    def tela_clientes(self):
        self.abrir_tela_placeholder(
            "Clientes",
            "Tela de Clientes\n\nAqui vamos listar, cadastrar e editar clientes."
        )

    def tela_materiais(self):
        self.abrir_tela_placeholder(
            "Materiais",
            "Tela de Materiais\n\nAqui vamos cadastrar e gerenciar os materiais."
        )

    def tela_historico(self):
        self.abrir_tela_placeholder(
            "Histórico",
            "Tela de Histórico\n\nAqui vamos visualizar compras, vendas e comprovantes."
        )

    def tela_relatorios(self):
        self.abrir_tela_placeholder(
            "Relatórios",
            "Tela de Relatórios\n\nAqui vamos gerar relatórios financeiros e operacionais."
        )

    def tela_estoque(self):
        self.abrir_tela_placeholder(
            "Estoque",
            "Tela de Estoque\n\nAqui vamos visualizar saldo e movimentações dos materiais."
        )

    def tela_nota_fiscal(self):
        self.abrir_tela_placeholder(
            "Nota Fiscal",
            "Tela de Nota Fiscal\n\nAqui vamos emitir e consultar notas/documentos."
        )

    def tela_nova_compra(self):
        self.tela_operacao("COMPRA")

    def tela_nova_venda(self):
        self.tela_operacao("VENDA")

    def tela_operacao(self, tipo):
        titulo = "Nova Compra" if tipo == "COMPRA" else "Nova Venda"
        corpo = self.create_top_bar(titulo)
        self.current_items = []

        clientes = self.get_clientes()
        materiais = self.get_materiais_mais_comprados(somente_ativos=True)

        cliente_panel = self.make_panel(corpo, "Dados do Cliente")
        cliente_grid = ctk.CTkFrame(cliente_panel, fg_color="transparent")
        cliente_grid.pack(fill="x", padx=15, pady=(0, 12))
        for i in range(4):
            cliente_grid.grid_columnconfigure(i, weight=1)

        cliente_var = ctk.StringVar(value=self.option_values(clientes)[0])
        cliente_select = ctk.CTkOptionMenu(cliente_grid, values=self.option_values(clientes), variable=cliente_var)
        cliente_select.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        documento = ctk.CTkEntry(cliente_grid, placeholder_text="CPF / CNPJ")
        documento.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        telefone = ctk.CTkEntry(cliente_grid, placeholder_text="Telefone")
        telefone.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        observacao = ctk.CTkEntry(cliente_grid, placeholder_text="Observação")
        observacao.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        def preencher_cliente(_nome=None):
            cliente = self.selected_row_by_name(clientes, cliente_var.get())
            documento.delete(0, "end")
            telefone.delete(0, "end")
            if cliente:
                documento.insert(0, cliente["cnpj"] or "")
                telefone.insert(0, cliente["telefone"] or "")

        cliente_select.configure(command=preencher_cliente)
        preencher_cliente()

        item_panel = self.make_panel(corpo, "Itens da Operação")
        item_grid = ctk.CTkFrame(item_panel, fg_color="transparent")
        item_grid.pack(fill="x", padx=15, pady=(0, 8))
        for i in range(5):
            item_grid.grid_columnconfigure(i, weight=1)

        material_var = ctk.StringVar(value=self.option_values(materiais)[0])
        material_select = ctk.CTkOptionMenu(item_grid, values=self.option_values(materiais), variable=material_var)
        material_select.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        peso = ctk.CTkEntry(item_grid, placeholder_text="Peso bruto")
        peso.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        desconto = ctk.CTkEntry(item_grid, placeholder_text="Desconto")
        desconto.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        preco = ctk.CTkEntry(item_grid, placeholder_text="Valor por kg")
        preco.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        itens_lista = ctk.CTkFrame(item_panel, fg_color="#F4F4F1", corner_radius=10)
        itens_lista.pack(fill="x", padx=15, pady=8)

        resumo_panel = self.make_panel(corpo, "Resumo da Operação")
        resumo_grid = ctk.CTkFrame(resumo_panel, fg_color="transparent")
        resumo_grid.pack(fill="x", padx=15, pady=(0, 12))
        resumo_labels = {}
        for i, label in enumerate(["Peso Bruto Total", "Desconto Total", "Peso Líquido", "Valor Total"]):
            resumo_grid.grid_columnconfigure(i, weight=1)
            box = ctk.CTkFrame(resumo_grid, fg_color="#F4F4F1", corner_radius=10)
            box.grid(row=0, column=i, padx=6, sticky="ew")
            ctk.CTkLabel(box, text=label, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 4))
            texto_inicial = "R$ 0,00" if label == "Valor Total" else "0,00 kg"
            resumo_labels[label] = ctk.CTkLabel(box, text=texto_inicial, font=ctk.CTkFont(size=18, weight="bold"))
            resumo_labels[label].pack(pady=(0, 10))

        def atualizar_preco(_nome=None):
            material = self.selected_row_by_name(materiais, material_var.get())
            preco.delete(0, "end")
            if material:
                valor = material["preco_compra"] if tipo == "COMPRA" else material["preco_venda"]
                preco.insert(0, f"{valor:.2f}".replace(".", ","))

        def remover_item(index):
            self.current_items.pop(index)
            atualizar_lista()

        def atualizar_lista():
            for widget in itens_lista.winfo_children():
                widget.destroy()
            if not self.current_items:
                ctk.CTkLabel(itens_lista, text="Nenhum item adicionado ainda.", text_color="#666666").pack(padx=12, pady=12)
            else:
                for idx, item in enumerate(self.current_items, start=1):
                    texto = (
                        f"{idx}. {item['material_nome']} | Bruto: {self.format_kg(item['peso_bruto'])} | "
                        f"Desc.: {self.format_kg(item['desconto'])} | Líquido: {self.format_kg(item['peso_liquido'])} | "
                        f"{self.format_money(item['preco_kg'])}/kg | Subtotal: {self.format_money(item['subtotal'])}"
                    )
                    linha = ctk.CTkFrame(itens_lista, fg_color="transparent")
                    linha.pack(fill="x", padx=10, pady=4)
                    ctk.CTkLabel(linha, text=texto, anchor="w").pack(side="left", fill="x", expand=True)
                    ctk.CTkButton(
                        linha,
                        text="Remover",
                        width=90,
                        fg_color="#B84545",
                        hover_color="#963636",
                        command=lambda pos=idx - 1: remover_item(pos)
                    ).pack(side="right")

            bruto_total = sum(item["peso_bruto"] for item in self.current_items)
            desconto_total = sum(item["desconto"] for item in self.current_items)
            liquido_total = sum(item["peso_liquido"] for item in self.current_items)
            valor_total = sum(item["subtotal"] for item in self.current_items)
            resumo_labels["Peso Bruto Total"].configure(text=self.format_kg(bruto_total))
            resumo_labels["Desconto Total"].configure(text=self.format_kg(desconto_total))
            resumo_labels["Peso Líquido"].configure(text=self.format_kg(liquido_total))
            resumo_labels["Valor Total"].configure(text=self.format_money(valor_total))

        def adicionar_item():
            material = self.selected_row_by_name(materiais, material_var.get())
            if not material:
                messagebox.showwarning("Material obrigatório", "Cadastre um material antes de adicionar itens.")
                return
            try:
                peso_bruto = self.parse_decimal(peso.get())
                desconto_valor = self.parse_decimal(desconto.get())
                preco_kg = self.parse_decimal(preco.get())
            except ValueError:
                messagebox.showerror("Valor inválido", "Confira peso, desconto e valor por kg.")
                return
            peso_liquido = peso_bruto - desconto_valor
            if peso_liquido <= 0 or preco_kg < 0:
                messagebox.showerror("Valor inválido", "O peso líquido precisa ser maior que zero.")
                return
            self.current_items.append({
                "material_id": material["id"],
                "material_nome": material["nome"],
                "peso_bruto": peso_bruto,
                "desconto": desconto_valor,
                "peso_liquido": peso_liquido,
                "preco_kg": preco_kg,
                "subtotal": peso_liquido * preco_kg,
            })
            peso.delete(0, "end")
            desconto.delete(0, "end")
            atualizar_preco()
            atualizar_lista()

        material_select.configure(command=atualizar_preco)
        atualizar_preco()
        ctk.CTkButton(
            item_grid,
            text="+ Adicionar Material",
            fg_color="#0E5A25",
            hover_color="#147032",
            command=adicionar_item
        ).grid(row=0, column=4, padx=5, pady=5, sticky="ew")
        atualizar_lista()

        botoes = self.make_panel(corpo)
        ctk.CTkButton(
            botoes,
            text="Salvar Rascunho",
            fg_color="#B0B0B0",
            hover_color="#999999",
            command=lambda: messagebox.showinfo("Rascunho", "Os dados permanecem na tela até você voltar ou finalizar.")
        ).pack(side="left", padx=15, pady=15)
        ctk.CTkButton(
            botoes,
            text="Gerar Comprovante",
            fg_color="#0E5A25",
            hover_color="#147032",
            height=50,
            width=220,
            command=lambda: self.finalizar_operacao(tipo, cliente_var.get(), observacao.get())
        ).pack(side="right", padx=15, pady=15)

    def finalizar_operacao(self, tipo, cliente_nome, observacao, gerar_comprovante=True, cliente_documento="", cliente_telefone="", destino_compra=""):
        cliente = self.cliente_por_nome_ou_criar(cliente_nome, tipo, cliente_telefone, cliente_documento)
        if not cliente:
            messagebox.showwarning("Cliente obrigatório", "Digite o nome do cliente.")
            return
        if not self.current_items:
            messagebox.showwarning("Itens obrigatórios", "Adicione pelo menos um material.")
            return

        total = sum(item["subtotal"] for item in self.current_items)
        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO transacoes (tipo, cliente_id, cliente_nome, data, total, observacao) VALUES (?, ?, ?, ?, ?, ?)",
                (tipo, cliente["id"], cliente["nome"], data, total, observacao)
            )
            transacao_id = cur.lastrowid
            for item in self.current_items:
                cur.execute("""
                    INSERT INTO transacao_itens
                    (transacao_id, material_id, material_nome, peso_bruto, desconto, peso_liquido, preco_kg, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    transacao_id,
                    item["material_id"],
                    item["material_nome"],
                    item["peso_bruto"],
                    item["desconto"],
                    item["peso_liquido"],
                    item["preco_kg"],
                    item["subtotal"],
                ))
            if gerar_comprovante:
                numero = f"{tipo[0]}-{transacao_id:06d}"
                conteudo = self.montar_comprovante(numero, tipo, cliente["nome"], data, self.current_items, total, observacao)
                cur.execute(
                    "INSERT INTO comprovantes (transacao_id, numero, tipo, cliente_nome, data, total, conteudo) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (transacao_id, numero, tipo, cliente["nome"], data, total, conteudo)
                )

        if gerar_comprovante:
            caminho = self.salvar_comprovante_txt(numero, conteudo)
        else:
            messagebox.showinfo("Operação salva", f"{tipo.title()} salva com sucesso.")
        self.current_items = []
        if gerar_comprovante:
            self.tela_comprovante(numero, conteudo, caminho)
        else:
            self.build_ui()

    def montar_comprovante(self, numero, tipo, cliente, data, itens, total, observacao):
        linhas = [
            "VR VINHESQUE RECICLAGEM",
            "SUSTENTABILIDADE QUE GERA VALOR",
            "",
            f"CONTROLE {numero}",
            f"DATA     {data[:16]}",
            "=" * 42,
            "DADOS DA OPERACAO",
            f"TIPO     {tipo.title()}",
            f"CLIENTE  {cliente}",
            "=" * 42,
            "PRODUTOS",
            "COD  DESCRICAO        QTD     PRECO   TOTAL",
            "-" * 42,
        ]
        for index, item in enumerate(itens, start=1):
            descricao = item["material_nome"][:15]
            quantidade = self.format_kg(item["peso_liquido"]).replace(" kg", "")
            linhas.append(
                f"{index:03d}  {descricao:<15} {quantidade:>7} {self.format_money(item['preco_kg']):>8} {self.format_money(item['subtotal']):>8}"
            )
        linhas.extend([
            "-" * 42,
            f"{'SUBTOTAL':<28}{self.format_money(total):>14}",
            f"{'DESCONTO':<28}{self.format_money(0):>14}",
            f"{'TOTAL':<28}{self.format_money(total):>14}",
            "",
            "Obrigado pela preferencia!",
        ])
        if observacao:
            linhas.extend(["", f"OBS: {observacao}"])
        return "\n".join(linhas)

    def salvar_comprovante_txt(self, numero, conteudo):
        return self.salvar_comprovante_visual(numero, conteudo)

    def comprovante_font(self, size=16, bold=False):
        candidates = [
            "consolab.ttf" if bold else "consola.ttf",
            "courbd.ttf" if bold else "cour.ttf",
            "arialbd.ttf" if bold else "arial.ttf",
        ]
        for candidate in candidates:
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                continue
        return ImageFont.load_default()

    def wrap_comprovante_line(self, text, max_chars=48):
        text = str(text)
        if len(text) <= max_chars:
            return [text]
        words = text.split()
        if not words:
            return [""]
        lines = []
        current = words[0]
        for word in words[1:]:
            if len(current) + len(word) + 1 <= max_chars:
                current += " " + word
            else:
                lines.append(current)
                current = word
        lines.append(current)
        return lines

    def wrap_comprovante_text_width(self, text, font, max_width, measure_draw):
        normalized = " ".join(str(text).strip().split())
        if not normalized:
            return [""]

        def split_long_word(word):
            chunks = []
            current = ""
            for char in word:
                candidate = f"{current}{char}"
                if current and measure_draw.textlength(candidate, font=font) > max_width:
                    chunks.append(current)
                    current = char
                else:
                    current = candidate
            if current:
                chunks.append(current)
            return chunks or [word]

        lines = []
        current = ""
        for word in normalized.split():
            candidate = word if not current else f"{current} {word}"
            if measure_draw.textlength(candidate, font=font) <= max_width:
                current = candidate
                continue

            if current:
                lines.append(current)
                current = ""

            if measure_draw.textlength(word, font=font) <= max_width:
                current = word
                continue

            word_chunks = split_long_word(word)
            lines.extend(word_chunks[:-1])
            current = word_chunks[-1]

        if current:
            lines.append(current)
        return lines

    def comprovante_logo_image(self, max_width, max_height):
        if not os.path.exists(self.comprovante_logo_path):
            return None

        with Image.open(self.comprovante_logo_path) as logo_source:
            logo = ImageOps.exif_transpose(logo_source).convert("RGBA")
            alpha_bbox = logo.getchannel("A").getbbox() if "A" in logo.getbands() else None
            if alpha_bbox:
                logo = logo.crop(alpha_bbox)
            else:
                fallback_bbox = ImageOps.invert(logo.convert("L")).getbbox()
                if fallback_bbox:
                    logo = logo.crop(fallback_bbox)
            logo.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            return logo

    def criar_imagem_comprovante(self, conteudo):
        width = 520
        padding = 34
        logo_space = 124
        line_height = 23
        top_margin = 24
        bottom_margin = 28
        font = self.comprovante_font(16)
        small_font = self.comprovante_font(14)
        bold_font = self.comprovante_font(16, bold=True)

        raw_lines = []
        for raw_line in conteudo.splitlines():
            if raw_line.strip() == "VR VINHESQUE RECICLAGEM":
                continue
            for wrapped in self.wrap_comprovante_line(raw_line, 48):
                raw_lines.append(wrapped)

        height = top_margin + logo_space + bottom_margin + max(1, len(raw_lines)) * line_height
        receipt = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(receipt)

        if os.path.exists(self.logo_path):
            logo = ImageOps.exif_transpose(Image.open(self.logo_path)).convert("RGBA")
            logo.thumbnail((280, 98), Image.Resampling.LANCZOS)
            logo_x = (width - logo.width) // 2
            receipt.paste(logo, (logo_x, top_margin), logo)

        y = top_margin + logo_space
        for line in raw_lines:
            stripped = line.strip()
            if not stripped:
                y += line_height // 2
                continue
            if set(stripped) <= {"=", "-"}:
                draw.line((padding, y + 9, width - padding, y + 9), fill="#202020", width=1)
                y += line_height
                continue

            is_heading = stripped in {"SUSTENTABILIDADE QUE GERA VALOR", "DADOS DA OPERACAO", "PRODUTOS", "Obrigado pela preferencia!"}
            is_total = stripped.startswith("TOTAL")
            active_font = bold_font if is_heading or is_total else font
            if is_heading:
                heading_font = small_font if stripped.startswith("SUSTENTABILIDADE") else active_font
                text_width = draw.textlength(stripped, font=heading_font)
                draw.text(((width - text_width) / 2, y), stripped, fill="#101010", font=heading_font)
            else:
                draw.text((padding, y), line, fill="#101010", font=active_font)
            y += line_height

        return receipt

    def salvar_comprovante_visual(self, numero, conteudo):
        pasta = os.path.join(self.script_dir, "comprovantes")
        os.makedirs(pasta, exist_ok=True)
        png_path = os.path.join(pasta, f"{numero}.png")
        imagem = self.criar_imagem_comprovante(conteudo)
        imagem.save(png_path)
        return png_path

    def imprimir_comprovante(self, numero, caminho=None):
        png_path = os.path.join(self.script_dir, "comprovantes", f"{numero}.png")
        caminho = png_path if os.path.exists(png_path) else caminho or png_path
        if not os.path.exists(caminho):
            messagebox.showwarning("Comprovante nao encontrado", "Salve o comprovante antes de imprimir.")
            return
        if not hasattr(os, "startfile"):
            messagebox.showwarning("Impressao indisponivel", "A impressao direta esta disponivel apenas no Windows.")
            return
        try:
            os.startfile(caminho, "print")
            messagebox.showinfo("Impressao enviada", "O comprovante foi enviado para a impressora padrao.")
        except Exception as exc:
            messagebox.showwarning(
                "Impressora nao configurada",
                "O comprovante ja esta salvo.\n\n"
                "Quando instalarem a impressora, abra este comprovante e clique em Imprimir novamente.\n\n"
                f"Detalhe: {exc}",
            )

    def conteudo_comprovante_atual(self, numero, fallback_conteudo=""):
        row = self.db_fetchone(
            """
            SELECT c.numero, c.tipo, c.cliente_nome, c.data, c.total, c.conteudo, c.transacao_id,
                   COALESCE(t.observacao, '') AS observacao
            FROM comprovantes c
            LEFT JOIN transacoes t ON t.id = c.transacao_id
            WHERE c.numero=?
            """,
            (numero,),
        )
        if not row:
            return fallback_conteudo

        itens = self.db_fetchall(
            """
            SELECT material_id, material_nome, desconto, peso_liquido, preco_kg, subtotal
            FROM transacao_itens
            WHERE transacao_id=?
            ORDER BY id
            """,
            (row["transacao_id"],),
        )
        if not itens:
            return row["conteudo"] or fallback_conteudo

        conteudo_atual = self.montar_comprovante(
            row["numero"],
            row["tipo"],
            row["cliente_nome"],
            row["data"],
            itens,
            row["total"],
            row["observacao"],
        )
        if conteudo_atual != row["conteudo"]:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("UPDATE comprovantes SET conteudo=? WHERE numero=?", (conteudo_atual, numero))
        return conteudo_atual

    def tela_comprovante(self, numero, conteudo, caminho=None):
        colors = self.modelo_colors()
        conteudo = self.conteudo_comprovante_atual(numero, conteudo)
        # Regera o cupom visual ao abrir para aplicar o layout atual
        # mesmo em comprovantes antigos salvos no historico.
        png_path = self.salvar_comprovante_visual(numero, conteudo)
        caminho = png_path
        proxima_operacao = "COMPRA" if str(numero).upper().startswith("C-") else "VENDA" if str(numero).upper().startswith("V-") else None
        texto_retorno = "Nova compra" if proxima_operacao == "COMPRA" else "Nova venda" if proxima_operacao == "VENDA" else "Voltar"
        page = self.modelo_page("Comprovante gerado", f"Confira o comprovante {numero} antes de imprimir")
        page.grid_rowconfigure(2, weight=1)

        actions = ctk.CTkFrame(page, fg_color="white", height=58, corner_radius=10, border_width=1, border_color=colors["line"])
        actions.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        actions.grid_propagate(False)
        ctk.CTkLabel(actions, text=f"{numero} pronto para uso", font=ctk.CTkFont(size=14, weight="bold"), text_color=colors["text"]).pack(side="left", padx=18)

        ctk.CTkButton(actions, text="Imprimir", width=130, height=38, corner_radius=7, fg_color=colors["green"], hover_color=colors["green_hover"], font=ctk.CTkFont(size=13, weight="bold"), command=lambda: self.imprimir_comprovante(numero, caminho)).pack(side="right", padx=(8, 16))
        ctk.CTkButton(actions, text=texto_retorno, width=150, height=38, corner_radius=7, fg_color="#4B5563", hover_color="#374151", font=ctk.CTkFont(size=13, weight="bold"), command=(lambda: self.tela_operacao(proxima_operacao)) if proxima_operacao else self.build_ui).pack(side="right", padx=8)

        preview = ctk.CTkScrollableFrame(page, corner_radius=10, border_width=1, border_color=colors["line"], fg_color="#ECEFF1")
        preview.grid(row=2, column=0, sticky="nsew")
        with Image.open(png_path) as imagem_source:
            imagem = imagem_source.copy()
        available_width = max(760, self.winfo_screenwidth() - 360)
        display_width = min(available_width, max(860, int(imagem.width * 1.9)))
        display_height = max(1, int(imagem.height * (display_width / imagem.width)))
        self.comprovante_preview_img = ctk.CTkImage(light_image=imagem, dark_image=imagem, size=(display_width, display_height))
        ctk.CTkLabel(preview, image=self.comprovante_preview_img, text="").pack(pady=18)

    def tela_clientes(self):
        corpo = self.create_top_bar("Clientes")
        form = self.make_panel(corpo, "Cadastro de Cliente")
        grid = ctk.CTkFrame(form, fg_color="transparent")
        grid.pack(fill="x", padx=15, pady=(0, 12))
        for i in range(5):
            grid.grid_columnconfigure(i, weight=1)

        selected_id = {"value": None}
        nome = ctk.CTkEntry(grid, placeholder_text="Nome")
        nome.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        telefone = ctk.CTkEntry(grid, placeholder_text="Telefone")
        telefone.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        cnpj = ctk.CTkEntry(grid, placeholder_text="CPF / CNPJ")
        cnpj.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        cidade = ctk.CTkEntry(grid, placeholder_text="Cidade")
        cidade.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        observacao = ctk.CTkEntry(grid, placeholder_text="Observação")
        observacao.grid(row=0, column=4, padx=5, pady=5, sticky="ew")

        tree = self.create_tree(corpo, ("id", "nome", "telefone", "cnpj", "cidade"), ("ID", "Nome", "Telefone", "CPF/CNPJ", "Cidade"), 12)

        def limpar():
            selected_id["value"] = None
            for entry in (nome, telefone, cnpj, cidade, observacao):
                entry.delete(0, "end")

        def carregar():
            for item in tree.get_children():
                tree.delete(item)
            for row in self.get_clientes():
                tree.insert("", "end", values=(row["id"], row["nome"], row["telefone"], row["cnpj"], row["cidade"]))

        def salvar():
            if not nome.get().strip():
                messagebox.showwarning("Nome obrigatório", "Informe o nome do cliente.")
                return
            try:
                with sqlite3.connect(self.db_path) as conn:
                    if selected_id["value"]:
                        conn.execute(
                            "UPDATE clientes SET nome=?, telefone=?, cnpj=?, cidade=?, observacao=? WHERE id=?",
                            (nome.get().strip(), telefone.get(), cnpj.get(), cidade.get(), observacao.get(), selected_id["value"])
                        )
                    else:
                        conn.execute(
                            "INSERT INTO clientes (nome, telefone, cnpj, cidade, observacao) VALUES (?, ?, ?, ?, ?)",
                            (nome.get().strip(), telefone.get(), cnpj.get(), cidade.get(), observacao.get())
                        )
            except sqlite3.IntegrityError:
                messagebox.showerror("Cliente duplicado", "Já existe um cliente com esse nome.")
                return
            limpar()
            carregar()

        def excluir():
            if not selected_id["value"]:
                messagebox.showwarning("Selecione", "Selecione um cliente na lista.")
                return
            if not messagebox.askyesno("Excluir cliente", "Deseja excluir este cliente?"):
                return
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM clientes WHERE id=?", (selected_id["value"],))
            except sqlite3.IntegrityError:
                messagebox.showerror("Não foi possível excluir", "Este cliente já possui operações registradas.")
            limpar()
            carregar()

        def selecionar(_event):
            selecionado = tree.focus()
            if not selecionado:
                return
            valores = tree.item(selecionado, "values")
            row = self.db_fetchone("SELECT * FROM clientes WHERE id=?", (valores[0],))
            if row:
                limpar()
                selected_id["value"] = row["id"]
                nome.insert(0, row["nome"])
                telefone.insert(0, row["telefone"] or "")
                cnpj.insert(0, row["cnpj"] or "")
                cidade.insert(0, row["cidade"] or "")
                observacao.insert(0, row["observacao"] or "")

        tree.bind("<<TreeviewSelect>>", selecionar)
        botoes = ctk.CTkFrame(form, fg_color="transparent")
        botoes.pack(fill="x", padx=15, pady=(0, 15))
        ctk.CTkButton(botoes, text="Salvar", fg_color="#0E5A25", hover_color="#147032", command=salvar).pack(side="left", padx=5)
        ctk.CTkButton(botoes, text="Limpar", fg_color="#777777", hover_color="#666666", command=limpar).pack(side="left", padx=5)
        ctk.CTkButton(botoes, text="Excluir", fg_color="#B84545", hover_color="#963636", command=excluir).pack(side="left", padx=5)
        carregar()

    def tela_materiais(self):
        corpo = self.create_top_bar("Materiais")
        form = self.make_panel(corpo, "Cadastro de Material")
        grid = ctk.CTkFrame(form, fg_color="transparent")
        grid.pack(fill="x", padx=15, pady=(0, 12))
        for i in range(3):
            grid.grid_columnconfigure(i, weight=1)

        selected_id = {"value": None}
        nome = ctk.CTkEntry(grid, placeholder_text="Material")
        nome.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        compra = ctk.CTkEntry(grid, placeholder_text="Preço de compra")
        compra.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        venda = ctk.CTkEntry(grid, placeholder_text="Preço de venda")
        venda.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        tree = self.create_tree(corpo, ("id", "nome", "compra", "venda"), ("ID", "Material", "Compra", "Venda"), 12)

        def limpar():
            selected_id["value"] = None
            for entry in (nome, compra, venda):
                entry.delete(0, "end")

        def carregar():
            for item in tree.get_children():
                tree.delete(item)
            for row in self.get_materiais():
                tree.insert("", "end", values=(row["id"], row["nome"], self.format_money(row["preco_compra"]), self.format_money(row["preco_venda"])))

        def salvar():
            if not nome.get().strip():
                messagebox.showwarning("Nome obrigatório", "Informe o nome do material.")
                return
            try:
                compra_valor = self.parse_decimal(compra.get())
                venda_valor = self.parse_decimal(venda.get())
                with sqlite3.connect(self.db_path) as conn:
                    if selected_id["value"]:
                        conn.execute(
                            "UPDATE materiais SET nome=?, preco_compra=?, preco_venda=? WHERE id=?",
                            (nome.get().strip(), compra_valor, venda_valor, selected_id["value"])
                        )
                    else:
                        conn.execute(
                            "INSERT INTO materiais (nome, preco_compra, preco_venda) VALUES (?, ?, ?)",
                            (nome.get().strip(), compra_valor, venda_valor)
                        )
            except ValueError:
                messagebox.showerror("Preço inválido", "Confira os preços informados.")
                return
            except sqlite3.IntegrityError:
                messagebox.showerror("Material duplicado", "Já existe um material com esse nome.")
                return
            limpar()
            carregar()

        def excluir():
            if not selected_id["value"]:
                messagebox.showwarning("Selecione", "Selecione um material na lista.")
                return
            if not messagebox.askyesno("Excluir material", "Deseja excluir este material?"):
                return
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM materiais WHERE id=?", (selected_id["value"],))
            except sqlite3.IntegrityError:
                messagebox.showerror("Não foi possível excluir", "Este material já possui operações registradas.")
            limpar()
            carregar()

        def selecionar(_event):
            selecionado = tree.focus()
            if not selecionado:
                return
            valores = tree.item(selecionado, "values")
            row = self.db_fetchone("SELECT * FROM materiais WHERE id=?", (valores[0],))
            if row:
                limpar()
                selected_id["value"] = row["id"]
                nome.insert(0, row["nome"])
                compra.insert(0, f"{row['preco_compra']:.2f}".replace(".", ","))
                venda.insert(0, f"{row['preco_venda']:.2f}".replace(".", ","))

        tree.bind("<<TreeviewSelect>>", selecionar)
        botoes = ctk.CTkFrame(form, fg_color="transparent")
        botoes.pack(fill="x", padx=15, pady=(0, 15))
        ctk.CTkButton(botoes, text="Salvar", fg_color="#0E5A25", hover_color="#147032", command=salvar).pack(side="left", padx=5)
        ctk.CTkButton(botoes, text="Limpar", fg_color="#777777", hover_color="#666666", command=limpar).pack(side="left", padx=5)
        ctk.CTkButton(botoes, text="Excluir", fg_color="#B84545", hover_color="#963636", command=excluir).pack(side="left", padx=5)
        carregar()

    def tela_historico(self):
        corpo = self.create_top_bar("Histórico")
        panel = self.make_panel(corpo, "Operações Realizadas")
        tree = self.create_tree(panel, ("id", "tipo", "cliente", "data", "total"), ("ID", "Tipo", "Cliente", "Data", "Total"), 14)
        for row in self.db_fetchall("SELECT * FROM transacoes ORDER BY data DESC, id DESC"):
            tree.insert("", "end", values=(row["id"], row["tipo"], row["cliente_nome"], row["data"], self.format_money(row["total"])))

        def ver_itens():
            selecionado = tree.focus()
            if not selecionado:
                messagebox.showwarning("Selecione", "Selecione uma operação.")
                return
            transacao_id = tree.item(selecionado, "values")[0]
            itens = self.db_fetchall("SELECT * FROM transacao_itens WHERE transacao_id=?", (transacao_id,))
            texto = "\n".join(
                f"{item['material_nome']} - {self.format_kg(item['peso_liquido'])} - {self.format_money(item['subtotal'])}"
                for item in itens
            ) or "Sem itens."
            messagebox.showinfo("Itens da operação", texto)

        ctk.CTkButton(panel, text="Ver Itens", fg_color="#0E5A25", hover_color="#147032", command=ver_itens).pack(anchor="e", padx=15, pady=(0, 15))

    def tela_relatorios(self):
        corpo = self.create_top_bar("Relatórios")
        total_compras = self.db_fetchone("SELECT COALESCE(SUM(total), 0) AS total FROM transacoes WHERE tipo='COMPRA'")["total"]
        total_vendas = self.db_fetchone("SELECT COALESCE(SUM(total), 0) AS total FROM transacoes WHERE tipo='VENDA'")["total"]
        peso_compras = self.db_fetchone("""
            SELECT COALESCE(SUM(i.peso_liquido), 0) AS total
            FROM transacao_itens i JOIN transacoes t ON t.id=i.transacao_id
            WHERE t.tipo='COMPRA'
        """)["total"]
        peso_vendas = self.db_fetchone("""
            SELECT COALESCE(SUM(i.peso_liquido), 0) AS total
            FROM transacao_itens i JOIN transacoes t ON t.id=i.transacao_id
            WHERE t.tipo='VENDA'
        """)["total"]

        panel = self.make_panel(corpo, "Resumo Geral")
        grid = ctk.CTkFrame(panel, fg_color="transparent")
        grid.pack(fill="x", padx=15, pady=15)
        dados = [
            ("Compras", self.format_money(total_compras)),
            ("Vendas", self.format_money(total_vendas)),
            ("Peso Comprado", self.format_kg(peso_compras)),
            ("Peso Vendido", self.format_kg(peso_vendas)),
            ("Resultado", self.format_money(total_vendas - total_compras)),
        ]
        for i, (titulo, valor) in enumerate(dados):
            grid.grid_columnconfigure(i, weight=1)
            box = ctk.CTkFrame(grid, fg_color="#F4F4F1", corner_radius=10)
            box.grid(row=0, column=i, padx=6, sticky="ew")
            ctk.CTkLabel(box, text=titulo, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 4))
            ctk.CTkLabel(box, text=valor, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 10))

    def tela_estoque(self):
        corpo = self.create_top_bar("Estoque")
        panel = self.make_panel(corpo, "Saldo por Material")
        tree = self.create_tree(panel, ("material", "compras", "vendas", "saldo"), ("Material", "Entradas", "Saídas", "Saldo"), 14)
        rows = self.db_fetchall("""
            SELECT
                m.nome AS material,
                COALESCE(SUM(CASE WHEN t.tipo='COMPRA' THEN i.peso_liquido ELSE 0 END), 0) AS compras,
                COALESCE(SUM(CASE WHEN t.tipo='VENDA' THEN i.peso_liquido ELSE 0 END), 0) AS vendas
            FROM materiais m
            LEFT JOIN transacao_itens i ON i.material_id = m.id
            LEFT JOIN transacoes t ON t.id = i.transacao_id
            GROUP BY m.id, m.nome
            ORDER BY m.nome
        """)
        for row in rows:
            saldo = row["compras"] - row["vendas"]
            tree.insert("", "end", values=(row["material"], self.format_kg(row["compras"]), self.format_kg(row["vendas"]), self.format_kg(saldo)))

    def tela_nota_fiscal(self):
        corpo = self.create_top_bar("Nota Fiscal")
        panel = self.make_panel(corpo, "Comprovantes Emitidos")
        tree = self.create_tree(panel, ("numero", "tipo", "cliente", "data", "total"), ("Número", "Tipo", "Cliente", "Data", "Total"), 14)
        for row in self.db_fetchall("SELECT * FROM comprovantes ORDER BY data DESC, id DESC"):
            tree.insert("", "end", values=(row["numero"], row["tipo"], row["cliente_nome"], row["data"], self.format_money(row["total"])))

        def abrir():
            selecionado = tree.focus()
            if not selecionado:
                messagebox.showwarning("Selecione", "Selecione um comprovante.")
                return
            numero = tree.item(selecionado, "values")[0]
            row = self.db_fetchone("SELECT conteudo FROM comprovantes WHERE numero=?", (numero,))
            if row:
                messagebox.showinfo(f"Comprovante {numero}", row["conteudo"])

        ctk.CTkButton(panel, text="Abrir Comprovante", fg_color="#0E5A25", hover_color="#147032", command=abrir).pack(anchor="e", padx=15, pady=(0, 15))

    def create_top_bar(self, title, subtitle=""):
        self.clear_main()
        self.main_container = ctk.CTkFrame(self, fg_color="#F7F8F6", corner_radius=0)
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.build_header()

        page = ctk.CTkFrame(self.main_container, fg_color="#F7F8F6", corner_radius=0)
        page.grid(row=1, column=0, sticky="nsew", padx=32, pady=(14, 8))

        title_row = ctk.CTkFrame(page, fg_color="transparent")
        title_row.pack(fill="x", pady=(0, 18))

        ctk.CTkButton(
            title_row,
            text="←  Voltar",
            width=132,
            height=56,
            corner_radius=8,
            fg_color="#EEF0EF",
            hover_color="#E1E5E2",
            text_color="#18221D",
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.build_ui
        ).pack(side="left", padx=(0, 28))

        title_box = ctk.CTkFrame(title_row, fg_color="transparent")
        title_box.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            title_box,
            text=title,
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="#171C21"
        ).pack(anchor="w")
        if subtitle:
            ctk.CTkLabel(
                title_box,
                text=subtitle,
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color="#66707A"
            ).pack(anchor="w", pady=(6, 0))

        content = ctk.CTkFrame(page, fg_color="transparent")
        content.pack(fill="both", expand=True)
        self.build_footer()
        return content

    def operation_table_row(self, parent, values, delete_command=None, header=False):
        bg = "#F8F9FA" if header else "white"
        row = ctk.CTkFrame(parent, fg_color=bg, corner_radius=0)
        row.pack(fill="x")
        widths = [160, 190, 150, 150, 160, 150, 170, 110]
        for index, text in enumerate(values):
            color = "#111827"
            weight = "bold" if header or index in (0, 6) else "normal"
            if not header and index == 6:
                color = "#10812C"
            label = ctk.CTkLabel(
                row,
                text=text,
                width=widths[index],
                anchor="w" if index < 2 else "center",
                font=ctk.CTkFont(size=13, weight=weight),
                text_color=color
            )
            label.pack(side="left", padx=0, pady=10)

        if not header:
            actions = ctk.CTkFrame(row, fg_color="transparent", width=100)
            actions.pack(side="left", pady=6)
            ctk.CTkButton(
                actions,
                text="✎",
                width=38,
                height=34,
                corner_radius=6,
                fg_color="#F1F4F2",
                hover_color="#E4E9E6",
                text_color="#374151"
            ).pack(side="left", padx=4)
            ctk.CTkButton(
                actions,
                text="🗑",
                width=38,
                height=34,
                corner_radius=6,
                fg_color="#FFF0F0",
                hover_color="#FFE0E0",
                text_color="#E33434",
                command=delete_command
            ).pack(side="left", padx=4)

    def tela_operacao(self, tipo):
        titulo = "Nova Compra" if tipo == "COMPRA" else "Nova Venda"
        subtitulo = "Registre a entrada de materiais no estoque" if tipo == "COMPRA" else "Registre a saída de materiais do estoque"
        corpo = self.create_top_bar(titulo, subtitulo)
        self.current_items = []

        clientes = self.get_clientes()
        materiais = self.get_materiais_mais_comprados(somente_ativos=True)

        cliente_panel = self.make_panel(corpo, "  👤  Dados do Cliente")
        tipo_cliente = ctk.CTkFrame(cliente_panel, fg_color="transparent")
        tipo_cliente.pack(fill="x", padx=22, pady=(0, 10))
        ctk.CTkRadioButton(tipo_cliente, text="Cliente cadastrado", value=1).pack(side="left", padx=(0, 28))
        ctk.CTkRadioButton(tipo_cliente, text="Cliente anônimo", value=2).pack(side="left")

        cliente_grid = ctk.CTkFrame(cliente_panel, fg_color="transparent")
        cliente_grid.pack(fill="x", padx=22, pady=(0, 18))
        for i in range(5):
            cliente_grid.grid_columnconfigure(i, weight=1)

        cliente_var = ctk.StringVar(value=self.option_values(clientes)[0])
        cliente_select = ctk.CTkOptionMenu(cliente_grid, values=self.option_values(clientes), variable=cliente_var, height=48, fg_color="white", button_color="white", button_hover_color="#EEF0EF", text_color="#4B5563")
        cliente_select.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(cliente_grid, text="+  Novo", height=48, fg_color="#E5F5DF", hover_color="#D9EFD1", text_color="#15772C", command=self.tela_clientes).grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        documento = ctk.CTkEntry(cliente_grid, height=48, placeholder_text="00.000.000/0000-00")
        documento.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        telefone = ctk.CTkEntry(cliente_grid, height=48, placeholder_text="(19) 99999-9999")
        telefone.grid(row=0, column=4, padx=5, pady=5, sticky="ew")
        observacao = ctk.CTkEntry(cliente_grid, height=48, placeholder_text="Digite uma observação...")
        observacao.grid(row=1, column=0, columnspan=5, padx=5, pady=5, sticky="ew")

        def preencher_cliente(_nome=None):
            cliente = self.selected_row_by_name(clientes, cliente_var.get())
            documento.delete(0, "end")
            telefone.delete(0, "end")
            if cliente:
                documento.insert(0, cliente["cnpj"] or "")
                telefone.insert(0, cliente["telefone"] or "")

        cliente_select.configure(command=preencher_cliente)
        preencher_cliente()

        item_panel = self.make_panel(corpo, "  ▦  Itens da Compra" if tipo == "COMPRA" else "  ▦  Itens da Venda")
        item_sub = ctk.CTkLabel(item_panel, text="Adicione os materiais adquiridos" if tipo == "COMPRA" else "Adicione os materiais vendidos", text_color="#6B7280", font=ctk.CTkFont(size=13, weight="bold"))
        item_sub.pack(anchor="w", padx=22, pady=(0, 10))

        add_grid = ctk.CTkFrame(item_panel, fg_color="transparent")
        add_grid.pack(fill="x", padx=18, pady=(0, 8))
        for i in range(5):
            add_grid.grid_columnconfigure(i, weight=1)

        material_var = ctk.StringVar(value=self.option_values(materiais)[0])
        material_select = ctk.CTkOptionMenu(add_grid, values=self.option_values(materiais), variable=material_var, height=44, fg_color="white", button_color="white", button_hover_color="#EEF0EF", text_color="#111827")
        material_select.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        peso = ctk.CTkEntry(add_grid, height=44, placeholder_text="Peso bruto")
        peso.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        desconto = ctk.CTkEntry(add_grid, height=44, placeholder_text="Desconto")
        desconto.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        preco = ctk.CTkEntry(add_grid, height=44, placeholder_text="Valor por kg")
        preco.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        table = ctk.CTkFrame(item_panel, fg_color="white", corner_radius=8, border_width=1, border_color="#E5E7EB")
        table.pack(fill="x", padx=18, pady=(8, 18))
        self.operation_table_row(table, ["Material", "Descrição", "Peso Bruto (kg)", "Desconto (kg)", "Peso Líquido (kg)", "Valor por kg (R$)", "Subtotal (R$)", "Ações"], header=True)

        resumo_refs = {}

        def atualizar_preco(_nome=None):
            material = self.selected_row_by_name(materiais, material_var.get())
            preco.delete(0, "end")
            if material:
                valor = material["preco_compra"] if tipo == "COMPRA" else material["preco_venda"]
                preco.insert(0, f"{valor:.2f}".replace(".", ","))

        def remover_item(index):
            self.current_items.pop(index)
            atualizar_tabela()

        def atualizar_tabela():
            for widget in list(table.winfo_children())[1:]:
                widget.destroy()
            if not self.current_items:
                ctk.CTkLabel(table, text="⊕  Clique em “Adicionar Material” para incluir mais itens", height=46, text_color="#6B7280", font=ctk.CTkFont(size=14, weight="bold")).pack(fill="x")
            else:
                for idx, item in enumerate(self.current_items):
                    self.operation_table_row(
                        table,
                        [
                            item["material_nome"],
                            f"{item['material_nome']} limpo",
                            f"{item['peso_bruto']:.2f}".replace(".", ","),
                            f"{item['desconto']:.2f}".replace(".", ","),
                            f"{item['peso_liquido']:.2f}".replace(".", ","),
                            self.format_money(item["preco_kg"]),
                            self.format_money(item["subtotal"]),
                            "",
                        ],
                        delete_command=lambda pos=idx: remover_item(pos)
                    )

            bruto_total = sum(item["peso_bruto"] for item in self.current_items)
            desconto_total = sum(item["desconto"] for item in self.current_items)
            liquido_total = sum(item["peso_liquido"] for item in self.current_items)
            valor_total = sum(item["subtotal"] for item in self.current_items)
            if resumo_refs:
                resumo_refs["bruto"].configure(text=self.format_kg(bruto_total))
                resumo_refs["desconto"].configure(text=self.format_kg(desconto_total))
                resumo_refs["liquido"].configure(text=self.format_kg(liquido_total))
                resumo_refs["total"].configure(text=self.format_money(valor_total))

        def adicionar_item():
            material = self.selected_row_by_name(materiais, material_var.get())
            if not material:
                messagebox.showwarning("Material obrigatório", "Cadastre um material antes de adicionar itens.")
                return
            try:
                peso_bruto = self.parse_decimal(peso.get())
                desconto_valor = self.parse_decimal(desconto.get())
                preco_kg = self.parse_decimal(preco.get())
            except ValueError:
                messagebox.showerror("Valor inválido", "Confira peso, desconto e valor por kg.")
                return
            peso_liquido = peso_bruto - desconto_valor
            if peso_liquido <= 0:
                messagebox.showerror("Valor inválido", "O peso líquido precisa ser maior que zero.")
                return
            self.current_items.append({
                "material_id": material["id"],
                "material_nome": material["nome"],
                "peso_bruto": peso_bruto,
                "desconto": desconto_valor,
                "peso_liquido": peso_liquido,
                "preco_kg": preco_kg,
                "subtotal": peso_liquido * preco_kg,
            })
            peso.delete(0, "end")
            desconto.delete(0, "end")
            atualizar_preco()
            atualizar_tabela()

        ctk.CTkButton(add_grid, text="+  Adicionar Material", height=44, fg_color="#08721D", hover_color="#075E19", command=adicionar_item).grid(row=0, column=4, padx=5, pady=5, sticky="ew")
        material_select.configure(command=atualizar_preco)
        atualizar_preco()

        bottom = ctk.CTkFrame(corpo, fg_color="transparent")
        bottom.pack(fill="x", pady=(0, 12))
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=1)

        resumo = ctk.CTkFrame(bottom, fg_color="white", corner_radius=14, border_width=1, border_color="#E5E7EB")
        resumo.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        ctk.CTkLabel(resumo, text="⌁  Resumo da Operação", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1F2937").pack(anchor="w", padx=18, pady=(14, 10))
        resumo_grid = ctk.CTkFrame(resumo, fg_color="transparent")
        resumo_grid.pack(fill="x", padx=16, pady=(0, 16))
        summary_data = [("Peso Bruto Total", "bruto"), ("Desconto (kg)", "desconto"), ("Peso Líquido Total", "liquido"), ("Valor Total", "total")]
        for i, (label, key) in enumerate(summary_data):
            resumo_grid.grid_columnconfigure(i, weight=1)
            box_color = "#E9F7E3" if key in ("liquido", "total") else "#FBFCFD"
            box = ctk.CTkFrame(resumo_grid, fg_color=box_color, corner_radius=8)
            box.grid(row=0, column=i, padx=6, sticky="ew")
            ctk.CTkLabel(box, text=label, font=ctk.CTkFont(size=13, weight="bold"), text_color="#374151").pack(pady=(12, 6))
            resumo_refs[key] = ctk.CTkLabel(box, text="R$ 0,00" if key == "total" else "0,00 kg", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1F2937")
            resumo_refs[key].pack(pady=(0, 12))

        acoes = ctk.CTkFrame(bottom, fg_color="white", corner_radius=14, border_width=1, border_color="#E5E7EB")
        acoes.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        ctk.CTkLabel(acoes, text="⚡  Ações", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1F2937").pack(anchor="w", padx=18, pady=(14, 10))
        action_row = ctk.CTkFrame(acoes, fg_color="transparent")
        action_row.pack(fill="x", padx=18, pady=(0, 8))
        ctk.CTkButton(action_row, text="▣  Salvar Venda" if tipo == "VENDA" else "▣  Salvar Compra", height=58, fg_color="#EEF0EF", hover_color="#E2E6E3", text_color="#1F2937", font=ctk.CTkFont(size=15, weight="bold"), command=lambda: messagebox.showinfo("Rascunho", "Os dados permanecem na tela até você finalizar.")).pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(action_row, text="▤  Gerar Comprovante\ne finalizar compra" if tipo == "COMPRA" else "▤  Gerar Comprovante\ne finalizar venda", height=58, fg_color="#08721D", hover_color="#075E19", font=ctk.CTkFont(size=15, weight="bold"), command=lambda: self.finalizar_operacao(tipo, cliente_var.get(), observacao.get())).pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(acoes, text="A operação será registrada no sistema e o estoque será atualizado.", text_color="#6B7280", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=18, pady=(0, 14))

        atualizar_tabela()


    def tela_operacao(self, tipo):
        titulo = "Nova Compra" if tipo == "COMPRA" else "Nova Venda"
        subtitulo = "Entrada de materiais no estoque" if tipo == "COMPRA" else "Saida de materiais para cliente"
        self.current_items = []

        clientes = self.get_clientes()
        materiais = self.get_materiais_mais_comprados(somente_ativos=True)

        self.clear_main()
        self.main_container = ctk.CTkFrame(self, fg_color="#F7F8F6", corner_radius=0)
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.build_header()
        self.build_footer()

        page = ctk.CTkFrame(self.main_container, fg_color="#F7F8F6", corner_radius=0)
        page.grid(row=1, column=0, sticky="nsew", padx=20, pady=(6, 4))
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)

        heading = ctk.CTkFrame(page, fg_color="transparent", height=42)
        heading.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        heading.grid_propagate(False)
        ctk.CTkButton(
            heading,
            text="<  Voltar",
            width=100,
            height=34,
            corner_radius=8,
            fg_color="#EEF0EF",
            hover_color="#E1E5E2",
            text_color="#18221D",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.build_ui
        ).pack(side="left", padx=(0, 14), pady=4)

        title_box = ctk.CTkFrame(heading, fg_color="transparent")
        title_box.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(title_box, text=titulo, font=ctk.CTkFont(size=22, weight="bold"), text_color="#171C21").pack(anchor="w")
        ctk.CTkLabel(title_box, text=subtitulo, font=ctk.CTkFont(size=11, weight="bold"), text_color="#66707A").pack(anchor="w")

        workspace = ctk.CTkFrame(page, fg_color="transparent")
        workspace.grid(row=1, column=0, sticky="nsew")
        workspace.grid_columnconfigure(0, weight=1)
        workspace.grid_columnconfigure(1, weight=0)
        workspace.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(workspace, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(1, weight=1)

        summary = ctk.CTkFrame(workspace, width=300, fg_color="white", corner_radius=14, border_width=1, border_color="#E5E7EB")
        summary.grid(row=0, column=1, sticky="nsew")
        summary.grid_propagate(False)

        cliente_panel = ctk.CTkFrame(left, fg_color="white", corner_radius=14, border_width=1, border_color="#E5E7EB")
        cliente_panel.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        cliente_panel.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(cliente_panel, text="Cliente da operacao", font=ctk.CTkFont(size=14, weight="bold"), text_color="#1F2937").grid(row=0, column=0, sticky="w", padx=12, pady=(8, 0))

        cliente_grid = ctk.CTkFrame(cliente_panel, fg_color="transparent")
        cliente_grid.grid(row=1, column=0, sticky="ew", padx=9, pady=(0, 8))
        for i in range(5):
            cliente_grid.grid_columnconfigure(i, weight=1)

        cliente_var = ctk.StringVar(value=self.option_values(clientes)[0])
        cliente_select = ctk.CTkEntry(cliente_grid, textvariable=cliente_var, height=32, placeholder_text="Digite o cliente")
        cliente_select.grid(row=0, column=0, columnspan=2, padx=4, pady=3, sticky="ew")
        ctk.CTkButton(cliente_grid, text="+ Novo", height=32, fg_color="#E5F5DF", hover_color="#D9EFD1", text_color="#15772C", command=self.tela_clientes).grid(row=0, column=2, padx=4, pady=3, sticky="ew")
        documento = ctk.CTkEntry(cliente_grid, height=32, placeholder_text="CPF / CNPJ")
        documento.grid(row=0, column=3, padx=4, pady=3, sticky="ew")
        telefone = ctk.CTkEntry(cliente_grid, height=32, placeholder_text="Telefone")
        telefone.grid(row=0, column=4, padx=4, pady=3, sticky="ew")
        cliente_suggestions = ctk.CTkFrame(cliente_grid, fg_color="transparent")
        cliente_suggestions.grid(row=1, column=0, columnspan=5, sticky="ew", padx=4, pady=(0, 2))
        observacao = ctk.CTkEntry(cliente_grid, height=32, placeholder_text="Observacao")
        observacao.grid(row=2, column=0, columnspan=5, padx=4, pady=3, sticky="ew")

        def preencher_cliente(_nome=None):
            cliente = self.selected_row_by_name(clientes, cliente_var.get())
            documento.delete(0, "end")
            telefone.delete(0, "end")
            if cliente:
                documento.insert(0, cliente["cnpj"] or "")
                telefone.insert(0, cliente["telefone"] or "")

        def escolher_cliente(row):
            cliente_var.set(row["nome"])
            preencher_cliente()
            for widget in cliente_suggestions.winfo_children():
                widget.destroy()

        def atualizar_sugestoes_cliente(*_args):
            preencher_cliente()
            self.render_suggestions(cliente_suggestions, clientes, cliente_var.get(), escolher_cliente)

        cliente_var.trace_add("write", atualizar_sugestoes_cliente)
        cliente_select.bind("<FocusIn>", lambda _event: atualizar_sugestoes_cliente())
        cliente_select.bind("<KeyRelease>", lambda _event: atualizar_sugestoes_cliente())
        preencher_cliente()

        item_panel = ctk.CTkFrame(left, fg_color="white", corner_radius=14, border_width=1, border_color="#E5E7EB")
        item_panel.grid(row=1, column=0, sticky="nsew")
        item_panel.grid_columnconfigure(0, weight=1)
        item_panel.grid_rowconfigure(3, weight=1)
        ctk.CTkLabel(item_panel, text="Itens da operacao", font=ctk.CTkFont(size=14, weight="bold"), text_color="#1F2937").grid(row=0, column=0, sticky="w", padx=12, pady=(8, 0))

        add_grid = ctk.CTkFrame(item_panel, fg_color="#F8FAF8", corner_radius=10)
        add_grid.grid(row=1, column=0, sticky="ew", padx=9, pady=(2, 6))
        for i in range(6):
            add_grid.grid_columnconfigure(i, weight=1)

        material_var = ctk.StringVar(value=self.option_values(materiais)[0])
        material_select = ctk.CTkEntry(add_grid, textvariable=material_var, height=32, placeholder_text="Digite o material")
        material_select.grid(row=0, column=0, columnspan=2, padx=4, pady=7, sticky="ew")
        peso = ctk.CTkEntry(add_grid, height=32, placeholder_text="Peso bruto")
        peso.grid(row=0, column=2, padx=4, pady=7, sticky="ew")
        desconto = ctk.CTkEntry(add_grid, height=32, placeholder_text="Desconto")
        desconto.grid(row=0, column=3, padx=4, pady=7, sticky="ew")
        preco = ctk.CTkEntry(add_grid, height=32, placeholder_text="Valor kg")
        preco.grid(row=0, column=4, padx=4, pady=7, sticky="ew")
        material_suggestions = ctk.CTkFrame(add_grid, fg_color="transparent")
        material_suggestions.grid(row=1, column=0, columnspan=6, sticky="ew", padx=4, pady=(0, 5))

        preview = ctk.CTkFrame(item_panel, fg_color="#F1F6F1", corner_radius=10)
        preview.grid(row=2, column=0, sticky="ew", padx=9, pady=(0, 6))
        preview.grid_columnconfigure(0, weight=1)
        preview.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(preview, text="Peso liquido do item", font=ctk.CTkFont(size=11, weight="bold"), text_color="#66707A").grid(row=0, column=0, sticky="w", padx=12, pady=(6, 0))
        ctk.CTkLabel(preview, text="Subtotal do item", font=ctk.CTkFont(size=11, weight="bold"), text_color="#66707A").grid(row=0, column=1, sticky="w", padx=12, pady=(6, 0))
        preview_liquido = ctk.CTkLabel(preview, text="0,00 kg", font=ctk.CTkFont(size=14, weight="bold"), text_color="#1F2937")
        preview_liquido.grid(row=1, column=0, sticky="w", padx=12, pady=(0, 6))
        preview_subtotal = ctk.CTkLabel(preview, text="R$ 0,00", font=ctk.CTkFont(size=14, weight="bold"), text_color="#0E5A25")
        preview_subtotal.grid(row=1, column=1, sticky="w", padx=12, pady=(0, 6))

        lista = ctk.CTkScrollableFrame(item_panel, fg_color="white", corner_radius=10)
        lista.grid(row=3, column=0, sticky="nsew", padx=9, pady=(0, 8))

        resumo_refs = {}

        def atualizar_previa(_event=None):
            try:
                peso_bruto = self.parse_decimal(peso.get())
                desconto_valor = self.parse_decimal(desconto.get())
                preco_kg = self.parse_decimal(preco.get())
                peso_liquido = max(0, peso_bruto - desconto_valor)
                subtotal_item = peso_liquido * preco_kg
            except ValueError:
                peso_liquido = 0
                subtotal_item = 0
            preview_liquido.configure(text=self.format_kg(peso_liquido))
            preview_subtotal.configure(text=self.format_money(subtotal_item))

        def atualizar_preco(_nome=None):
            material = self.selected_row_by_name(materiais, material_var.get())
            preco.delete(0, "end")
            if material:
                valor = material["preco_compra"] if tipo == "COMPRA" else material["preco_venda"]
                preco.insert(0, f"{valor:.2f}".replace(".", ","))
            atualizar_previa()

        def remover_item(index):
            self.current_items.pop(index)
            atualizar_tabela()

        def atualizar_tabela():
            for widget in lista.winfo_children():
                widget.destroy()

            if not self.current_items:
                empty = ctk.CTkFrame(lista, fg_color="#F8FAF8", corner_radius=10)
                empty.pack(fill="x", padx=2, pady=2)
                ctk.CTkLabel(empty, text="Nenhum material adicionado ainda.", height=72, text_color="#6B7280", font=ctk.CTkFont(size=14, weight="bold")).pack(expand=True)
            else:
                for idx, item in enumerate(self.current_items):
                    row = ctk.CTkFrame(lista, fg_color="#F8FAF8", corner_radius=10)
                    row.pack(fill="x", padx=2, pady=4)
                    row.grid_columnconfigure(0, weight=1)
                    ctk.CTkLabel(row, text=item["material_nome"], font=ctk.CTkFont(size=14, weight="bold"), text_color="#111827").grid(row=0, column=0, sticky="w", padx=12, pady=(8, 0))
                    ctk.CTkLabel(row, text=f"Bruto {self.format_kg(item['peso_bruto'])}  |  Desc. {self.format_kg(item['desconto'])}  |  Liquido {self.format_kg(item['peso_liquido'])}", font=ctk.CTkFont(size=12), text_color="#66707A").grid(row=1, column=0, sticky="w", padx=12, pady=(2, 8))
                    ctk.CTkLabel(row, text=self.format_money(item["subtotal"]), font=ctk.CTkFont(size=15, weight="bold"), text_color="#0E5A25").grid(row=0, column=1, rowspan=2, padx=10)
                    ctk.CTkButton(row, text="Remover", width=82, height=30, corner_radius=7, fg_color="#FFF0F0", hover_color="#FFE0E0", text_color="#B84545", command=lambda pos=idx: remover_item(pos)).grid(row=0, column=2, rowspan=2, padx=(0, 10))

            bruto_total = sum(item["peso_bruto"] for item in self.current_items)
            desconto_total = sum(item["desconto"] for item in self.current_items)
            liquido_total = sum(item["peso_liquido"] for item in self.current_items)
            valor_total = sum(item["subtotal"] for item in self.current_items)
            if resumo_refs:
                resumo_refs["itens"].configure(text=str(len(self.current_items)))
                resumo_refs["bruto"].configure(text=self.format_kg(bruto_total))
                resumo_refs["desconto"].configure(text=self.format_kg(desconto_total))
                resumo_refs["liquido"].configure(text=self.format_kg(liquido_total))
                resumo_refs["total_destaque"].configure(text=self.format_money(valor_total))

        def adicionar_item():
            material = self.selected_row_by_name(materiais, material_var.get())
            if not material:
                messagebox.showwarning("Material obrigatorio", "Cadastre um material antes de adicionar itens.")
                return
            try:
                peso_bruto = self.parse_decimal(peso.get())
                desconto_valor = self.parse_decimal(desconto.get())
                preco_kg = self.parse_decimal(preco.get())
            except ValueError:
                messagebox.showerror("Valor invalido", "Confira peso, desconto e valor por kg.")
                return
            peso_liquido = peso_bruto - desconto_valor
            if peso_liquido <= 0:
                messagebox.showerror("Valor invalido", "O peso liquido precisa ser maior que zero.")
                return
            self.current_items.append({
                "material_id": material["id"],
                "material_nome": material["nome"],
                "peso_bruto": peso_bruto,
                "desconto": desconto_valor,
                "peso_liquido": peso_liquido,
                "preco_kg": preco_kg,
                "subtotal": peso_liquido * preco_kg,
            })
            peso.delete(0, "end")
            desconto.delete(0, "end")
            atualizar_preco()
            atualizar_previa()
            atualizar_tabela()

        ctk.CTkButton(add_grid, text="+ Adicionar", height=36, fg_color="#08721D", hover_color="#075E19", command=adicionar_item).grid(row=0, column=5, padx=5, pady=8, sticky="ew")
        def escolher_material(row):
            material_var.set(row["nome"])
            atualizar_preco()
            for widget in material_suggestions.winfo_children():
                widget.destroy()

        def atualizar_sugestoes_material(*_args):
            atualizar_preco()
            self.render_suggestions(material_suggestions, materiais, material_var.get(), escolher_material)

        material_var.trace_add("write", atualizar_sugestoes_material)
        material_select.bind("<FocusIn>", lambda _event: atualizar_sugestoes_material())
        material_select.bind("<KeyRelease>", lambda _event: atualizar_sugestoes_material())
        for entry in (peso, desconto, preco):
            entry.bind("<KeyRelease>", atualizar_previa)
            entry.bind("<FocusOut>", atualizar_previa)
        atualizar_preco()

        ctk.CTkLabel(summary, text="Resumo", font=ctk.CTkFont(size=18, weight="bold"), text_color="#1F2937").pack(anchor="w", padx=16, pady=(14, 0))
        ctk.CTkLabel(summary, text="Conferencia final", font=ctk.CTkFont(size=11, weight="bold"), text_color="#66707A").pack(anchor="w", padx=16, pady=(0, 10))

        total_box = ctk.CTkFrame(summary, fg_color="#063B18", corner_radius=12)
        total_box.pack(fill="x", padx=14, pady=(0, 8))
        ctk.CTkLabel(
            total_box,
            text="Total da compra" if tipo == "COMPRA" else "Total da venda",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#D8EBDC"
        ).pack(anchor="w", padx=12, pady=(10, 0))
        resumo_refs["total_destaque"] = ctk.CTkLabel(
            total_box,
            text="R$ 0,00",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        resumo_refs["total_destaque"].pack(anchor="w", padx=12, pady=(0, 10))

        action_box = ctk.CTkFrame(summary, fg_color="transparent")
        action_box.pack(fill="x", padx=14, pady=(0, 8))
        ctk.CTkButton(
            action_box,
            text="Salvar compra" if tipo == "COMPRA" else "Salvar venda",
            height=36,
            corner_radius=8,
            fg_color="#EEF0EF",
            hover_color="#E2E6E3",
            text_color="#1F2937",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: self.finalizar_operacao(tipo, cliente_var.get(), observacao.get(), False)
        ).pack(fill="x", pady=(0, 8))
        ctk.CTkButton(
            action_box,
            text="Gerar comprovante",
            height=40,
            corner_radius=8,
            fg_color="#08721D",
            hover_color="#075E19",
            font=ctk.CTkFont(size=15, weight="bold"),
            command=lambda: self.finalizar_operacao(tipo, cliente_var.get(), observacao.get(), True)
        ).pack(fill="x")

        summary_data = [
            ("Itens", "itens", "0", "#FBFCFD"),
            ("Peso bruto", "bruto", "0,00 kg", "#FBFCFD"),
            ("Desconto", "desconto", "0,00 kg", "#FBFCFD"),
            ("Peso liquido", "liquido", "0,00 kg", "#E9F7E3"),
        ]
        detail_grid = ctk.CTkFrame(summary, fg_color="transparent")
        detail_grid.pack(fill="x", padx=12, pady=(0, 8))
        detail_grid.grid_columnconfigure(0, weight=1)
        detail_grid.grid_columnconfigure(1, weight=1)
        for idx, (label, key, initial, color) in enumerate(summary_data):
            box = ctk.CTkFrame(detail_grid, fg_color=color, corner_radius=9)
            box.grid(row=idx // 2, column=idx % 2, sticky="ew", padx=4, pady=4)
            ctk.CTkLabel(box, text=label, font=ctk.CTkFont(size=10, weight="bold"), text_color="#66707A").pack(anchor="w", padx=9, pady=(7, 0))
            resumo_refs[key] = ctk.CTkLabel(box, text=initial, font=ctk.CTkFont(size=14, weight="bold"), text_color="#1F2937")
            resumo_refs[key].pack(anchor="w", padx=9, pady=(0, 7))

        atualizar_tabela()


    def tela_operacao(self, tipo):
        titulo = "Nova Compra" if tipo == "COMPRA" else "Nova Venda"
        subtitulo = "Entrada de materiais" if tipo == "COMPRA" else "Saida de materiais"
        self.current_items = []

        clientes = self.get_clientes()
        materiais = self.get_materiais_mais_comprados(somente_ativos=True)

        self.clear_main()
        self.main_container = ctk.CTkFrame(self, fg_color="#F7F8F6", corner_radius=0)
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.build_header()
        self.build_footer()

        page = ctk.CTkFrame(self.main_container, fg_color="#F7F8F6", corner_radius=0)
        page.grid(row=1, column=0, sticky="nsew", padx=22, pady=(7, 5))
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(page, fg_color="white", corner_radius=14, border_width=1, border_color="#E5E7EB", height=58)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        top.grid_propagate(False)
        ctk.CTkButton(
            top,
            text="< Voltar",
            width=96,
            height=34,
            corner_radius=8,
            fg_color="#EEF0EF",
            hover_color="#E1E5E2",
            text_color="#18221D",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.build_ui
        ).pack(side="left", padx=12, pady=12)
        ctk.CTkFrame(top, width=4, height=34, fg_color="#0E7A24", corner_radius=2).pack(side="left", padx=(2, 12), pady=12)
        title_box = ctk.CTkFrame(top, fg_color="transparent")
        title_box.pack(side="left", fill="x", expand=True, pady=7)
        ctk.CTkLabel(title_box, text=titulo, font=ctk.CTkFont(size=21, weight="bold"), text_color="#17202A").pack(anchor="w")
        ctk.CTkLabel(title_box, text=subtitulo, font=ctk.CTkFont(size=11, weight="bold"), text_color="#66707A").pack(anchor="w")

        workspace = ctk.CTkFrame(page, fg_color="transparent")
        workspace.grid(row=1, column=0, sticky="nsew")
        workspace.grid_columnconfigure(0, weight=1)
        workspace.grid_columnconfigure(1, weight=0)
        workspace.grid_rowconfigure(0, weight=1)

        main_card = ctk.CTkFrame(workspace, fg_color="white", corner_radius=14, border_width=1, border_color="#E5E7EB")
        main_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        main_card.grid_columnconfigure(0, weight=1)
        main_card.grid_rowconfigure(3, weight=1)

        side = ctk.CTkFrame(workspace, width=306, fg_color="white", corner_radius=14, border_width=1, border_color="#E5E7EB")
        side.grid(row=0, column=1, sticky="nsew")
        side.grid_propagate(False)

        ctk.CTkLabel(main_card, text="Cliente", font=ctk.CTkFont(size=15, weight="bold"), text_color="#17202A").grid(row=0, column=0, sticky="w", padx=14, pady=(10, 0))
        client_grid = ctk.CTkFrame(main_card, fg_color="transparent")
        client_grid.grid(row=1, column=0, sticky="ew", padx=10, pady=(2, 6))
        for col in range(5):
            client_grid.grid_columnconfigure(col, weight=1)

        cliente_var = ctk.StringVar(value="")
        cliente_entry = ctk.CTkEntry(client_grid, textvariable=cliente_var, height=32, placeholder_text="Digite o cliente")
        cliente_entry.grid(row=0, column=0, columnspan=2, padx=4, pady=3, sticky="ew")
        ctk.CTkButton(client_grid, text="+ Novo", height=32, fg_color="#E5F5DF", hover_color="#D9EFD1", text_color="#15772C", command=self.tela_clientes).grid(row=0, column=2, padx=4, pady=3, sticky="ew")
        documento = ctk.CTkEntry(client_grid, height=32, placeholder_text="CPF / CNPJ")
        documento.grid(row=0, column=3, padx=4, pady=3, sticky="ew")
        telefone = ctk.CTkEntry(client_grid, height=32, placeholder_text="Telefone")
        telefone.grid(row=0, column=4, padx=4, pady=3, sticky="ew")
        cliente_suggestions = ctk.CTkFrame(client_grid, fg_color="transparent", height=28)
        cliente_suggestions.grid(row=1, column=0, columnspan=5, sticky="ew", padx=4, pady=(0, 1))
        observacao = ctk.CTkEntry(client_grid, height=32, placeholder_text="Observacao")
        observacao.grid(row=2, column=0, columnspan=5, padx=4, pady=3, sticky="ew")

        def preencher_cliente():
            cliente = self.selected_row_by_name(clientes, cliente_var.get())
            documento.delete(0, "end")
            telefone.delete(0, "end")
            if cliente:
                documento.insert(0, cliente["cnpj"] or "")
                telefone.insert(0, cliente["telefone"] or "")

        def escolher_cliente(row):
            cliente_var.set(row["nome"])
            preencher_cliente()
            for widget in cliente_suggestions.winfo_children():
                widget.destroy()

        def sugestoes_cliente(*_args):
            preencher_cliente()
            self.render_suggestions(cliente_suggestions, clientes, cliente_var.get(), escolher_cliente)

        cliente_entry.bind("<FocusIn>", lambda _event: sugestoes_cliente())
        cliente_entry.bind("<KeyRelease>", lambda _event: sugestoes_cliente())

        ctk.CTkLabel(main_card, text="Material", font=ctk.CTkFont(size=15, weight="bold"), text_color="#17202A").grid(row=2, column=0, sticky="w", padx=14, pady=(2, 0))
        material_area = ctk.CTkFrame(main_card, fg_color="#F8FAF8", corner_radius=12)
        material_area.grid(row=3, column=0, sticky="nsew", padx=10, pady=(2, 10))
        material_area.grid_columnconfigure(0, weight=1)
        material_area.grid_rowconfigure(3, weight=1)

        fields = ctk.CTkFrame(material_area, fg_color="transparent")
        fields.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 2))
        for col in range(6):
            fields.grid_columnconfigure(col, weight=1)

        material_var = ctk.StringVar(value="")
        material_entry = ctk.CTkEntry(fields, textvariable=material_var, height=32, placeholder_text="Digite o material")
        material_entry.grid(row=0, column=0, columnspan=2, padx=4, pady=4, sticky="ew")
        peso = ctk.CTkEntry(fields, height=32, placeholder_text="Peso bruto")
        peso.grid(row=0, column=2, padx=4, pady=4, sticky="ew")
        desconto = ctk.CTkEntry(fields, height=32, placeholder_text="Desconto")
        desconto.grid(row=0, column=3, padx=4, pady=4, sticky="ew")
        preco = ctk.CTkEntry(fields, height=32, placeholder_text="Valor kg")
        preco.grid(row=0, column=4, padx=4, pady=4, sticky="ew")

        material_suggestions = ctk.CTkFrame(fields, fg_color="transparent", height=28)
        material_suggestions.grid(row=1, column=0, columnspan=6, sticky="ew", padx=4, pady=(0, 2))

        preview = ctk.CTkFrame(material_area, fg_color="white", corner_radius=10)
        preview.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 6))
        preview.grid_columnconfigure(0, weight=1)
        preview.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(preview, text="Peso liquido do item", font=ctk.CTkFont(size=11, weight="bold"), text_color="#66707A").grid(row=0, column=0, sticky="w", padx=12, pady=(6, 0))
        ctk.CTkLabel(preview, text="Subtotal do item", font=ctk.CTkFont(size=11, weight="bold"), text_color="#66707A").grid(row=0, column=1, sticky="w", padx=12, pady=(6, 0))
        preview_liquido = ctk.CTkLabel(preview, text="0,00 kg", font=ctk.CTkFont(size=15, weight="bold"), text_color="#17202A")
        preview_liquido.grid(row=1, column=0, sticky="w", padx=12, pady=(0, 6))
        preview_subtotal = ctk.CTkLabel(preview, text="R$ 0,00", font=ctk.CTkFont(size=15, weight="bold"), text_color="#0E7A24")
        preview_subtotal.grid(row=1, column=1, sticky="w", padx=12, pady=(0, 6))

        ctk.CTkButton(fields, text="+ Adicionar", height=32, fg_color="#0E7A24", hover_color="#0A631D", command=lambda: adicionar_item()).grid(row=0, column=5, padx=4, pady=4, sticky="ew")

        list_box = ctk.CTkScrollableFrame(material_area, fg_color="white", corner_radius=10)
        list_box.grid(row=3, column=0, sticky="nsew", padx=12, pady=(0, 10))

        resumo_refs = {}

        def atualizar_previa(_event=None):
            try:
                peso_bruto = self.parse_decimal(peso.get())
                desconto_valor = self.parse_decimal(desconto.get())
                preco_kg = self.parse_decimal(preco.get())
                peso_liquido = max(0, peso_bruto - desconto_valor)
                subtotal_item = peso_liquido * preco_kg
            except ValueError:
                peso_liquido = 0
                subtotal_item = 0
            preview_liquido.configure(text=self.format_kg(peso_liquido))
            preview_subtotal.configure(text=self.format_money(subtotal_item))

        def atualizar_preco():
            material = self.selected_row_by_name(materiais, material_var.get())
            preco.delete(0, "end")
            if material:
                valor = material["preco_compra"] if tipo == "COMPRA" else material["preco_venda"]
                preco.insert(0, f"{valor:.2f}".replace(".", ","))
            atualizar_previa()

        def escolher_material(row):
            material_var.set(row["nome"])
            atualizar_preco()
            for widget in material_suggestions.winfo_children():
                widget.destroy()

        def sugestoes_material(*_args):
            atualizar_preco()
            self.render_suggestions(material_suggestions, materiais, material_var.get(), escolher_material)

        def remover_item(index):
            self.current_items.pop(index)
            atualizar_tabela()

        def atualizar_tabela():
            for widget in list_box.winfo_children():
                widget.destroy()

            if not self.current_items:
                empty = ctk.CTkFrame(list_box, fg_color="#F8FAF8", corner_radius=10)
                empty.pack(fill="x", padx=2, pady=2)
                ctk.CTkLabel(empty, text="Nenhum material adicionado ainda.", height=66, text_color="#66707A", font=ctk.CTkFont(size=13, weight="bold")).pack(expand=True)
            else:
                for idx, item in enumerate(self.current_items):
                    row = ctk.CTkFrame(list_box, fg_color="#F8FAF8", corner_radius=10)
                    row.pack(fill="x", padx=2, pady=4)
                    row.grid_columnconfigure(0, weight=1)
                    ctk.CTkLabel(row, text=item["material_nome"], font=ctk.CTkFont(size=14, weight="bold"), text_color="#111827").grid(row=0, column=0, sticky="w", padx=12, pady=(8, 0))
                    ctk.CTkLabel(row, text=f"Bruto {self.format_kg(item['peso_bruto'])} | Desc. {self.format_kg(item['desconto'])} | Liquido {self.format_kg(item['peso_liquido'])}", font=ctk.CTkFont(size=12), text_color="#66707A").grid(row=1, column=0, sticky="w", padx=12, pady=(2, 8))
                    ctk.CTkLabel(row, text=self.format_money(item["subtotal"]), font=ctk.CTkFont(size=15, weight="bold"), text_color="#0E7A24").grid(row=0, column=1, rowspan=2, padx=10)
                    ctk.CTkButton(row, text="Remover", width=78, height=30, corner_radius=7, fg_color="#FFF0F0", hover_color="#FFE0E0", text_color="#B84545", command=lambda pos=idx: remover_item(pos)).grid(row=0, column=2, rowspan=2, padx=(0, 10))

            bruto_total = sum(item["peso_bruto"] for item in self.current_items)
            desconto_total = sum(item["desconto"] for item in self.current_items)
            liquido_total = sum(item["peso_liquido"] for item in self.current_items)
            valor_total = sum(item["subtotal"] for item in self.current_items)
            if resumo_refs:
                resumo_refs["itens"].configure(text=str(len(self.current_items)))
                resumo_refs["bruto"].configure(text=self.format_kg(bruto_total))
                resumo_refs["desconto"].configure(text=self.format_kg(desconto_total))
                resumo_refs["liquido"].configure(text=self.format_kg(liquido_total))
                resumo_refs["total"].configure(text=self.format_money(valor_total))

        def adicionar_item():
            material = self.selected_row_by_name(materiais, material_var.get())
            if not material:
                messagebox.showwarning("Material obrigatorio", "Digite e selecione um material cadastrado.")
                return
            try:
                peso_bruto = self.parse_decimal(peso.get())
                desconto_valor = self.parse_decimal(desconto.get())
                preco_kg = self.parse_decimal(preco.get())
            except ValueError:
                messagebox.showerror("Valor invalido", "Confira peso, desconto e valor por kg.")
                return
            peso_liquido = peso_bruto - desconto_valor
            if peso_liquido <= 0:
                messagebox.showerror("Valor invalido", "O peso liquido precisa ser maior que zero.")
                return
            self.current_items.append({
                "material_id": material["id"],
                "material_nome": material["nome"],
                "peso_bruto": peso_bruto,
                "desconto": desconto_valor,
                "peso_liquido": peso_liquido,
                "preco_kg": preco_kg,
                "subtotal": peso_liquido * preco_kg,
            })
            material_var.set("")
            peso.delete(0, "end")
            desconto.delete(0, "end")
            preco.delete(0, "end")
            atualizar_previa()
            atualizar_tabela()
            peso.focus_set()

        cliente_var.trace_add("write", sugestoes_cliente)
        material_var.trace_add("write", sugestoes_material)
        material_entry.bind("<FocusIn>", lambda _event: sugestoes_material())
        material_entry.bind("<KeyRelease>", lambda _event: sugestoes_material())
        for entry in (peso, desconto, preco):
            entry.bind("<KeyRelease>", atualizar_previa)
            entry.bind("<FocusOut>", atualizar_previa)

        ctk.CTkLabel(side, text="Resumo", font=ctk.CTkFont(size=18, weight="bold"), text_color="#17202A").pack(anchor="w", padx=15, pady=(14, 0))
        total_card = ctk.CTkFrame(side, fg_color="#063B18", corner_radius=12)
        total_card.pack(fill="x", padx=14, pady=(10, 8))
        ctk.CTkLabel(total_card, text="Total da compra" if tipo == "COMPRA" else "Total da venda", font=ctk.CTkFont(size=12, weight="bold"), text_color="#D8EBDC").pack(anchor="w", padx=12, pady=(10, 0))
        resumo_refs["total"] = ctk.CTkLabel(total_card, text="R$ 0,00", font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
        resumo_refs["total"].pack(anchor="w", padx=12, pady=(0, 10))

        ctk.CTkButton(side, text="Salvar compra" if tipo == "COMPRA" else "Salvar venda", height=36, corner_radius=8, fg_color="#EEF0EF", hover_color="#E2E6E3", text_color="#17202A", font=ctk.CTkFont(size=14, weight="bold"), command=lambda: self.finalizar_operacao(tipo, cliente_var.get(), observacao.get(), False)).pack(fill="x", padx=14, pady=(0, 8))
        ctk.CTkButton(side, text="Gerar comprovante", height=40, corner_radius=8, fg_color="#0E7A24", hover_color="#0A631D", font=ctk.CTkFont(size=15, weight="bold"), command=lambda: self.finalizar_operacao(tipo, cliente_var.get(), observacao.get(), True)).pack(fill="x", padx=14, pady=(0, 10))

        detail_grid = ctk.CTkFrame(side, fg_color="transparent")
        detail_grid.pack(fill="x", padx=10)
        detail_grid.grid_columnconfigure(0, weight=1)
        detail_grid.grid_columnconfigure(1, weight=1)
        for idx, (label, key, initial, color) in enumerate([
            ("Itens", "itens", "0", "#FBFCFD"),
            ("Bruto", "bruto", "0,00 kg", "#FBFCFD"),
            ("Desconto", "desconto", "0,00 kg", "#FBFCFD"),
            ("Liquido", "liquido", "0,00 kg", "#E9F7E3"),
        ]):
            box = ctk.CTkFrame(detail_grid, fg_color=color, corner_radius=9)
            box.grid(row=idx // 2, column=idx % 2, sticky="ew", padx=4, pady=4)
            ctk.CTkLabel(box, text=label, font=ctk.CTkFont(size=10, weight="bold"), text_color="#66707A").pack(anchor="w", padx=9, pady=(7, 0))
            resumo_refs[key] = ctk.CTkLabel(box, text=initial, font=ctk.CTkFont(size=13, weight="bold"), text_color="#17202A")
            resumo_refs[key].pack(anchor="w", padx=9, pady=(0, 7))

        atualizar_previa()
        atualizar_tabela()


    def tela_operacao(self, tipo):
        colors = {
            "bg": "#F7F8F6",
            "line": "#E5E7EB",
            "text": "#17202A",
            "muted": "#66707A",
            "green": "#0E7A24",
            "green_hover": "#0A631D",
            "danger": "#C94040",
        }
        title = "Nova Compra" if tipo == "COMPRA" else "Nova Venda"
        subtitle = "Registre a entrada de materiais no estoque" if tipo == "COMPRA" else "Registre a saida de materiais do estoque"
        self.current_items = []

        clientes = self.get_clientes()
        materiais = self.get_materiais_mais_comprados(somente_ativos=True)
        cliente_names = self.option_values(clientes)
        material_names = self.option_values(materiais)

        self.clear_main()
        self.main_container = ctk.CTkFrame(self, fg_color=colors["bg"], corner_radius=0)
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.build_header()
        self.build_footer()

        page = ctk.CTkFrame(self.main_container, fg_color=colors["bg"], corner_radius=0)
        page.grid(row=1, column=0, sticky="nsew", padx=22, pady=(7, 5))
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(2, weight=1)

        heading = ctk.CTkFrame(page, fg_color="transparent", height=54)
        heading.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        heading.grid_propagate(False)
        ctk.CTkButton(
            heading,
            text="<  Voltar",
            width=116,
            height=38,
            corner_radius=8,
            fg_color="#EEF0EF",
            hover_color="#E1E5E2",
            text_color=colors["text"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.build_ui,
        ).pack(side="left", padx=(0, 20), pady=8)

        title_box = ctk.CTkFrame(heading, fg_color="transparent")
        title_box.pack(side="left", fill="x", expand=True, pady=5)
        ctk.CTkLabel(title_box, text=title, font=ctk.CTkFont(size=22, weight="bold"), text_color=colors["text"]).pack(anchor="w")
        ctk.CTkLabel(title_box, text=subtitle, font=ctk.CTkFont(size=12, weight="bold"), text_color=colors["muted"]).pack(anchor="w")

        def small_entry(master, placeholder="", textvariable=None):
            return ctk.CTkEntry(
                master,
                height=34,
                corner_radius=6,
                border_width=1,
                border_color=colors["line"],
                fg_color="white",
                placeholder_text=placeholder,
                textvariable=textvariable,
            )

        client_panel = ctk.CTkFrame(page, height=154, fg_color="white", corner_radius=12, border_width=1, border_color=colors["line"])
        client_panel.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        client_panel.grid_propagate(False)
        ctk.CTkLabel(client_panel, text="Dados do Cliente", font=ctk.CTkFont(size=14, weight="bold"), text_color=colors["text"]).place(x=20, y=8)

        tipo_cliente = ctk.StringVar(value="cadastrado")
        radio_row = ctk.CTkFrame(client_panel, fg_color="transparent")
        radio_row.place(x=20, y=30)
        ctk.CTkRadioButton(radio_row, text="Cliente cadastrado", variable=tipo_cliente, value="cadastrado", radiobutton_width=16, radiobutton_height=16, border_width_checked=5, fg_color=colors["green"], font=ctk.CTkFont(size=11, weight="bold"), text_color="#3D464F").pack(side="left", padx=(0, 24))
        ctk.CTkRadioButton(radio_row, text="Cliente anonimo", variable=tipo_cliente, value="anonimo", radiobutton_width=16, radiobutton_height=16, border_width_checked=5, fg_color=colors["green"], font=ctk.CTkFont(size=11, weight="bold"), text_color="#3D464F").pack(side="left")

        client_grid = ctk.CTkFrame(client_panel, fg_color="transparent")
        client_grid.place(x=18, y=56, relwidth=0.97)
        for index, weight in enumerate([2, 2, 0, 1, 1, 2]):
            client_grid.grid_columnconfigure(index, weight=weight, minsize=86 if index == 2 else 0)

        for col, text, span in [
            (0, "Cliente *", 2),
            (2, "", 1),
            (3, "CPF / CNPJ", 1),
            (4, "Telefone", 1),
            (5, "Observacao (opcional)", 1),
        ]:
            ctk.CTkLabel(client_grid, text=text, font=ctk.CTkFont(size=10, weight="bold"), text_color="#3D464F").grid(row=0, column=col, columnspan=span, sticky="w", padx=4)

        cliente_var = ctk.StringVar(value="")
        cliente_entry = ctk.CTkEntry(client_grid, textvariable=cliente_var, height=34, corner_radius=6, border_color=colors["line"], fg_color="white", placeholder_text="Digite para buscar cliente")
        cliente_entry.grid(row=1, column=0, columnspan=2, padx=4, pady=(2, 0), sticky="ew")
        ctk.CTkButton(client_grid, text="+  Novo", height=34, corner_radius=6, fg_color="#E5F5DF", hover_color="#D9EFD1", text_color=colors["green"], font=ctk.CTkFont(size=12, weight="bold"), command=self.tela_clientes).grid(row=1, column=2, padx=4, pady=(2, 0), sticky="ew")
        documento = small_entry(client_grid, "00.000.000/0000-00")
        documento.grid(row=1, column=3, padx=4, pady=(2, 0), sticky="ew")
        telefone = small_entry(client_grid, "(19) 99999-9999")
        telefone.grid(row=1, column=4, padx=4, pady=(2, 0), sticky="ew")
        observacao = small_entry(client_grid, "Digite uma observacao...")
        observacao.grid(row=1, column=5, padx=4, pady=(2, 0), sticky="ew")
        cliente_suggestions = ctk.CTkFrame(client_grid, fg_color="transparent", height=26)
        cliente_suggestions.grid(row=2, column=0, columnspan=2, sticky="ew", padx=4, pady=(0, 0))

        def cliente_digitado():
            return self.selected_row_by_name(clientes, cliente_var.get())

        def fill_client(*_args):
            documento.delete(0, "end")
            telefone.delete(0, "end")
            if tipo_cliente.get() == "anonimo":
                return
            cliente = cliente_digitado()
            if cliente:
                documento.insert(0, cliente["cnpj"] or "")
                telefone.insert(0, cliente["telefone"] or "")

        def escolher_cliente(row):
            cliente_var.set(row["nome"])
            for widget in cliente_suggestions.winfo_children():
                widget.destroy()
            fill_client()

        def atualizar_sugestoes_cliente(*_args):
            if tipo_cliente.get() == "anonimo" or not cliente_var.get().strip():
                for widget in cliente_suggestions.winfo_children():
                    widget.destroy()
                fill_client()
                return
            self.render_suggestions(cliente_suggestions, clientes, cliente_var.get(), escolher_cliente)
            fill_client()

        cliente_var.trace_add("write", atualizar_sugestoes_cliente)
        cliente_entry.bind("<FocusIn>", lambda _event: atualizar_sugestoes_cliente())
        cliente_entry.bind("<KeyRelease>", lambda _event: atualizar_sugestoes_cliente())
        tipo_cliente.trace_add("write", fill_client)
        fill_client()

        work_area = ctk.CTkFrame(page, fg_color="transparent")
        work_area.grid(row=2, column=0, sticky="nsew", pady=(0, 6))
        work_area.grid_columnconfigure(0, weight=5)
        work_area.grid_columnconfigure(1, weight=2, minsize=310)
        work_area.grid_rowconfigure(0, weight=1)

        item_panel = ctk.CTkFrame(work_area, fg_color="white", corner_radius=12, border_width=1, border_color=colors["line"])
        item_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        item_panel.grid_columnconfigure(0, weight=1)
        item_panel.grid_rowconfigure(2, weight=1)

        item_top = ctk.CTkFrame(item_panel, fg_color="transparent", height=48)
        item_top.grid(row=0, column=0, sticky="ew")
        item_top.grid_propagate(False)
        ctk.CTkLabel(item_top, text="Itens da Compra" if tipo == "COMPRA" else "Itens da Venda", font=ctk.CTkFont(size=14, weight="bold"), text_color=colors["text"]).place(x=18, y=7)
        ctk.CTkLabel(item_top, text="Adicione os materiais adquiridos" if tipo == "COMPRA" else "Adicione os materiais vendidos", font=ctk.CTkFont(size=11, weight="bold"), text_color=colors["muted"]).place(x=18, y=27)
        ctk.CTkButton(item_top, text="+  Adicionar Material", width=190, height=32, corner_radius=6, fg_color=colors["green"], hover_color=colors["green_hover"], font=ctk.CTkFont(size=12, weight="bold"), command=lambda: add_item_row()).place(relx=1.0, x=-18, y=8, anchor="ne")

        table_header = ctk.CTkFrame(item_panel, fg_color="#F8F9FA", height=32, corner_radius=0)
        table_header.grid(row=1, column=0, sticky="ew", padx=16)
        table_header.grid_propagate(False)
        col_weights = [13, 24, 13, 14, 14, 15, 7]

        def configure_table_columns(frame):
            for index, weight in enumerate(col_weights):
                frame.grid_columnconfigure(index, weight=weight, uniform="operation_table")

        configure_table_columns(table_header)
        headers = ["Peso Bruto (kg)", "Material", "Desconto (kg)", "Peso Liquido (kg)", "Valor por kg (R$)", "Subtotal (R$)", "Acoes"]
        for index, text in enumerate(headers):
            ctk.CTkLabel(table_header, text=text, anchor="w" if index == 1 else "center", font=ctk.CTkFont(size=11, weight="bold"), text_color="#303942").grid(row=0, column=index, sticky="nsew", padx=4)

        table_body = ctk.CTkScrollableFrame(item_panel, fg_color="white", corner_radius=0, height=170)
        table_body.grid(row=2, column=0, sticky="nsew", padx=16)

        item_rows = []
        empty_state = {"widget": None}
        summary_refs = {}

        def readonly_cell(parent, color="white", text_color=None):
            box = ctk.CTkFrame(parent, height=32, fg_color=color, corner_radius=6, border_width=1, border_color=colors["line"])
            box.grid_propagate(False)
            label = ctk.CTkLabel(box, text="0,00", font=ctk.CTkFont(size=11, weight="bold"), text_color=text_color or colors["text"])
            label.pack(expand=True)
            return box, label

        def parse_or_zero(widget):
            try:
                return self.parse_decimal(widget.get())
            except ValueError:
                return 0.0

        def material_digitado(nome):
            return self.selected_row_by_name(materiais, nome)

        def valid_items_from_rows(validate=False):
            items = []
            for row_data in item_rows:
                material = material_digitado(row_data["material_var"].get())
                touched = bool(row_data["material_var"].get().strip() or row_data["peso"].get().strip() or row_data["desconto"].get().strip())
                if not material:
                    if validate and touched:
                        messagebox.showwarning("Material obrigatorio", "Selecione um material cadastrado.")
                        return None
                    continue
                try:
                    peso_bruto = self.parse_decimal(row_data["peso"].get())
                    desconto_valor = self.parse_decimal(row_data["desconto"].get())
                    preco_kg = self.parse_decimal(row_data["preco"].get())
                except ValueError:
                    if validate:
                        messagebox.showerror("Valor invalido", "Confira peso, desconto e valor por kg.")
                        return None
                    continue
                peso_liquido = peso_bruto - desconto_valor
                if peso_liquido <= 0:
                    if validate and touched:
                        messagebox.showerror("Peso invalido", "O peso liquido precisa ser maior que zero.")
                        return None
                    continue
                items.append({
                    "material_id": material["id"],
                    "material_nome": material["nome"],
                    "peso_bruto": peso_bruto,
                    "desconto": desconto_valor,
                    "peso_liquido": peso_liquido,
                    "preco_kg": preco_kg,
                    "subtotal": peso_liquido * preco_kg,
                })
            return items

        def update_empty_state():
            if item_rows and empty_state["widget"] is not None:
                empty_state["widget"].destroy()
                empty_state["widget"] = None
            if not item_rows and empty_state["widget"] is None:
                empty_state["widget"] = ctk.CTkLabel(table_body, text="Nenhum material adicionado ainda.", height=56, text_color=colors["muted"], font=ctk.CTkFont(size=12, weight="bold"))
                empty_state["widget"].pack(fill="x")

        def recalculate_rows(_event=None):
            bruto_total = 0.0
            desconto_total = 0.0
            liquido_total = 0.0
            valor_total = 0.0
            for row_data in item_rows:
                peso_bruto = parse_or_zero(row_data["peso"])
                desconto_valor = parse_or_zero(row_data["desconto"])
                preco_kg = parse_or_zero(row_data["preco"])
                peso_liquido = max(0.0, peso_bruto - desconto_valor)
                subtotal = peso_liquido * preco_kg
                row_data["liquido_label"].configure(text=f"{peso_liquido:.2f}".replace(".", ","))
                row_data["subtotal_label"].configure(text=self.format_money(subtotal))
                bruto_total += peso_bruto
                desconto_total += desconto_valor
                liquido_total += peso_liquido
                valor_total += subtotal
            if summary_refs:
                summary_refs["bruto"].configure(text=self.format_kg(bruto_total))
                summary_refs["desconto"].configure(text=self.format_kg(desconto_total))
                summary_refs["liquido"].configure(text=self.format_kg(liquido_total))
                summary_refs["total"].configure(text=self.format_money(valor_total))
            self.current_items = valid_items_from_rows(validate=False) or []
            update_empty_state()

        def apply_material(row_data):
            material = material_digitado(row_data["material_var"].get())
            row_data["preco"].delete(0, "end")
            if material:
                price = material["preco_compra"] if tipo == "COMPRA" else material["preco_venda"]
                row_data["preco"].insert(0, f"{price:.2f}".replace(".", ","))
            recalculate_rows()

        def remove_row(row_data):
            if row_data in item_rows:
                item_rows.remove(row_data)
            row_data["frame"].destroy()
            recalculate_rows()

        shortcut_actions = {"finalize": None}

        def shortcut_add_item(_event=None):
            add_item_row()
            return "break"

        def shortcut_finalize(_event=None):
            finalize_callback = shortcut_actions["finalize"]
            if finalize_callback:
                finalize_callback(True)
            return "break"

        def bind_operation_shortcuts(widget):
            for sequence in ("<KeyPress-plus>", "<KP_Add>"):
                widget.bind(sequence, shortcut_add_item, add="+")
            for sequence in ("<Return>", "<KP_Enter>"):
                widget.bind(sequence, shortcut_finalize, add="+")

        def add_item_row():
            row_frame = ctk.CTkFrame(table_body, fg_color="white", height=78, corner_radius=0)
            row_frame.pack(fill="x", pady=(0, 4))
            row_frame.grid_propagate(False)
            configure_table_columns(row_frame)
            material_var = ctk.StringVar(value="")
            peso = small_entry(row_frame, "0,00")
            peso.grid(row=0, column=0, sticky="ew", padx=4, pady=5)
            material_entry = ctk.CTkEntry(row_frame, textvariable=material_var, height=32, corner_radius=6, border_color=colors["line"], fg_color="white", placeholder_text="Digite o material")
            material_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=5)
            material_suggestions = ctk.CTkFrame(row_frame, fg_color="transparent", height=26)
            material_suggestions.grid(row=1, column=1, columnspan=2, sticky="ew", padx=4, pady=(0, 2))
            desconto = small_entry(row_frame, "0,00")
            desconto.grid(row=0, column=2, sticky="ew", padx=4, pady=5)
            liquido_box, liquido_label = readonly_cell(row_frame, "#E9F7E3")
            liquido_box.grid(row=0, column=3, sticky="ew", padx=4, pady=5)
            preco = small_entry(row_frame, "0,00")
            preco.grid(row=0, column=4, sticky="ew", padx=4, pady=5)
            subtotal_box, subtotal_label = readonly_cell(row_frame, "white", colors["green"])
            subtotal_box.grid(row=0, column=5, sticky="ew", padx=4, pady=5)
            actions = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions.grid(row=0, column=6, sticky="nsew", padx=2, pady=4)
            row_data = {
                "frame": row_frame,
                "material_var": material_var,
                "material_suggestions": material_suggestions,
                "peso": peso,
                "desconto": desconto,
                "preco": preco,
                "liquido_label": liquido_label,
                "subtotal_label": subtotal_label,
            }
            ctk.CTkButton(actions, text="X", width=30, height=30, corner_radius=6, fg_color="#FFF0F0", hover_color="#FFE0E0", text_color=colors["danger"], command=lambda data=row_data: remove_row(data)).pack(side="left", padx=2)

            def escolher_material(row, data=row_data):
                data["material_var"].set(row["nome"])
                for widget in data["material_suggestions"].winfo_children():
                    widget.destroy()
                apply_material(data)

            def atualizar_sugestoes_material(_event=None, data=row_data):
                self.render_suggestions(data["material_suggestions"], materiais, data["material_var"].get(), lambda row: escolher_material(row, data))

            material_entry.bind("<FocusIn>", atualizar_sugestoes_material)
            material_entry.bind("<KeyRelease>", atualizar_sugestoes_material)
            material_entry.bind("<Return>", lambda _event, data=row_data: apply_material(data))
            material_entry.bind("<FocusOut>", lambda _event, data=row_data: apply_material(data))
            for widget in (peso, desconto, preco):
                widget.bind("<KeyRelease>", recalculate_rows)
                widget.bind("<FocusOut>", recalculate_rows)
            item_rows.append(row_data)

        side_panel = ctk.CTkFrame(work_area, fg_color="transparent")
        side_panel.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        side_panel.grid_columnconfigure(0, weight=1)
        side_panel.grid_rowconfigure(0, weight=0)
        side_panel.grid_rowconfigure(1, weight=0)

        resumo = ctk.CTkFrame(side_panel, fg_color="white", corner_radius=12, border_width=1, border_color=colors["line"])
        resumo.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        ctk.CTkLabel(resumo, text="Resumo da Operacao", font=ctk.CTkFont(size=14, weight="bold"), text_color=colors["text"]).pack(anchor="w", padx=16, pady=(12, 8))
        resumo_grid = ctk.CTkFrame(resumo, fg_color="transparent")
        resumo_grid.pack(fill="x", padx=12, pady=(0, 12))
        resumo_lines = []
        for _row_index in range(2):
            line = ctk.CTkFrame(resumo_grid, height=66, fg_color="transparent")
            line.pack(fill="x", pady=4)
            line.pack_propagate(False)
            line.grid_columnconfigure(0, weight=1)
            line.grid_columnconfigure(1, weight=1)
            resumo_lines.append(line)
        for index, (label, key) in enumerate([
            ("Peso Bruto", "bruto"),
            ("Desconto (kg)", "desconto"),
            ("Peso Liquido", "liquido"),
            ("Total", "total"),
        ]):
            box_color = "#E9F7E3" if key in ("liquido", "total") else "#FBFCFD"
            box = ctk.CTkFrame(resumo_lines[index // 2], height=62, fg_color=box_color, corner_radius=8)
            box.grid(row=0, column=index % 2, sticky="nsew", padx=5)
            box.grid_propagate(False)
            box.pack_propagate(False)
            ctk.CTkLabel(box, text=label, font=ctk.CTkFont(size=11, weight="bold"), text_color="#374151").pack(anchor="w", padx=12, pady=(9, 2))
            summary_refs[key] = ctk.CTkLabel(box, text="R$ 0,00" if key == "total" else "0,00 kg", font=ctk.CTkFont(size=18 if key == "total" else 15, weight="bold"), text_color=colors["green"] if key == "total" else colors["text"])
            summary_refs[key].pack(anchor="w", padx=12)

        acoes = ctk.CTkFrame(side_panel, fg_color="white", corner_radius=12, border_width=1, border_color=colors["line"])
        acoes.grid(row=1, column=0, sticky="ew")
        ctk.CTkLabel(acoes, text="Acoes", font=ctk.CTkFont(size=14, weight="bold"), text_color=colors["text"]).pack(anchor="w", padx=16, pady=(12, 8))

        def ensure_anonymous_client():
            anon_name = "Cliente Anonimo"
            if self.selected_row_by_name(self.get_clientes(), anon_name):
                return anon_name
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        "INSERT INTO clientes (nome, telefone, cnpj, cidade, observacao) VALUES (?, ?, ?, ?, ?)",
                        (anon_name, "", "", "", "Cadastro automatico para operacoes sem cliente identificado.")
                    )
            except sqlite3.IntegrityError:
                pass
            return anon_name

        def finalizar(gerar_comprovante=True):
            items = valid_items_from_rows(validate=True)
            if items is None:
                return
            if not items:
                messagebox.showwarning("Itens obrigatorios", "Adicione pelo menos um material.")
                return
            cliente_nome = ensure_anonymous_client() if tipo_cliente.get() == "anonimo" else cliente_var.get()
            self.current_items = items
            self.finalizar_operacao(
                tipo,
                cliente_nome,
                observacao.get().strip(),
                gerar_comprovante,
                documento.get() if tipo_cliente.get() != "anonimo" else "",
                telefone.get() if tipo_cliente.get() != "anonimo" else "",
            )

        ctk.CTkButton(acoes, text="Salvar Compra" if tipo == "COMPRA" else "Salvar Venda", height=32, corner_radius=6, fg_color="#EEF0EF", hover_color="#E2E6E3", text_color=colors["text"], font=ctk.CTkFont(size=12, weight="bold"), command=lambda: finalizar(False)).pack(fill="x", padx=22, pady=(0, 7))
        ctk.CTkButton(acoes, text="Gerar Comprovante", height=36, corner_radius=6, fg_color=colors["green"], hover_color=colors["green_hover"], font=ctk.CTkFont(size=12, weight="bold"), command=lambda: finalizar(True)).pack(fill="x", padx=22, pady=(0, 8))
        ctk.CTkLabel(acoes, text="A operacao sera registrada no sistema e o estoque sera atualizado.", wraplength=250, justify="left", text_color=colors["muted"], font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w", padx=22, pady=(0, 10))

        add_item_row()
        recalculate_rows()


    def tela_clientes(self):
        colors = {
            "bg": "#F7F8F6",
            "line": "#E5E7EB",
            "text": "#17202A",
            "muted": "#66707A",
            "green": "#0E7A24",
            "green_hover": "#0A631D",
            "danger": "#C94040",
        }

        self.clear_main()
        self.main_container = ctk.CTkFrame(self, fg_color=colors["bg"], corner_radius=0)
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.build_header()
        self.build_footer()

        page = ctk.CTkFrame(self.main_container, fg_color=colors["bg"], corner_radius=0)
        page.grid(row=1, column=0, sticky="nsew", padx=28, pady=(10, 0))
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(2, weight=1)

        heading = ctk.CTkFrame(page, fg_color="transparent", height=82)
        heading.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        heading.grid_propagate(False)
        ctk.CTkButton(
            heading,
            text="<  Voltar",
            width=128,
            height=50,
            corner_radius=8,
            fg_color="#EEF0EF",
            hover_color="#E1E5E2",
            text_color=colors["text"],
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.build_ui,
        ).pack(side="left", padx=(0, 28), pady=16)

        title_box = ctk.CTkFrame(heading, fg_color="transparent")
        title_box.pack(side="left", fill="x", expand=True, pady=14)
        ctk.CTkLabel(title_box, text="Clientes", font=ctk.CTkFont(size=25, weight="bold"), text_color=colors["text"]).pack(anchor="w")
        ctk.CTkLabel(title_box, text="Gerencie seus clientes e fornecedores", font=ctk.CTkFont(size=13, weight="bold"), text_color="#555D66").pack(anchor="w", pady=(5, 0))

        controls = ctk.CTkFrame(page, fg_color="transparent", height=52)
        controls.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        controls.grid_propagate(False)
        controls.grid_columnconfigure(0, weight=0)
        controls.grid_columnconfigure(1, weight=0)
        controls.grid_columnconfigure(2, weight=1)
        controls.grid_columnconfigure(3, weight=0)

        tipo_var = ctk.StringVar(value="Todos tipos")
        estado_var = ctk.StringVar(value="Todos estados")
        busca_var = ctk.StringVar(value="")
        per_page_var = ctk.StringVar(value="10")
        current_page = {"value": 1}

        tipo_menu = ctk.CTkOptionMenu(
            controls,
            values=["Todos tipos", "Comprador", "Vendedor"],
            variable=tipo_var,
            width=188,
            height=42,
            corner_radius=6,
            fg_color="white",
            button_color="white",
            button_hover_color="#EEF0EF",
            text_color="#2D333A",
        )
        tipo_menu.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)

        estado_menu = ctk.CTkOptionMenu(
            controls,
            values=["Todos estados"],
            variable=estado_var,
            width=176,
            height=42,
            corner_radius=6,
            fg_color="white",
            button_color="white",
            button_hover_color="#EEF0EF",
            text_color="#2D333A",
        )
        estado_menu.grid(row=0, column=1, sticky="w", padx=(0, 18), pady=5)

        search_box = ctk.CTkFrame(controls, fg_color="white", corner_radius=6, border_width=1, border_color=colors["line"], height=42)
        search_box.grid(row=0, column=2, sticky="ew", padx=(0, 10), pady=5)
        search_box.grid_propagate(False)
        ctk.CTkLabel(search_box, text="Buscar", width=62, font=ctk.CTkFont(size=12, weight="bold"), text_color="#6B7280").pack(side="left", padx=(8, 0))
        search_entry = ctk.CTkEntry(search_box, textvariable=busca_var, height=38, border_width=0, fg_color="white", placeholder_text="Buscar nome, documento, telefone...")
        search_entry.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=2)

        ctk.CTkButton(
            controls,
            text="+  Cadastrar Cliente",
            width=230,
            height=42,
            corner_radius=6,
            fg_color=colors["green"],
            hover_color=colors["green_hover"],
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: open_editor(),
        ).grid(row=0, column=3, sticky="e", pady=5)

        table = ctk.CTkFrame(page, fg_color="white", corner_radius=0, border_width=1, border_color=colors["line"])
        table.grid(row=2, column=0, sticky="nsew")
        table.grid_columnconfigure(0, weight=1)
        table.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(table, fg_color="#FBFBFB", height=42, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        col_weights = [24, 12, 16, 17, 19, 16]

        def configure_columns(frame):
            for index, weight in enumerate(col_weights):
                frame.grid_columnconfigure(index, weight=weight, uniform="clientes_table")

        configure_columns(header)
        for index, text in enumerate(["Nome / Empresa", "Tipo", "Telefone", "Documento", "Cidade / Estado", ""]):
            ctk.CTkLabel(
                header,
                text=text,
                anchor="w" if index != 5 else "center",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#2E3338",
            ).grid(row=0, column=index, sticky="nsew", padx=16 if index == 0 else 8)

        body = ctk.CTkScrollableFrame(table, fg_color="white", corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew")

        pager = ctk.CTkFrame(page, fg_color="white", height=52, corner_radius=0)
        pager.grid(row=3, column=0, sticky="ew")
        pager.grid_propagate(False)

        def row_tipo(row):
            return row["tipo"] if "tipo" in row.keys() and row["tipo"] else "Comprador"

        def row_estado(row):
            if "estado" in row.keys() and row["estado"]:
                return row["estado"].strip().upper()
            cidade = (row["cidade"] or "").strip()
            if "/" in cidade:
                return cidade.rsplit("/", 1)[-1].strip().upper()
            return "SP" if cidade else ""

        def row_local(row):
            cidade = (row["cidade"] or "").strip()
            estado = row_estado(row)
            if cidade and estado and "/" not in cidade:
                return f"{cidade}/{estado}"
            return cidade if cidade else "-"

        def filtered_rows():
            rows = list(self.get_clientes())
            tipos = sorted({row_tipo(row) for row in rows if row_tipo(row)})
            tipo_menu.configure(values=["Todos tipos"] + tipos)
            estados = sorted({row_estado(row) for row in rows if row_estado(row)})
            estado_menu.configure(values=["Todos estados"] + estados)

            query = busca_var.get().strip().lower()
            result = []
            for row in rows:
                tipo_ok = tipo_var.get() == "Todos tipos" or row_tipo(row) == tipo_var.get()
                estado_ok = estado_var.get() == "Todos estados" or row_estado(row) == estado_var.get()
                haystack = " ".join([
                    row["nome"] or "",
                    row["telefone"] or "",
                    row["cnpj"] or "",
                    row["cidade"] or "",
                    row["email"] if "email" in row.keys() and row["email"] else "",
                    row["estado"] if "estado" in row.keys() and row["estado"] else "",
                    row["endereco"] if "endereco" in row.keys() and row["endereco"] else "",
                    row_tipo(row),
                ]).lower()
                search_ok = not query or query in haystack
                if tipo_ok and estado_ok and search_ok:
                    result.append(row)
            return result

        def delete_client(row):
            if not messagebox.askyesno("Excluir cliente", f"Deseja excluir {row['nome']}?"):
                return
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM clientes WHERE id=?", (row["id"],))
            except sqlite3.IntegrityError:
                messagebox.showerror("Nao foi possivel excluir", "Este cliente possui operacoes registradas.")
                return
            render()

        def table_row(parent, row_data):
            line = ctk.CTkFrame(parent, fg_color="white", height=48, corner_radius=0)
            line.pack(fill="x")
            line.grid_propagate(False)
            configure_columns(line)
            ctk.CTkButton(
                line,
                text=row_data["nome"] or "",
                anchor="w",
                height=32,
                corner_radius=6,
                fg_color="transparent",
                hover_color="#F3FAF2",
                text_color=colors["green"],
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda row=row_data: self.tela_cliente_historico(row),
            ).grid(row=0, column=0, sticky="ew", padx=(10, 8), pady=6)
            values = [
                row_tipo(row_data),
                row_data["telefone"] or "-",
                row_data["cnpj"] or "-",
                row_local(row_data),
            ]
            for index, value in enumerate(values, start=1):
                ctk.CTkLabel(
                    line,
                    text=value,
                    anchor="w",
                    font=ctk.CTkFont(size=13),
                    text_color="#2E3338",
                ).grid(row=0, column=index, sticky="nsew", padx=8)
            actions = ctk.CTkFrame(line, fg_color="transparent")
            actions.grid(row=0, column=5, sticky="e", padx=(0, 12))
            ctk.CTkButton(
                actions,
                text="Editar",
                width=78,
                height=32,
                corner_radius=6,
                fg_color=colors["green"],
                hover_color=colors["green_hover"],
                text_color="white",
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda: open_editor(row_data),
            ).pack(side="left", padx=(0, 6))
            ctk.CTkButton(
                actions,
                text="Excluir",
                width=78,
                height=32,
                corner_radius=6,
                fg_color=colors["danger"],
                hover_color="#B93535",
                text_color="white",
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda: delete_client(row_data),
            ).pack(side="left")

        def render_pager(total, start, end, pages):
            for widget in pager.winfo_children():
                widget.destroy()

            ctk.CTkLabel(pager, text=f"{start} a {end} de {total} registros", font=ctk.CTkFont(size=13), text_color="#4B5563").pack(side="left", padx=(14, 8))
            ctk.CTkLabel(pager, text="Mostrando", font=ctk.CTkFont(size=13), text_color="#4B5563").pack(side="left", padx=(240, 8))
            ctk.CTkOptionMenu(
                pager,
                values=["10", "20", "50"],
                variable=per_page_var,
                width=82,
                height=32,
                corner_radius=6,
                fg_color="#F8F8F8",
                button_color="#F8F8F8",
                button_hover_color="#ECECEC",
                text_color="#2E3338",
                command=lambda value: (per_page_var.set(str(value)), reset_and_render()),
            ).pack(side="left", padx=(0, 12))

            def page_button(text, target=None, active=False):
                ctk.CTkButton(
                    pager,
                    text=str(text),
                    width=38,
                    height=32,
                    corner_radius=6,
                    fg_color="#E9F4E6" if active else "#F5F5F5",
                    hover_color="#E3EEE0",
                    text_color=colors["green"] if active else "#303942",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    command=lambda: go_page(target if target else int(text)),
                ).pack(side="left", padx=2)

            page_button("<", max(1, current_page["value"] - 1), False)
            for page_number in range(1, min(pages, 3) + 1):
                page_button(page_number, page_number, page_number == current_page["value"])
            page_button(">", min(pages, current_page["value"] + 1), False)

        def render():
            rows = filtered_rows()
            per_page = int(per_page_var.get())
            pages = max(1, (len(rows) + per_page - 1) // per_page)
            current_page["value"] = min(current_page["value"], pages)
            start_index = (current_page["value"] - 1) * per_page
            visible = rows[start_index:start_index + per_page]

            for widget in body.winfo_children():
                widget.destroy()
            if not visible:
                ctk.CTkLabel(body, text="Nenhum cliente encontrado.", height=120, font=ctk.CTkFont(size=14, weight="bold"), text_color=colors["muted"]).pack(fill="x")
            for row in visible:
                table_row(body, row)

            total = len(rows)
            start = start_index + 1 if total else 0
            end = min(start_index + per_page, total)
            render_pager(total, start, end, pages)

        def reset_and_render(*_args):
            current_page["value"] = 1
            render()

        def go_page(page_number):
            current_page["value"] = page_number
            render()

        def form_entry(master, placeholder):
            return ctk.CTkEntry(master, height=38, corner_radius=8, border_color=colors["line"], placeholder_text=placeholder)

        def open_editor(row=None):
            self.clear_main()
            self.main_container = ctk.CTkFrame(self, fg_color=colors["bg"], corner_radius=0)
            self.main_container.pack(fill="both", expand=True)
            self.main_container.grid_rowconfigure(1, weight=1)
            self.main_container.grid_columnconfigure(0, weight=1)
            self.build_header()
            self.build_footer()

            form_tipo = ctk.StringVar(value=row_tipo(row) if row is not None else "Comprador")
            estados = ["Selecione um estado", "SP", "MG", "RJ", "PR", "SC", "RS", "MS", "GO", "MT", "BA", "ES"]
            initial_estado = row["estado"] if row is not None and "estado" in row.keys() and row["estado"] else row_estado(row) if row is not None else estados[0]
            estado_var = ctk.StringVar(value=initial_estado if initial_estado in estados else estados[0])

            page_form = ctk.CTkFrame(self.main_container, fg_color=colors["bg"], corner_radius=0)
            page_form.grid(row=1, column=0, sticky="nsew", padx=26, pady=(4, 0))
            page_form.grid_columnconfigure(0, weight=1)
            page_form.grid_rowconfigure(2, weight=1)

            heading_form = ctk.CTkFrame(page_form, fg_color="transparent", height=84)
            heading_form.grid(row=0, column=0, sticky="ew")
            heading_form.grid_propagate(False)
            ctk.CTkButton(
                heading_form,
                text="<  Voltar",
                width=112,
                height=44,
                corner_radius=8,
                fg_color="#EEF0EF",
                hover_color="#E1E5E2",
                text_color=colors["text"],
                font=ctk.CTkFont(size=14, weight="bold"),
                command=self.tela_clientes,
            ).pack(side="left", padx=(0, 24), pady=(20, 0))
            heading_text = ctk.CTkFrame(heading_form, fg_color="transparent")
            heading_text.pack(side="left", fill="x", expand=True, pady=(16, 0))
            ctk.CTkLabel(heading_text, text="Cadastrar Cliente" if row is None else "Editar Cliente", font=ctk.CTkFont(size=22, weight="bold"), text_color=colors["text"]).pack(anchor="w")
            ctk.CTkLabel(heading_text, text="Preencha os dados do cliente para cadastrá-lo no sistema", font=ctk.CTkFont(size=12, weight="bold"), text_color="#545C65").pack(anchor="w", pady=(6, 0))
            type_tabs = ctk.CTkFrame(page_form, fg_color="transparent", height=40)
            type_tabs.grid(row=1, column=0, sticky="w", padx=(12, 0))
            type_tabs.grid_propagate(False)
            type_buttons = {}

            def set_tipo(value):
                form_tipo.set(value)
                for key, button in type_buttons.items():
                    active = key == value
                    button.configure(
                        fg_color="#EAF2E6" if active else "#F7F7F7",
                        text_color="#193B22" if active else "#4A4F55",
                        border_color="#DDE7DB" if active else colors["line"],
                    )

            for value in ["Comprador", "Vendedor"]:
                button = ctk.CTkButton(
                    type_tabs,
                    text=value,
                    width=168,
                    height=40,
                    corner_radius=8,
                    fg_color="#F7F7F7",
                    hover_color="#EAF2E6",
                    text_color="#4A4F55",
                    border_width=1,
                    border_color=colors["line"],
                    font=ctk.CTkFont(size=14, weight="bold"),
                    command=lambda selected=value: set_tipo(selected),
                )
                button.pack(side="left")
                type_buttons[value] = button
            set_tipo(form_tipo.get())

            card = ctk.CTkFrame(page_form, fg_color="white", corner_radius=12, border_width=1, border_color=colors["line"])
            card.grid(row=2, column=0, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)
            card.grid_rowconfigure(1, weight=1)

            inner_tabs = ctk.CTkFrame(card, fg_color="transparent", height=54)
            inner_tabs.grid(row=0, column=0, sticky="ew")
            inner_tabs.grid_propagate(False)
            for index, label in enumerate(["Dados do Cliente", "Endereço", "Ações"]):
                width = 220 if index == 0 else 140
                ctk.CTkLabel(
                    inner_tabs,
                    text=label,
                    width=width,
                    height=54,
                    anchor="w",
                    font=ctk.CTkFont(size=15 if index == 0 else 14, weight="bold" if index == 0 else "normal"),
                    text_color=colors["text"] if index == 0 else "#666D75",
                    fg_color="white",
                ).pack(side="left", padx=(22 if index == 0 else 0, 0))
            ctk.CTkFrame(card, height=1, fg_color=colors["line"]).grid(row=0, column=0, sticky="sew")

            form = ctk.CTkFrame(card, fg_color="transparent")
            form.grid(row=1, column=0, sticky="nsew", padx=28, pady=(12, 0))
            for index, weight in enumerate([3, 3, 3, 3, 0]):
                form.grid_columnconfigure(index, weight=weight, minsize=54 if index == 4 else 0)

            def labeled_entry(label, row_index, column, columnspan=1, required=False, placeholder=""):
                caption = f"{label} *" if required else label
                ctk.CTkLabel(form, text=caption, font=ctk.CTkFont(size=12, weight="bold"), text_color=colors["text"]).grid(row=row_index * 2, column=column, columnspan=columnspan, sticky="w", padx=4, pady=(0, 4))
                entry = ctk.CTkEntry(form, height=38, corner_radius=7, border_color=colors["line"], fg_color="white", placeholder_text=placeholder)
                entry.grid(row=row_index * 2 + 1, column=column, columnspan=columnspan, sticky="ew", padx=4, pady=(0, 10))
                return entry

            nome = labeled_entry("Nome / Empresa", 0, 0, required=True, placeholder="Clara Souza")
            documento = labeled_entry("CPF / CNPJ", 0, 1, placeholder="00.000.000/0000-00")
            email = labeled_entry("E-mail", 0, 2, placeholder="")
            telefone = labeled_entry("Telefone", 0, 3, placeholder="(19) 99999-9999")
            ctk.CTkButton(form, text="O", width=38, height=38, corner_radius=7, fg_color="#FAFAFA", hover_color="#ECECEC", text_color="#303942").grid(row=1, column=4, padx=(8, 0), pady=(0, 10))

            ctk.CTkLabel(form, text="Estado", font=ctk.CTkFont(size=12, weight="bold"), text_color=colors["text"]).grid(row=2, column=0, sticky="w", padx=4, pady=(0, 4))
            estado = ctk.CTkOptionMenu(form, values=estados, variable=estado_var, height=38, corner_radius=7, fg_color="white", button_color="white", button_hover_color="#EEF0EF", text_color="#4B5563")
            estado.grid(row=3, column=0, sticky="ew", padx=4, pady=(0, 10))
            cidade = labeled_entry("Cidade", 1, 1, placeholder="")
            endereco = labeled_entry("Cidade", 1, 2, columnspan=2, placeholder="")
            ctk.CTkButton(form, text="O", width=38, height=38, corner_radius=7, fg_color="#FAFAFA", hover_color="#ECECEC", text_color="#303942").grid(row=3, column=4, padx=(8, 0), pady=(0, 10))

            observacao = labeled_entry("Observação (opcional)", 2, 0, columnspan=5, placeholder="")

            required = ctk.CTkFrame(card, fg_color="transparent", height=28)
            required.grid(row=2, column=0, sticky="ew", padx=28)
            required.grid_propagate(False)
            ctk.CTkLabel(required, text="* Campo obrigatório", font=ctk.CTkFont(size=13, weight="bold"), text_color="#545C65").pack(side="left")

            footer_actions = ctk.CTkFrame(card, fg_color="transparent", height=56)
            footer_actions.grid(row=3, column=0, sticky="ew", padx=28, pady=(0, 8))
            footer_actions.grid_propagate(False)

            if row is not None:
                nome.insert(0, row["nome"] or "")
                telefone.insert(0, row["telefone"] or "")
                documento.insert(0, row["cnpj"] or "")
                email.insert(0, row["email"] if "email" in row.keys() and row["email"] else "")
                cidade.insert(0, row["cidade"] or "")
                endereco.insert(0, row["endereco"] if "endereco" in row.keys() and row["endereco"] else "")
                observacao.insert(0, row["observacao"] or "")

            def save():
                if not nome.get().strip():
                    messagebox.showwarning("Nome obrigatório", "Informe o nome do cliente.")
                    return
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        if row is not None:
                            conn.execute(
                                "UPDATE clientes SET nome=?, telefone=?, cnpj=?, cidade=?, observacao=?, tipo=?, email=?, estado=?, endereco=? WHERE id=?",
                                (nome.get().strip(), telefone.get().strip(), documento.get().strip(), cidade.get().strip(), observacao.get().strip(), form_tipo.get(), email.get().strip(), "" if estado_var.get() == estados[0] else estado_var.get(), endereco.get().strip(), row["id"])
                            )
                        else:
                            conn.execute(
                                "INSERT INTO clientes (nome, telefone, cnpj, cidade, observacao, tipo, email, estado, endereco) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (nome.get().strip(), telefone.get().strip(), documento.get().strip(), cidade.get().strip(), observacao.get().strip(), form_tipo.get(), email.get().strip(), "" if estado_var.get() == estados[0] else estado_var.get(), endereco.get().strip())
                            )
                except sqlite3.IntegrityError:
                    messagebox.showerror("Cliente duplicado", "Ja existe um cliente com esse nome.")
                    return
                self.log_notification(
                    "cliente",
                    "Cliente atualizado" if row is not None else "Novo cliente cadastrado",
                    f"{nome.get().strip()} foi {'atualizado' if row is not None else 'cadastrado'} com sucesso.",
                )
                self.tela_clientes()

            ctk.CTkButton(footer_actions, text="Cadastrar Cliente" if row is None else "Salvar Cliente", width=220, height=42, corner_radius=6, fg_color=colors["green"], hover_color=colors["green_hover"], font=ctk.CTkFont(size=14, weight="bold"), command=save).pack(side="right", pady=7)
            ctk.CTkButton(footer_actions, text="Cancelar", width=150, height=42, corner_radius=6, fg_color="#EFEFEF", hover_color="#E2E2E2", text_color=colors["text"], font=ctk.CTkFont(size=14, weight="bold"), command=self.tela_clientes).pack(side="right", padx=(0, 14), pady=7)

            visual_pager = ctk.CTkFrame(page_form, fg_color="white", height=40, corner_radius=0)
            visual_pager.grid(row=3, column=0, sticky="ew")
            visual_pager.grid_propagate(False)
            total = len(self.get_clientes())
            ctk.CTkLabel(visual_pager, text=f"1 a 10 de {total} registros  v", font=ctk.CTkFont(size=13), text_color="#4B5563").pack(side="left", padx=(18, 0))
            ctk.CTkLabel(visual_pager, text="Mostrando", font=ctk.CTkFont(size=13), text_color="#4B5563").pack(side="left", padx=(620, 10))
            ctk.CTkOptionMenu(visual_pager, values=["10", "25", "50"], variable=per_page_var, width=86, height=30, corner_radius=6, fg_color="#F8F8F8", button_color="#F8F8F8", text_color=colors["text"]).pack(side="left", padx=(0, 12))
            for text in ["<", "1", "2", "3", ">"]:
                ctk.CTkButton(visual_pager, text=text, width=34, height=30, corner_radius=6, fg_color="#E9F4E6" if text == "<" else "#F5F5F5", hover_color="#E3EEE0", text_color=colors["green"] if text == "<" else colors["text"]).pack(side="left", padx=3)

            self.after(100, lambda widget=nome: widget.focus_set() if widget.winfo_exists() else None)

        for var in (tipo_var, estado_var, busca_var):
            var.trace_add("write", reset_and_render)
        render()

    def tela_cliente_historico(self, cliente_row):
        colors = self.modelo_colors()
        cliente_nome = cliente_row["nome"] if "nome" in cliente_row.keys() else cliente_row.get("nome", "")
        cliente_id = cliente_row["id"] if "id" in cliente_row.keys() else cliente_row.get("id")

        page = self.modelo_page(
            f"Historico de {cliente_nome}",
            "Todas as compras e vendas registradas para este cliente",
            back_command=self.tela_clientes,
        )
        page.grid_rowconfigure(1, weight=0)
        page.grid_rowconfigure(2, weight=0)
        page.grid_rowconfigure(3, weight=1)
        page.grid_rowconfigure(4, weight=0)
        tipo_var = ctk.StringVar(value="TODAS")
        busca_var = ctk.StringVar(value="")
        per_page_var = ctk.StringVar(value="10")
        page_state = {"current": 1}

        summary = ctk.CTkFrame(page, fg_color="transparent", height=94)
        summary.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        summary.grid_propagate(False)
        for index in range(4):
            summary.grid_columnconfigure(index, weight=1)

        summary_refs = {}
        summary_cards = [
            ("Operacoes", "operacoes", "#EEF4FB", colors["text"]),
            ("Compras", "compras", "#EEF8EA", colors["text"]),
            ("Vendas", "vendas", "#FBF4E7", colors["text"]),
            ("Total Movimentado", "total", "#E8F7E2", colors["green"]),
        ]
        for index, (label, key, bg_color, value_color) in enumerate(summary_cards):
            box = ctk.CTkFrame(summary, fg_color=bg_color, corner_radius=10, border_width=1, border_color=colors["line"])
            box.grid(row=0, column=index, sticky="nsew", padx=5, pady=5)
            ctk.CTkLabel(box, text=label, font=ctk.CTkFont(size=12, weight="bold"), text_color=colors["muted"]).pack(anchor="w", padx=14, pady=(12, 2))
            summary_refs[key] = ctk.CTkLabel(box, text="0", font=ctk.CTkFont(size=18, weight="bold"), text_color=value_color)
            summary_refs[key].pack(anchor="w", padx=14, pady=(0, 12))

        controls = ctk.CTkFrame(page, fg_color="transparent", height=50)
        controls.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        controls.grid_propagate(False)
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkOptionMenu(
            controls,
            values=["TODAS", "COMPRA", "VENDA"],
            variable=tipo_var,
            width=180,
            height=40,
            corner_radius=7,
            fg_color="white",
            button_color="white",
            button_hover_color="#EEF0EF",
            text_color=colors["text"],
        ).grid(row=0, column=0, padx=(0, 10), pady=5)
        self.modelo_entry(controls, "Buscar observacao ou tipo...", busca_var).grid(row=0, column=1, sticky="ew", pady=5)

        body, configure_columns = self.modelo_table(page, ["Operacao", "Data", "Observacao", "Total", ""], [24, 18, 36, 14, 8], row=3)

        def details(transacao_id):
            self.tela_detalhes_transacao(
                transacao_id,
                back_command=lambda current=cliente_row: self.tela_cliente_historico(current),
            )

        def filtered_rows():
            term = f"%{busca_var.get().strip()}%"
            tipo_filter = tipo_var.get()
            return self.db_fetchall(
                """
                SELECT *
                FROM transacoes
                WHERE (cliente_id = ? OR cliente_nome = ?)
                  AND (?='TODAS' OR tipo=?)
                  AND (
                        cliente_nome LIKE ?
                     OR observacao LIKE ?
                     OR tipo LIKE ?
                     OR destino_compra LIKE ?
                  )
                ORDER BY data DESC, id DESC
                """,
                (cliente_id, cliente_nome, tipo_filter, tipo_filter, term, term, term, term),
            )

        def set_page(new_page):
            rows = filtered_rows()
            per_page = max(1, int(per_page_var.get()))
            total_pages = max(1, (len(rows) + per_page - 1) // per_page)
            page_state["current"] = max(1, min(new_page, total_pages))
            render()

        def reset_and_render(*_args):
            page_state["current"] = 1
            render()

        def render(*_args):
            for widget in body.winfo_children():
                widget.destroy()

            rows = filtered_rows()
            compras_total = sum(float(row["total"] or 0) for row in rows if row["tipo"] == "COMPRA")
            vendas_total = sum(float(row["total"] or 0) for row in rows if row["tipo"] == "VENDA")
            summary_refs["operacoes"].configure(text=str(len(rows)))
            summary_refs["compras"].configure(text=self.format_money(compras_total))
            summary_refs["vendas"].configure(text=self.format_money(vendas_total))
            summary_refs["total"].configure(text=self.format_money(compras_total + vendas_total))

            per_page = max(1, int(per_page_var.get()))
            total_pages = max(1, (len(rows) + per_page - 1) // per_page)
            page_state["current"] = max(1, min(page_state["current"], total_pages))
            start = (page_state["current"] - 1) * per_page
            end = start + per_page

            if not rows:
                self.modelo_empty(body, "Nenhuma operacao encontrada para este cliente.")

            for row in rows[start:end]:
                observacao = (row["observacao"] or "").strip() or "-"
                if len(observacao) > 56:
                    observacao = f"{observacao[:53]}..."
                self.modelo_row(
                    body,
                    configure_columns,
                    [self.transacao_label(row), row["data"][:16], observacao, self.format_money(row["total"]), ""],
                    actions=[("Itens", "#4B5563", lambda rid=row["id"]: details(rid))],
                    highlight_index=3,
                )

            self.modelo_pager(
                page,
                len(rows),
                row=4,
                current_page=page_state["current"],
                per_page=per_page,
                on_page_change=set_page,
                per_page_var=per_page_var,
                on_per_page_change=lambda _value: reset_and_render(),
            )

        for var in (tipo_var, busca_var):
            var.trace_add("write", reset_and_render)
        render()

    def modelo_colors(self):
        return {
            "bg": "#F7F8F6",
            "line": "#E5E7EB",
            "text": "#17202A",
            "muted": "#66707A",
            "green": "#0E7A24",
            "green_hover": "#0A631D",
            "danger": "#C94040",
        }

    def modelo_page(self, title, subtitle, back_command=None):
        colors = self.modelo_colors()
        self.clear_main()
        self.main_container = ctk.CTkFrame(self, fg_color=colors["bg"], corner_radius=0)
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.build_header()
        self.build_footer()

        page = ctk.CTkFrame(self.main_container, fg_color=colors["bg"], corner_radius=0)
        page.grid(row=1, column=0, sticky="nsew", padx=26, pady=(6, 0))
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(2, weight=1)

        heading = ctk.CTkFrame(page, fg_color="transparent", height=72)
        heading.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        heading.grid_propagate(False)
        ctk.CTkButton(heading, text="<  Voltar", width=112, height=44, corner_radius=8, fg_color="#EEF0EF", hover_color="#E1E5E2", text_color=colors["text"], font=ctk.CTkFont(size=14, weight="bold"), command=back_command or self.build_ui).pack(side="left", padx=(0, 24), pady=14)
        title_box = ctk.CTkFrame(heading, fg_color="transparent")
        title_box.pack(side="left", fill="x", expand=True, pady=10)
        ctk.CTkLabel(title_box, text=title, font=ctk.CTkFont(size=24, weight="bold"), text_color=colors["text"]).pack(anchor="w")
        ctk.CTkLabel(title_box, text=subtitle, font=ctk.CTkFont(size=12, weight="bold"), text_color="#545C65").pack(anchor="w", pady=(4, 0))
        return page

    def modelo_entry(self, master, placeholder="", textvariable=None):
        colors = self.modelo_colors()
        return ctk.CTkEntry(master, height=40, corner_radius=7, border_color=colors["line"], fg_color="white", placeholder_text=placeholder, textvariable=textvariable)

    def modelo_table(self, page, headers, weights, row=2):
        colors = self.modelo_colors()
        table = ctk.CTkFrame(page, fg_color="white", corner_radius=0, border_width=1, border_color=colors["line"])
        table.grid(row=row, column=0, sticky="nsew")
        table.grid_columnconfigure(0, weight=1)
        table.grid_rowconfigure(1, weight=1)
        header = ctk.CTkFrame(table, fg_color="#FBFBFB", height=40, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        def configure_columns(frame):
            for index, weight in enumerate(weights):
                frame.grid_columnconfigure(index, weight=weight, uniform="model_table")

        configure_columns(header)
        for index, text in enumerate(headers):
            ctk.CTkLabel(header, text=text, anchor="w" if index < len(headers) - 1 else "center", font=ctk.CTkFont(size=12, weight="bold"), text_color="#2E3338").grid(row=0, column=index, sticky="nsew", padx=14 if index == 0 else 8)
        body = ctk.CTkScrollableFrame(table, fg_color="white", corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew")
        return body, configure_columns

    def modelo_row(self, parent, configure_columns, values, actions=None, highlight_index=None):
        colors = self.modelo_colors()
        line = ctk.CTkFrame(parent, fg_color="white", height=42, corner_radius=0)
        line.pack(fill="x")
        line.grid_propagate(False)
        configure_columns(line)
        last_value_index = len(values) - 1
        for index, value in enumerate(values):
            ctk.CTkLabel(line, text=value, anchor="w" if index < last_value_index else "center", font=ctk.CTkFont(size=12, weight="bold" if index == 0 or index == highlight_index else "normal"), text_color=colors["green"] if index == highlight_index else "#2E3338").grid(row=0, column=index, sticky="nsew", padx=14 if index == 0 else 8)
        if actions:
            action_frame = ctk.CTkFrame(line, fg_color="transparent")
            action_frame.grid(row=0, column=last_value_index, sticky="e", padx=(0, 10))
            for label, color, callback in actions:
                ctk.CTkButton(action_frame, text=label, width=58, height=30, corner_radius=6, fg_color=color, hover_color=color, text_color="white", font=ctk.CTkFont(size=11, weight="bold"), command=callback).pack(side="left", padx=3)

    def modelo_empty(self, parent, text):
        colors = self.modelo_colors()
        ctk.CTkLabel(parent, text=text, height=120, font=ctk.CTkFont(size=14, weight="bold"), text_color=colors["muted"]).pack(fill="x")

    def modelo_pager(self, page, total, row=3, current_page=1, per_page=10, on_page_change=None, per_page_var=None, on_per_page_change=None):
        colors = self.modelo_colors()
        pager_attr = f"_modelo_pager_row_{row}"
        existing = getattr(page, pager_attr, None)
        if existing is not None and existing.winfo_exists():
            existing.destroy()

        total_pages = max(1, (total + per_page - 1) // per_page) if per_page > 0 else 1
        current_page = max(1, min(current_page, total_pages))
        start = 0 if total == 0 else (current_page - 1) * per_page + 1
        end = min(current_page * per_page, total) if total else 0

        pager = ctk.CTkFrame(page, fg_color="white", height=40, corner_radius=0)
        setattr(page, pager_attr, pager)
        pager.grid(row=row, column=0, sticky="ew")
        pager.grid_propagate(False)
        pager.grid_columnconfigure(0, weight=1)
        pager.grid_columnconfigure(1, weight=1)

        left = ctk.CTkFrame(pager, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", padx=(18, 0))
        right = ctk.CTkFrame(pager, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e", padx=(0, 18))

        ctk.CTkLabel(left, text=f"{start} a {end} de {total} registros", font=ctk.CTkFont(size=13), text_color="#4B5563").pack(side="left")
        ctk.CTkLabel(right, text="Mostrando", font=ctk.CTkFont(size=13), text_color="#4B5563").pack(side="left", padx=(0, 10))

        local_per_page_var = per_page_var or ctk.StringVar(value=str(per_page))
        def handle_per_page_change(value):
            local_per_page_var.set(str(value))
            if on_per_page_change:
                on_per_page_change(int(value))

        ctk.CTkOptionMenu(
            right,
            values=["10", "20", "50"],
            variable=local_per_page_var,
            width=86,
            height=30,
            corner_radius=6,
            fg_color="#F8F8F8",
            button_color="#F8F8F8",
            text_color=colors["text"],
            command=handle_per_page_change,
        ).pack(side="left", padx=(0, 12))

        def visible_pages():
            if total_pages <= 5:
                return list(range(1, total_pages + 1))
            pages = {1, total_pages, current_page - 1, current_page, current_page + 1}
            ordered = sorted(page_no for page_no in pages if 1 <= page_no <= total_pages)
            items = []
            previous = None
            for page_no in ordered:
                if previous is not None and page_no - previous > 1:
                    items.append("...")
                items.append(page_no)
                previous = page_no
            return items

        def nav_button(text, target_page, active=False):
            enabled = on_page_change is not None and 1 <= target_page <= total_pages and target_page != current_page
            fg_color = "#E9F4E6" if active else "#F5F5F5"
            text_color = colors["green"] if active else colors["text"]
            ctk.CTkButton(
                right,
                text=text,
                width=34,
                height=30,
                corner_radius=6,
                fg_color=fg_color,
                hover_color="#E3EEE0" if enabled else fg_color,
                text_color=text_color,
                state="normal" if enabled else "disabled",
                command=(lambda: on_page_change(target_page)) if enabled else None,
            ).pack(side="left", padx=3)

        nav_button("<", current_page - 1)
        for item in visible_pages():
            if item == "...":
                ctk.CTkLabel(right, text="...", font=ctk.CTkFont(size=13, weight="bold"), text_color="#6B7280").pack(side="left", padx=4)
            else:
                nav_button(str(item), item, active=item == current_page)
        nav_button(">", current_page + 1)

    def tela_materiais(self):
        colors = self.modelo_colors()
        page = self.modelo_page("Materiais", "Materiais mais comprados primeiro")
        status_var = ctk.StringVar(value="Todos status")
        busca_var = ctk.StringVar(value="")
        per_page_var = ctk.StringVar(value="10")
        page_state = {"current": 1}
        controls = ctk.CTkFrame(page, fg_color="transparent", height=50)
        controls.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        controls.grid_propagate(False)
        controls.grid_columnconfigure(1, weight=1)
        ctk.CTkOptionMenu(controls, values=["Todos status", "Ativo", "Inativo"], variable=status_var, width=180, height=40, corner_radius=7, fg_color="white", button_color="white", button_hover_color="#EEF0EF", text_color=colors["text"]).grid(row=0, column=0, padx=(0, 10), pady=5)
        self.modelo_entry(controls, "Buscar material, descrição...", busca_var).grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=5)
        ctk.CTkButton(controls, text="+  Cadastrar Material", width=210, height=40, corner_radius=7, fg_color=colors["green"], hover_color=colors["green_hover"], font=ctk.CTkFont(size=14, weight="bold"), command=lambda: open_editor()).grid(row=0, column=2, pady=5)
        body, configure_columns = self.modelo_table(page, ["Material", "Comprado", "Compra", "Venda", "Mínimo", "Status", ""], [22, 14, 12, 12, 12, 12, 16])

        def material_status(row):
            return "Ativo" if ("ativo" not in row.keys() or row["ativo"]) else "Inativo"

        def filtered():
            query = busca_var.get().strip().lower()
            rows = []
            for row in self.get_materiais_mais_comprados():
                descricao = row["descricao"] if "descricao" in row.keys() else ""
                status = material_status(row)
                if status_var.get() != "Todos status" and status != status_var.get():
                    continue
                if query and query not in f"{row['nome']} {descricao} {status}".lower():
                    continue
                rows.append(row)
            return rows

        def delete(row):
            if messagebox.askyesno("Excluir material", f"Deseja excluir ou inativar {row['nome']}?"):
                try:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("DELETE FROM materiais WHERE id=?", (row["id"],))
                except sqlite3.IntegrityError:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("UPDATE materiais SET ativo=0 WHERE id=?", (row["id"],))
                render()

        def set_page(new_page):
            rows = filtered()
            per_page = max(1, int(per_page_var.get()))
            total_pages = max(1, (len(rows) + per_page - 1) // per_page)
            page_state["current"] = max(1, min(new_page, total_pages))
            render()

        def reset_and_render(*_args):
            page_state["current"] = 1
            render()

        def render(*_args):
            for widget in body.winfo_children():
                widget.destroy()
            rows = filtered()
            per_page = max(1, int(per_page_var.get()))
            total_pages = max(1, (len(rows) + per_page - 1) // per_page)
            page_state["current"] = max(1, min(page_state["current"], total_pages))
            start = (page_state["current"] - 1) * per_page
            end = start + per_page
            if not rows:
                self.modelo_empty(body, "Nenhum material encontrado.")
            for row in rows[start:end]:
                minimo = row["estoque_minimo"] if "estoque_minimo" in row.keys() else 0
                comprado = row["total_comprado"] if "total_comprado" in row.keys() else 0
                self.modelo_row(body, configure_columns, [row["nome"], self.format_kg(comprado), self.format_money(row["preco_compra"]), self.format_money(row["preco_venda"]), self.format_kg(minimo), material_status(row), ""], actions=[("Editar", "#4B5563", lambda r=row: open_editor(r)), ("Excluir", colors["danger"], lambda r=row: delete(r))], highlight_index=1)
            self.modelo_pager(
                page,
                len(rows),
                current_page=page_state["current"],
                per_page=per_page,
                on_page_change=set_page,
                per_page_var=per_page_var,
                on_per_page_change=lambda _value: reset_and_render(),
            )

        def open_editor(row=None):
            editor = self.modelo_page("Cadastrar Material" if row is None else "Editar Material", "Preencha os dados do material")
            tabs = ctk.CTkFrame(editor, fg_color="transparent", height=40)
            tabs.grid(row=1, column=0, sticky="w", padx=(12, 0))
            ctk.CTkLabel(tabs, text="Dados do Material", width=220, height=40, fg_color="#EAF2E6", corner_radius=8, font=ctk.CTkFont(size=14, weight="bold"), text_color="#193B22").pack(side="left")
            card = ctk.CTkFrame(editor, fg_color="white", corner_radius=12, border_width=1, border_color=colors["line"])
            card.grid(row=2, column=0, sticky="nsew")
            for idx in range(5):
                card.grid_columnconfigure(idx, weight=1)

            def label(text, r, c):
                ctk.CTkLabel(card, text=text, font=ctk.CTkFont(size=12, weight="bold"), text_color=colors["text"]).grid(row=r, column=c, sticky="w", padx=22, pady=(18 if r == 0 else 8, 4))

            labels = ["Material *", "Descrição", "Preço compra", "Preço venda", "Estoque mínimo"]
            for idx, text in enumerate(labels):
                label(text, 0, idx)
            nome = self.modelo_entry(card, "Cobre")
            desc = self.modelo_entry(card, "Cobre limpo")
            compra = self.modelo_entry(card, "0,00")
            venda = self.modelo_entry(card, "0,00")
            minimo = self.modelo_entry(card, "0,00")
            for index, widget in enumerate([nome, desc, compra, venda, minimo]):
                widget.grid(row=1, column=index, sticky="ew", padx=18 if index in (0, 4) else 6, pady=(0, 16))
            ativo = ctk.StringVar(value="Ativo")
            ctk.CTkOptionMenu(card, values=["Ativo", "Inativo"], variable=ativo, height=40, fg_color="white", button_color="white", text_color=colors["text"]).grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 16))
            if row:
                nome.insert(0, row["nome"])
                desc.insert(0, row["descricao"] if "descricao" in row.keys() and row["descricao"] else "")
                compra.insert(0, f"{row['preco_compra']:.2f}".replace(".", ","))
                venda.insert(0, f"{row['preco_venda']:.2f}".replace(".", ","))
                minimo.insert(0, f"{row['estoque_minimo'] if 'estoque_minimo' in row.keys() else 0:.2f}".replace(".", ","))
                ativo.set(material_status(row))

            actions = ctk.CTkFrame(card, fg_color="transparent", height=54)
            actions.grid(row=3, column=0, columnspan=5, sticky="ew", padx=18, pady=(2, 14))
            actions.grid_propagate(False)

            def save():
                if not nome.get().strip():
                    messagebox.showwarning("Nome obrigatório", "Informe o material.")
                    return
                try:
                    values = (nome.get().strip(), desc.get().strip(), self.parse_decimal(compra.get()), self.parse_decimal(venda.get()), self.parse_decimal(minimo.get()), 1 if ativo.get() == "Ativo" else 0)
                    with sqlite3.connect(self.db_path) as conn:
                        if row:
                            conn.execute("UPDATE materiais SET nome=?, descricao=?, preco_compra=?, preco_venda=?, estoque_minimo=?, ativo=? WHERE id=?", (*values, row["id"]))
                        else:
                            conn.execute("INSERT INTO materiais (nome, descricao, preco_compra, preco_venda, estoque_minimo, ativo) VALUES (?, ?, ?, ?, ?, ?)", values)
                except ValueError:
                    messagebox.showerror("Valor inválido", "Confira preços e estoque mínimo.")
                    return
                except sqlite3.IntegrityError:
                    messagebox.showerror("Duplicado", "Já existe material com esse nome.")
                    return
                self.log_notification(
                    "material",
                    "Material atualizado" if row else "Novo material cadastrado",
                    f"{nome.get().strip()} foi {'atualizado' if row else 'cadastrado'} com sucesso.",
                )
                self.tela_materiais()

            ctk.CTkButton(actions, text="Salvar Material", width=220, height=42, corner_radius=6, fg_color=colors["green"], hover_color=colors["green_hover"], font=ctk.CTkFont(size=14, weight="bold"), command=save).pack(side="right", pady=6)
            ctk.CTkButton(actions, text="Cancelar", width=150, height=42, corner_radius=6, fg_color="#EFEFEF", hover_color="#E2E2E2", text_color=colors["text"], font=ctk.CTkFont(size=14, weight="bold"), command=self.tela_materiais).pack(side="right", padx=(0, 14), pady=6)
            self.modelo_pager(editor, len(self.get_materiais()))

        for var in (status_var, busca_var):
            var.trace_add("write", reset_and_render)
        render()

    def tela_historico(self):
        page = self.modelo_page("Histórico", "Consulte compras, vendas e itens registrados")
        tipo_var = ctk.StringVar(value="TODAS")
        busca_var = ctk.StringVar(value="")
        per_page_var = ctk.StringVar(value="10")
        page_state = {"current": 1}
        controls = ctk.CTkFrame(page, fg_color="transparent", height=50)
        controls.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        controls.grid_propagate(False)
        controls.grid_columnconfigure(1, weight=1)
        colors = self.modelo_colors()
        ctk.CTkOptionMenu(controls, values=["TODAS", "COMPRA", "VENDA"], variable=tipo_var, width=180, height=40, corner_radius=7, fg_color="white", button_color="white", text_color=colors["text"]).grid(row=0, column=0, padx=(0, 10), pady=5)
        self.modelo_entry(controls, "Buscar cliente ou observação...", busca_var).grid(row=0, column=1, sticky="ew", pady=5)
        body, configure_columns = self.modelo_table(page, ["Operação", "Cliente", "Data", "Pagamento", "Total", "Status", ""], [14, 24, 16, 12, 12, 12, 10])

        def details(transacao_id):
            itens = self.db_fetchall("SELECT * FROM transacao_itens WHERE transacao_id=?", (transacao_id,))
            text = "\n".join(f"{item['material_nome']} - {self.format_kg(item['peso_liquido'])} - {self.format_money(item['subtotal'])}" for item in itens)
            messagebox.showinfo("Itens da operação", text or "Sem itens.")

        def render(*_args):
            for widget in body.winfo_children():
                widget.destroy()
            term = f"%{busca_var.get().strip()}%"
            tipo_filter = tipo_var.get()
            rows = self.db_fetchall(
                """
                SELECT * FROM transacoes
                WHERE (?='TODAS' OR tipo=?)
                  AND (cliente_nome LIKE ? OR observacao LIKE ?)
                ORDER BY data DESC, id DESC
                """,
                (tipo_filter, tipo_filter, term, term)
            )
            if not rows:
                self.modelo_empty(body, "Nenhuma operação encontrada.")
            for row in rows[:10]:
                pagamento = row["pagamento"] if "pagamento" in row.keys() and row["pagamento"] else "-"
                status = row["status"] if "status" in row.keys() and row["status"] else "FINALIZADA"
                self.modelo_row(body, configure_columns, [f"{row['tipo'].title()} #{row['id']}", row["cliente_nome"], row["data"][:16], pagamento, self.format_money(row["total"]), status, ""], actions=[("Itens", "#4B5563", lambda rid=row["id"]: details(rid))], highlight_index=4)
            self.modelo_pager(page, len(rows))

        for var in (tipo_var, busca_var):
            var.trace_add("write", render)
        render()

    def tela_relatorios(self):
        page = self.modelo_page("Relatórios", "Indicadores financeiros e operacionais")
        total_compras = self.db_fetchone("SELECT COALESCE(SUM(total), 0) AS total FROM transacoes WHERE tipo='COMPRA'")["total"]
        total_vendas = self.db_fetchone("SELECT COALESCE(SUM(total), 0) AS total FROM transacoes WHERE tipo='VENDA'")["total"]
        peso_compras = self.db_fetchone("SELECT COALESCE(SUM(i.peso_liquido), 0) AS total FROM transacao_itens i JOIN transacoes t ON t.id=i.transacao_id WHERE t.tipo='COMPRA'")["total"]
        peso_vendas = self.db_fetchone("SELECT COALESCE(SUM(i.peso_liquido), 0) AS total FROM transacao_itens i JOIN transacoes t ON t.id=i.transacao_id WHERE t.tipo='VENDA'")["total"]
        top = ctk.CTkFrame(page, fg_color="transparent", height=92)
        top.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        top.grid_propagate(False)
        cards = [("Compras", self.format_money(total_compras), "#EEF8EA"), ("Vendas", self.format_money(total_vendas), "#EEF4FB"), ("Peso Comprado", self.format_kg(peso_compras), "#FBF4E7"), ("Peso Vendido", self.format_kg(peso_vendas), "#F5ECFA"), ("Resultado", self.format_money(total_vendas - total_compras), "#E8F7E2" if total_vendas >= total_compras else "#FCECED")]
        colors = self.modelo_colors()
        for index, (label, value, color) in enumerate(cards):
            top.grid_columnconfigure(index, weight=1)
            box = ctk.CTkFrame(top, fg_color=color, corner_radius=8, border_width=1, border_color=colors["line"])
            box.grid(row=0, column=index, sticky="nsew", padx=5, pady=5)
            ctk.CTkLabel(box, text=label, font=ctk.CTkFont(size=12, weight="bold"), text_color=colors["muted"]).pack(pady=(12, 4))
            ctk.CTkLabel(box, text=value, font=ctk.CTkFont(size=17, weight="bold"), text_color=colors["text"]).pack(pady=(0, 10))
        body, configure_columns = self.modelo_table(page, ["Operação", "Cliente", "Data", "Total", ""], [18, 30, 18, 14, 8])
        rows = self.db_fetchall("SELECT * FROM transacoes ORDER BY data DESC, id DESC")
        if not rows:
            self.modelo_empty(body, "Nenhuma operação registrada.")
        for row in rows[:10]:
            self.modelo_row(body, configure_columns, [f"{row['tipo'].title()} #{row['id']}", row["cliente_nome"], row["data"][:16], self.format_money(row["total"]), ""], highlight_index=3)
        self.modelo_pager(page, len(rows))

    def tela_estoque(self):
        page = self.modelo_page("Estoque", "Visualize saldo, entradas e saídas por material")
        body, configure_columns = self.modelo_table(page, ["Material", "Entradas", "Saídas", "Mínimo", "Saldo", "Status"], [28, 15, 15, 15, 15, 12], row=1)
        rows = self.db_fetchall("""
            SELECT
                m.nome,
                m.estoque_minimo,
                COALESCE(SUM(CASE WHEN t.tipo='COMPRA' THEN i.peso_liquido ELSE 0 END), 0) AS entradas,
                COALESCE(SUM(CASE WHEN t.tipo='VENDA' THEN i.peso_liquido ELSE 0 END), 0) AS saidas
            FROM materiais m
            LEFT JOIN transacao_itens i ON i.material_id = m.id
            LEFT JOIN transacoes t ON t.id = i.transacao_id
            WHERE m.ativo = 1
            GROUP BY m.id, m.nome, m.estoque_minimo
            ORDER BY m.nome
        """)
        if not rows:
            self.modelo_empty(body, "Nenhum material ativo cadastrado.")
        for row in rows[:10]:
            saldo = row["entradas"] - row["saidas"]
            baixo = saldo <= row["estoque_minimo"]
            self.modelo_row(body, configure_columns, [row["nome"], self.format_kg(row["entradas"]), self.format_kg(row["saidas"]), self.format_kg(row["estoque_minimo"]), self.format_kg(saldo), "Estoque baixo" if baixo else "OK"], highlight_index=4)
        self.modelo_pager(page, len(rows), row=2)

    def tela_sangrias(self):
        colors = self.modelo_colors()
        categorias = self.sangria_categories()
        page = self.modelo_page("Sangrias / Retiradas", "Registre saidas de caixa para gasolina, manutencao e outras despesas")
        page.grid_rowconfigure(3, weight=1)
        categoria_var = ctk.StringVar(value="Todas categorias")
        busca_var = ctk.StringVar(value="")
        per_page_var = ctk.StringVar(value="10")
        page_state = {"current": 1}

        resumo = ctk.CTkFrame(page, fg_color="transparent", height=92)
        resumo.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        resumo.grid_propagate(False)
        resumo_cards = {}
        for index, (titulo, cor) in enumerate([
            ("Hoje", "#FFF4E8"),
            ("Mes", "#EEF8EA"),
            ("Filtrado", "#EEF4FB"),
            ("Registros", "#F5ECFA"),
        ]):
            resumo.grid_columnconfigure(index, weight=1)
            box = ctk.CTkFrame(resumo, fg_color=cor, corner_radius=8, border_width=1, border_color=colors["line"])
            box.grid(row=0, column=index, sticky="nsew", padx=5, pady=5)
            ctk.CTkLabel(box, text=titulo, font=ctk.CTkFont(size=12, weight="bold"), text_color=colors["muted"]).pack(pady=(12, 4))
            label = ctk.CTkLabel(box, text="R$ 0,00", font=ctk.CTkFont(size=17, weight="bold"), text_color=colors["text"])
            label.pack(pady=(0, 10))
            resumo_cards[titulo] = label

        controls = ctk.CTkFrame(page, fg_color="transparent", height=50)
        controls.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        controls.grid_propagate(False)
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkOptionMenu(
            controls,
            values=["Todas categorias"] + categorias,
            variable=categoria_var,
            width=220,
            height=40,
            corner_radius=7,
            fg_color="white",
            button_color="white",
            button_hover_color="#EEF0EF",
            text_color=colors["text"],
        ).grid(row=0, column=0, padx=(0, 10), pady=5)
        self.modelo_entry(controls, "Buscar descricao, observacao ou usuario...", busca_var).grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=5)
        ctk.CTkButton(
            controls,
            text="+  Registrar Sangria",
            width=220,
            height=40,
            corner_radius=7,
            fg_color=colors["green"],
            hover_color=colors["green_hover"],
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: open_editor(),
        ).grid(row=0, column=2, pady=5)

        body, configure_columns = self.modelo_table(page, ["Data", "Categoria", "Descricao", "Valor", "Observacao", ""], [14, 18, 24, 12, 22, 10], row=3)

        def today_total():
            return self.db_fetchone(
                "SELECT COALESCE(SUM(valor), 0) AS total FROM sangrias WHERE date(data) = ?",
                (self.today_iso(),),
            )["total"]

        def month_total():
            return self.db_fetchone(
                "SELECT COALESCE(SUM(valor), 0) AS total FROM sangrias WHERE strftime('%Y-%m', data) = ?",
                (datetime.now().strftime("%Y-%m"),),
            )["total"]

        def filtered_rows():
            query = busca_var.get().strip().lower()
            rows = self.db_fetchall("SELECT * FROM sangrias ORDER BY data DESC, id DESC")
            resultado = []
            for row in rows:
                if categoria_var.get() != "Todas categorias" and row["categoria"] != categoria_var.get():
                    continue
                texto_busca = " ".join([
                    str(row["data"] or ""),
                    str(row["categoria"] or ""),
                    str(row["descricao"] or ""),
                    str(row["observacao"] or ""),
                    str(row["usuario"] or ""),
                ]).lower()
                if query and query not in texto_busca:
                    continue
                resultado.append(row)
            return resultado

        def delete(row):
            if not messagebox.askyesno("Excluir sangria", f"Deseja excluir a retirada '{row['descricao']}'?"):
                return
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM sangrias WHERE id=?", (row["id"],))
            render()

        def set_page(new_page):
            rows = filtered_rows()
            per_page = max(1, int(per_page_var.get()))
            total_pages = max(1, (len(rows) + per_page - 1) // per_page)
            page_state["current"] = max(1, min(new_page, total_pages))
            render()

        def reset_and_render(*_args):
            page_state["current"] = 1
            render()

        def open_editor(row=None):
            editor = self.modelo_page("Registrar Sangria" if row is None else "Editar Sangria", "Informe o valor retirado e o motivo")
            card = ctk.CTkFrame(editor, fg_color="white", corner_radius=12, border_width=1, border_color=colors["line"])
            card.grid(row=1, column=0, sticky="nsew")
            for index in range(4):
                card.grid_columnconfigure(index, weight=1)

            def label(text, row_index, column, pady_top=18):
                ctk.CTkLabel(
                    card,
                    text=text,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=colors["text"],
                ).grid(row=row_index, column=column, sticky="w", padx=18, pady=(pady_top, 4))

            label("Data *", 0, 0)
            label("Categoria *", 0, 1)
            label("Valor *", 0, 2)
            label("Usuario", 0, 3)
            data_entry = self.modelo_entry(card, "dd/mm/aaaa")
            categoria_editor_var = ctk.StringVar(value=row["categoria"] if row else categorias[0])
            categoria_menu = ctk.CTkOptionMenu(
                card,
                values=categorias,
                variable=categoria_editor_var,
                height=40,
                corner_radius=7,
                fg_color="white",
                button_color="white",
                button_hover_color="#EEF0EF",
                text_color=colors["text"],
            )
            valor_entry = self.modelo_entry(card, "0,00")
            usuario_entry = self.modelo_entry(card, "Responsavel")
            for index, widget in enumerate([data_entry, categoria_menu, valor_entry, usuario_entry]):
                widget.grid(row=1, column=index, sticky="ew", padx=18 if index in (0, 3) else 6, pady=(0, 14))

            label("Descricao *", 2, 0, pady_top=4)
            label("Observacao", 2, 2, pady_top=4)
            descricao_entry = self.modelo_entry(card, "Ex.: gasolina do caminhao")
            observacao_entry = self.modelo_entry(card, "Detalhes adicionais")
            descricao_entry.grid(row=3, column=0, columnspan=2, sticky="ew", padx=(18, 6), pady=(0, 16))
            observacao_entry.grid(row=3, column=2, columnspan=2, sticky="ew", padx=(6, 18), pady=(0, 16))

            if row:
                data_entry.insert(0, self.format_date_br(row["data"]))
                valor_entry.insert(0, f"{row['valor']:.2f}".replace(".", ","))
                descricao_entry.insert(0, row["descricao"] or "")
                observacao_entry.insert(0, row["observacao"] or "")
                usuario_entry.insert(0, row["usuario"] or "")
            else:
                data_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))
                usuario_entry.insert(0, self.usuario_logado or "Administrador")

            actions = ctk.CTkFrame(card, fg_color="transparent", height=54)
            actions.grid(row=4, column=0, columnspan=4, sticky="ew", padx=18, pady=(2, 14))
            actions.grid_propagate(False)

            def save():
                if not descricao_entry.get().strip():
                    messagebox.showwarning("Descricao obrigatoria", "Informe o motivo da retirada.")
                    return
                try:
                    data_value = self.parse_date_value(data_entry.get())
                    valor = self.parse_decimal(valor_entry.get())
                except ValueError:
                    messagebox.showerror("Valor invalido", "Confira a data e o valor informados.")
                    return
                if valor <= 0:
                    messagebox.showwarning("Valor obrigatorio", "Informe um valor maior que zero.")
                    return
                valores = (
                    data_value,
                    categoria_editor_var.get().strip() or "Outros",
                    descricao_entry.get().strip(),
                    valor,
                    observacao_entry.get().strip(),
                    usuario_entry.get().strip() or (self.usuario_logado or "Administrador"),
                )
                with sqlite3.connect(self.db_path) as conn:
                    if row:
                        conn.execute(
                            """
                            UPDATE sangrias
                            SET data=?, categoria=?, descricao=?, valor=?, observacao=?, usuario=?
                            WHERE id=?
                            """,
                            (*valores, row["id"]),
                        )
                    else:
                        conn.execute(
                            """
                            INSERT INTO sangrias (data, categoria, descricao, valor, observacao, usuario)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            valores,
                        )
                self.log_notification(
                    "sangria",
                    "Sangria registrada" if row is None else "Sangria atualizada",
                    f"{descricao_entry.get().strip()} - {self.format_money(valor)}.",
                )
                self.tela_sangrias()

            ctk.CTkButton(
                actions,
                text="Salvar Sangria",
                width=220,
                height=42,
                corner_radius=6,
                fg_color=colors["green"],
                hover_color=colors["green_hover"],
                font=ctk.CTkFont(size=14, weight="bold"),
                command=save,
            ).pack(side="right", pady=6)
            ctk.CTkButton(
                actions,
                text="Cancelar",
                width=150,
                height=42,
                corner_radius=6,
                fg_color="#EFEFEF",
                hover_color="#E2E2E2",
                text_color=colors["text"],
                font=ctk.CTkFont(size=14, weight="bold"),
                command=self.tela_sangrias,
            ).pack(side="right", padx=(0, 14), pady=6)

        def render(*_args):
            for widget in body.winfo_children():
                widget.destroy()

            rows = filtered_rows()
            filtered_total = sum(float(row["valor"] or 0) for row in rows)
            resumo_cards["Hoje"].configure(text=self.format_money(today_total()))
            resumo_cards["Mes"].configure(text=self.format_money(month_total()))
            resumo_cards["Filtrado"].configure(text=self.format_money(filtered_total))
            resumo_cards["Registros"].configure(text=str(len(rows)))

            per_page = max(1, int(per_page_var.get()))
            total_pages = max(1, (len(rows) + per_page - 1) // per_page)
            page_state["current"] = max(1, min(page_state["current"], total_pages))
            start = (page_state["current"] - 1) * per_page
            end = start + per_page

            if not rows:
                self.modelo_empty(body, "Nenhuma sangria registrada.")
            for row in rows[start:end]:
                observacao = row["observacao"] or "-"
                if len(observacao) > 40:
                    observacao = f"{observacao[:37]}..."
                self.modelo_row(
                    body,
                    configure_columns,
                    [
                        self.format_date_br(row["data"]),
                        row["categoria"],
                        row["descricao"],
                        self.format_money(row["valor"]),
                        observacao,
                        "",
                    ],
                    actions=[
                        ("Editar", "#4B5563", lambda r=row: open_editor(r)),
                        ("Excluir", colors["danger"], lambda r=row: delete(r)),
                    ],
                    highlight_index=3,
                )
            self.modelo_pager(
                page,
                len(rows),
                row=4,
                current_page=page_state["current"],
                per_page=per_page,
                on_page_change=set_page,
                per_page_var=per_page_var,
                on_per_page_change=lambda _value: reset_and_render(),
            )

        for var in (categoria_var, busca_var):
            var.trace_add("write", reset_and_render)
        render()

    def tela_comprovantes(self):
        page = self.modelo_page("Comprovantes", "Comprovantes internos gerados nas compras e vendas")
        colors = self.modelo_colors()
        busca_var = ctk.StringVar(value="")
        per_page_var = ctk.StringVar(value="10")
        page_state = {"current": 1}
        page.grid_rowconfigure(2, weight=1)
        page.grid_rowconfigure(3, weight=0)

        controls = ctk.CTkFrame(page, fg_color="transparent", height=52)
        controls.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        controls.grid_propagate(False)
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            controls,
            text="Buscar",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=colors["text"],
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))

        busca_entry = self.modelo_entry(controls, "Número, cliente ou data", busca_var)
        busca_entry.grid(row=0, column=1, sticky="ew")

        body, configure_columns = self.modelo_table(page, ["Número", "Tipo", "Cliente", "Data", "Total", ""], [16, 12, 28, 18, 14, 12], row=2)
        rows = self.db_fetchall("SELECT * FROM comprovantes ORDER BY data DESC, id DESC")

        def abrir(numero):
            self.tela_comprovante(numero, "")

        def filtered_rows():
            query = str(busca_var.get() or "").strip().lower()
            if not query:
                return rows

            query_digits = "".join(char for char in query if char.isdigit())
            query_only_digits = bool(query_digits) and query_digits == query

            def numero_normalizado(valor):
                digits = "".join(char for char in str(valor or "") if char.isdigit())
                return digits.lstrip("0") or "0"

            if query_only_digits:
                exact_number_matches = [
                    row for row in rows
                    if numero_normalizado(row["numero"]) == numero_normalizado(query_digits)
                ]
                if exact_number_matches:
                    return exact_number_matches

            filtrados = []
            for row in rows:
                numero = str(row["numero"] or "")
                cliente = str(row["cliente_nome"] or "")
                data_raw = str(row["data"] or "")
                data_short = data_raw[:16]
                data_br = self.format_date_br(data_raw[:10]) if data_raw[:10] else ""
                haystack = " ".join(
                    piece for piece in (numero, numero_normalizado(numero), cliente, data_raw, data_short, data_br) if piece
                ).lower()
                if query in haystack:
                    filtrados.append(row)
            return filtrados

        def set_page(new_page):
            visible_rows = filtered_rows()
            per_page = max(1, int(per_page_var.get()))
            total_pages = max(1, (len(visible_rows) + per_page - 1) // per_page)
            page_state["current"] = max(1, min(new_page, total_pages))
            render()

        def reset_and_render(*_args):
            page_state["current"] = 1
            render()

        def render(*_args):
            for widget in body.winfo_children():
                widget.destroy()

            visible_rows = filtered_rows()
            per_page = max(1, int(per_page_var.get()))
            total_pages = max(1, (len(visible_rows) + per_page - 1) // per_page)
            page_state["current"] = max(1, min(page_state["current"], total_pages))
            start = (page_state["current"] - 1) * per_page
            end = start + per_page

            if not visible_rows:
                self.modelo_empty(body, "Nenhum comprovante encontrado para a busca informada.")

            for row in visible_rows[start:end]:
                self.modelo_row(
                    body,
                    configure_columns,
                    [row["numero"], row["tipo"].title(), row["cliente_nome"], row["data"][:16], self.format_money(row["total"]), ""],
                    actions=[("Abrir", colors["green"], lambda n=row["numero"]: abrir(n))],
                    highlight_index=4,
                )

            self.modelo_pager(
                page,
                len(visible_rows),
                row=3,
                current_page=page_state["current"],
                per_page=per_page,
                on_page_change=set_page,
                per_page_var=per_page_var,
                on_per_page_change=lambda _value: reset_and_render(),
            )

        busca_var.trace_add("write", reset_and_render)
        render()

    def tela_nota_fiscal(self):
        page = self.modelo_page("Nota Fiscal", "Emissão e consulta de documentos fiscais")
        colors = self.modelo_colors()
        page.grid_rowconfigure(1, weight=1)
        page.grid_rowconfigure(2, weight=0)

        panel = ctk.CTkFrame(page, fg_color="white", corner_radius=12, border_width=1, border_color=colors["line"])
        panel.grid(row=1, column=0, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(0, weight=1)

        content = ctk.CTkFrame(panel, fg_color="transparent")
        content.grid(row=0, column=0)
        ctk.CTkLabel(content, text="Nota Fiscal", font=ctk.CTkFont(size=22, weight="bold"), text_color=colors["text"]).pack(pady=(0, 8))
        ctk.CTkLabel(
            content,
            text="Área reservada para notas fiscais. Os comprovantes internos ficam separados na opção Comprovante.",
            wraplength=620,
            justify="center",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["muted"],
        ).pack(pady=(0, 18))
        ctk.CTkButton(
            content,
            text="Abrir Comprovantes",
            width=190,
            height=40,
            corner_radius=7,
            fg_color=colors["green"],
            hover_color=colors["green_hover"],
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.tela_comprovantes,
        ).pack()

    def tela_operacao(self, tipo):
        colors = {
            "bg": "#F7F8F6",
            "panel": "white",
            "line": "#E5E7EB",
            "soft": "#F8F9FA",
            "soft_green": "#E9F7E3",
            "text": "#17202A",
            "muted": "#66707A",
            "green": "#0E7A24",
            "green_hover": "#0A631D",
            "danger": "#C94040",
        }
        title = "Nova Compra" if tipo == "COMPRA" else "Nova Venda"
        subtitle = "Registre a entrada de materiais no estoque" if tipo == "COMPRA" else "Registre a saida de materiais do estoque"
        item_title = "Itens da Compra" if tipo == "COMPRA" else "Itens da Venda"
        item_subtitle = "Adicione os materiais adquiridos" if tipo == "COMPRA" else "Adicione os materiais vendidos"
        total_title = "Valor Total" if tipo == "COMPRA" else "Valor Total"

        self.current_items = []
        clientes = list(self.get_clientes())
        materiais = list(self.get_materiais_mais_comprados(somente_ativos=True))

        self.clear_main()
        self.main_container = ctk.CTkFrame(self, fg_color=colors["bg"], corner_radius=0)
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.build_header()
        self.build_footer()

        page = ctk.CTkFrame(self.main_container, fg_color=colors["bg"], corner_radius=0)
        page.grid(row=1, column=0, sticky="nsew", padx=22, pady=(4, 3))
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(2, weight=1)

        def small_entry(master, placeholder="", textvariable=None):
            return ctk.CTkEntry(
                master,
                height=32,
                corner_radius=6,
                border_width=1,
                border_color=colors["line"],
                fg_color="white",
                placeholder_text=placeholder,
                textvariable=textvariable,
                font=ctk.CTkFont(size=12),
            )

        def bind_entry_widget(widget, sequence, callback, add=None):
            if add is None:
                widget.bind(sequence, callback)
            else:
                widget.bind(sequence, callback, add=add)
            inner_widget = getattr(widget, "_entry", None)
            if inner_widget is not None:
                if add is None:
                    inner_widget.bind(sequence, callback)
                else:
                    inner_widget.bind(sequence, callback, add=add)

        heading = ctk.CTkFrame(page, fg_color="transparent", height=50)
        heading.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        heading.grid_propagate(False)

        ctk.CTkButton(
            heading,
            text="<  Voltar",
            width=96,
            height=36,
            corner_radius=8,
            fg_color="#EEF0EF",
            hover_color="#E1E5E2",
            text_color=colors["text"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.build_ui,
        ).pack(side="left", padx=(0, 18), pady=10)

        heading_text = ctk.CTkFrame(heading, fg_color="transparent")
        heading_text.pack(side="left", fill="x", expand=True, pady=2)
        ctk.CTkLabel(heading_text, text=title, font=ctk.CTkFont(size=24, weight="bold"), text_color=colors["text"]).pack(anchor="w")
        ctk.CTkLabel(heading_text, text=subtitle, font=ctk.CTkFont(size=12, weight="bold"), text_color=colors["muted"]).pack(anchor="w", pady=(2, 0))

        folhas_path = self.first_existing_path(
            os.path.join(self.asset_dir, "folhas_design.png"),
            os.path.join(self.script_dir, "folhas_design.png"),
        )
        if os.path.exists(folhas_path):
            folhas_pil = Image.open(folhas_path)
            self.operation_leaf_img = ctk.CTkImage(light_image=folhas_pil, dark_image=folhas_pil, size=(120, 92))
            ctk.CTkLabel(heading, image=self.operation_leaf_img, text="").place(relx=1.0, x=-6, y=-10, anchor="ne")

        client_panel_height = 176 if tipo == "COMPRA" else 150
        client_panel = ctk.CTkFrame(page, height=client_panel_height, fg_color=colors["panel"], corner_radius=12, border_width=1, border_color=colors["line"])
        client_panel.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        client_panel.grid_propagate(False)

        ctk.CTkLabel(client_panel, text="Dados do Cliente", font=ctk.CTkFont(size=15, weight="bold"), text_color=colors["text"]).place(x=18, y=8)

        tipo_cliente = ctk.StringVar(value="cadastrado")
        radio_row = ctk.CTkFrame(client_panel, fg_color="transparent")
        radio_row.place(x=18, y=32)
        ctk.CTkRadioButton(
            radio_row,
            text="Cliente cadastrado",
            variable=tipo_cliente,
            value="cadastrado",
            radiobutton_width=16,
            radiobutton_height=16,
            border_width_checked=5,
            fg_color=colors["green"],
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#3D464F",
        ).pack(side="left", padx=(0, 24))
        ctk.CTkRadioButton(
            radio_row,
            text="Cliente anonimo",
            variable=tipo_cliente,
            value="anonimo",
            radiobutton_width=16,
            radiobutton_height=16,
            border_width_checked=5,
            fg_color=colors["green"],
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#3D464F",
        ).pack(side="left")

        client_grid = ctk.CTkFrame(client_panel, fg_color="transparent")
        client_grid.place(x=16, y=58, relwidth=0.975)
        for index, weight in enumerate([20, 10, 18, 14, 24]):
            client_grid.grid_columnconfigure(index, weight=weight, uniform="client_grid")

        for col, text in enumerate(["Cliente *", "", "CPF / CNPJ", "Telefone", "Observacao (opcional)"]):
            ctk.CTkLabel(
                client_grid,
                text=text,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#3D464F",
            ).grid(row=0, column=col, sticky="w", padx=4)

        cliente_var = ctk.StringVar(value="")
        cliente_entry = small_entry(client_grid, "Selecione ou digite o cliente", cliente_var)
        cliente_entry.grid(row=1, column=0, sticky="ew", padx=4, pady=(1, 0))
        ctk.CTkButton(
            client_grid,
            text="+  Novo",
            height=32,
            corner_radius=6,
            fg_color="#E5F5DF",
            hover_color="#D9EFD1",
            text_color=colors["green"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.tela_clientes,
        ).grid(row=1, column=1, sticky="ew", padx=4, pady=(1, 0))
        documento = small_entry(client_grid, "00.000.000/0000-00")
        documento.grid(row=1, column=2, sticky="ew", padx=4, pady=(1, 0))
        telefone = small_entry(client_grid, "(19) 99999-9999")
        telefone.grid(row=1, column=3, sticky="ew", padx=4, pady=(1, 0))
        observacao = small_entry(client_grid, "Digite uma observacao...")
        observacao.grid(row=1, column=4, sticky="ew", padx=4, pady=(1, 0))
        destino_compra_var = ctk.StringVar(value="Venda interna" if tipo == "COMPRA" else "")
        destino_entry = None
        destino_rows = [{"nome": "Venda interna"}, {"nome": "Venda externa"}]

        cliente_suggestions = ctk.CTkFrame(client_grid, fg_color="transparent", width=1, height=1)

        if tipo == "COMPRA":
            destino_frame = ctk.CTkFrame(client_panel, fg_color="transparent")
            destino_frame.place(x=18, y=136)
            ctk.CTkLabel(
                destino_frame,
                text="Destino da compra",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#3D464F",
            ).pack(side="left", padx=(0, 10))
            destino_field = ctk.CTkFrame(
                destino_frame,
                width=220,
                height=32,
                fg_color="white",
                corner_radius=6,
                border_width=1,
                border_color=colors["line"],
            )
            destino_field.pack(side="left")
            destino_field.pack_propagate(False)
            destino_field.grid_columnconfigure(0, weight=1)

            destino_entry = ctk.CTkEntry(
                destino_field,
                textvariable=destino_compra_var,
                height=28,
                border_width=0,
                corner_radius=0,
                fg_color="white",
                text_color=colors["text"],
                font=ctk.CTkFont(size=12),
            )
            destino_entry.grid(row=0, column=0, sticky="ew", padx=10, pady=1)

            destino_suggestions = ctk.CTkFrame(destino_frame, fg_color="transparent", width=1, height=1)

            def escolher_destino(row):
                destino_compra_var.set(row["nome"])
                self.clear_suggestion_popup()

            def atualizar_sugestoes_destino(show_all=False):
                if destino_entry is None or not destino_entry.winfo_exists():
                    return
                query = "" if show_all else destino_compra_var.get()
                self.render_suggestions(
                    destino_suggestions,
                    destino_rows,
                    query,
                    escolher_destino,
                    limit=4,
                    anchor_widget=destino_entry,
                    focus_widget=destino_entry,
                )

            def destino_key_release(_event):
                if getattr(_event, "keysym", "") in {"Up", "Down", "Left", "Right", "Return", "KP_Enter", "Tab"}:
                    return
                atualizar_sugestoes_destino()

            def destino_arrow(step):
                if not self.suggestion_state or not self._suggestion_matches_widget(destino_entry):
                    atualizar_sugestoes_destino(True)
                    return "break"
                return self.move_suggestion_selection(destino_entry, step) or "break"

            destino_field.bind("<Button-1>", lambda _event: (destino_entry.focus_set(), atualizar_sugestoes_destino(True)))
            bind_entry_widget(destino_entry, "<FocusIn>", lambda _event: atualizar_sugestoes_destino(True))
            bind_entry_widget(destino_entry, "<KeyRelease>", destino_key_release)
            bind_entry_widget(destino_entry, "<Down>", lambda _event: destino_arrow(1))
            bind_entry_widget(destino_entry, "<Up>", lambda _event: destino_arrow(-1))
            bind_entry_widget(destino_entry, "<FocusOut>", lambda _event: self.schedule_suggestion_popup_close(destino_entry))

        def cliente_digitado():
            return self.selected_row_by_name(clientes, cliente_var.get())

        def fill_client(*_args):
            documento.configure(state="normal")
            telefone.configure(state="normal")
            documento.delete(0, "end")
            telefone.delete(0, "end")
            if tipo_cliente.get() == "anonimo":
                cliente_entry.configure(state="disabled")
                if cliente_var.get():
                    cliente_var.set("")
                for widget in cliente_suggestions.winfo_children():
                    widget.destroy()
                return
            cliente_entry.configure(state="normal")
            cliente = cliente_digitado()
            if cliente:
                documento.insert(0, cliente["cnpj"] or "")
                telefone.insert(0, cliente["telefone"] or "")

        def escolher_cliente(row):
            cliente_var.set(row["nome"])
            self.clear_suggestion_popup()
            fill_client()

        def atualizar_sugestoes_cliente(*_args):
            if tipo_cliente.get() == "anonimo":
                fill_client()
                self.clear_suggestion_popup()
                return
            if cliente_var.get().strip():
                self.render_suggestions(
                    cliente_suggestions,
                    clientes,
                    cliente_var.get(),
                    escolher_cliente,
                    limit=5,
                    anchor_widget=cliente_entry,
                    focus_widget=cliente_entry,
                )
            else:
                self.clear_suggestion_popup()
            fill_client()

        def cliente_key_release(_event):
            if getattr(_event, "keysym", "") in {"Up", "Down", "Left", "Right", "Return", "KP_Enter", "Tab"}:
                return
            atualizar_sugestoes_cliente()

        def cliente_arrow(step):
            if not self.suggestion_state or not self._suggestion_matches_widget(cliente_entry):
                atualizar_sugestoes_cliente()
                return "break"
            return self.move_suggestion_selection(cliente_entry, step) or "break"

        cliente_var.trace_add("write", atualizar_sugestoes_cliente)
        bind_entry_widget(cliente_entry, "<FocusIn>", lambda _event: atualizar_sugestoes_cliente())
        bind_entry_widget(cliente_entry, "<KeyRelease>", cliente_key_release)
        bind_entry_widget(cliente_entry, "<Down>", lambda _event: cliente_arrow(1))
        bind_entry_widget(cliente_entry, "<Up>", lambda _event: cliente_arrow(-1))
        bind_entry_widget(cliente_entry, "<FocusOut>", lambda _event: self.schedule_suggestion_popup_close(cliente_entry))
        tipo_cliente.trace_add("write", fill_client)
        fill_client()

        work_area = ctk.CTkFrame(page, fg_color="transparent")
        work_area.grid(row=2, column=0, sticky="nsew", pady=(0, 4))
        work_area.grid_columnconfigure(0, weight=5)
        work_area.grid_columnconfigure(1, weight=2, minsize=320)
        work_area.grid_rowconfigure(0, weight=0)

        item_panel = ctk.CTkFrame(work_area, fg_color=colors["panel"], corner_radius=12, border_width=1, border_color=colors["line"])
        item_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        item_panel.grid_columnconfigure(0, weight=1)
        item_panel.grid_rowconfigure(2, weight=1)

        item_top = ctk.CTkFrame(item_panel, fg_color="transparent", height=50)
        item_top.grid(row=0, column=0, sticky="ew")
        item_top.grid_propagate(False)
        ctk.CTkLabel(item_top, text=item_title, font=ctk.CTkFont(size=15, weight="bold"), text_color=colors["text"]).place(x=18, y=7)
        ctk.CTkLabel(item_top, text=item_subtitle, font=ctk.CTkFont(size=11, weight="bold"), text_color=colors["muted"]).place(x=18, y=29)

        table_body = None
        item_rows = []
        summary_refs = {}
        empty_state = {"widget": None}

        ctk.CTkButton(
            item_top,
            text="+  Adicionar Material",
            width=180,
            height=34,
            corner_radius=6,
            fg_color=colors["green"],
            hover_color=colors["green_hover"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: add_item_row(),
        ).place(relx=1.0, x=-18, y=8, anchor="ne")

        col_weights = [13, 24, 13, 14, 14, 15, 7]

        def configure_table_columns(frame):
            for index, weight in enumerate(col_weights):
                frame.grid_columnconfigure(index, weight=weight, uniform="operation_table")

        table_header = ctk.CTkFrame(item_panel, fg_color=colors["soft"], height=32, corner_radius=0)
        table_header.grid(row=1, column=0, sticky="ew", padx=16)
        table_header.grid_propagate(False)
        configure_table_columns(table_header)
        headers = ["Peso Bruto (kg)", "Material", "Desconto (kg)", "Peso Liquido (kg)", "Valor por kg (R$)", "Subtotal (R$)", "Acoes"]
        for index, text in enumerate(headers):
            ctk.CTkLabel(
                table_header,
                text=text,
                anchor="w" if index == 1 else "center",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#303942",
            ).grid(row=0, column=index, sticky="nsew", padx=4)

        table_body = ctk.CTkScrollableFrame(item_panel, fg_color="white", corner_radius=0, height=170)
        table_body.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 8))

        def readonly_box(master, initial="0,00", fg_color="white", text_color=None):
            box = ctk.CTkFrame(master, height=32, fg_color=fg_color, corner_radius=6, border_width=1, border_color=colors["line"])
            box.grid_propagate(False)
            label = ctk.CTkLabel(
                box,
                text=initial,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=text_color or colors["text"],
            )
            label.pack(expand=True)
            return box, label

        def parse_or_zero(widget):
            try:
                return self.parse_decimal(widget.get())
            except ValueError:
                return 0.0

        def material_digitado(nome):
            return self.selected_row_by_name(materiais, nome)

        def update_empty_state():
            if item_rows and empty_state["widget"] is not None:
                empty_state["widget"].destroy()
                empty_state["widget"] = None
            if not item_rows and empty_state["widget"] is None:
                empty_state["widget"] = ctk.CTkFrame(table_body, fg_color="#FBFCFD", corner_radius=6, height=40)
                empty_state["widget"].pack(fill="x", padx=0, pady=5)
                empty_state["widget"].pack_propagate(False)
                ctk.CTkLabel(
                    empty_state["widget"],
                    text="Clique em Adicionar Material para incluir itens",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=colors["muted"],
                ).pack(expand=True)

        def valid_items_from_rows(validate=False):
            items = []
            for row_data in item_rows:
                material = material_digitado(row_data["material_var"].get())
                touched = bool(
                    row_data["material_var"].get().strip()
                    or row_data["peso"].get().strip()
                    or row_data["desconto"].get().strip()
                    or row_data["preco"].get().strip()
                )
                if not material:
                    if validate and touched:
                        messagebox.showwarning("Material obrigatorio", "Digite e selecione um material cadastrado.")
                        return None
                    continue
                try:
                    peso_bruto = self.parse_decimal(row_data["peso"].get())
                    desconto_valor = self.parse_decimal(row_data["desconto"].get())
                    preco_kg = self.parse_decimal(row_data["preco"].get())
                except ValueError:
                    if validate:
                        messagebox.showerror("Valor invalido", "Confira peso, desconto e valor por kg.")
                        return None
                    continue
                peso_liquido = peso_bruto - desconto_valor
                if peso_liquido <= 0:
                    if validate and touched:
                        messagebox.showerror("Peso invalido", "O peso liquido precisa ser maior que zero.")
                        return None
                    continue
                items.append({
                    "material_id": material["id"],
                    "material_nome": material["nome"],
                    "peso_bruto": peso_bruto,
                    "desconto": desconto_valor,
                    "peso_liquido": peso_liquido,
                    "preco_kg": preco_kg,
                    "subtotal": peso_liquido * preco_kg,
                })
            return items

        def recalculate_rows(_event=None):
            bruto_total = 0.0
            desconto_total = 0.0
            liquido_total = 0.0
            valor_total = 0.0
            for row_data in item_rows:
                peso_bruto = parse_or_zero(row_data["peso"])
                desconto_valor = parse_or_zero(row_data["desconto"])
                preco_kg = parse_or_zero(row_data["preco"])
                peso_liquido = max(0.0, peso_bruto - desconto_valor)
                subtotal = peso_liquido * preco_kg
                row_data["liquido_label"].configure(text=f"{peso_liquido:.2f}".replace(".", ","))
                row_data["subtotal_label"].configure(text=self.format_money(subtotal))
                bruto_total += peso_bruto
                desconto_total += desconto_valor
                liquido_total += peso_liquido
                valor_total += subtotal
            if summary_refs:
                summary_refs["bruto"].configure(text=self.format_kg(bruto_total))
                summary_refs["desconto"].configure(text=self.format_kg(desconto_total))
                summary_refs["liquido"].configure(text=self.format_kg(liquido_total))
                summary_refs["total"].configure(text=self.format_money(valor_total))
            self.current_items = valid_items_from_rows(validate=False) or []
            update_empty_state()

        shortcut_actions = {"finalize": None}

        def shortcut_add_item(_event=None):
            add_item_row()
            return "break"

        def shortcut_finalize(_event=None):
            focus_widget = self.focus_get()
            if self.confirm_suggestion_selection(focus_widget):
                return "break"
            finalize_callback = shortcut_actions["finalize"]
            if finalize_callback:
                finalize_callback(True)
            return "break"

        def bind_operation_shortcuts(widget):
            for sequence in ("<KeyPress-plus>", "<KP_Add>"):
                bind_entry_widget(widget, sequence, shortcut_add_item, add="+")
            for sequence in ("<Return>", "<KP_Enter>"):
                bind_entry_widget(widget, sequence, shortcut_finalize, add="+")

        def apply_material(row_data):
            material = material_digitado(row_data["material_var"].get())
            if material:
                if row_data.get("last_material_id") != material["id"]:
                    price = material["preco_compra"] if tipo == "COMPRA" else material["preco_venda"]
                    row_data["preco"].delete(0, "end")
                    row_data["preco"].insert(0, f"{price:.2f}".replace(".", ","))
                    row_data["last_material_id"] = material["id"]
            else:
                row_data["last_material_id"] = None
            recalculate_rows()

        def remove_row(row_data):
            if row_data in item_rows:
                item_rows.remove(row_data)
            row_data["frame"].destroy()
            recalculate_rows()

        def add_item_row():
            row_frame = ctk.CTkFrame(table_body, fg_color="white", height=68, corner_radius=0)
            row_frame.pack(fill="x", pady=(0, 3))
            row_frame.grid_propagate(False)
            configure_table_columns(row_frame)

            material_var = ctk.StringVar(value="")
            peso = small_entry(row_frame, "0,00")
            peso.grid(row=0, column=0, sticky="ew", padx=4, pady=(5, 0))
            material_entry = ctk.CTkEntry(
                row_frame,
                textvariable=material_var,
                height=32,
                corner_radius=6,
                border_width=1,
                border_color=colors["line"],
                fg_color="white",
                placeholder_text="Digite o material",
                font=ctk.CTkFont(size=12),
            )
            material_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=(5, 0))
            material_suggestions = ctk.CTkFrame(row_frame, fg_color="transparent", width=1, height=1)
            desconto = small_entry(row_frame, "0,00")
            desconto.grid(row=0, column=2, sticky="ew", padx=4, pady=(5, 0))
            liquido_box, liquido_label = readonly_box(row_frame, "0,00", colors["soft_green"])
            liquido_box.grid(row=0, column=3, sticky="ew", padx=4, pady=(5, 0))
            preco = small_entry(row_frame, "0,00")
            preco.grid(row=0, column=4, sticky="ew", padx=4, pady=(5, 0))
            subtotal_box, subtotal_label = readonly_box(row_frame, "R$ 0,00", "white", colors["green"])
            subtotal_box.grid(row=0, column=5, sticky="ew", padx=4, pady=(5, 0))
            row_data = {
                "frame": row_frame,
                "material_var": material_var,
                "material_suggestions": material_suggestions,
                "material_entry": material_entry,
                "peso": peso,
                "desconto": desconto,
                "preco": preco,
                "liquido_label": liquido_label,
                "subtotal_label": subtotal_label,
                "last_material_id": None,
            }
            actions = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions.grid(row=0, column=6, sticky="nsew", padx=2, pady=(5, 0))
            ctk.CTkButton(
                actions,
                text="X",
                width=30,
                height=30,
                corner_radius=6,
                fg_color="#FFF0F0",
                hover_color="#FFE0E0",
                text_color=colors["danger"],
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda data=row_data: remove_row(data),
            ).pack()

            def escolher_material(row, data=row_data):
                data["material_var"].set(row["nome"])
                self.clear_suggestion_popup()
                apply_material(data)

            def atualizar_sugestoes_material(*_args, data=row_data):
                query = data["material_var"].get()
                if query.strip():
                    self.render_suggestions(
                        data["material_suggestions"],
                        materiais,
                        query,
                        lambda row: escolher_material(row, data),
                        limit=4,
                        anchor_widget=data["material_entry"],
                        focus_widget=data["material_entry"],
                    )
                else:
                    self.clear_suggestion_popup()
                apply_material(data)

            def material_key_release(_event, data=row_data):
                if getattr(_event, "keysym", "") in {"Up", "Down", "Left", "Right", "Return", "KP_Enter", "Tab"}:
                    return
                atualizar_sugestoes_material(data=data)

            def material_arrow(step, data=row_data):
                if not self.suggestion_state or not self._suggestion_matches_widget(data["material_entry"]):
                    atualizar_sugestoes_material(data=data)
                    return "break"
                return self.move_suggestion_selection(data["material_entry"], step) or "break"

            material_var.trace_add("write", atualizar_sugestoes_material)
            bind_entry_widget(material_entry, "<FocusIn>", lambda _event, data=row_data: atualizar_sugestoes_material(data=data))
            bind_entry_widget(material_entry, "<KeyRelease>", material_key_release)
            bind_entry_widget(material_entry, "<Down>", lambda _event, data=row_data: material_arrow(1, data))
            bind_entry_widget(material_entry, "<Up>", lambda _event, data=row_data: material_arrow(-1, data))
            bind_entry_widget(material_entry, "<FocusOut>", lambda _event, data=row_data: self.schedule_suggestion_popup_close(data["material_entry"]))
            for widget in (peso, desconto, preco):
                widget.bind("<KeyRelease>", recalculate_rows)
                widget.bind("<FocusOut>", recalculate_rows)
            for widget in (peso, material_entry, desconto, preco):
                bind_operation_shortcuts(widget)

            item_rows.append(row_data)
            update_empty_state()
            peso.focus_set()

        side_panel = ctk.CTkFrame(work_area, fg_color="transparent")
        side_panel.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        side_panel.grid_columnconfigure(0, weight=1)
        side_panel.grid_rowconfigure(0, weight=0)
        side_panel.grid_rowconfigure(1, weight=0)
        side_panel.grid_rowconfigure(2, weight=0)

        resumo = ctk.CTkFrame(side_panel, fg_color="white", corner_radius=12, border_width=1, border_color=colors["line"])
        resumo.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        ctk.CTkLabel(resumo, text="Resumo da Operacao", font=ctk.CTkFont(size=14, weight="bold"), text_color=colors["text"]).pack(anchor="w", padx=16, pady=(10, 8))
        resumo_grid = ctk.CTkFrame(resumo, fg_color="transparent")
        resumo_grid.pack(fill="x", padx=12, pady=(0, 10))
        for index, (label, key, initial, box_color) in enumerate([
            ("Peso Bruto Total", "bruto", "0,00 kg", "#FBFCFD"),
            ("Desconto (kg)", "desconto", "0,00 kg", "#FBFCFD"),
            ("Peso Liquido Total", "liquido", "0,00 kg", colors["soft_green"]),
            (total_title, "total", "R$ 0,00", colors["soft_green"]),
        ]):
            resumo_grid.grid_columnconfigure(index % 2, weight=1, uniform="summary")
            box = ctk.CTkFrame(resumo_grid, fg_color=box_color, corner_radius=8)
            box.grid(row=index // 2, column=index % 2, sticky="nsew", padx=5, pady=5)
            ctk.CTkLabel(box, text=label, font=ctk.CTkFont(size=10, weight="bold"), text_color="#3D464F").pack(anchor="w", padx=12, pady=(10, 2))
            summary_refs[key] = ctk.CTkLabel(
                box,
                text=initial,
                font=ctk.CTkFont(size=18 if key == "total" else 14, weight="bold"),
                text_color=colors["green"] if key == "total" else colors["text"],
            )
            summary_refs[key].pack(anchor="w", padx=12)

        acoes = ctk.CTkFrame(side_panel, fg_color="white", corner_radius=12, border_width=1, border_color=colors["line"])
        acoes.grid(row=1, column=0, sticky="ew")
        ctk.CTkLabel(acoes, text="Acoes", font=ctk.CTkFont(size=14, weight="bold"), text_color=colors["text"]).pack(anchor="w", padx=16, pady=(10, 8))

        def finalizar(gerar_comprovante=True):
            items = valid_items_from_rows(validate=True)
            if items is None:
                return
            if not items:
                messagebox.showwarning("Itens obrigatorios", "Adicione pelo menos um material.")
                return
            cliente_nome = "Cliente Anonimo" if tipo_cliente.get() == "anonimo" else cliente_var.get().strip()
            self.current_items = items
            self.finalizar_operacao(
                tipo,
                cliente_nome,
                observacao.get().strip(),
                gerar_comprovante,
                documento.get().strip() if tipo_cliente.get() != "anonimo" else "",
                telefone.get().strip() if tipo_cliente.get() != "anonimo" else "",
                destino_compra_var.get().strip() if tipo == "COMPRA" else "",
            )

        shortcut_actions["finalize"] = finalizar
        shortcut_widgets = [cliente_entry, documento, telefone, observacao]
        if destino_entry is not None:
            shortcut_widgets.append(destino_entry)
        for widget in shortcut_widgets:
            bind_operation_shortcuts(widget)
        ctk.CTkButton(
            acoes,
            text="Gerar Comprovante" if tipo == "COMPRA" else "Finalizar e Imprimir",
            height=38,
            corner_radius=6,
            fg_color=colors["green"],
            hover_color=colors["green_hover"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: finalizar(True),
        ).pack(fill="x", padx=18, pady=(0, 8))
        ctk.CTkLabel(
            acoes,
            text="A operacao sera registrada no sistema e o estoque sera atualizado." if tipo == "COMPRA" else "A venda sera registrada, o estoque sera atualizado e o comprovante sera enviado para a impressora.",
            wraplength=250,
            justify="left",
            text_color=colors["muted"],
            font=ctk.CTkFont(size=10, weight="bold"),
        ).pack(anchor="w", padx=18, pady=(0, 10))

        add_item_row()
        recalculate_rows()

    def tela_relatorios(self):
        page = self.modelo_page("Relatorios", "Indicadores financeiros e operacionais por periodo")
        colors = self.modelo_colors()
        page.grid_rowconfigure(2, weight=0)
        page.grid_rowconfigure(3, weight=0)
        page.grid_rowconfigure(4, weight=1)

        data_inicial_var = ctk.StringVar(value="")
        data_final_var = ctk.StringVar(value="")
        material_var = ctk.StringVar(value="")
        destino_var = ctk.StringVar(value="Todos destinos")
        per_page_var = ctk.StringVar(value="10")
        page_state = {"current": 1}
        filtro_periodo = {"data_inicial": None, "data_final": None}

        material_values = ["Todos materiais"]
        for material_row in self.db_fetchall(
            """
            SELECT DISTINCT TRIM(material_nome) AS nome
            FROM transacao_itens
            WHERE TRIM(material_nome) <> ''
            ORDER BY material_nome
            """
        ):
            nome = str(material_row["nome"] or "").strip()
            if nome and nome not in material_values:
                material_values.append(nome)
        material_rows = [{"nome": nome} for nome in material_values[1:]]

        controls = ctk.CTkFrame(page, fg_color="transparent", height=126)
        controls.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        controls.grid_propagate(False)
        controls.grid_columnconfigure(0, weight=1)
        controls.grid_columnconfigure(1, weight=0)

        periodo_box = ctk.CTkFrame(controls, fg_color="transparent")
        periodo_box.grid(row=0, column=0, sticky="ew", pady=4)
        periodo_box.grid_columnconfigure(1, weight=1)
        periodo_box.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(periodo_box, text="Periodo", font=ctk.CTkFont(size=12, weight="bold"), text_color=colors["text"]).grid(row=0, column=0, sticky="w", padx=(0, 8))
        data_inicial_entry = self.modelo_entry(periodo_box, "Data inicial (dd/mm/aaaa)", data_inicial_var)
        data_inicial_entry.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        ctk.CTkLabel(periodo_box, text="ate", font=ctk.CTkFont(size=12, weight="bold"), text_color=colors["muted"]).grid(row=0, column=2, sticky="w", padx=(0, 8))
        data_final_entry = self.modelo_entry(periodo_box, "Data final (dd/mm/aaaa)", data_final_var)
        data_final_entry.grid(row=0, column=3, sticky="ew")

        filtros_box = ctk.CTkFrame(controls, fg_color="transparent")
        filtros_box.grid(row=1, column=0, sticky="ew", pady=(2, 4))
        filtros_box.grid_columnconfigure(1, weight=1)
        filtros_box.grid_columnconfigure(3, weight=1)

        def bind_entry_widget(widget, sequence, callback, add=None):
            if add is None:
                widget.bind(sequence, callback)
            else:
                widget.bind(sequence, callback, add=add)
            inner_widget = getattr(widget, "_entry", None)
            if inner_widget is not None:
                if add is None:
                    inner_widget.bind(sequence, callback)
                else:
                    inner_widget.bind(sequence, callback, add=add)

        ctk.CTkLabel(filtros_box, text="Material", font=ctk.CTkFont(size=12, weight="bold"), text_color=colors["text"]).grid(row=0, column=0, sticky="w", padx=(0, 8))
        material_entry = self.modelo_entry(filtros_box, "Digite para buscar material", material_var)
        material_entry.grid(row=0, column=1, sticky="ew", padx=(0, 18))
        material_suggestions = ctk.CTkFrame(filtros_box, fg_color="transparent", width=1, height=1)
        material_suggestions.grid(row=1, column=1, sticky="ew")

        ctk.CTkLabel(filtros_box, text="Destino", font=ctk.CTkFont(size=12, weight="bold"), text_color=colors["text"]).grid(row=0, column=2, sticky="w", padx=(0, 8))
        ctk.CTkOptionMenu(
            filtros_box,
            values=["Todos destinos", "Venda interna", "Venda externa"],
            variable=destino_var,
            width=210,
            height=40,
            corner_radius=7,
            fg_color="white",
            button_color="white",
            button_hover_color="#F1F5F0",
            text_color=colors["text"],
            dropdown_fg_color="white",
            dropdown_hover_color="#EEF6EC",
            dropdown_text_color=colors["text"],
            command=lambda _value: reset_and_render(),
        ).grid(row=0, column=3, sticky="ew")

        actions = ctk.CTkFrame(controls, fg_color="transparent")
        actions.grid(row=0, column=1, rowspan=2, sticky="ne", padx=(12, 0), pady=4)

        periodo_label = ctk.CTkLabel(
            controls,
            text="Periodo: todos os registros. Aceita DD/MM/AAAA ou AAAA-MM-DD.",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=colors["muted"],
            anchor="w",
        )
        periodo_label.grid(row=2, column=0, sticky="ew", pady=(0, 4))

        top = ctk.CTkFrame(page, fg_color="transparent", height=92)
        top.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        top.grid_propagate(False)

        card_specs = [
            ("Compras", "#EEF8EA"),
            ("Vendas", "#EEF4FB"),
            ("Peso Comprado", "#FBF4E7"),
            ("Peso Vendido", "#F5ECFA"),
            ("Resultado", "#E8F7E2"),
        ]
        card_widgets = {}
        for index, (label, color) in enumerate(card_specs):
            top.grid_columnconfigure(index, weight=1)
            box = ctk.CTkFrame(top, fg_color=color, corner_radius=8, border_width=1, border_color=colors["line"])
            box.grid(row=0, column=index, sticky="nsew", padx=5, pady=5)
            ctk.CTkLabel(box, text=label, font=ctk.CTkFont(size=12, weight="bold"), text_color=colors["muted"]).pack(pady=(12, 4))
            value_label = ctk.CTkLabel(box, text="R$ 0,00", font=ctk.CTkFont(size=17, weight="bold"), text_color=colors["text"])
            value_label.pack(pady=(0, 10))
            card_widgets[label] = {"box": box, "value_label": value_label}

        body, configure_columns = self.modelo_table(page, ["Operacao", "Cliente", "Data", "Total", ""], [18, 30, 18, 14, 8], row=4)

        def material_digitado():
            return self.selected_row_by_name(material_rows, material_var.get())

        def material_selecionado():
            selecionado = material_digitado()
            if not selecionado:
                return ""
            return str(selecionado["nome"] or "").strip()

        def destino_selecionado():
            valor = str(destino_var.get() or "").strip()
            return "" if not valor or valor == "Todos destinos" else valor

        def filtros_texto():
            data_inicial = filtro_periodo["data_inicial"]
            data_final = filtro_periodo["data_final"]
            partes = []
            if data_inicial and data_final:
                partes.append(f"Periodo: {self.format_date_br(data_inicial)} ate {self.format_date_br(data_final)}")
            elif data_inicial:
                partes.append(f"Periodo: a partir de {self.format_date_br(data_inicial)}")
            elif data_final:
                partes.append(f"Periodo: ate {self.format_date_br(data_final)}")
            else:
                partes.append("Periodo: todos os registros")

            material = material_selecionado()
            destino = destino_selecionado()
            if material:
                partes.append(f"Material: {material}")
            if destino:
                partes.append(f"Destino: {destino}")

            texto = " | ".join(partes)
            if not data_inicial and not data_final and not material and not destino:
                texto += ". Aceita DD/MM/AAAA ou AAAA-MM-DD."
            else:
                texto += "."
            return texto

        def condicoes_transacao(alias=""):
            prefixo = f"{alias}." if alias else ""
            conditions, params = self.build_date_range_conditions(
                f"{prefixo}data",
                filtro_periodo["data_inicial"],
                filtro_periodo["data_final"],
            )
            destino = destino_selecionado()
            if destino:
                conditions.append(f"{prefixo}destino_compra = ?")
                params.append(destino)
            return conditions, params

        def transacoes_no_periodo():
            conditions, params = condicoes_transacao()
            material = material_selecionado()
            if material:
                conditions.append(
                    "EXISTS (SELECT 1 FROM transacao_itens filtro_item WHERE filtro_item.transacao_id = id AND filtro_item.material_nome = ?)"
                )
                params.append(material)
            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
            return self.db_fetchall(
                f"SELECT * FROM transacoes {where_clause} ORDER BY data DESC, id DESC",
                tuple(params),
            )

        def total_transacoes(tipo):
            conditions = ["t.tipo = ?"]
            params = [tipo]
            extra_conditions, extra_params = condicoes_transacao("t")
            conditions.extend(extra_conditions)
            params.extend(extra_params)
            material = material_selecionado()
            if material:
                conditions.append("i.material_nome = ?")
                params.append(material)
            row = self.db_fetchone(
                """
                SELECT COALESCE(SUM(i.subtotal), 0) AS total
                FROM transacao_itens i
                JOIN transacoes t ON t.id = i.transacao_id
                WHERE """ + " AND ".join(conditions),
                tuple(params),
            )
            return row["total"]

        def total_peso(tipo):
            conditions = ["t.tipo = ?"]
            params = [tipo]
            extra_conditions, extra_params = condicoes_transacao("t")
            conditions.extend(extra_conditions)
            params.extend(extra_params)
            material = material_selecionado()
            if material:
                conditions.append("i.material_nome = ?")
                params.append(material)
            row = self.db_fetchone(
                """
                SELECT COALESCE(SUM(i.peso_liquido), 0) AS total
                FROM transacao_itens i
                JOIN transacoes t ON t.id = i.transacao_id
                WHERE """ + " AND ".join(conditions),
                tuple(params),
            )
            return row["total"]

        def set_page(new_page):
            rows = transacoes_no_periodo()
            per_page = max(1, int(per_page_var.get()))
            total_pages = max(1, (len(rows) + per_page - 1) // per_page)
            page_state["current"] = max(1, min(new_page, total_pages))
            render()

        def reset_and_render(*_args):
            page_state["current"] = 1
            render()

        def escolher_material(row):
            material_var.set(str(row["nome"]))
            self.clear_suggestion_popup()
            reset_and_render()

        def atualizar_sugestoes_material(show_all=False):
            if material_entry is None or not material_entry.winfo_exists():
                return
            query = "" if show_all else material_var.get()
            if query.strip() or show_all:
                self.render_suggestions(
                    material_suggestions,
                    material_rows,
                    query,
                    escolher_material,
                    anchor_widget=material_entry,
                    focus_widget=material_entry,
                )
            else:
                self.clear_suggestion_popup()
                reset_and_render()

        def material_key_release(_event):
            if getattr(_event, "keysym", "") in {"Up", "Down", "Left", "Right", "Return", "KP_Enter", "Tab"}:
                return
            atualizar_sugestoes_material()
            reset_and_render()

        def material_arrow(step):
            if not self.suggestion_state or not self._suggestion_matches_widget(material_entry):
                atualizar_sugestoes_material(True)
                return "break"
            return self.move_suggestion_selection(material_entry, step) or "break"

        def material_confirm(_event=None):
            if self.confirm_suggestion_selection(material_entry):
                return "break"
            if material_digitado():
                reset_and_render()
            elif not material_var.get().strip():
                reset_and_render()
            return None

        def material_focus_out(_event=None):
            self.schedule_suggestion_popup_close(material_entry)
            if material_digitado():
                reset_and_render()
            elif not material_var.get().strip():
                reset_and_render()

        bind_entry_widget(material_entry, "<FocusIn>", lambda _event: atualizar_sugestoes_material(not material_var.get().strip()))
        bind_entry_widget(material_entry, "<KeyRelease>", material_key_release)
        bind_entry_widget(material_entry, "<Down>", lambda _event: material_arrow(1))
        bind_entry_widget(material_entry, "<Up>", lambda _event: material_arrow(-1))
        bind_entry_widget(material_entry, "<Return>", material_confirm)
        bind_entry_widget(material_entry, "<KP_Enter>", material_confirm)
        bind_entry_widget(material_entry, "<FocusOut>", material_focus_out)

        def aplicar_periodo():
            try:
                data_inicial, data_final = self.normalize_date_range(data_inicial_var.get(), data_final_var.get())
            except ValueError as exc:
                messagebox.showwarning("Periodo invalido", str(exc))
                return
            filtro_periodo["data_inicial"] = data_inicial
            filtro_periodo["data_final"] = data_final
            reset_and_render()

        def limpar_periodo():
            data_inicial_var.set("")
            data_final_var.set("")
            material_var.set("")
            destino_var.set("Todos destinos")
            filtro_periodo["data_inicial"] = None
            filtro_periodo["data_final"] = None
            reset_and_render()

        ctk.CTkButton(
            actions,
            text="Aplicar periodo",
            width=150,
            height=40,
            corner_radius=7,
            fg_color=colors["green"],
            hover_color=colors["green_hover"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=aplicar_periodo,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            actions,
            text="Limpar filtros",
            width=126,
            height=40,
            corner_radius=7,
            fg_color="#EFEFEF",
            hover_color="#E2E2E2",
            text_color=colors["text"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=limpar_periodo,
        ).pack(side="left")

        data_inicial_entry.bind("<Return>", lambda _event: aplicar_periodo())
        data_final_entry.bind("<Return>", lambda _event: aplicar_periodo())

        def render(*_args):
            for widget in body.winfo_children():
                widget.destroy()

            rows = transacoes_no_periodo()
            total_compras = total_transacoes("COMPRA")
            total_vendas = total_transacoes("VENDA")
            peso_compras = total_peso("COMPRA")
            peso_vendas = total_peso("VENDA")
            resultado = total_vendas - total_compras

            card_widgets["Compras"]["value_label"].configure(text=self.format_money(total_compras))
            card_widgets["Vendas"]["value_label"].configure(text=self.format_money(total_vendas))
            card_widgets["Peso Comprado"]["value_label"].configure(text=self.format_kg(peso_compras))
            card_widgets["Peso Vendido"]["value_label"].configure(text=self.format_kg(peso_vendas))
            card_widgets["Resultado"]["value_label"].configure(text=self.format_money(resultado))
            card_widgets["Resultado"]["box"].configure(fg_color="#E8F7E2" if resultado >= 0 else "#FCECED")
            periodo_label.configure(text=filtros_texto())

            per_page = max(1, int(per_page_var.get()))
            total_pages = max(1, (len(rows) + per_page - 1) // per_page)
            page_state["current"] = max(1, min(page_state["current"], total_pages))
            start = (page_state["current"] - 1) * per_page
            end = start + per_page

            if not rows:
                self.modelo_empty(body, "Nenhuma operacao encontrada no periodo informado.")
            for row in rows[start:end]:
                self.modelo_row(
                    body,
                    configure_columns,
                    [self.transacao_label(row), row["cliente_nome"], row["data"][:16], self.format_money(row["total"]), ""],
                    highlight_index=3,
                )
            self.modelo_pager(
                page,
                len(rows),
                row=5,
                current_page=page_state["current"],
                per_page=per_page,
                on_page_change=set_page,
                per_page_var=per_page_var,
                on_per_page_change=lambda _value: reset_and_render(),
            )

        render()

    def tela_historico(self):
        page = self.modelo_page("Historico", "Consulte compras, vendas e itens registrados")
        tipo_var = ctk.StringVar(value="TODAS")
        destino_var = ctk.StringVar(value="Todos destinos")
        data_var = ctk.StringVar(value="")
        busca_var = ctk.StringVar(value="")
        per_page_var = ctk.StringVar(value="10")
        page_state = {"current": 1}
        colors = self.modelo_colors()

        controls = ctk.CTkFrame(page, fg_color="transparent", height=92)
        controls.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        controls.grid_propagate(False)
        controls.grid_columnconfigure(3, weight=1)

        ctk.CTkOptionMenu(
            controls,
            values=["TODAS", "COMPRA", "VENDA"],
            variable=tipo_var,
            width=180,
            height=40,
            corner_radius=7,
            fg_color="white",
            button_color="white",
            text_color=colors["text"],
        ).grid(row=0, column=0, padx=(0, 10), pady=(5, 8), sticky="w")
        ctk.CTkOptionMenu(
            controls,
            values=["Todos destinos", "Venda interna", "Venda externa"],
            variable=destino_var,
            width=190,
            height=40,
            corner_radius=7,
            fg_color="white",
            button_color="white",
            text_color=colors["text"],
        ).grid(row=0, column=1, padx=(0, 10), pady=(5, 8), sticky="w")
        self.modelo_entry(controls, "Data (dd/mm/aaaa ou aaaa-mm-dd)", data_var).grid(row=0, column=2, sticky="ew", padx=(0, 10), pady=(5, 8))
        self.modelo_entry(controls, "Buscar cliente, observacao ou destino...", busca_var).grid(row=0, column=3, sticky="ew", pady=(5, 8))
        ctk.CTkLabel(
            controls,
            text="Filtre por nome, tipo, destino da compra e data.",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=colors["muted"],
            anchor="w",
        ).grid(row=1, column=0, columnspan=4, sticky="ew")

        body, configure_columns = self.modelo_table(page, ["Operacao", "Cliente", "Data", "Pagamento", "Total", "Status", ""], [15, 21, 15, 10, 12, 11, 16])

        def details(transacao_id):
            self.tela_detalhes_transacao(transacao_id, back_command=self.tela_historico)

        def filtered_rows():
            rows = self.db_fetchall("SELECT * FROM transacoes ORDER BY data DESC, id DESC")
            query = busca_var.get().strip().lower()
            date_query = data_var.get().strip()
            destino_filter = destino_var.get().strip()
            tipo_filter = tipo_var.get().strip()

            normalized_date = None
            if date_query:
                try:
                    normalized_date = self.parse_date_value(date_query)
                except ValueError:
                    normalized_date = None

            result = []
            for row in rows:
                if tipo_filter != "TODAS" and row["tipo"] != tipo_filter:
                    continue
                destino_row = str(row["destino_compra"] or "").strip() if "destino_compra" in row.keys() else ""
                if destino_filter != "Todos destinos" and destino_row != destino_filter:
                    continue

                if date_query:
                    row_date_iso = str(row["data"])[:10]
                    row_date_br = self.format_date_br(row["data"])
                    date_ok = (
                        date_query in row_date_iso
                        or date_query in row_date_br
                        or (normalized_date is not None and normalized_date == row_date_iso)
                    )
                    if not date_ok:
                        continue

                haystack = " ".join(
                    [
                        self.transacao_label(row),
                        row["cliente_nome"] or "",
                        row["observacao"] or "",
                        destino_row,
                        str(row["data"])[:16],
                        self.format_date_br(row["data"]),
                    ]
                ).lower()
                if query and query not in haystack:
                    continue
                result.append(row)
            return result

        def delete_row(row):
            self.excluir_transacao(row, on_success=self.tela_historico)

        def edit_row(row):
            self.tela_editar_transacao(row["id"], back_command=self.tela_historico)

        def set_page(new_page):
            rows = filtered_rows()
            per_page = max(1, int(per_page_var.get()))
            total_pages = max(1, (len(rows) + per_page - 1) // per_page)
            page_state["current"] = max(1, min(new_page, total_pages))
            render()

        def reset_and_render(*_args):
            page_state["current"] = 1
            render()

        def render(*_args):
            for widget in body.winfo_children():
                widget.destroy()

            rows = filtered_rows()
            per_page = max(1, int(per_page_var.get()))
            total_pages = max(1, (len(rows) + per_page - 1) // per_page)
            page_state["current"] = max(1, min(page_state["current"], total_pages))
            start = (page_state["current"] - 1) * per_page
            end = start + per_page

            if not rows:
                self.modelo_empty(body, "Nenhuma operacao encontrada.")

            for row in rows[start:end]:
                pagamento = row["pagamento"] if "pagamento" in row.keys() and row["pagamento"] else "-"
                status = row["status"] if "status" in row.keys() and row["status"] else "FINALIZADA"
                self.modelo_row(
                    body,
                    configure_columns,
                    [self.transacao_label(row), row["cliente_nome"], row["data"][:16], pagamento, self.format_money(row["total"]), status, ""],
                    actions=[
                        ("Itens", "#4B5563", lambda rid=row["id"]: details(rid)),
                        ("Editar", colors["green"], lambda current=row: edit_row(current)),
                        ("Excluir", colors["danger"], lambda current=row: delete_row(current)),
                    ],
                    highlight_index=4,
                )

            self.modelo_pager(
                page,
                len(rows),
                row=3,
                current_page=page_state["current"],
                per_page=per_page,
                on_page_change=set_page,
                per_page_var=per_page_var,
                on_per_page_change=lambda _value: reset_and_render(),
            )

        for var in (tipo_var, destino_var, data_var, busca_var):
            var.trace_add("write", reset_and_render)
        render()

    def tela_detalhes_transacao(self, transacao_id, back_command=None):
        transacao = self.db_fetchone("SELECT * FROM transacoes WHERE id=?", (transacao_id,))
        if not transacao:
            messagebox.showerror("Operacao nao encontrada", "Nao foi possivel localizar esta operacao.")
            if back_command:
                back_command()
            return

        itens = self.db_fetchall(
            "SELECT * FROM transacao_itens WHERE transacao_id=? ORDER BY id",
            (transacao_id,),
        )
        colors = self.modelo_colors()
        page = self.modelo_page(
            self.transacao_label(transacao),
            "Detalhes completos da operacao registrada",
            back_command=back_command or self.tela_historico,
        )
        page.grid_rowconfigure(1, weight=0)
        page.grid_rowconfigure(2, weight=1)

        info_card = ctk.CTkFrame(page, fg_color="white", corner_radius=12, border_width=1, border_color=colors["line"])
        info_card.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        info_grid = ctk.CTkFrame(info_card, fg_color="transparent")
        info_grid.pack(fill="x", padx=18, pady=16)
        for index in range(4):
            info_grid.grid_columnconfigure(index, weight=1)

        info_items = [
            ("Cliente", transacao["cliente_nome"] or "-"),
            ("Data", transacao["data"][:16]),
            ("Observacao", (transacao["observacao"] or "-")[:70]),
            ("Total", self.format_money(transacao["total"])),
        ]
        for index, (label, value) in enumerate(info_items):
            box = ctk.CTkFrame(info_grid, fg_color="#FBFCFD", corner_radius=8)
            box.grid(row=0, column=index, sticky="nsew", padx=5)
            ctk.CTkLabel(box, text=label, font=ctk.CTkFont(size=11, weight="bold"), text_color=colors["muted"]).pack(anchor="w", padx=12, pady=(10, 2))
            ctk.CTkLabel(
                box,
                text=value,
                font=ctk.CTkFont(size=13, weight="bold" if index in (0, 3) else "normal"),
                text_color=colors["green"] if index == 3 else colors["text"],
                wraplength=220,
                justify="left",
            ).pack(anchor="w", padx=12, pady=(0, 10))

        items_card = ctk.CTkFrame(page, fg_color="white", corner_radius=12, border_width=1, border_color=colors["line"])
        items_card.grid(row=2, column=0, sticky="nsew")
        items_card.grid_columnconfigure(0, weight=1)
        use_scroll = len(itens) > 6
        items_card.grid_rowconfigure(1, weight=1 if use_scroll else 0)

        ctk.CTkLabel(items_card, text="Itens da Operacao", font=ctk.CTkFont(size=15, weight="bold"), text_color=colors["text"]).grid(row=0, column=0, sticky="w", padx=18, pady=(14, 8))
        if use_scroll:
            items_body = ctk.CTkScrollableFrame(items_card, fg_color="white", corner_radius=0, height=420)
        else:
            items_body = ctk.CTkFrame(items_card, fg_color="white", corner_radius=0)
        items_body.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 10))

        total_liquido = 0.0
        total_geral = 0.0
        if not itens:
            self.modelo_empty(items_body, "Nenhum item registrado nesta operacao.")
        for item in itens:
            total_liquido += float(item["peso_liquido"] or 0)
            total_geral += float(item["subtotal"] or 0)
            item_box = ctk.CTkFrame(items_body, fg_color="#FBFCFD", corner_radius=10, border_width=1, border_color=colors["line"])
            item_box.pack(fill="x", pady=(0, 8))
            ctk.CTkLabel(
                item_box,
                text=item["material_nome"],
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=colors["text"],
            ).pack(anchor="w", padx=14, pady=(12, 8))

            metrics = ctk.CTkFrame(item_box, fg_color="transparent")
            metrics.pack(fill="x", padx=10, pady=(0, 10))
            for index in range(4):
                metrics.grid_columnconfigure(index, weight=1)
            metric_items = [
                ("Peso Bruto", self.format_kg(item["peso_bruto"])),
                ("Desconto", self.format_kg(item["desconto"])),
                ("Peso Liquido", self.format_kg(item["peso_liquido"])),
                ("Valor por kg", self.format_money(item["preco_kg"])),
            ]
            for index, (label, value) in enumerate(metric_items):
                metric_box = ctk.CTkFrame(metrics, fg_color="white", corner_radius=8)
                metric_box.grid(row=0, column=index, sticky="nsew", padx=4)
                ctk.CTkLabel(metric_box, text=label, font=ctk.CTkFont(size=10, weight="bold"), text_color=colors["muted"]).pack(anchor="w", padx=10, pady=(9, 2))
                ctk.CTkLabel(metric_box, text=value, font=ctk.CTkFont(size=12, weight="bold"), text_color=colors["text"]).pack(anchor="w", padx=10, pady=(0, 9))

            subtotal_box = ctk.CTkFrame(item_box, fg_color="#EEF7EE", corner_radius=8)
            subtotal_box.pack(fill="x", padx=10, pady=(0, 10))
            ctk.CTkLabel(subtotal_box, text="Subtotal", font=ctk.CTkFont(size=11, weight="bold"), text_color=colors["muted"]).pack(anchor="w", padx=12, pady=(9, 2))
            ctk.CTkLabel(subtotal_box, text=self.format_money(item["subtotal"]), font=ctk.CTkFont(size=14, weight="bold"), text_color=colors["green"]).pack(anchor="w", padx=12, pady=(0, 10))

        resumo = ctk.CTkFrame(items_card, fg_color="#EEF7EE", corner_radius=10, border_width=1, border_color="#DDECDC")
        resumo.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 14))
        resumo.grid_columnconfigure(0, weight=1)
        resumo.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(resumo, text="Peso Liquido Total", font=ctk.CTkFont(size=11, weight="bold"), text_color=colors["muted"]).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 2))
        ctk.CTkLabel(resumo, text="Valor Total", font=ctk.CTkFont(size=11, weight="bold"), text_color=colors["muted"]).grid(row=0, column=1, sticky="w", padx=14, pady=(12, 2))
        ctk.CTkLabel(resumo, text=self.format_kg(total_liquido), font=ctk.CTkFont(size=16, weight="bold"), text_color=colors["text"]).grid(row=1, column=0, sticky="w", padx=14, pady=(0, 12))
        ctk.CTkLabel(resumo, text=self.format_money(total_geral), font=ctk.CTkFont(size=16, weight="bold"), text_color=colors["green"]).grid(row=1, column=1, sticky="w", padx=14, pady=(0, 12))

    def validar_estoque_venda_editando(self, transacao_id, novos_itens):
        antigos = self.db_fetchall(
            "SELECT material_id, material_nome, peso_liquido FROM transacao_itens WHERE transacao_id=?",
            (transacao_id,),
        )
        antigos_por_material = {}
        nomes = {}
        for item in antigos:
            material_id = item["material_id"]
            antigos_por_material[material_id] = antigos_por_material.get(material_id, 0.0) + float(item["peso_liquido"] or 0)
            nomes[material_id] = item["material_nome"]

        novos_por_material = {}
        for item in novos_itens:
            material_id = item["material_id"]
            novos_por_material[material_id] = novos_por_material.get(material_id, 0.0) + float(item["peso_liquido"] or 0)
            nomes[material_id] = item["material_nome"]

        faltas = []
        for material_id in set(list(antigos_por_material.keys()) + list(novos_por_material.keys())):
            saldo_atual = self.saldo_material(material_id)
            saldo_final = saldo_atual + antigos_por_material.get(material_id, 0.0) - novos_por_material.get(material_id, 0.0)
            if saldo_final < -1e-9:
                faltas.append(
                    f"{nomes.get(material_id, 'Material')}: disponivel {self.format_kg(saldo_atual + antigos_por_material.get(material_id, 0.0))} | venda {self.format_kg(novos_por_material.get(material_id, 0.0))}"
                )
        if faltas:
            raise ValueError("Estoque insuficiente para salvar a edicao.\n\n" + "\n".join(faltas))

    def tela_editar_transacao(self, transacao_id, back_command=None):
        transacao = self.db_fetchone("SELECT * FROM transacoes WHERE id=?", (transacao_id,))
        if not transacao:
            messagebox.showerror("Operacao nao encontrada", "Nao foi possivel localizar esta operacao.")
            if back_command:
                back_command()
            return

        itens_db = self.db_fetchall("SELECT * FROM transacao_itens WHERE transacao_id=? ORDER BY id", (transacao_id,))
        clientes = list(self.get_clientes())
        materiais = list(self.get_materiais_mais_comprados(somente_ativos=False))
        colors = self.modelo_colors()

        page = self.modelo_page(
            f"Editar {self.transacao_label(transacao)}",
            "Ajuste cliente, observacao e itens desta operacao",
            back_command=back_command or self.tela_historico,
        )
        page.grid_rowconfigure(1, weight=0)
        page.grid_rowconfigure(2, weight=1)
        page.grid_rowconfigure(3, weight=0)

        info_card = ctk.CTkFrame(page, fg_color="white", corner_radius=12, border_width=1, border_color=colors["line"])
        info_card.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        info_card.grid_columnconfigure(0, weight=1)
        info_card.grid_columnconfigure(1, weight=1)
        info_card.grid_columnconfigure(2, weight=1)
        info_card.grid_columnconfigure(3, weight=1)

        def field_label(master, text, row, column):
            ctk.CTkLabel(master, text=text, font=ctk.CTkFont(size=11, weight="bold"), text_color=colors["text"]).grid(row=row, column=column, sticky="w", padx=12, pady=(12 if row == 0 else 4, 4))

        cliente_var = ctk.StringVar(value=transacao["cliente_nome"])
        observacao_var = ctk.StringVar(value=transacao["observacao"] or "")
        destino_var = ctk.StringVar(value=(transacao["destino_compra"] or "Venda interna") if transacao["tipo"] == "COMPRA" else "")

        field_label(info_card, "Cliente", 0, 0)
        cliente_values = self.option_values(clientes)
        if transacao["cliente_nome"] not in cliente_values:
            cliente_values.append(transacao["cliente_nome"])
        ctk.CTkOptionMenu(
            info_card,
            values=cliente_values,
            variable=cliente_var,
            height=38,
            corner_radius=7,
            fg_color="white",
            button_color="white",
            button_hover_color="#EEF0EF",
            text_color=colors["text"],
        ).grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 10))

        field_label(info_card, "Tipo", 0, 1)
        tipo_box = ctk.CTkFrame(info_card, fg_color="#FBFCFD", corner_radius=8, border_width=1, border_color=colors["line"], height=38)
        tipo_box.grid(row=1, column=1, sticky="ew", padx=12, pady=(0, 10))
        tipo_box.grid_propagate(False)
        ctk.CTkLabel(tipo_box, text=transacao["tipo"].title(), font=ctk.CTkFont(size=12, weight="bold"), text_color=colors["text"]).pack(anchor="w", padx=12, pady=9)

        field_label(info_card, "Data", 0, 2)
        data_box = ctk.CTkFrame(info_card, fg_color="#FBFCFD", corner_radius=8, border_width=1, border_color=colors["line"], height=38)
        data_box.grid(row=1, column=2, sticky="ew", padx=12, pady=(0, 10))
        data_box.grid_propagate(False)
        ctk.CTkLabel(data_box, text=transacao["data"][:16], font=ctk.CTkFont(size=12), text_color=colors["text"]).pack(anchor="w", padx=12, pady=9)

        field_label(info_card, "Destino da compra" if transacao["tipo"] == "COMPRA" else "Observacao", 0, 3)
        if transacao["tipo"] == "COMPRA":
            ctk.CTkOptionMenu(
                info_card,
                values=["Venda interna", "Venda externa"],
                variable=destino_var,
                height=38,
                corner_radius=7,
                fg_color="white",
                button_color="white",
                button_hover_color="#EEF0EF",
                text_color=colors["text"],
            ).grid(row=1, column=3, sticky="ew", padx=12, pady=(0, 10))
        else:
            filler_box = ctk.CTkFrame(info_card, fg_color="#FBFCFD", corner_radius=8, border_width=1, border_color=colors["line"], height=38)
            filler_box.grid(row=1, column=3, sticky="ew", padx=12, pady=(0, 10))
            filler_box.grid_propagate(False)
            ctk.CTkLabel(filler_box, text="-", font=ctk.CTkFont(size=12), text_color=colors["muted"]).pack(anchor="w", padx=12, pady=9)

        field_label(info_card, "Observacao", 2, 0)
        observacao_entry = ctk.CTkEntry(
            info_card,
            textvariable=observacao_var,
            height=38,
            corner_radius=7,
            border_color=colors["line"],
            fg_color="white",
            placeholder_text="Digite uma observacao...",
        )
        observacao_entry.grid(row=3, column=0, columnspan=4, sticky="ew", padx=12, pady=(0, 14))

        work = ctk.CTkFrame(page, fg_color="transparent")
        work.grid(row=2, column=0, sticky="nsew")
        work.grid_columnconfigure(0, weight=5)
        work.grid_columnconfigure(1, weight=2)
        work.grid_rowconfigure(0, weight=1)

        item_panel = ctk.CTkFrame(work, fg_color="white", corner_radius=12, border_width=1, border_color=colors["line"])
        item_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        item_panel.grid_columnconfigure(0, weight=1)
        item_panel.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(item_panel, text="Itens da Operacao", font=ctk.CTkFont(size=15, weight="bold"), text_color=colors["text"]).grid(row=0, column=0, sticky="w", padx=18, pady=(12, 8))
        ctk.CTkButton(
            item_panel,
            text="+ Adicionar Material",
            width=180,
            height=34,
            corner_radius=6,
            fg_color=colors["green"],
            hover_color=colors["green_hover"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: add_item_row(),
        ).grid(row=0, column=0, sticky="e", padx=18, pady=(10, 8))

        header = ctk.CTkFrame(item_panel, fg_color="#FBFBFB", height=38, corner_radius=0)
        header.grid(row=1, column=0, sticky="ew", padx=14)
        header.grid_propagate(False)
        col_weights = [20, 13, 13, 13, 14, 15, 6]

        def configure_columns(frame):
            for index, weight in enumerate(col_weights):
                frame.grid_columnconfigure(index, weight=weight, uniform="edit_items")

        configure_columns(header)
        for index, text in enumerate(["Material", "Peso Bruto", "Desconto", "Peso Liquido", "Valor/kg", "Subtotal", ""]):
            ctk.CTkLabel(header, text=text, anchor="w" if index == 0 else "center", font=ctk.CTkFont(size=10, weight="bold"), text_color="#303942").grid(row=0, column=index, sticky="nsew", padx=6)

        body = ctk.CTkScrollableFrame(item_panel, fg_color="white", corner_radius=0)
        body.grid(row=2, column=0, sticky="nsew", padx=14, pady=(0, 10))

        summary_panel = ctk.CTkFrame(work, fg_color="white", corner_radius=12, border_width=1, border_color=colors["line"])
        summary_panel.grid(row=0, column=1, sticky="nsew")
        summary_panel.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(summary_panel, text="Resumo", font=ctk.CTkFont(size=15, weight="bold"), text_color=colors["text"]).pack(anchor="w", padx=16, pady=(12, 8))
        summary_grid = ctk.CTkFrame(summary_panel, fg_color="transparent")
        summary_grid.pack(fill="x", padx=12, pady=(0, 10))
        summary_refs = {}
        for index, (label, key, bg_color) in enumerate([
            ("Peso Bruto Total", "bruto", "#FBFCFD"),
            ("Desconto Total", "desconto", "#FBFCFD"),
            ("Peso Liquido Total", "liquido", "#EEF7EE"),
            ("Valor Total", "total", "#EEF7EE"),
        ]):
            summary_grid.grid_columnconfigure(index % 2, weight=1, uniform="summary_edit")
            box = ctk.CTkFrame(summary_grid, fg_color=bg_color, corner_radius=8)
            box.grid(row=index // 2, column=index % 2, sticky="nsew", padx=5, pady=5)
            ctk.CTkLabel(box, text=label, font=ctk.CTkFont(size=10, weight="bold"), text_color=colors["muted"]).pack(anchor="w", padx=12, pady=(10, 2))
            summary_refs[key] = ctk.CTkLabel(
                box,
                text="R$ 0,00" if key == "total" else "0,00 kg",
                font=ctk.CTkFont(size=15 if key == "total" else 13, weight="bold"),
                text_color=colors["green"] if key == "total" else colors["text"],
            )
            summary_refs[key].pack(anchor="w", padx=12, pady=(0, 10))

        material_values = self.option_values(materiais)
        item_rows = []

        def parse_or_zero(widget):
            try:
                return self.parse_decimal(widget.get())
            except ValueError:
                return 0.0

        def recalculate():
            bruto_total = 0.0
            desconto_total = 0.0
            liquido_total = 0.0
            valor_total = 0.0
            for row_data in item_rows:
                peso_bruto = parse_or_zero(row_data["peso"])
                desconto_valor = parse_or_zero(row_data["desconto"])
                preco_kg = parse_or_zero(row_data["preco"])
                peso_liquido = max(0.0, peso_bruto - desconto_valor)
                subtotal = peso_liquido * preco_kg
                row_data["liquido_label"].configure(text=f"{peso_liquido:.2f}".replace(".", ","))
                row_data["subtotal_label"].configure(text=self.format_money(subtotal))
                bruto_total += peso_bruto
                desconto_total += desconto_valor
                liquido_total += peso_liquido
                valor_total += subtotal
            summary_refs["bruto"].configure(text=self.format_kg(bruto_total))
            summary_refs["desconto"].configure(text=self.format_kg(desconto_total))
            summary_refs["liquido"].configure(text=self.format_kg(liquido_total))
            summary_refs["total"].configure(text=self.format_money(valor_total))

        def valid_items(validate=False):
            items = []
            for row_data in item_rows:
                material = self.selected_row_by_name(materiais, row_data["material_var"].get())
                touched = bool(
                    row_data["material_var"].get().strip()
                    or row_data["peso"].get().strip()
                    or row_data["desconto"].get().strip()
                    or row_data["preco"].get().strip()
                )
                if not material:
                    if validate and touched:
                        messagebox.showwarning("Material obrigatorio", "Selecione um material valido em todos os itens.")
                        return None
                    continue
                try:
                    peso_bruto = self.parse_decimal(row_data["peso"].get())
                    desconto_valor = self.parse_decimal(row_data["desconto"].get())
                    preco_kg = self.parse_decimal(row_data["preco"].get())
                except ValueError:
                    if validate:
                        messagebox.showerror("Valor invalido", "Confira peso, desconto e valor por kg.")
                        return None
                    continue
                peso_liquido = peso_bruto - desconto_valor
                if peso_liquido <= 0:
                    if validate and touched:
                        messagebox.showerror("Peso invalido", "O peso liquido precisa ser maior que zero.")
                        return None
                    continue
                items.append(
                    {
                        "material_id": material["id"],
                        "material_nome": material["nome"],
                        "peso_bruto": peso_bruto,
                        "desconto": desconto_valor,
                        "peso_liquido": peso_liquido,
                        "preco_kg": preco_kg,
                        "subtotal": peso_liquido * preco_kg,
                    }
                )
            return items

        def remove_row(row_data):
            if row_data in item_rows:
                item_rows.remove(row_data)
            row_data["frame"].destroy()
            recalculate()

        def add_item_row(existing=None):
            row_frame = ctk.CTkFrame(body, fg_color="white", height=66, corner_radius=0)
            row_frame.pack(fill="x", pady=(0, 3))
            row_frame.grid_propagate(False)
            configure_columns(row_frame)

            material_name = existing["material_nome"] if existing else material_values[0]
            if material_name not in material_values:
                material_values.append(material_name)
            material_var = ctk.StringVar(value=material_name)
            material_menu = ctk.CTkOptionMenu(
                row_frame,
                values=material_values,
                variable=material_var,
                height=32,
                corner_radius=6,
                fg_color="white",
                button_color="white",
                button_hover_color="#EEF0EF",
                text_color=colors["text"],
            )
            material_menu.grid(row=0, column=0, sticky="ew", padx=4, pady=(5, 0))

            peso = ctk.CTkEntry(row_frame, height=32, corner_radius=6, border_color=colors["line"], fg_color="white")
            peso.grid(row=0, column=1, sticky="ew", padx=4, pady=(5, 0))
            desconto = ctk.CTkEntry(row_frame, height=32, corner_radius=6, border_color=colors["line"], fg_color="white")
            desconto.grid(row=0, column=2, sticky="ew", padx=4, pady=(5, 0))
            liquido_box = ctk.CTkFrame(row_frame, height=32, fg_color="#EEF7EE", corner_radius=6, border_width=1, border_color=colors["line"])
            liquido_box.grid(row=0, column=3, sticky="ew", padx=4, pady=(5, 0))
            liquido_box.grid_propagate(False)
            liquido_label = ctk.CTkLabel(liquido_box, text="0,00", font=ctk.CTkFont(size=11, weight="bold"), text_color=colors["text"])
            liquido_label.pack(expand=True)
            preco = ctk.CTkEntry(row_frame, height=32, corner_radius=6, border_color=colors["line"], fg_color="white")
            preco.grid(row=0, column=4, sticky="ew", padx=4, pady=(5, 0))
            subtotal_box = ctk.CTkFrame(row_frame, height=32, fg_color="white", corner_radius=6, border_width=1, border_color=colors["line"])
            subtotal_box.grid(row=0, column=5, sticky="ew", padx=4, pady=(5, 0))
            subtotal_box.grid_propagate(False)
            subtotal_label = ctk.CTkLabel(subtotal_box, text="R$ 0,00", font=ctk.CTkFont(size=11, weight="bold"), text_color=colors["green"])
            subtotal_label.pack(expand=True)
            actions = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions.grid(row=0, column=6, sticky="nsew", padx=2, pady=(5, 0))

            row_data = {
                "frame": row_frame,
                "material_var": material_var,
                "peso": peso,
                "desconto": desconto,
                "preco": preco,
                "liquido_label": liquido_label,
                "subtotal_label": subtotal_label,
            }

            ctk.CTkButton(
                actions,
                text="X",
                width=30,
                height=30,
                corner_radius=6,
                fg_color="#FFF0F0",
                hover_color="#FFE0E0",
                text_color=colors["danger"],
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda data=row_data: remove_row(data),
            ).pack()

            for widget in (peso, desconto, preco):
                widget.bind("<KeyRelease>", lambda _event: recalculate())
                widget.bind("<FocusOut>", lambda _event: recalculate())
            material_menu.configure(command=lambda _value: recalculate())

            if existing:
                peso.insert(0, f"{float(existing['peso_bruto']):.2f}".replace(".", ","))
                desconto.insert(0, f"{float(existing['desconto']):.2f}".replace(".", ","))
                preco.insert(0, f"{float(existing['preco_kg']):.2f}".replace(".", ","))

            item_rows.append(row_data)
            recalculate()

        def save_edit():
            cliente = self.selected_row_by_name(clientes, cliente_var.get())
            if not cliente:
                messagebox.showwarning("Cliente obrigatorio", "Selecione um cliente valido.")
                return
            items = valid_items(validate=True)
            if items is None:
                return
            if not items:
                messagebox.showwarning("Itens obrigatorios", "Adicione pelo menos um material.")
                return
            if transacao["tipo"] == "VENDA":
                try:
                    self.validar_estoque_venda_editando(transacao["id"], items)
                except ValueError as exc:
                    messagebox.showerror("Estoque insuficiente", str(exc))
                    return

            total = sum(item["subtotal"] for item in items)
            observacao_texto = observacao_var.get().strip()
            destino_texto = destino_var.get().strip() if transacao["tipo"] == "COMPRA" else ""

            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                cur = conn.cursor()
                cur.execute(
                    "UPDATE transacoes SET cliente_id=?, cliente_nome=?, total=?, observacao=?, destino_compra=? WHERE id=?",
                    (cliente["id"], cliente["nome"], total, observacao_texto, destino_texto, transacao["id"]),
                )
                cur.execute("DELETE FROM transacao_itens WHERE transacao_id=?", (transacao["id"],))
                for item in items:
                    cur.execute(
                        """
                        INSERT INTO transacao_itens
                        (transacao_id, material_id, material_nome, peso_bruto, desconto, peso_liquido, preco_kg, subtotal)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            transacao["id"],
                            item["material_id"],
                            item["material_nome"],
                            item["peso_bruto"],
                            item["desconto"],
                            item["peso_liquido"],
                            item["preco_kg"],
                            item["subtotal"],
                        ),
                    )

                comprovante = cur.execute(
                    "SELECT numero FROM comprovantes WHERE transacao_id=?",
                    (transacao["id"],),
                ).fetchone()
                if comprovante:
                    conteudo = self.montar_comprovante(
                        comprovante[0],
                        transacao["tipo"],
                        cliente["nome"],
                        transacao["data"],
                        items,
                        total,
                        observacao_texto,
                    )
                    cur.execute(
                        "UPDATE comprovantes SET cliente_nome=?, total=?, conteudo=? WHERE transacao_id=?",
                        (cliente["nome"], total, conteudo, transacao["id"]),
                    )

            self.log_notification(
                str(transacao["tipo"]).strip().lower(),
                "Operacao atualizada",
                f"{self.transacao_label(transacao)} foi atualizada com sucesso.",
            )
            messagebox.showinfo("Operacao atualizada", "A operacao foi atualizada com sucesso.")
            if back_command:
                back_command()
            else:
                self.tela_historico()

        for item in itens_db:
            add_item_row(item)
        if not itens_db:
            add_item_row()
        recalculate()

        footer = ctk.CTkFrame(page, fg_color="transparent", height=56)
        footer.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        footer.grid_propagate(False)
        ctk.CTkButton(
            footer,
            text="Cancelar",
            width=150,
            height=42,
            corner_radius=6,
            fg_color="#EFEFEF",
            hover_color="#E2E2E2",
            text_color=colors["text"],
            font=ctk.CTkFont(size=14, weight="bold"),
            command=back_command or self.tela_historico,
        ).pack(side="right", padx=(0, 14), pady=7)
        ctk.CTkButton(
            footer,
            text="Salvar Alteracoes",
            width=220,
            height=42,
            corner_radius=6,
            fg_color=colors["green"],
            hover_color=colors["green_hover"],
            font=ctk.CTkFont(size=14, weight="bold"),
            command=save_edit,
        ).pack(side="right", pady=7)

    def excluir_transacao(self, row, on_success=None):
        if not messagebox.askyesno("Excluir operacao", f"Deseja excluir {self.transacao_label(row)}?"):
            return
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("DELETE FROM comprovantes WHERE transacao_id=?", (row["id"],))
            conn.execute("DELETE FROM transacao_itens WHERE transacao_id=?", (row["id"],))
            conn.execute("DELETE FROM transacoes WHERE id=?", (row["id"],))
        self.log_notification(
            str(row["tipo"]).strip().lower(),
            "Operacao excluida",
            f"{self.transacao_label(row)} foi excluida do sistema.",
        )
        messagebox.showinfo("Operacao excluida", "A operacao foi excluida com sucesso.")
        if on_success:
            on_success()

    def consolidar_itens_comprovante(self, itens):
        agrupados = {}
        ordem = []

        for item in itens:
            material_id = item["material_id"] if "material_id" in item.keys() else item.get("material_id")
            material_nome = " ".join(str(item["material_nome"]).strip().split())
            chave = material_id if material_id is not None else material_nome.lower()

            if chave not in agrupados:
                ordem.append(chave)
                agrupados[chave] = {
                    "material_id": material_id,
                    "material_nome": material_nome,
                    "desconto": 0.0,
                    "peso_liquido": 0.0,
                    "subtotal": 0.0,
                    "preco_kg": float(item["preco_kg"]),
                }

            agrupados[chave]["desconto"] += float(item["desconto"])
            agrupados[chave]["peso_liquido"] += float(item["peso_liquido"])
            agrupados[chave]["subtotal"] += float(item["subtotal"])

        consolidado = []
        for chave in ordem:
            item = agrupados[chave]
            peso_liquido = item["peso_liquido"]
            item["preco_kg"] = (item["subtotal"] / peso_liquido) if peso_liquido > 0 else float(item["preco_kg"])
            consolidado.append(item)
        return consolidado

    def montar_comprovante(self, numero, tipo, cliente, data, itens, total, observacao):
        data_texto = str(data)
        data_br = self.format_date_br(data_texto)
        hora = data_texto[11:16] if len(data_texto) >= 16 else ""
        itens_consolidados = self.consolidar_itens_comprovante(itens)
        peso_total = sum(float(item["peso_liquido"]) for item in itens_consolidados)
        largura_linha = 38
        cliente_texto = " ".join(str(cliente).strip().split())[:25]

        linhas = [
            "VR VINHESQUE RECICLAGEM",
            "SUSTENTABILIDADE QUE GERA VALOR",
            "",
            f"CONTROLE {numero}",
            f"DATA     {data_br} {hora}".rstrip(),
            "=" * largura_linha,
            "DADOS DA OPERACAO",
            f"TIPO     {tipo.title()}",
            f"CLIENTE  {cliente_texto}",
            "=" * largura_linha,
            "PRODUTOS",
            "MATERIAL|QTD|DESC|V/KG|TOTAL",
            "-" * largura_linha,
        ]

        for item in itens_consolidados:
            descricao = " ".join(str(item["material_nome"]).strip().split())
            quantidade = self.format_kg(item["peso_liquido"]).replace(" kg", "")
            desconto = self.format_kg(item["desconto"]).replace(" kg", "")
            valor_kg = self.format_money(item["preco_kg"]).replace("R$ ", "")
            subtotal = self.format_money(item["subtotal"]).replace("R$ ", "")
            linhas.append(f"{descricao}|{quantidade}|{desconto}|{valor_kg}|{subtotal}")

        linhas.extend([
            "-" * largura_linha,
            f"{'PESO TOTAL':<23}{self.format_kg(peso_total):>13}",
            f"{'TOTAL':<23}{self.format_money(total):>13}",
            "",
            "Obrigado pela preferencia!",
        ])

        if observacao:
            linhas.extend(["", "OBSERVACOES"])
            for linha_obs in self.wrap_comprovante_line(str(observacao).strip(), 30):
                linhas.append(linha_obs)

        return "\n".join(linhas)

    def finalizar_operacao(self, tipo, cliente_nome, observacao, gerar_comprovante=True, cliente_documento="", cliente_telefone="", destino_compra=""):
        cliente = self.cliente_por_nome_ou_criar(cliente_nome, tipo, cliente_telefone, cliente_documento)
        if not cliente:
            messagebox.showwarning("Cliente obrigatorio", "Digite o nome do cliente.")
            return
        if not self.current_items:
            messagebox.showwarning("Itens obrigatorios", "Adicione pelo menos um material.")
            return

        total = sum(item["subtotal"] for item in self.current_items)
        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO transacoes (tipo, cliente_id, cliente_nome, data, total, observacao, destino_compra) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (tipo, cliente["id"], cliente["nome"], data, total, observacao, destino_compra if tipo == "COMPRA" else ""),
            )
            transacao_id = cur.lastrowid
            for item in self.current_items:
                cur.execute(
                    """
                    INSERT INTO transacao_itens
                    (transacao_id, material_id, material_nome, peso_bruto, desconto, peso_liquido, preco_kg, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        transacao_id,
                        item["material_id"],
                        item["material_nome"],
                        item["peso_bruto"],
                        item["desconto"],
                        item["peso_liquido"],
                        item["preco_kg"],
                        item["subtotal"],
                    ),
                )
            if gerar_comprovante:
                numero = f"{tipo[0]}-{transacao_id:06d}"
                conteudo = self.montar_comprovante(numero, tipo, cliente["nome"], data, self.current_items, total, observacao)
                cur.execute(
                    "INSERT INTO comprovantes (transacao_id, numero, tipo, cliente_nome, data, total, conteudo) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (transacao_id, numero, tipo, cliente["nome"], data, total, conteudo),
                )

        tipo_lower = str(tipo).strip().lower()
        destino_info = f" ({destino_compra})" if tipo == "COMPRA" and destino_compra else ""
        self.log_notification(
            tipo_lower,
            f"Nova {tipo_lower} registrada",
            f"{tipo.title()}{destino_info} #{transacao_id} para {cliente['nome']} no valor de {self.format_money(total)}.",
        )
        if gerar_comprovante:
            self.log_notification(
                "comprovante",
                "Novo comprovante emitido",
                f"{numero} foi gerado para {cliente['nome']}.",
            )

        auto_print = gerar_comprovante and tipo == "VENDA"
        if gerar_comprovante:
            caminho = self.salvar_comprovante_txt(numero, conteudo)
        else:
            messagebox.showinfo("Operacao salva", f"{tipo.title()} salva com sucesso.")

        self.current_items = []
        if not gerar_comprovante:
            self.build_ui()
            return

        if auto_print and self.imprimir_comprovante(numero, caminho, show_success=False):
            self.build_ui()
            return

        self.tela_comprovante(numero, conteudo, caminho)

    def criar_imagem_comprovante(self, conteudo):
        config = self.comprovante_print_config()
        layout_width_mm = min(config["printable_width_mm"], config.get("content_width_mm", config["printable_width_mm"]))
        width = self.mm_to_px(layout_width_mm, config["render_dpi"])
        padding = 12
        top_margin = 6
        bottom_margin = 18

        raw_lines = []
        for raw_line in conteudo.splitlines():
            stripped = raw_line.strip()
            if not stripped:
                raw_lines.append(("blank", ""))
                continue
            if "|" in stripped:
                parts = [part.strip() for part in stripped.split("|")]
                if len(parts) == 5:
                    if parts[0].upper() == "MATERIAL" and parts[1].upper() == "QTD":
                        raw_lines.append(("table_header", parts))
                    else:
                        raw_lines.append(("table_item", parts))
                    continue
            if set(stripped) <= {"=", "-"}:
                raw_lines.append(("rule", stripped))
                continue
            if stripped == "VR VINHESQUE RECICLAGEM":
                raw_lines.append(("company", stripped))
                continue
            if stripped in {"SUSTENTABILIDADE QUE GERA VALOR"}:
                raw_lines.append(("subtitle", stripped))
                continue
            if stripped.startswith("COMPROVANTE DE "):
                raw_lines.append(("title", stripped))
                continue
            if stripped.startswith(("CONTROLE", "DATA", "TIPO", "CLIENTE")):
                raw_lines.append(("meta", stripped))
                continue
            if stripped in {"DADOS DA OPERACAO", "PRODUTOS", "ITENS", "OBSERVACOES", "OBRIGADO PELA PREFERENCIA", "Obrigado pela preferencia!"}:
                raw_lines.append(("section", stripped))
                continue
            if stripped.startswith(("PESO TOTAL", "SUBTOTAL")):
                raw_lines.append(("summary", stripped))
                continue
            if stripped.startswith("TOTAL"):
                raw_lines.append(("total", stripped))
                continue
            if stripped.startswith(("DESCRICAO", "COD  DESCRICAO")):
                raw_lines.append(("table_header", stripped))
                continue
            raw_lines.append(("text", stripped))

        measure = ImageDraw.Draw(Image.new("RGB", (10, 10), "white"))
        available_text_width = width - (padding * 2)
        usable_width = width - (padding * 2)
        numeric_column_rights = [
            padding + int(usable_width * 0.44),
            padding + int(usable_width * 0.58),
            padding + int(usable_width * 0.72),
            width - padding,
        ]

        def fit_font(lines, start_size, min_size, bold=False):
            valid_lines = [line for line in lines if line]
            if not valid_lines:
                return self.comprovante_font(start_size, bold=bold)
            for size in range(start_size, min_size - 1, -1):
                candidate = self.comprovante_font(size, bold=bold)
                if max(measure.textlength(line, font=candidate) for line in valid_lines) <= available_text_width:
                    return candidate
            return self.comprovante_font(min_size, bold=bold)

        company_font = fit_font([text for kind, text in raw_lines if kind == "company"], 26, 20, bold=True)
        subtitle_font = fit_font([text for kind, text in raw_lines if kind == "subtitle"], 18, 14, bold=False)
        title_font = fit_font([text for kind, text in raw_lines if kind == "title"], 24, 18, bold=True)
        section_font = fit_font([text for kind, text in raw_lines if kind == "section"], 22, 17, bold=True)
        meta_font = fit_font([text for kind, text in raw_lines if kind == "meta"], 21, 16, bold=False)
        table_font = fit_font([text for kind, text in raw_lines if kind in {"text", "summary"}], 20, 15, bold=False)
        total_font = fit_font([text for kind, text in raw_lines if kind == "total"], 26, 18, bold=True)
        table_header_font = self.comprovante_font(18, bold=True)
        item_desc_font = self.comprovante_font(21, bold=True)
        item_value_font = self.comprovante_font(20, bold=False)
        qty_reserved_width = max(
            measure.textlength("999,99", font=item_value_font),
            measure.textlength("9999,99", font=item_value_font),
        )
        description_max_width = max(120, int(numeric_column_rights[0] - padding - qty_reserved_width - 2))

        receipt_logo = self.comprovante_logo_image(int(width * 0.58), 150)
        show_company_text = receipt_logo is None
        prepared_lines = []
        for kind, payload in raw_lines:
            if kind == "company" and not show_company_text:
                continue
            if kind == "table_item":
                descricao_linhas = self.wrap_comprovante_text_width(payload[0], item_desc_font, description_max_width, measure)
                prepared_lines.append((kind, payload, descricao_linhas))
                continue
            prepared_lines.append((kind, payload, None))

        logo_block_height = receipt_logo.height + 24 if receipt_logo else 0

        line_heights = {
            "blank": 10,
            "rule": 14,
            "company": 32,
            "subtitle": 22,
            "title": 30,
            "meta": 26,
            "section": 28,
            "summary": 26,
            "total": 38,
            "table_header": 34,
            "text": 26,
        }
        height = top_margin + logo_block_height + bottom_margin
        for kind, _payload, extra in prepared_lines:
            if kind == "table_item":
                height += max(36, (len(extra or [""]) * 23) + 8)
            else:
                height += line_heights.get(kind, 22)
        receipt = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(receipt)

        if receipt_logo:
            logo_x = (width - receipt_logo.width) // 2
            receipt.paste(receipt_logo, (logo_x, top_margin), receipt_logo)

        y = top_margin + logo_block_height

        for kind, payload, extra in prepared_lines:
            line_height = line_heights.get(kind, 22)
            if kind == "blank":
                y += line_height
                continue

            if kind == "rule":
                line_y = y + (line_height // 2)
                draw.line(
                    (padding, line_y, width - padding, line_y),
                    fill="#111111",
                    width=2 if "=" in payload else 1,
                )
                y += line_height
                continue

            if kind == "table_header":
                if isinstance(payload, str):
                    draw.text((padding, y), payload, fill="#111111", font=table_header_font)
                    y += line_height
                    continue
                left_label, *header_labels = payload
                draw.text((padding, y), left_label, fill="#111111", font=table_header_font)
                for label, col_right in zip(header_labels, numeric_column_rights):
                    text_width = draw.textlength(label, font=table_header_font)
                    draw.text((col_right - text_width, y), label, fill="#111111", font=table_header_font)
                y += line_height
                continue

            if kind == "table_item":
                descricao, quantidade, desconto, valor_kg, subtotal = payload
                descricao_linhas = extra or [descricao]
                row_top = y
                for index, descricao_linha in enumerate(descricao_linhas):
                    draw.text((padding, row_top + (index * 23)), descricao_linha, fill="#111111", font=item_desc_font)
                for value, col_right in zip((quantidade, desconto, valor_kg, subtotal), numeric_column_rights):
                    text_width = draw.textlength(value, font=item_value_font)
                    draw.text((col_right - text_width, row_top), value, fill="#111111", font=item_value_font)
                y += max(36, (len(descricao_linhas) * 23) + 8)
                continue

            text = payload

            if kind == "company":
                active_font = company_font
            elif kind == "subtitle":
                active_font = subtitle_font
            elif kind == "title":
                active_font = title_font
            elif kind == "section":
                active_font = section_font
            elif kind == "meta":
                active_font = meta_font
            elif kind == "total":
                active_font = total_font
            else:
                active_font = table_font

            if kind == "total":
                text_width = draw.textlength(text, font=active_font)
                draw.text(((width - text_width) / 2, y), text, fill="#111111", font=active_font)
            elif kind in {"company", "subtitle", "title", "section"}:
                text_width = draw.textlength(text, font=active_font)
                draw.text(((width - text_width) / 2, y), text, fill="#111111", font=active_font)
            else:
                draw.text((padding, y), text, fill="#111111", font=active_font)
            y += line_height

        return receipt

    def salvar_comprovante_visual(self, numero, conteudo):
        config = self.comprovante_print_config()
        pasta = os.path.join(self.script_dir, "comprovantes")
        os.makedirs(pasta, exist_ok=True)
        png_path = os.path.join(pasta, f"{numero}.png")
        imagem = self.criar_imagem_comprovante(conteudo)
        imagem.save(png_path, dpi=(config["render_dpi"], config["render_dpi"]))
        return png_path

    def default_printer_name(self):
        if os.name != "nt":
            return None
        try:
            import ctypes
            from ctypes import wintypes
            winspool = ctypes.WinDLL("winspool.drv")

            size = wintypes.DWORD(0)
            winspool.GetDefaultPrinterW(None, ctypes.byref(size))
            if size.value <= 1:
                return None

            buffer = ctypes.create_unicode_buffer(size.value)
            if not winspool.GetDefaultPrinterW(buffer, ctypes.byref(size)):
                return None
            return buffer.value
        except Exception:
            return None

    def imprimir_comprovante(self, numero, caminho=None, show_success=True):
        png_path = os.path.join(self.script_dir, "comprovantes", f"{numero}.png")
        caminho = png_path if os.path.exists(png_path) else caminho or png_path
        if not os.path.exists(caminho):
            messagebox.showwarning("Comprovante nao encontrado", "Salve o comprovante antes de imprimir.")
            return False
        if os.name != "nt":
            messagebox.showwarning("Impressao indisponivel", "A impressao direta esta disponivel apenas no Windows.")
            return False

        try:
            import ctypes
            from ctypes import wintypes

            printer_name = self.default_printer_name()
            if not printer_name:
                raise RuntimeError("Nenhuma impressora padrao configurada.")

            class DOCINFOW(ctypes.Structure):
                _fields_ = [
                    ("cbSize", ctypes.c_int),
                    ("lpszDocName", wintypes.LPCWSTR),
                    ("lpszOutput", wintypes.LPCWSTR),
                    ("lpszDatatype", wintypes.LPCWSTR),
                    ("fwType", wintypes.DWORD),
                ]

            HORZRES = 8
            VERTRES = 10
            LOGPIXELSX = 88
            LOGPIXELSY = 90
            PHYSICALOFFSETX = 112
            PHYSICALOFFSETY = 113

            gdi32 = ctypes.windll.gdi32
            hdc = gdi32.CreateDCW("WINSPOOL", printer_name, None, None)
            if not hdc:
                raise RuntimeError("Nao foi possivel acessar a impressora padrao.")

            config = self.comprovante_print_config()
            doc_started = False
            page_started = False
            try:
                with Image.open(caminho) as source_image:
                    imagem = source_image.convert("RGB")

                printable_width = gdi32.GetDeviceCaps(hdc, HORZRES)
                printable_height = gdi32.GetDeviceCaps(hdc, VERTRES)
                dpi_x = gdi32.GetDeviceCaps(hdc, LOGPIXELSX) or config["render_dpi"]
                dpi_y = gdi32.GetDeviceCaps(hdc, LOGPIXELSY) or config["render_dpi"]
                offset_x = gdi32.GetDeviceCaps(hdc, PHYSICALOFFSETX)
                offset_y = gdi32.GetDeviceCaps(hdc, PHYSICALOFFSETY)

                target_width = min(
                    printable_width,
                    self.mm_to_px(config.get("content_width_mm", config["printable_width_mm"]), dpi_x),
                )
                target_height_limit = min(printable_height, self.mm_to_px(config["paper_height_mm"], dpi_y))
                scale = target_width / float(imagem.width)
                draw_width = max(1, int(round(imagem.width * scale)))
                draw_height = max(1, int(round(imagem.height * scale)))

                if draw_height > target_height_limit:
                    fit_scale = target_height_limit / float(draw_height)
                    draw_width = max(1, int(round(draw_width * fit_scale)))
                    draw_height = max(1, int(round(draw_height * fit_scale)))

                x = offset_x + max(0, (printable_width - draw_width) // 2)
                y = offset_y

                doc_info = DOCINFOW()
                doc_info.cbSize = ctypes.sizeof(DOCINFOW)
                doc_info.lpszDocName = f"Comprovante {numero}"
                doc_info.lpszOutput = None
                doc_info.lpszDatatype = None
                doc_info.fwType = 0

                if gdi32.StartDocW(hdc, ctypes.byref(doc_info)) <= 0:
                    raise RuntimeError("Nao foi possivel iniciar a impressao.")
                doc_started = True
                if gdi32.StartPage(hdc) <= 0:
                    raise RuntimeError("Nao foi possivel iniciar a pagina de impressao.")
                page_started = True

                dib = ImageWin.Dib(imagem)
                dib.draw(hdc, (x, y, x + draw_width, y + draw_height))

                if gdi32.EndPage(hdc) <= 0:
                    raise RuntimeError("Nao foi possivel finalizar a pagina de impressao.")
                page_started = False
                if gdi32.EndDoc(hdc) <= 0:
                    raise RuntimeError("Nao foi possivel concluir o envio para a impressora.")
                doc_started = False
            except Exception:
                if page_started or doc_started:
                    try:
                        gdi32.AbortDoc(hdc)
                    except Exception:
                        pass
                raise
            finally:
                gdi32.DeleteDC(hdc)

            if show_success:
                messagebox.showinfo("Impressao enviada", "O comprovante foi enviado para a impressora padrao.")
            return True
        except Exception as exc:
            messagebox.showwarning(
                "Impressora nao configurada",
                "O comprovante ja esta salvo.\n\n"
                "Quando precisarem, abram a tela de comprovantes e tentem imprimir novamente.\n\n"
                f"Detalhe: {exc}",
            )
            return False


class MenuCard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        title,
        subtitle,
        icon="",
        icon_image=None,
        color="#EAF2E7",
        button_color="#84C75B",
        command=None,
        *args,
        **kwargs
    ):
        super().__init__(master, fg_color="white", corner_radius=22, *args, **kwargs)
        self.grid_propagate(False)
        self.command = command if command else lambda: None
        self.default_border_color = "#E7EEE4"
        self.hover_border_color = "#D4E6D1"
        self.default_fg = "white"
        self.hover_fg = "#FBFDFB"
        self.configure(border_width=1, border_color=self.default_border_color)

        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=18, pady=13)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        self.icon_shadow = ctk.CTkFrame(
            content_frame,
            width=60,
            height=60,
            fg_color="transparent",
            corner_radius=20,
        )
        self.icon_shadow.grid(row=0, column=0, padx=(0, 12), sticky="w")
        self.icon_shadow.grid_propagate(False)

        self.icon_box = ctk.CTkFrame(
            self.icon_shadow,
            width=60,
            height=60,
            fg_color=color,
            corner_radius=20,
            border_width=0,
        )
        self.icon_box.place(relx=0.5, rely=0.5, anchor="center")
        self.icon_box.grid_propagate(False)
        self.icon_image = icon_image

        self.icon_label = ctk.CTkLabel(
            self.icon_box,
            text="" if self.icon_image is not None else icon,
            image=self.icon_image,
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=button_color
        )
        self.icon_label.pack(expand=True)

        text_box = ctk.CTkFrame(content_frame, fg_color="transparent")
        text_box.grid(row=0, column=1, sticky="nsew", pady=(2, 20), padx=(0, 20))
        text_box.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            text_box,
            text=title,
            anchor="w",
            justify="left",
            font=ctk.CTkFont(family="Poppins SemiBold", size=14, weight="bold"),
            text_color="#1B1F23",
            wraplength=162,
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        self.subtitle_label = ctk.CTkLabel(
            text_box,
            text=subtitle,
            anchor="w",
            justify="left",
            font=ctk.CTkFont(family="Inter", size=11, weight="normal"),
            text_color="#59636E",
            wraplength=162
        )
        self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(6, 0))

        self.arrow_box = ctk.CTkButton(
            self,
            text="›",
            width=28,
            height=28,
            corner_radius=14,
            fg_color=color,
            hover_color=color,
            text_color=button_color,
            font=ctk.CTkFont(size=18, weight="bold"),
            border_width=0,
            command=self.command,
        )
        self.arrow_box.place(relx=1.0, rely=1.0, x=-12, y=-12, anchor="se")
        self.arrow_label = self.arrow_box

        self._bind_click_recursive(self)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        for widget in (self.icon_shadow, self.icon_box, self.icon_label, self.title_label, self.subtitle_label, self.arrow_box):
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
        try:
            self.configure(cursor="hand2")
            for widget in (self.icon_shadow, self.icon_box, self.icon_label, self.title_label, self.subtitle_label, self.arrow_box):
                widget.configure(cursor="hand2")
        except Exception:
            pass

    def _bind_click_recursive(self, widget):
        widget.bind("<Button-1>", lambda _event: self.command())
        for child in widget.winfo_children():
            self._bind_click_recursive(child)

    def _on_enter(self, _event=None):
        self.configure(border_color=self.hover_border_color, fg_color=self.hover_fg)

    def _on_leave(self, _event=None):
        self.configure(border_color=self.default_border_color, fg_color=self.default_fg)


if __name__ == "__main__":
    app = VRReciclagemApp()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        app.destroy()
