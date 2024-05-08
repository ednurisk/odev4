import sys
import sqlite3
from PyQt5 import QtWidgets, QtGui ,QtCore
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QFileDialog, QDialog, QLineEdit, QLabel, QHBoxLayout
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Veritabanı bağlantısı kurma
def create_connection():
    conn = sqlite3.connect("users.db")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )
    """)
    return conn

# Giriş ve kayıt penceresi
class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.conn = create_connection()
        self.initUI()

    def initUI(self):
        # Pencere boyutları ayarlanıyor
        self.setGeometry(100, 100, 400, 200)
        self.setWindowTitle("Giriş Yap / Kayıt Ol")

        layout = QtWidgets.QVBoxLayout()

        self.username_label = QtWidgets.QLabel("Kullanıcı Adı:")
        self.username_input = QtWidgets.QLineEdit()

        self.password_label = QtWidgets.QLabel("Şifre:")
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        self.login_button = QtWidgets.QPushButton("Giriş Yap")
        self.login_button.clicked.connect(self.handle_login)

        self.signup_button = QtWidgets.QPushButton("Kayıt Ol")
        self.signup_button.clicked.connect(self.handle_signup)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.signup_button)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cur.fetchone()

        if user:
            self.open_main_window(username)  # Kullanıcı adını ilet
        else:
            QtWidgets.QMessageBox.warning(self, "Hata", "Kullanıcı adı veya şifre yanlış.")

    def handle_signup(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()

        if user:
            QtWidgets.QMessageBox.warning(self, "Hata", "Kullanıcı zaten var.")
        else:
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            self.conn.commit()
            print("Kayıtlı kullanıcılar:")
            for row in cur.execute("SELECT * FROM users"):
                print(row)
            QtWidgets.QMessageBox.information(self, "Başarılı", "Kayıt başarılı.")

    def open_main_window(self, username):
        self.main_window = MainMenu(username)  # Kullanıcı adını ilet
        self.main_window.show()
        self.close()

# Ana menü penceresi
class MainMenu(QtWidgets.QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 400, 200)
        self.setWindowTitle("Ana Menü")

        layout = QtWidgets.QVBoxLayout()

        self.compare_button = QtWidgets.QPushButton("Karşılaştır")
        self.compare_button.clicked.connect(self.show_comparison_menu)
        
        self.operations_button = QtWidgets.QPushButton("İşlemler")
        self.operations_button.clicked.connect(self.open_operations_menu)

        self.exit_button = QtWidgets.QPushButton("Çıkış")
        self.exit_button.clicked.connect(self.close)

        layout.addWidget(self.compare_button)
        layout.addWidget(self.operations_button)
        layout.addWidget(self.exit_button)

        self.setLayout(layout)



    def show_comparison_menu(self):
        menu = QtWidgets.QMenu()

        compare_x_action = menu.addAction("Metin X algoritması kullanarak karşılaştır")
        compare_x_action.triggered.connect(lambda: self.open_comparison_window("X"))

        compare_y_action = menu.addAction("Metin Y algoritması kullanarak karşılaştır")
        compare_y_action.triggered.connect(lambda: self.open_comparison_windowY("Y"))

        menu.exec_(QtGui.QCursor.pos())

    def open_comparison_window(self, algorithm_type):
        comparison_window = ComparisonWindow(algorithm_type)
        comparison_window.exec_()

    def open_comparison_windowY(self, algorithm_type):
        comparison_window = ComparisonWindowY(algorithm_type)
        comparison_window.exec_()


    def open_operations_menu(self):
        self.operations_window = OperationsMenu(self.username)  # Kullanıcı adını ilet
        self.operations_window.show()



#karsilastir menüsü x için
class ComparisonWindow(QDialog):
    def __init__(self, comparison_algorithm):
        super().__init__()
        self.comparison_algorithm = comparison_algorithm
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()

        # İlk dosya için text box ve dosya seç butonu
        self.file1_input = QLineEdit(self)
        self.file1_button = QPushButton("Dosya Seç", self)
        self.file1_button.clicked.connect(self.select_file1)
        file1_layout = QHBoxLayout()
        file1_layout.addWidget(self.file1_input)
        file1_layout.addWidget(self.file1_button)
        layout.addLayout(file1_layout)

        # İkinci dosya için text box ve dosya seç butonu
        self.file2_input = QLineEdit(self)
        self.file2_button = QPushButton("Dosya Seç", self)
        self.file2_button.clicked.connect(self.select_file2)
        file2_layout = QHBoxLayout()
        file2_layout.addWidget(self.file2_input)
        file2_layout.addWidget(self.file2_button)
        layout.addLayout(file2_layout)

        # Karşılaştırma butonu ve sonuç ekranı
        self.compare_button = QPushButton("Karşılaştır", self)
        self.compare_button.clicked.connect(self.compare_files)
        layout.addWidget(self.compare_button)

        self.result_label = QLabel("", self)
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def select_file1(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Birinci Dosyayı Seç", "", "Text Files (*.txt);;All Files (*)", options=options)
        if filename:
            self.file1_input.setText(filename)

    def select_file2(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "İkinci Dosyayı Seç", "", "Text Files (*.txt);;All Files (*)", options=options)
        if filename:
            self.file2_input.setText(filename)

    def compare_files(self):
        file1_path = self.file1_input.text()
        file2_path = self.file2_input.text()

        try:
            # Dosyaları oku
            with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
                content1 = f1.read()
                content2 = f2.read()

            # Uzunluk farkını hesapla
            uzunluk_farki = abs(len(content1) - len(content2))

            # Uzunluk farkına göre kısa metni uzat
            if len(content1) > len(content2):
                content2 += " " * uzunluk_farki
            else:
                content1 += " " * uzunluk_farki

            # Hataları say ve benzerlik oranını hesapla
            hatalar = 0
            for char1, char2 in zip(content1, content2):
                if char1 != char2:
                    hatalar += 1

            # Benzerlik oranını hesapla
            uzun_metni_sec = content1 if len(content1) > len(content2) else content2
            benzerlik_orani = (len(uzun_metni_sec) - hatalar) / len(uzun_metni_sec)

            # Sonucu etikete yaz
            self.result_label.setText(f"Benzerlik Oranı: {benzerlik_orani:.2%}")

        except Exception as e:
            self.result_label.setText(f"Hata: {str(e)}")



#karsilastir menüsü y için
class ComparisonWindowY(QDialog):
    def __init__(self, comparison_algorithm):
        super().__init__()
        self.comparison_algorithm = comparison_algorithm
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()

        # İlk dosya için text box ve dosya seç butonu
        self.file1_input = QLineEdit(self)
        self.file1_button = QPushButton("Dosya Seç", self)
        self.file1_button.clicked.connect(self.select_file1)
        file1_layout = QHBoxLayout()
        file1_layout.addWidget(self.file1_input)
        file1_layout.addWidget(self.file1_button)
        layout.addLayout(file1_layout)

        # İkinci dosya için text box ve dosya seç butonu
        self.file2_input = QLineEdit(self)
        self.file2_button = QPushButton("Dosya Seç", self)
        self.file2_button.clicked.connect(self.select_file2)
        file2_layout = QHBoxLayout()
        file2_layout.addWidget(self.file2_input)
        file2_layout.addWidget(self.file2_button)
        layout.addLayout(file2_layout)

        # Karşılaştırma butonu ve sonuç ekranı
        self.compare_button = QPushButton("Karşılaştır", self)
        self.compare_button.clicked.connect(self.compare_files)
        layout.addWidget(self.compare_button)

        self.result_label = QLabel("", self)
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def select_file1(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Birinci Dosyayı Seç", "", "Text Files (*.txt);;All Files (*)", options=options)
        if filename:
            self.file1_input.setText(filename)

    def select_file2(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "İkinci Dosyayı Seç", "", "Text Files (*.txt);;All Files (*)", options=options)
        if filename:
            self.file2_input.setText(filename)

    def compare_files(self):
        file1_path = self.file1_input.text()
        file2_path = self.file2_input.text()

        try:
            # Dosyaları oku
            with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
                content1 = f1.read()
                content2 = f2.read()
            
            texts = [content1, content2]
                        # TF-IDF vektörizerini özelleştirerek boş sonuçları önleme
            tfidf_vectorizer = TfidfVectorizer(min_df=1, max_df=1.0, stop_words=None)
            tfidf_matrix = tfidf_vectorizer.fit_transform(texts)

            # TF-IDF matrisini ve kosinüs benzerliğini kontrol etme
            print("TF-IDF Matrisinin Şekli:", tfidf_matrix.shape)
            print("TF-IDF Matrisinin İçeriği:")
            print(tfidf_matrix.toarray())

            cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            # Sonucu etikete yaz
            self.result_label.setText(f"Cosinus Benzerlik Oranı: {cosine_similarities[0][0]}")

        except Exception as e:
            self.result_label.setText(f"Hata: {str(e)}")



# İşlemler menüsü
class OperationsMenu(QtWidgets.QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 400, 200)
        self.setWindowTitle("İşlemler")

        layout = QtWidgets.QVBoxLayout()

        self.password_menu = QtWidgets.QPushButton("Şifre")
        self.password_menu.clicked.connect(self.open_password_menu)

        layout.addWidget(self.password_menu)

        self.setLayout(layout)

    def open_password_menu(self):
        self.password_window = PasswordMenu(self.username)  # Kullanıcı adını ilet
        self.password_window.show()

# Şifre güncelleme ekranı
class PasswordMenu(QtWidgets.QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.conn = create_connection()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 400, 200)
        self.setWindowTitle("Şifre Değiştir")

        layout = QtWidgets.QVBoxLayout()

        self.current_password_label = QtWidgets.QLabel("Mevcut Şifre:")
        self.current_password_input = QtWidgets.QLineEdit()
        self.current_password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        self.new_password_label = QtWidgets.QLabel("Yeni Şifre:")
        self.new_password_input = QtWidgets.QLineEdit()
        self.new_password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        self.change_password_button = QtWidgets.QPushButton("Değiştir")
        self.change_password_button.clicked.connect(self.handle_password_change)

        layout.addWidget(self.current_password_label)
        layout.addWidget(self.current_password_input)
        layout.addWidget(self.new_password_label)
        layout.addWidget(self.new_password_input)
        layout.addWidget(self.change_password_button)

        self.setLayout(layout)

    def handle_password_change(self):
        current_password = self.current_password_input.text().strip()
        new_password = self.new_password_input.text().strip()

        cur = self.conn.cursor()

        # Mevcut şifrenin doğruluğunu kontrol edin
        cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (self.username, current_password))
        user = cur.fetchone()

        if not user:
            QtWidgets.QMessageBox.warning(self, "Hata", "Mevcut şifre yanlış.")
            return

        # Şifreyi güncelle
        cur.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, self.username))
        self.conn.commit()

        # Terminalde güncellenen şifreyi göster
        print("Güncellenen şifreler:")
        for row in cur.execute("SELECT * FROM users"):
            print(row)

        QtWidgets.QMessageBox.information(self, "Başarılı", "Şifre başarıyla değiştirildi.")

# Uygulamayı çalıştırma
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
