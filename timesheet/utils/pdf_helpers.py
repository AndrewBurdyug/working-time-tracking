import os.path

from reportlab.pdfgen import canvas
from reportlab.lib.colors import green, black, gray

from django.conf import settings


def inverse_y(self, y):
    return 832 - y


def draw_header(self):
    self.pdf_filename = os.path.join(settings.INVOICES_DIR, self.title)
    self.pdf = canvas.Canvas(self.pdf_filename)

    self.pdf.setFillColor(green)
    self.pdf.setFont("Helvetica", 16, leading=True)
    self.pdf.drawString(30, self.inverse_y(30), "Invoice")

    self.pdf.setStrokeColor(gray)
    self.pdf.rect(20, self.inverse_y(60), 520, 20, stroke=1)
    self.pdf.rect(20, self.inverse_y(60), 130, 20, stroke=1)
    self.pdf.rect(20, self.inverse_y(60), 270, 20, stroke=1)
    self.pdf.rect(20, self.inverse_y(60), 400, 20, stroke=1)

    self.pdf.setFont("Helvetica-Bold", 9)
    self.pdf.setFillColor(black)
    self.pdf.drawString(35, self.inverse_y(52), "Invoice #")
    self.pdf.drawString(165, self.inverse_y(52), "Invoice Date")
    self.pdf.drawString(305, self.inverse_y(52), "Total Amount")
    self.pdf.drawString(435, self.inverse_y(52), "Status")

    self.pdf.setFont("Helvetica", 9)
    self.pdf.setFillColorRGB(0.3, 0.3, 0.3)
    self.pdf.drawString(80, self.inverse_y(52), "%s-%d" % (
        self.company.slug, self.number))
    self.pdf.drawString(225, self.inverse_y(52), self.date.strftime(
        "%b %d, %Y"))

    if self.amount_eq:
        if 'RUB' in self.amount_eq:
            self.pdf.drawString(368, self.inverse_y(52), self.amount_eq)
        else:
            self.pdf.drawString(375, self.inverse_y(52), self.amount_eq)
    else:
        if 'RUB' in self.amount:
            self.pdf.drawString(368, self.inverse_y(52), self.amount)
        else:
            self.pdf.drawString(375, self.inverse_y(52), self.amount)

    self.pdf.drawString(475, self.inverse_y(52), "Sent")


def draw_legal_parties_info(self):
    self.pdf.setFont("Helvetica-Bold", 9)
    self.pdf.drawString(25, self.inverse_y(92), "FROM")
    self.pdf.drawString(292, self.inverse_y(92), "TO")

    self.pdf.setFont("Helvetica", 9)

    self.pdf.setFillColorRGB(0.5, 0.5, 0.8)
    self.pdf.drawString(
        25, self.inverse_y(108), self.worker.iv_data.mention_name)
    self.pdf.drawString(
        292, self.inverse_y(108), self.company.iv_data.mention_name)

    self.pdf.setFillColorRGB(0.3, 0.3, 0.3)
    self.pdf.drawString(25, self.inverse_y(124), self.worker.iv_data.address)
    self.pdf.drawString(292, self.inverse_y(124), self.company.iv_data.address)

    self.pdf.setFont("Helvetica-Bold", 9)
    self.pdf.setFillColor(black)
    self.pdf.drawString(25, self.inverse_y(156), "Tax / VAT ID:")
    self.pdf.drawString(292, self.inverse_y(156), "Tax / VAT ID:")
    self.pdf.drawString(25, self.inverse_y(168), "Contact Name:")
    self.pdf.drawString(292, self.inverse_y(168), "Contact Name:")
    self.pdf.drawString(25, self.inverse_y(180), "Phone:")
    self.pdf.drawString(292, self.inverse_y(180), "Phone:")
    self.pdf.drawString(25, self.inverse_y(192), "PayPal:")
    self.pdf.drawString(292, self.inverse_y(192), "PayPal:")

    self.pdf.setFont("Helvetica", 9)
    self.pdf.setFillColorRGB(0.3, 0.3, 0.3)
    self.pdf.drawString(
        90, self.inverse_y(156), self.worker.iv_data.tax_or_vat_id)
    self.pdf.drawString(
        355, self.inverse_y(156), self.company.iv_data.tax_or_vat_id)
    self.pdf.drawString(
        98, self.inverse_y(168), self.worker.iv_data.contact_name)
    self.pdf.drawString(
        362, self.inverse_y(168), self.company.iv_data.contact_name)
    self.pdf.drawString(
        65, self.inverse_y(180), self.worker.iv_data.phone)
    self.pdf.drawString(
        332, self.inverse_y(180), self.company.iv_data.phone)
    self.pdf.drawString(
        65, self.inverse_y(192), self.worker.iv_data.paypal)
    self.pdf.drawString(
        332, self.inverse_y(192), self.company.iv_data.paypal)


def draw_items_header(self):
    self.pdf.setFillColorRGB(0.9, 0.9, 0.9)
    self.pdf.rect(20, self.inverse_y(240), 520, 20, stroke=0, fill=1)

    self.pdf.setFont("Helvetica-Bold", 9)
    self.pdf.setFillColor(black)
    self.pdf.drawString(25, self.inverse_y(232), "Item Description")
    self.pdf.drawString(322, self.inverse_y(232), "Delivery Date")
    self.pdf.drawString(462, self.inverse_y(232), "Line Total")


