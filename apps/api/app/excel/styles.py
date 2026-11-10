from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

THIN = Side(style="thin", color="000000")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

TITLE_FONT = Font(name="Calibri", size=14, bold=True)
HEADER_FONT = Font(name="Calibri", size=11, bold=True)
BOLD = Font(name="Calibri", size=11, bold=True)
BODY_FONT = Font(name="Calibri", size=11)

HEADER_FILL = PatternFill("solid", start_color="D9E1F2")
SUBTOTAL_FILL = PatternFill("solid", start_color="F2F2F2")
GRAND_FILL = PatternFill("solid", start_color="FFF2CC")

CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)
RIGHT = Alignment(horizontal="right", vertical="center")
TOP_LEFT = Alignment(horizontal="left", vertical="top", wrap_text=True)

MONEY_FMT = "#,##0.00"
PERCENT_FMT = "0%"
MONTH_FMT = "mmm-yy"
INT_FMT = "0"
QTY_FMT = "#,##0.###"
