import sys
from datetime import date
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QFormLayout, 
                             QLineEdit, QDoubleSpinBox, QDateEdit, QPushButton, 
                             QLabel, QComboBox, QGroupBox, QMessageBox, QCheckBox, QHBoxLayout)
from PyQt6.QtCore import Qt, QDate

class StartupCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kalkulator (Netto/Brutto + Multi-Dilution)")
        self.resize(550, 850)
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        finance_group = QGroupBox("1. Dane Finansowe i Wycena Firmy")
        finance_layout = QFormLayout()
        
        self.eur_rate_input = QDoubleSpinBox()
        self.eur_rate_input.setRange(0.01, 100.0)
        self.eur_rate_input.setValue(4.30)
        self.eur_rate_input.setSuffix(" PLN")
        finance_layout.addRow("Kurs EUR/PLN:", self.eur_rate_input)

        self.pre_seed_input = QDoubleSpinBox()
        self.pre_seed_input.setRange(0, 10_000_000_000)
        self.pre_seed_input.setValue(20_000_000)
        self.pre_seed_input.setSuffix(" €")
        self.pre_seed_input.setGroupSeparatorShown(True)
        finance_layout.addRow("Wycena Pre-Seed (Post-Money):", self.pre_seed_input)

        self.series_a_input = QDoubleSpinBox()
        self.series_a_input.setRange(0, 10_000_000_000)
        self.series_a_input.setValue(200_000_000)
        self.series_a_input.setSuffix(" €")
        self.series_a_input.setGroupSeparatorShown(True)
        finance_layout.addRow("Wycena Series A (Post-Money):", self.series_a_input)

        self.valuation_choice = QComboBox()
        self.valuation_choice.addItems(["Użyj wyceny Pre-Seed", "Użyj wyceny Series A"])
        self.valuation_choice.setCurrentIndex(1)
        finance_layout.addRow("Baza obliczeń (Wartość firmy):", self.valuation_choice)

        finance_group.setLayout(finance_layout)
        main_layout.addWidget(finance_group)

        work_group = QGroupBox("2. Twoje Udziały i Praca")
        work_layout = QFormLayout()

        self.shares_input = QDoubleSpinBox()
        self.shares_input.setRange(0, 100)
        self.shares_input.setValue(0.15)
        self.shares_input.setSuffix(" %")
        work_layout.addRow("Posiadane udziały (Start):", self.shares_input)

        self.hourly_wage_input = QDoubleSpinBox()
        self.hourly_wage_input.setRange(0, 10000)
        self.hourly_wage_input.setValue(100)
        self.hourly_wage_input.setSuffix(" PLN")
        work_layout.addRow("Stawka godzinowa:", self.hourly_wage_input)

        self.hours_month_input = QDoubleSpinBox()
        self.hours_month_input.setRange(0, 744)
        self.hours_month_input.setValue(160)
        work_layout.addRow("Godziny w miesiącu:", self.hours_month_input)

        work_group.setLayout(work_layout)
        main_layout.addWidget(work_group)

        tax_group = QGroupBox("3. Opcje Podatkowe")
        tax_layout = QFormLayout()

        self.tax_enabled = QCheckBox("Uwzględnij podatki w wynikach")
        self.tax_enabled.setChecked(True)
        self.tax_enabled.stateChanged.connect(self.toggle_tax_inputs)
        tax_layout.addRow(self.tax_enabled)

        self.salary_tax_combo = QComboBox()
        self.salary_tax_combo.addItems([
            "Brak (0%)", 
            "B2B Ryczałt IT (12%)", 
            "B2B Liniowy (19%)", 
            "Umowa o Pracę (est. 30%)"
        ])
        self.salary_tax_combo.currentIndexChanged.connect(self.update_salary_tax_rate)
        
        self.salary_tax_rate = QDoubleSpinBox()
        self.salary_tax_rate.setRange(0, 100)
        self.salary_tax_rate.setSuffix(" %")
        self.salary_tax_rate.setValue(12.0) 
        
        tax_row_salary = QHBoxLayout()
        tax_row_salary.addWidget(self.salary_tax_combo)
        tax_row_salary.addWidget(QLabel("Własna stawka:"))
        tax_row_salary.addWidget(self.salary_tax_rate)
        tax_layout.addRow("Podatek - Praca:", tax_row_salary)

        self.shares_tax_combo = QComboBox()
        self.shares_tax_combo.addItems(["Brak (0%)", "Podatek Belki (19%)"])
        self.shares_tax_combo.setCurrentIndex(1)
        self.shares_tax_combo.currentIndexChanged.connect(self.update_shares_tax_rate)

        self.shares_tax_rate = QDoubleSpinBox()
        self.shares_tax_rate.setRange(0, 100)
        self.shares_tax_rate.setSuffix(" %")
        self.shares_tax_rate.setValue(19.0)

        tax_row_shares = QHBoxLayout()
        tax_row_shares.addWidget(self.shares_tax_combo)
        tax_row_shares.addWidget(QLabel("Własna stawka:"))
        tax_row_shares.addWidget(self.shares_tax_rate)
        tax_layout.addRow("Podatek - Udziały:", tax_row_shares)

        tax_group.setLayout(tax_layout)
        main_layout.addWidget(tax_group)

        time_group = QGroupBox("4. Oś Czasu")
        time_layout = QFormLayout()

        self.exit_date_input = QDateEdit()
        self.exit_date_input.setDate(QDate.currentDate().addYears(2))
        self.exit_date_input.setCalendarPopup(True)
        time_layout.addRow("Data potencjalnego wykupu:", self.exit_date_input)

        time_group.setLayout(time_layout)
        main_layout.addWidget(time_group)

        dilution_group = QGroupBox("5. Symulacja Rozwodnienia (Inwestorzy)")
        dilution_layout = QFormLayout()
        
        self.dilution_seed_cb = QCheckBox("Runda Pre-Seed / Seed")
        self.dilution_seed_cb.toggled.connect(self.toggle_dilution_inputs)
        dilution_layout.addRow(self.dilution_seed_cb)

        self.seed_invest_input = QDoubleSpinBox()
        self.seed_invest_input.setRange(0, 10_000_000_000)
        self.seed_invest_input.setValue(3_000_000)
        self.seed_invest_input.setSuffix(" €")
        self.seed_invest_input.setGroupSeparatorShown(True)
        self.seed_invest_input.setEnabled(False)
        dilution_layout.addRow("   Kwota Inwestycji Seed:", self.seed_invest_input)

        self.dilution_series_a_cb = QCheckBox("Runda Series A")
        self.dilution_series_a_cb.toggled.connect(self.toggle_dilution_inputs)
        dilution_layout.addRow(self.dilution_series_a_cb)

        self.series_a_invest_input = QDoubleSpinBox()
        self.series_a_invest_input.setRange(0, 10_000_000_000)
        self.series_a_invest_input.setValue(2_000_000)
        self.series_a_invest_input.setSuffix(" €")
        self.series_a_invest_input.setGroupSeparatorShown(True)
        self.series_a_invest_input.setEnabled(False)
        dilution_layout.addRow("   Kwota Inwestycji Serii A:", self.series_a_invest_input)

        dilution_group.setLayout(dilution_layout)
        main_layout.addWidget(dilution_group)

        self.calc_button = QPushButton("Oblicz Wynik Netto")
        self.calc_button.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px; font-size: 14px;")
        self.calc_button.clicked.connect(self.calculate_results)
        main_layout.addWidget(self.calc_button)

        self.result_label = QLabel("Wprowadź dane i kliknij Oblicz.")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet("font-size: 13px; margin-top: 5px;")
        self.result_label.setWordWrap(True)
        main_layout.addWidget(self.result_label)

    def toggle_tax_inputs(self):
        state = self.tax_enabled.isChecked()
        self.salary_tax_combo.setEnabled(state)
        self.salary_tax_rate.setEnabled(state)
        self.shares_tax_combo.setEnabled(state)
        self.shares_tax_rate.setEnabled(state)
        self.calc_button.setText("Oblicz Wynik Netto" if state else "Oblicz Wynik Brutto")

    def toggle_dilution_inputs(self):
        self.seed_invest_input.setEnabled(self.dilution_seed_cb.isChecked())
        self.series_a_invest_input.setEnabled(self.dilution_series_a_cb.isChecked())

    def update_salary_tax_rate(self):
        idx = self.salary_tax_combo.currentIndex()
        if idx == 0: self.salary_tax_rate.setValue(0.0)
        elif idx == 1: self.salary_tax_rate.setValue(12.0)
        elif idx == 2: self.salary_tax_rate.setValue(19.0)
        elif idx == 3: self.salary_tax_rate.setValue(30.0)

    def update_shares_tax_rate(self):
        idx = self.shares_tax_combo.currentIndex()
        if idx == 0: self.shares_tax_rate.setValue(0.0)
        elif idx == 1: self.shares_tax_rate.setValue(19.0)

    def calculate_results(self):
        eur_rate = self.eur_rate_input.value()
        pre_seed_val = self.pre_seed_input.value()
        series_a_val = self.series_a_input.value()
        
        if self.valuation_choice.currentIndex() == 0:
            valuation_at_exit = pre_seed_val
            val_name = "Pre-Seed"
        else:
            valuation_at_exit = series_a_val
            val_name = "Series A"

        initial_share_percent = self.shares_input.value()
        current_share_percent = initial_share_percent
        dilution_info_html = ""
        
        dilution_steps = []

        if self.dilution_seed_cb.isChecked():
            inv = self.seed_invest_input.value()
            if inv >= pre_seed_val:
                QMessageBox.warning(self, "Błąd", "Inwestycja Seed nie może być większa niż wycena Pre-Seed!")
                return
            ratio = inv / pre_seed_val
            current_share_percent = current_share_percent * (1 - ratio)
            dilution_steps.append(f"Seed (-{ratio*100:.1f}%)")

        if self.dilution_series_a_cb.isChecked():
            inv = self.series_a_invest_input.value()
            if inv >= series_a_val:
                QMessageBox.warning(self, "Błąd", "Inwestycja Series A nie może być większa niż wycena Series A!")
                return
            ratio = inv / series_a_val
            current_share_percent = current_share_percent * (1 - ratio)
            dilution_steps.append(f"Seria A (-{ratio*100:.1f}%)")

        if dilution_steps:
            dilution_str = " -> ".join(dilution_steps)
            dilution_info_html = (
                f"<br><span style='font-size:11px; color:#e67e22'>"
                f"Rozwodnienie: {dilution_str}<br>"
                f"Twoje udziały: <b>{initial_share_percent}% &rarr; {current_share_percent:.4f}%</b>"
                f"</span>"
            )

        hourly_wage = self.hourly_wage_input.value()
        avg_hours = self.hours_month_input.value()
        
        today = date.today()
        exit_date_q = self.exit_date_input.date()
        exit_date = date(exit_date_q.year(), exit_date_q.month(), exit_date_q.day())

        if exit_date <= today:
            QMessageBox.warning(self, "Błąd", "Data wykupu musi być w przyszłości!")
            return

        delta_days = (exit_date - today).days
        months_to_exit = delta_days / 30.44
        
        salary_gross = months_to_exit * avg_hours * hourly_wage
        
        shares_gross_pln = (valuation_at_exit * (current_share_percent / 100.0)) * eur_rate
        total_gross = salary_gross + shares_gross_pln

        if self.tax_enabled.isChecked():
            sal_tax_rate = self.salary_tax_rate.value() / 100.0
            shr_tax_rate = self.shares_tax_rate.value() / 100.0
            
            salary_net = salary_gross * (1 - sal_tax_rate)
            shares_net = shares_gross_pln * (1 - shr_tax_rate)
            total_net = salary_net + shares_net
            is_net = True
        else:
            salary_net = salary_gross
            shares_net = shares_gross_pln
            total_net = total_gross
            is_net = False

        color_main = "#27ae60" if is_net else "#2c3e50"
        title_type = "NETTO (na rękę)" if is_net else "BRUTTO"

        res_html = (
            f"<h3 style='color:{color_main}'>Wynik Symulacji: {title_type}</h3>"
            f"Exit: {val_name} | Czas: {months_to_exit:.1f} msc<hr>"
            
            f"<b>1. Pensja:</b> <span style='font-size:14px'>{salary_net:,.2f} PLN</span> "
            f"<span style='color:gray; font-size:10px'>(Brutto: {salary_gross:,.0f})</span><br>"
            
            f"<b>2. Udziały:</b> <span style='font-size:14px'>{shares_net:,.2f} PLN</span> "
            f"<span style='color:gray; font-size:10px'>(Brutto: {shares_gross_pln:,.0f})</span>"
            f"{dilution_info_html}"
            f"<br><br>"
            
            f"<div style='background-color:#f0f0f0; padding:10px; border-radius:5px;'>"
            f"<span style='font-size:16px; font-weight:bold; color:{color_main}'>"
            f"RAZEM DO RĘKI: {total_net:,.2f} PLN"
            f"</span></div>"
        )
        
        res_html = res_html.replace(",", " ")
        self.result_label.setText(res_html)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = StartupCalculator()
    window.show()
    sys.exit(app.exec())
