from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import re
import os

class BibleScraper:
    def __init__(self):
        self.setup_driver()
        self.results_dir = "bible_kirundi_versets"
        os.makedirs(self.results_dir, exist_ok=True)
        self.seen_verses = set()

        # Noms des livres en kirundi
        self.books_kirundi = [
            "Itanguriro", "Kuvayo", "Abalewi", "Guharura", "Gusubira mu vyagezwe",
            "Yosuwa", "Abacamanza", "Rusi", "Samweli wa mbere", "Samweli wa kabiri",
            "Abami ba mbere", "Abami ba kabiri", "Ngoma za mbere", "Ngoma za kabiri", "Ezira", "Nehemiya",
            "Esiteri", "Yobu", "Zaburi", "Imigani", "Umusiguzi", "Indirimbo ya Salomo",
            "Yesaya", "Yeremiya", "Gucura intimba", "Ezekiyeli", "Daniyeli", "Hoseya",
            "Yoweli", "Amosi", "Obadiya", "Yona", "Mika", "Nahumu", "Habakuki",
            "Zefaniya", "Hagayi", "Zakariya", "Malaki", "Matayo", "Mariko",
            "Luka", "Yohani", "Ivyakozwe n intumwa", "Abaroma", "Abakorinto ba mbere", "Abakorinto ba kabiri",
            "Abagalatiya", "Abanyefeso", "Abafilipi", "Abakolosayi", "Abatesalonika ba mbere", "Abatesalonika ba kabiri",
            "Timoteyo wa mbere", "Timoteyo wa kabiri", "Tito", "Filemoni", "Abaheburayo", "Ikete rya Yakobo",
            "Petero wa mbere", "Petero wa kabiri", "Yohani wa mbere", "Yohani wa kabiri", "Yohani wa gatatu", "Ikete rya Yuda",
            "Ivyahishuriwe Yohani"
        ]

        # Nombre de chapitres par livre (Genèse à Apocalypse)
        self.chapters_per_book = [
        50, 40, 27, 36, 34, 24, 21, 4, 31, 24,
        22, 25, 29, 36, 10, 13, 10, 42, 150, 31,
        12, 8, 66, 52, 5, 48, 12, 14, 3, 9,
        1, 4, 7, 3, 3, 3, 2, 14, 4, 28,
        16, 24, 21, 28, 16, 16, 13, 6, 6, 4,
        4, 5, 3, 6, 4, 3, 1, 13, 5, 5, 3, 5, 1, 1, 1, 22
        ]

    def setup_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.implicitly_wait(10)

    def wait_for_content_load(self, timeout=30):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.v"))
            )
            self.scroll_to_load_content()
            time.sleep(2)
            return True
        except TimeoutException:
            print("⚠️ Timeout en attendant le contenu")
            return False

    def scroll_to_load_content(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def extract_verse_number_and_text_js(self):
        """Extraire tous les versets via JavaScript"""
        verses_js = self.driver.execute_script('''
            let verses = [];
            document.querySelectorAll("span.v").forEach(el => {
                let text = el.innerText.trim();
                if (text) verses.push(text);
            });
            return verses;
        ''')
        return verses_js

    def parse_verse(self, verse_text):
        """Analyse robuste du verset avec gestion des formats variés"""
        verse_text = verse_text.strip()
        if not verse_text:
            return None, None

        # Essayer plusieurs motifs possibles
        patterns = [
            r'^(\d+)[\.\)\]\*\s]+(.+)$',          # "1. Texte"
            r'^(\d+)(?:[a-zA-Z]?)\s+(.+)$',       # "1 Texte"
            r'.*?(\d+)[\.\)\]\*\s]+(.+)$',        # "Texte 1. ..."
            r'([a-zA-Z])\s+(\d+)[\.\)\]\*\s]+(.+)$',  # "a 1. Texte"
        ]

        for pattern in patterns:
            match = re.match(pattern, verse_text, re.DOTALL)
            if match:
                if pattern.startswith(r'^'):
                    verse_num = int(match.group(1))
                    verse_text_cleaned = match.group(2).strip()
                else:
                    verse_num = int(match.group(2)) if len(match.groups()) == 3 else int(match.group(1))
                    verse_text_cleaned = match.group(3).strip() if len(match.groups()) == 3 else match.group(2).strip()
                cleaned_text = self.clean_verse_text(verse_text_cleaned)
                if len(cleaned_text) > 5:
                    return verse_num, cleaned_text

        # Dernière tentative : extraire le numéro quelque part dans le texte
        verse_num_guess = re.search(r'\b(\d+)\b', verse_text[:40])
        if verse_num_guess:
            verse_num = int(verse_num_guess.group(1))
            cleaned_text = self.clean_verse_text(re.sub(str(verse_num), '', verse_text, count=1).strip())
            if cleaned_text and len(cleaned_text) > 5:
                return verse_num, cleaned_text

        return None, None

    def clean_verse_text(self, text):
        text = re.sub(r'\s*[\(\[]([^)\]]*?)[\)\]]\s*', ' ', text)
        text = re.sub(r'[+*†‡§¶#]', '', text)
        text = re.sub(r'\s+[a-z]\s+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def scrape_chapter(self, book_id, chapter):
        url = f"https://wol.jw.org/run/wol/b/r82/lp-ru/nwt/{book_id}/{chapter}#study=discover"  
        print(f"\n📖 Scraping chapitre {chapter} (Livre {book_id})...")
        print(f"🔗 URL: {url}")
        try:
            self.driver.get(url)
            print("⏳ Chargement de la page...")

            if not self.wait_for_content_load():
                print("❌ Échec du chargement du contenu")
                return []

            raw_verses = self.extract_verse_number_and_text_js()
            if not raw_verses or len(raw_verses) < 1:
                print("❌ Aucun verset trouvé ou incomplet")
                return []

            verses_data = []
            seen_verses = set()

            # Réinitialiser à chaque chapitre
            self.seen_verses.clear()

            for idx, verse_text in enumerate(raw_verses):
                verse_num, cleaned_text = self.parse_verse(verse_text)
                if verse_num and cleaned_text and cleaned_text not in seen_verses:
                    seen_verses.add(cleaned_text)
                    verses_data.append((verse_num, cleaned_text))

            verses_data.sort(key=lambda x: x[0])
            return verses_data
        except Exception as e:
            print(f"❌ Erreur chapitre {chapter}: {e}")
            return []

    def save_book_results(self, book_id, book_name, all_verses):
        try:
            markdown = f"# {book_name}\n"
            markdown += f"*{len(all_verses)} inyandiko*\n"
            markdown += f"*Itariki: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n\n"

            for verse_num, verse_text in all_verses:
                markdown += f"**{verse_num}.** {verse_text}\n\n"

            filename = f"{self.results_dir}/{book_name.replace(' ', '_')}.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(markdown)
            print(f"💾 Fichier sauvegardé: {filename}")
            return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde livre {book_name}: {e}")
            return False

    def run_full_scraping(self):
        print("🌟 SCRAPING BIBLE KIRUNDI - VERSION FINALE")
        print("=" * 60)
        failed_books = {}
        total_books = 0
        total_verses = 0

        for book_id in range(1, 67):  # 66 livres
            book_name = self.books_kirundi[book_id - 1]
            max_chapters = self.chapters_per_book[book_id - 1]

            print(f"\n📚 LIVRE {book_id} : {book_name}")
            print(f"📘 Ce livre a {max_chapters} chapitres")

            all_verses = []
            failed_chapters = []

            for chapter in range(1, max_chapters + 1):
                print(f"📍 Chapitre {chapter}/{max_chapters}...")
                verses = self.scrape_chapter(book_id, chapter)
                if verses:
                    all_verses.extend(verses)
                else:
                    failed_chapters.append(chapter)
                    print(f"❌ Chapitre {chapter} a échoué")
                time.sleep(2)

            if all_verses:
                success = self.save_book_results(book_id, book_name, all_verses)
                if success:
                    total_books += 1
                    total_verses += len(all_verses)

            if failed_chapters:
                failed_books[book_name] = failed_chapters

        print(f"\n🏁 SCRAPING TERMINÉ!")
        print(f"✅ Livres réussis: {total_books}/66")
        print(f"📖 Total versets extraits: {total_verses}")
        self.create_summary_report(total_books, total_verses, failed_books)

    def create_summary_report(self, total_books, total_verses, failed_books):
        report = "# Rapport de Scraping - Bible Kirundi (Tout les livres)\n"
        report += "## Résumé Global\n"
        report += f"- **Date du scraping**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"- **Livres réussis**: {total_books}/66\n"
        report += f"- **Total versets extraits**: {total_verses}\n"

        report += "\n## Livres ayant échoué\n"
        if failed_books:
            for book, chapters in failed_books.items():
                report += f"- **{book}** : chapitres ratés → {chapters}\n"
        else:
            report += "- ✅ Aucun livre n'a complètement échoué\n"

        report += "\n## Détails par Livre\n"
        report += "| Livre | Versets | Statut |\n"
        report += "|-------|---------|--------|\n"

        for i, book_name in enumerate(self.books_kirundi):
            file_path = f"{self.results_dir}/{book_name.replace(' ', '_')}.md"
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    verse_count = len(re.findall(r'\*\*(\d+)\.\*\*', content))
                    status = "✅ Réussi"
            report += f"| {book_name} | {verse_count} | {status} |\n"
        else:
            verse_count = 0
            status = "❌ Échec"
            report += f"| {book_name} | {verse_count} | {status} |\n"

        with open(f"{self.results_dir}/RAPPORT_SCRAPING_BIBLE.md", "w", encoding="utf-8") as f:
            f.write(report)
        print("📋 Rapport détaillé créé: RAPPORT_SCRAPING_BIBLE.md")

    def close(self):
        if hasattr(self, 'driver'):
            self.driver.quit()
            print("🔧 Navigateur fermé")


def main():
    scraper = None
    try:
        scraper = BibleScraper()
        scraper.run_full_scraping()
    except KeyboardInterrupt:
        print("\n⏹️ Arrêt par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
    finally:
        if scraper:
            scraper.close()


if __name__ == "__main__":
    main()