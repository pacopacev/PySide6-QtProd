from datetime import date

import win32print
import time


class PrintLabel:
    # max bytes per QR version 1..10, byte mode, error level Q
    QR_CAPACITY_Q = [11, 20, 32, 46, 60, 74, 86, 108, 130, 151]

    def __init__(self, printer_name="ZDesigner GC420t (EPL)",
                 label_width_mm=72, label_height_mm=46,
                 dpi_dots_per_mm=8, qr_mag=6, margin=21):
        self.printer_name = printer_name
        self.label_width = label_width_mm * dpi_dots_per_mm    # 576
        self.label_height = label_height_mm * dpi_dots_per_mm  # 368
        self.qr_mag = qr_mag
        self.margin = margin

    @staticmethod
    def zpl_safe(text):
        return str(text).replace("^", " ").replace("~", " ")

    def qr_size(self, data):
        n = len(data.encode("ascii", errors="replace"))
        for version, cap in enumerate(self.QR_CAPACITY_Q, start=1):
            if n <= cap:
                return (17 + 4 * version) * self.qr_mag
        raise ValueError("QR data too long")

    def build_zpl(self, product, ma, qty, job, barcode, pon, copies=1, date=date):
        product = self.zpl_safe(product)
        ma = self.zpl_safe(ma)
        qty = self.zpl_safe(qty)
        job = self.zpl_safe(job)
        
        pon = self.zpl_safe(pon)
        
        barcode = self.zpl_safe(f"{product}-{ma}-{job}-{qty}-{pon}-{date}")
        barcode = self.zpl_safe(barcode)

        m = self.margin
        qy = 150
        modules = self.qr_size(barcode) // self.qr_mag
        max_qr_width = self.label_width - 2 * m
        max_qr_height = self.label_height - qy - m
        qr_mag = min(self.qr_mag, max_qr_width // modules, max_qr_height // modules)
        if qr_mag < 1:
            raise ValueError("QR code does not fit on the label")

        size = modules * qr_mag
        qx = self.label_width - m - size      # right-aligned QR
        block_w = qx - 2 * m

        return (
            "^XA\n"
            "^LH8,8\n"
            "^LS0\n"
            f"^PW{self.label_width}\n"
            f"^LL{self.label_height}\n"
            f"^FO1,19^GB{self.label_width - 10},{self.label_height - 10},3,B,1^FS\n"
            f"^PQ{int(copies)}\n"
            f"^FO{m},48^FB{block_w},1,0,L,0^A0N,32,32^FDPRODUCT: {product}^FS\n"
            f"^FO{m},93^FB{block_w},1,0,L,0^A0N,32,32^FDMA: {ma}^FS\n"
            f"^FO{m},138^FB{block_w},1,0,L,0^A0N,32,32^FDQTY: {qty}^FS\n"
            f"^FO{m},183^FB{block_w},1,0,L,0^A0N,32,32^FDJO: {job}^FS\n"
            f"^FO{qx},{qy}^BQN,2,{qr_mag}^FDQA,{barcode}^FS\n"
            f"^FO{m},296^FB{block_w},1,0,L,0^A0N,28,28^FDPON: {pon}^FS\n"
            f"^FO{m},328^FB{block_w},1,0,L,0^A0N,28,28^FDDATE: {date}^FS\n"
            "^XZ\n"
        )

    def print_label(self, product, ma, qty, job, barcode, pon, copies=1, date=date ):
        zpl = self.build_zpl(product, ma, qty, job, barcode, pon,  copies,date,)

        printer = win32print.OpenPrinter(self.printer_name)
        try:
            win32print.StartDocPrinter(printer, 1, ("Zebra Label", None, "RAW"))
            try:
                win32print.StartPagePrinter(printer)
                win32print.WritePrinter(printer, zpl.encode("ascii", errors="replace"))
                win32print.EndPagePrinter(printer)
            finally:
                win32print.EndDocPrinter(printer)
        finally:
            win32print.ClosePrinter(printer)


if __name__ == "__main__":
    PrintLabel().print_label(
        product="7283556630",
        ma="10.21.56996A",
        qty=1,
        job="265214",
        barcode="",
        pon="I10131",
        
        copies=1,
        date=time.strftime("%d.%m.%Y")
    )