def draw_item(self, item_number, project, hours, amount, currency,
              hourly_rate):
    self.pdf.setFont("Helvetica", 9)
    self.pdf.setFillColorRGB(0.3, 0.3, 0.3)
    self.pdf.drawString(
        25, self.inverse_y(252 + 42 * (item_number - 1)), project.description)
    self.pdf.drawString(
        25, self.inverse_y(265 + 42 * (item_number - 1)),
        "%d.   Number of Hours: %.2f" % (item_number, hours))

    self.pdf.drawString(
        25, self.inverse_y(278 + 42 * (item_number - 1)),
        "      Hourly Rate: %s" % hourly_rate)

    self.pdf.drawString(
        325, self.inverse_y(265 + 42 * (item_number - 1)),
        self.date.strftime("%b %d, %Y"))

    if currency != 'RUB':
        amount = '%s%.2f' % (currency, amount)
    else:
        amount = '%.2f %s' % (amount, currency)
    self.pdf.drawString(
        465, self.inverse_y(265 + 42 * (item_number - 1)), amount)


def draw_items(self):
    for item_number, project_data in enumerate(self.projects_amount, 1):
        self.draw_item(
            item_number, project_data['project'], project_data['hours'],
            project_data['amount'], project_data['currency'],
            project_data['hourly_rate']
        )
        self.projects_count = item_number - 1


def draw_bonuses(self):
    self.pdf.setFont("Helvetica", 9)
    self.pdf.setFillColorRGB(0.3, 0.3, 0.3)

    if self.bonuses:
        for bonus_number, bonus in enumerate(self.bonuses, 1):
            item_number = self.projects_count + 1 + bonus_number
            self.pdf.drawString(
                25, self.inverse_y(252 + 42 * (item_number - 1)), '[bonuses]')
            if bonus.currency != 'RUB':
                self.pdf.drawString(
                    25, self.inverse_y(265 + 42 * (item_number - 1)),
                    "%d.   Amount: %s%.2f" % (
                        item_number, bonus.currency_sign, bonus.amount))
            else:
                self.pdf.drawString(
                    25, self.inverse_y(265 + 42 * (item_number - 1)),
                    "%d.   Amount: %.2f RUB" % (
                        item_number, bonus.currency_sign, bonus.amount))

            # self.pdf.drawString(
            #     325, self.inverse_y(265 + 42 * (item_number - 1)),
            #     self.date.strftime("%b %d, %Y"))

            # self.pdf.drawString(
            #     465, self.inverse_y(265 + 42 * (item_number - 1)),
            #     "%s%.2f" % (bonus.currency_sign, bonus.amount))


def draw_footer(self):
    shift = self.projects_count + len(self.bonuses)

    self.pdf.setStrokeColor(gray)
    self.pdf.rect(
        290, self.inverse_y(350 + 42 * shift), 250, 60, stroke=1)
    self.pdf.rect(
        290, self.inverse_y(350 + 42 * shift), 250, 20, stroke=1)

    if self.bonuses:
        self.pdf.rect(
            290, self.inverse_y(370 + 42 * shift), 250, 20, stroke=1)

    self.pdf.setFont("Helvetica-Bold", 9)
    self.pdf.setFillColor(black)
    self.pdf.drawString(
        322, self.inverse_y(305 + 42 * shift), "Invoice Total")
    self.pdf.drawString(
        322, self.inverse_y(322 + 42 * shift), "Paid to Date")
    if self.amount_eq:
        if self.bonuses:
            self.pdf.drawString(
                322, self.inverse_y(342 + 42 * shift), "Bonuses")
            self.pdf.drawString(
                322, self.inverse_y(359 + 42 * shift),
                "Balance in %s equivalent" %
                self.get_currency_equivalent_display().upper())

        else:
            self.pdf.drawString(
                322, self.inverse_y(342 + 42 * shift),
                "Balance in %s equivalent" %
                self.get_currency_equivalent_display().upper())
    else:
        self.pdf.drawString(
            322, self.inverse_y(342 + 42 * shift), "Balance")

    self.pdf.setFont("Helvetica", 9)
    self.pdf.setFillColorRGB(0.3, 0.3, 0.3)
    self.pdf.drawString(
        465, self.inverse_y(305 + 42 * shift), self.amount)
    self.pdf.drawString(
        465, self.inverse_y(322 + 42 * shift), self.amount)

    if self.bonuses:
        self.pdf.drawString(
            465, self.inverse_y(342 + 42 * shift),
            '%s%.2f' % (
                self.bonuses[0].currency_sign, self.bonuses[0].amount))

    self.pdf.setFont("Helvetica-Bold", 9)
    self.pdf.setFillColor(black)

    if self.amount_eq:
        if self.bonuses:
            self.pdf.drawString(
                465, self.inverse_y(359 + 42 * shift),
                self.amount_eq)
        else:
            self.pdf.drawString(
                465, self.inverse_y(342 + 42 * shift),
                self.amount_eq)

    else:
        self.pdf.drawString(
            465, self.inverse_y(342 + 42 * shift), self.amount)

    self.pdf.setFont("Helvetica", 9)
    self.pdf.setFillColorRGB(0.3, 0.3, 0.3)
    self.pdf.drawString(10, 10, self.timestamp.strftime('%c %Z'))


def draw(self):
    self.draw_header()
    self.draw_legal_parties_info()
    self.draw_items_header()
    self.draw_items()
    self.draw_bonuses()
    self.draw_footer()


def create_invoice(self):
    self.draw()
    self.pdf.showPage()
    self.pdf.save()
    return '/media/invoices/' + self.title
